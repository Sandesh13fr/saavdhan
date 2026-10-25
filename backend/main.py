from __future__ import annotations

import hashlib
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import storage, telemetry, auth
from .agent import RA_LIST_DATE, analyze
from .exports import packet_zip
from .fixtures import DEMO_OFFERS
from .ingest import ingest_bytes, MAX_FILE_BYTES, ocr_available
from .providers import provider_available
from .rules import FEE_CAP_INR, RULES
from .reports import aggregate, synthetic_reports
from . import safety
from .models import SafetyPlan

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1]/".env",override=False)
except ImportError:
    pass

@asynccontextmanager
async def lifespan(app):
    if os.getenv("SAAVDHAN_ENV", "local") not in {"local","production"}:
        raise RuntimeError("SAAVDHAN_ENV must be local or production")
    if auth.production() and not os.getenv("SAAVDHAN_PUBLIC_ORIGIN", "").startswith("https://"):
        raise RuntimeError("Production requires SAAVDHAN_PUBLIC_ORIGIN with HTTPS")
    if auth.production() and len(os.getenv("SAAVDHAN_HASH_SALT", ""))<16:
        raise RuntimeError("Production requires SAAVDHAN_HASH_SALT (16+ characters)")
    yield


app=FastAPI(title="Saavdhan",version="0.1.0",description="Check an overseas job offer against India's emigration rules. Nothing is sent or reported automatically.", lifespan=lifespan)
TRUSTED_HOSTS = {"localhost", "127.0.0.1", "[::1]", "testserver"}
TRUSTED_HOSTS.update(h.strip() for h in os.getenv("SAAVDHAN_ALLOWED_HOSTS", "").split(",") if h.strip())
app.add_middleware(TrustedHostMiddleware, allowed_hosts=sorted(TRUSTED_HOSTS), www_redirect=False)


@app.middleware("http")
async def session_guard(request: Request, call_next):
    identity = auth.session(request.cookies.get("saavdhan_session"))
    mutation = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    origin = request.headers.get("origin")
    if auth.production() and request.url.path == "/api/auth/login" and mutation and origin != os.getenv("SAAVDHAN_PUBLIC_ORIGIN"):
        return Response("Same-origin login required", status_code=403)
    if mutation and origin:
        expected = os.getenv("SAAVDHAN_PUBLIC_ORIGIN") if auth.production() else str(request.base_url).rstrip("/")
        if origin.rstrip("/") != expected:
            return Response("Cross-origin mutation rejected", status_code=403)
    path = request.url.path
    if path.startswith("/api/") and path not in {"/api/health", "/api/auth/login", "/api/auth/me"}:
        # Offer checks are anonymous; only the authority pattern map needs an account.
        if path.startswith("/api/reports/") and not identity:
            return Response("Sign in required", status_code=401)
        if identity and mutation and not __import__("hmac").compare_digest(request.headers.get("x-csrf-token", ""), identity["csrf_token"]):
            return Response("CSRF token required", status_code=403)
        if identity and mutation and identity["user"]["role"] == "viewer" and path != "/api/auth/logout":
            return Response("Read-only account", status_code=403)
    user_token = auth.USER.set(identity["user"] if identity else None)
    tenant_token = storage.TENANT.set(identity["user"]["tenant_id"] if identity else "local-demo")
    try:
        response = await call_next(request)
        if path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        auth.USER.reset(user_token)
        storage.TENANT.reset(tenant_token)


RATE_WINDOW_SECONDS, RATE_MAX = 600, int(os.getenv("SAAVDHAN_RATE_MAX", "30"))
_hits: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    # ponytail: in-process per-IP limit on case creation; use the proxy/Redis limiter if scaled out
    path = request.url.path
    if request.method == "POST" and (path == "/api/offers" or path.startswith("/api/demo/offers/")):
        now = __import__("time").monotonic()
        key = request.client.host if request.client else "unknown"
        recent = [t for t in _hits.get(key, []) if now - t < RATE_WINDOW_SECONDS]
        if len(recent) >= RATE_MAX:
            return Response("Too many offer checks; try again in a few minutes", status_code=429)
        _hits[key] = recent + [now]
    return await call_next(request)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.tile.openstreetmap.org; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if auth.production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.get("/api/auth/me")
def auth_me(request: Request):
    identity = auth.session(request.cookies.get("saavdhan_session"))
    return {"authenticated": bool(identity), "local_demo": not auth.production() and not identity, "external_calls_allowed":auth.external_calls_allowed(), **(identity or {})}


@app.post("/api/auth/login")
def auth_login(body: dict, response: Response, request: Request):
    if not isinstance(body.get("email"), str) or not isinstance(body.get("password"), str):
        raise HTTPException(422, "Email and password required")
    token, identity = auth.login(body["email"], body["password"], request.client.host if request.client else "unknown")
    response.set_cookie("saavdhan_session", token, httponly=True, secure=auth.production(), samesite="strict", max_age=auth.SESSION_SECONDS, path="/")
    response.headers["Cache-Control"] = "no-store"
    return identity


@app.post("/api/auth/logout")
def auth_logout(request: Request, response: Response):
    token = request.cookies.get("saavdhan_session", "")
    with auth.database() as conn:
        conn.execute("DELETE FROM sessions WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie("saavdhan_session", path="/", secure=auth.production(), httponly=True, samesite="strict")
    return {"authenticated": False, "local_demo": not auth.production()}


@app.exception_handler(storage.TenantCapacityExceeded)
async def tenant_capacity_error(request: Request, exc):
    return JSONResponse({"detail":str(exc)},status_code=413)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def audit(state, action, detail):
    state["audit"].append({"at":stamp(),"action":action,"detail":detail})


def require_case(case_id):
    state=storage.get_case(case_id)
    if not state:
        raise HTTPException(404,"Case not found")
    return state


def view(state):
    result={key:state.get(key) for key in ("id","created_at","demo","revision","sources","audit","analysis")}
    result["safety"]=safety.status(state,datetime.now(timezone.utc))
    return result


def new_case(sources, staged, demo=False):
    if storage.TENANT.get()==storage.ANONYMOUS:
        storage.purge_anonymous(float(os.getenv("SAAVDHAN_RETENTION_HOURS","24")),int(os.getenv("SAAVDHAN_ANON_CASE_CAP","200"))-1)
    elif auth.production() and len(storage.list_cases())>=10:
        raise storage.TenantCapacityExceeded("Case capacity reached; try again later")
    state={"id":uuid.uuid4().hex,"created_at":stamp(),"demo":demo,"revision":1,"audit":[],"analysis":None,
           "sources":[s.model_dump(mode="json") for s in sources]}
    storage.reserve_upload_bytes(sum(len(data) for _,data in staged))
    for name,data in staged:
        (storage.upload_dir(state["id"])/Path(name).name).write_bytes(data)
    audit(state,"created","SYNTHETIC demo offer" if demo else f"{len(staged)} source(s) ingested; content treated as untrusted data")
    storage.save_case(state)
    return state


@app.get("/api/health")
def health():
    return {"status":"ok","service":"Saavdhan","model_extraction_configured":provider_available(),"ocr_configured":ocr_available(),"external_submission":False}


@app.get("/api/meta")
def meta():
    return {"app":"Saavdhan","version":app.version,"ra_list_date":RA_LIST_DATE,"fee_cap_inr":FEE_CAP_INR,
            "rules":[{"id":r["id"],"severity":r["severity"],"source":r["source"],"heuristic":r.get("heuristic",False)} for r in RULES]}


@app.get("/api/reports/map")
def reports_map():
    # ponytail: synthetic reports only; real reports need consent, retention and a DPDP review first
    return aggregate(synthetic_reports())


@app.post("/api/offers")
async def create_offer(files:list[UploadFile]=File(default=[]),text:str|None=Form(default=None)):
    uploads=[(file.filename or "upload",await file.read(MAX_FILE_BYTES+1)) for file in files[:11]]
    if len(uploads)>10:
        raise HTTPException(400,"At most 10 files per offer")
    if text and len(text)>50000:
        raise HTTPException(413,"Pasted text is limited to 50,000 characters")
    if text and text.strip():
        uploads.append(("pasted-offer.txt",text.encode("utf-8")))
    if not uploads:
        raise HTTPException(422,"Upload a file or paste the offer text")
    sources,staged,notes=[],[],[]
    for name,data in uploads:
        try:
            ingested,errors=ingest_bytes(name,data)
        except Exception as exc:
            raise HTTPException(400,f"Could not read {Path(name).name}: {exc}") from exc
        sources.extend(ingested)
        staged.append((ingested[0].stored_name,data))
        notes.extend(errors)
    state=new_case(sources,staged)
    if notes:
        audit(state,"ingest_notes","; ".join(notes))
        storage.save_case(state)
    return view(state)


@app.post("/api/demo/offers/{name}")
def demo_offer(name:str):
    if name not in DEMO_OFFERS:
        raise HTTPException(404,"Unknown demo offer")
    data=DEMO_OFFERS[name].encode("utf-8")
    sources,_=ingest_bytes(f"synthetic-{name}.txt",data)
    return view(new_case(sources,[(sources[0].stored_name,data)],demo=True))


@app.get("/api/offers/{case_id}")
def get_offer(case_id:str):
    return view(require_case(case_id))


@app.post("/api/offers/{case_id}/analyze")
async def analyze_offer(case_id:str):
    state=require_case(case_id)
    state["analysis"]=await analyze(state)
    state["revision"]+=1
    verdict=state["analysis"]["verdict"]
    audit(state,"analyzed",f"{state['analysis']['extraction_method']} extraction; verdict {verdict['level']} set by Python rules")
    storage.save_case(state)
    return view(state)


@app.get("/api/offers/{case_id}/packet")
def packet(case_id:str):
    state=require_case(case_id)
    if not state.get("analysis"):
        raise HTTPException(409,"Analyze the offer before downloading the packet")
    audit(state,"packet","Report packet downloaded locally; nothing sent")
    storage.save_case(state)
    return Response(packet_zip(view(state)),media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="saavdhan-{case_id[:8]}.zip"'})


@app.post("/api/offers/{case_id}/safety-plan")
def safety_plan(case_id:str,plan:SafetyPlan):
    state=require_case(case_id)
    safety.create_plan(state,plan,datetime.now(timezone.utc))
    audit(state,"safety_plan",f"{len(plan.contacts)} family contact(s); check-in every {plan.checkin_interval_hours}h")
    storage.save_case(state)
    return view(state)


@app.post("/api/offers/{case_id}/checkin")
def checkin(case_id:str,body:dict):
    state=require_case(case_id)
    try:
        safety.checkin(state,str(body.get("note",""))[:280],datetime.now(timezone.utc))
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc
    audit(state,"checkin","Traveller checked in")
    storage.save_case(state)
    return view(state)


@app.post("/api/demo/advance-clock")
def advance_clock(body:dict):
    state=require_case(str(body.get("case_id","")))
    if auth.production() and not state.get("demo"):
        raise HTTPException(404,"Demo clock is only available for demo offers")
    try:
        safety.advance_clock(state,int(body.get("hours",24)))
    except (ValueError,TypeError) as exc:
        raise HTTPException(422,str(exc)) from exc
    view(state)  # status() records simulated alerts for any missed check-in
    audit(state,"demo_clock",f"DEMO: simulated clock moved {body.get('hours',24)}h")
    storage.save_case(state)
    return view(state)


@app.get("/api/offers/{case_id}/sources/{source_id}")
def get_source(case_id:str,source_id:str):
    source=next((s for s in require_case(case_id)["sources"] if s["id"]==source_id),None)
    if source is None:
        raise HTTPException(404,"Source not found")
    return source


@app.get("/api/offers/{case_id}/sources/{source_id}/download")
def download_source(case_id:str,source_id:str):
    source=get_source(case_id,source_id)
    if not source.get("stored_name"):
        raise HTTPException(404,"Original file unavailable")
    path=storage.upload_dir(case_id)/Path(source["stored_name"]).name
    if not path.is_file():
        raise HTTPException(404,"Original file not found")
    return FileResponse(path,filename=source["file"])


frontend=Path(__file__).resolve().parents[1]/"frontend"/"dist"
if frontend.exists():
    app.mount("/assets",StaticFiles(directory=frontend/"assets"),name="assets")

    @app.get("/{path:path}")
    def frontend_page(path:str):
        if path.startswith("api/"):
            raise HTTPException(404,"API route not found")
        target=(frontend/path).resolve()
        if target.is_relative_to(frontend.resolve()) and target.is_file():
            return FileResponse(target)
        return FileResponse(frontend/"index.html")
