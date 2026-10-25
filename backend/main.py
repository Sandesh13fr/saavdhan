from __future__ import annotations

import hashlib
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError

from . import storage, telemetry, enrichment, auth
import neatlogs
from .engine import analyze
from .exports import packet_zip
from .fixtures import demo_case
from .ingest import ingest_bytes, MAX_FILE_BYTES, ocr_available
from .models import CaseInput, RunRequest, ReviewRequest, ApprovalRequest, SourceRef, AgentRequest
from .providers import provider_available, extract_records

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1]/".env",override=False)
except ImportError:
    pass

@asynccontextmanager
async def lifespan(app):
    if os.getenv("BAKAYA_ENV", "local") not in {"local","production"}:
        raise RuntimeError("BAKAYA_ENV must be local or production")
    if auth.production() and not os.getenv("BAKAYA_PUBLIC_ORIGIN", "").startswith("https://"):
        raise RuntimeError("Production requires BAKAYA_PUBLIC_ORIGIN with HTTPS")
    telemetry.initialize()
    try:
        yield
    finally:
        telemetry.shutdown()


app=FastAPI(title="Bakaya",version="0.1.0",description="Local evidence-backed claim preparation. No automatic filing or sending.", lifespan=lifespan)
TRUSTED_HOSTS = {"localhost", "127.0.0.1", "[::1]", "testserver"}
TRUSTED_HOSTS.update(h.strip() for h in os.getenv("BAKAYA_ALLOWED_HOSTS", "").split(",") if h.strip())
app.add_middleware(TrustedHostMiddleware, allowed_hosts=sorted(TRUSTED_HOSTS), www_redirect=False)


@app.middleware("http")
async def session_guard(request: Request, call_next):
    identity = auth.session(request.cookies.get("bakaya_session"))
    mutation = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    origin = request.headers.get("origin")
    if auth.production() and request.url.path == "/api/auth/login" and mutation and origin != os.getenv("BAKAYA_PUBLIC_ORIGIN"):
        return Response("Same-origin login required", status_code=403)
    if mutation and origin:
        expected = os.getenv("BAKAYA_PUBLIC_ORIGIN") if auth.production() else str(request.base_url).rstrip("/")
        if origin.rstrip("/") != expected:
            return Response("Cross-origin mutation rejected", status_code=403)
    path = request.url.path
    if path.startswith("/api/") and path not in {"/api/health", "/api/auth/login", "/api/auth/me"}:
        if auth.production() and not identity:
            return Response("Sign in required", status_code=401)
        if identity and mutation and not __import__("hmac").compare_digest(request.headers.get("x-csrf-token", ""), identity["csrf_token"]):
            return Response("CSRF token required", status_code=403)
        if identity and mutation and identity["user"]["role"] == "viewer" and path != "/api/auth/logout":
            return Response("Read-only account", status_code=403)
    user_token = auth.USER.set(identity["user"] if identity else None)
    tenant_token = storage.TENANT.set(identity["user"]["tenant_id"] if identity else "local-demo")
    try:
        if path == "/api/demo" and (auth.production() or (identity and identity["user"]["role"] == "viewer")):
            return Response("Use the authenticated POST demo endpoint", status_code=405)
        response = await call_next(request)
        if path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        auth.USER.reset(user_token)
        storage.TENANT.reset(tenant_token)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if auth.production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.get("/api/auth/me")
def auth_me(request: Request):
    identity = auth.session(request.cookies.get("bakaya_session"))
    return {"authenticated": bool(identity), "local_demo": not auth.production() and not identity, "external_calls_allowed":auth.external_calls_allowed(), **(identity or {})}


@app.post("/api/auth/login")
def auth_login(body: dict, response: Response, request: Request):
    if not isinstance(body.get("email"), str) or not isinstance(body.get("password"), str):
        raise HTTPException(422, "Email and password required")
    token, identity = auth.login(body["email"], body["password"], request.client.host if request.client else "unknown")
    response.set_cookie("bakaya_session", token, httponly=True, secure=auth.production(), samesite="strict", max_age=auth.SESSION_SECONDS, path="/")
    response.headers["Cache-Control"] = "no-store"
    return identity


@app.post("/api/auth/logout")
def auth_logout(request: Request, response: Response):
    token = request.cookies.get("bakaya_session", "")
    with auth.database() as conn:
        conn.execute("DELETE FROM sessions WHERE digest=?", (hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie("bakaya_session", path="/", secure=auth.production(), httponly=True, samesite="strict")
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


def invalidate(state):
    state["revision"]+=1
    state["approval"]=None


def current_approval(state):
    approval=state.get("approval")
    digest=hashlib.sha256(json.dumps(state["input"],sort_keys=True).encode()).hexdigest()
    return bool(approval and approval["revision"]==state["revision"] and approval.get("input_sha256")==digest and not state["analysis"]["blockers"])


def run_analysis(state,mode="fixed"):
    case=CaseInput.model_validate(state["input"])
    state["analysis"]=analyze(case,state["review"],mode)
    state["mode"]=mode


def view(state):
    case=state["input"]
    result={"id":state["id"],"name":case["name"],"supplier":case["supplier"],"buyer":case["buyer"],"as_of":case["as_of"],
            "sources":case["sources"],"rates":case["rates"],"audit":state["audit"],"review":state["review"],"revision":state["revision"],"approval":state["approval"],"mode":state.get("mode","fixed"),"evaluation":state.get("evaluation"),"agent":state.get("agent"),**state["analysis"]}
    if state["approval"] and state["approval"]["revision"]==state["revision"]:
        result["status"]="approved"
    result["buyer_context"] = enrichment.read(state["id"])
    return result


@app.post("/api/cases/{case_id}/buyer-context")
def buyer_context(case_id: str, body: dict):
    require_case(case_id)
    if not isinstance(body.get("domain"), str) or body.get("confirm") is not True:
        raise HTTPException(422, "Confirm the optional domain lookup before continuing")
    if not auth.external_calls_allowed():
        raise HTTPException(403, "External provider calls require an administrator")
    enrichment.lookup(case_id, body["domain"])
    return view(require_case(case_id))


def create(case:CaseInput,is_demo=False):
    if not is_demo:
        for source in case.sources:
            # Original-byte metadata is assigned only by ingestion, never by clients.
            source.stored_name=None
            source.sha256=""
    sid="PROFILE-"+uuid.uuid4().hex[:8]
    # A manually entered party profile is a user statement, not external proof.
    if not case.supplier.source_refs or not case.buyer.source_refs:
        source=SourceRef(id=sid,file="manual-party-profile.json",kind="user_statement",text=json.dumps({"supplier":case.supplier.model_dump(mode="json"),"buyer":case.buyer.model_dump(mode="json")}),line=1)
        case.sources.append(source)
        for party in [case.supplier,case.buyer]:
            if not party.source_refs:
                party.source_refs=[sid]
                party.field_sources={k:[sid] for k,v in party.model_dump().items() if v not in (None,"") and k not in {"source_refs","field_sources"}}
    state={"id":uuid.uuid4().hex,"input":case.model_dump(mode="json"),"review":{"rate_confirmed":False,"buyer_confirmed":False},"audit":[],"revision":1,"approval":None,"demo":is_demo}
    audit(state,"created","Synthetic fictional demo" if is_demo else "Local case created; party profile is a user statement pending review.")
    if auth.production() and len(storage.list_cases())>=10:
        raise storage.TenantCapacityExceeded("Tenant case capacity reached (10); contact the operator")
    if is_demo:
        storage.reserve_upload_bytes(sum(len(source.text.encode("utf-8")) for source in case.sources))
        for source in case.sources:
            content=source.text.encode("utf-8")
            stored_name=source.id+".txt"
            (storage.upload_dir(state["id"])/stored_name).write_bytes(content)
            source.stored_name=stored_name
            source.sha256=hashlib.sha256(content).hexdigest()
        state["input"]=case.model_dump(mode="json")
    run_analysis(state)
    storage.save_case(state)
    return state


@app.get("/api/health")
def health():
    return {"status":"ok","service":"Bakaya","local_demo":not auth.production(),"model_extraction_configured":provider_available(),"ocr_configured":ocr_available(),"external_submission":False}


@app.get("/api/cases")
def cases():
    return [view(state) for state in storage.list_cases()]


@app.post("/api/cases")
def new_case(case:CaseInput):
    return view(create(case))


@app.get("/api/demo")
@app.post("/api/cases/demo")
def new_demo():
    from .evaluation import evaluate
    state=create(demo_case(),True)
    state["evaluation"]=evaluate()
    audit(state,"evaluation","20 synthetic labeled scenarios measured locally; not an external benchmark.")
    storage.save_case(state)
    return view(state)


@app.get("/api/evaluation")
def evaluation():
    from .evaluation import evaluate
    return evaluate()


@app.get("/api/cases/{case_id}")
def get_case(case_id:str):
    return view(require_case(case_id))


def merge_records(payload,extracted):
    for key,records in extracted.items():
        if key in {"supplier","buyer","bank_total"}:
            payload[key]=records.model_dump(mode="json") if hasattr(records,"model_dump") else str(records) if key=="bank_total" else records
        else:
            payload.setdefault(key,[]).extend(r.model_dump(mode="json") if hasattr(r,"model_dump") else r for r in records)


def apply_linked_facts(case:CaseInput):
    """Use only explicit invoice IDs; conflicting facts remain blocked."""
    for inv in case.invoices:
        pos=[p for p in case.purchase_orders if p.invoice_id==inv.id]
        deliveries=[d for d in case.deliveries if d.invoice_id==inv.id]
        if len(pos)==1:
            po=pos[0]
            if inv.contract_date is None:
                inv.contract_date=po.date
                inv.field_sources["contract_date"]=po.field_sources.get("date",po.source_refs)
            if inv.written_term_days is None and po.written_term_days is not None:
                inv.written_term_days=po.written_term_days
                inv.field_sources["written_term_days"]=po.field_sources.get("written_term_days",po.source_refs)
            inv.source_refs=list(dict.fromkeys(inv.source_refs+po.source_refs))
        if len(deliveries)==1 and inv.delivery_date is None:
            d=deliveries[0]
            inv.delivery_date=d.date
            inv.field_sources["delivery_date"]=d.field_sources.get("date",d.source_refs)
            inv.source_refs=list(dict.fromkeys(inv.source_refs+d.source_refs))
    return case


@app.post("/api/cases/{case_id}/upload")
@neatlogs.span(kind="WORKFLOW", name="invoice-document-extraction", capture_input=False, capture_output=False)
async def upload(case_id:str,files:list[UploadFile]=File(...)):
    state=require_case(case_id)
    if len(state["input"]["sources"])+len(files)>100:
        raise HTTPException(413,"At most 100 evidence sources per case")
    if len(files)>30:
        raise HTTPException(400,"At most30 files per upload")
    payload=state["input"]
    staged=[]
    model_calls=0
    for file in files:
        data=await file.read(MAX_FILE_BYTES+1)
        try:
            sources,extracted,errors=ingest_bytes(file.filename or "upload",data)
            for source in sources:
                if source.page and source.text and provider_available() and model_calls<3:
                    model_calls+=1
                    try:
                        proposed=await extract_records(source.text,source.id)
                        if proposed:
                            merge_records(payload,proposed)
                            source.status="extracted_needs_review"
                            audit(state,"model_extraction",f"{source.file} page{source.page}: quoted typed proposals require review; no money computed by model.")
                    except ValueError as exc:
                        errors.append(str(exc))
            if Path(file.filename or "").suffix.lower()==".txt" and provider_available() and model_calls<3:
                model_calls+=1
                proposed=await extract_records(sources[0].text,sources[0].id)
                if proposed:
                    merge_records(payload,proposed)
                    sources[0].status="extracted_needs_review"
            merge_records(payload,extracted)
            payload["sources"].extend(s.model_dump(mode="json") for s in sources)
            staged.append((sources[0].stored_name,data))
            audit(state,"ingested",f"{Path(file.filename or 'upload').name}: {len(data)}bytes; SHA256{sources[0].sha256}; errors: {'; '.join(errors) or 'none'}")
        except Exception as exc:
            raise HTTPException(400,f"Could not ingest {Path(file.filename or 'upload').name}: {exc}") from exc
    try:
        checked=apply_linked_facts(CaseInput.model_validate(payload))
    except ValidationError as exc:
        raise HTTPException(422,str(exc)) from exc
    state["input"]=checked.model_dump(mode="json")
    storage.reserve_upload_bytes(sum(len(data) for _,data in staged))
    for filename,data in staged:
        (storage.upload_dir(case_id)/Path(filename).name).write_bytes(data)
    invalidate(state)
    state["review"]={"rate_confirmed":False,"buyer_confirmed":False}
    run_analysis(state)
    storage.save_case(state)
    return view(state)


@app.post("/api/cases/{case_id}/run")
@app.post("/api/cases/{case_id}/analyze")
def run(case_id:str,request:RunRequest=RunRequest()):
    state=require_case(case_id)
    invalidate(state)
    if request.simulate_rate_failure:
        audit(state,"rate_fetch_attempt","SIMULATION: attempt1 timed out; no external HTTP request made.")
        audit(state,"rate_fetch_retry","SIMULATION: retry1 returned unexpected format; no external HTTP request made.")
        audit(state,"rate_fallback","Recovery uses bundled synthetic dated rates for DEMO. Rate confirmation required; no RBI fetch claimed.")
        state["review"]["rate_confirmed"]=False
    run_analysis(state,request.mode)
    audit(state,"analyzed",f"{request.mode} matcher; {len(state['analysis']['blockers'])} blockers; deterministic Decimal engine.")
    storage.save_case(state)
    return view(state)


@app.patch("/api/cases/{case_id}/review")
@app.post("/api/cases/{case_id}/review")
def review(case_id:str,request:ReviewRequest):
    state=require_case(case_id)
    user=auth.require_role("reviewer", "admin")
    if user:
        request.reviewer=user["name"]
    case=CaseInput.model_validate(state["input"])
    sources={s.id:s for s in case.sources}
    for correction in request.invoice_updates:
        index=next((n for n,inv in enumerate(case.invoices) if inv.id==correction.invoice_id),None)
        source=sources.get(correction.source_id)
        if index is None or not source or source.status not in {"parsed","reviewed","extracted_needs_review","unstructured_review"}:
            raise HTTPException(422,"Invoice correction requires existing invoice and readable supporting source")
        data=case.invoices[index].model_dump(mode="json")
        data.update(correction.fields)
        for field in correction.fields:
            data["field_sources"][field]=[source.id]
        data["source_refs"]=list(dict.fromkeys(data["source_refs"]+[source.id]))
        try:
            case.invoices[index]=type(case.invoices[index]).model_validate(data)
        except ValidationError as exc:
            raise HTTPException(422,"Invoice correction failed typed date/amount validation") from exc
        audit(state,"invoice_correction",f"{request.reviewer}: corrected {correction.invoice_id} fields {', '.join(correction.fields)} using {source.id}; {correction.reason}")
    for resolution in request.resolutions:
        payment=next((p for p in case.payments if p.id==resolution.payment_id),None)
        if not payment or resolution.source_id not in sources:
            raise HTTPException(422,"Resolution must reference an existing payment and evidence source")
        if sources[resolution.source_id].status in {"ocr_unavailable","parse_error"}:
            raise HTTPException(422,"Unreadable evidence cannot support an allocation")
        payment.allocations=resolution.allocations
        payment.source_refs=list(dict.fromkeys(payment.source_refs+[resolution.source_id]))
        for item in payment.allocations:
            item.source_refs=[resolution.source_id]
            item.field_sources={"invoice_id":[resolution.source_id],"amount":[resolution.source_id],"tds_amount":[resolution.source_id]}
        audit(state,"payment_review",f"{request.reviewer}: {resolution.payment_id} allocated using{resolution.source_id}; {resolution.reason}")
    for decision in request.source_reviews:
        source=sources.get(decision.get("source_id",""))
        if not source or len(decision.get("reason",""))<5:
            raise HTTPException(422,"Source review requires existing source and reason")
        replacement=sources.get(decision.get("replacement_source_id",""))
        if source.status in {"ocr_unavailable","parse_error"}:
            if not replacement or replacement.id==source.id or replacement.status not in {"parsed","reviewed"}:
                raise HTTPException(422,"Unreadable source requires readable replacement evidence")
            source.status="superseded"
            source.replacement_source_id=replacement.id
        elif source.status in {"unstructured_review","extracted_needs_review"}:
            source.status="reviewed"
        if decision.get("kind") in {"tds_certificate","remittance_note"}:
            source.kind=decision["kind"]
        audit(state,"source_review",f"{request.reviewer}: {source.id}; {decision['reason']}")
    for key in ["rate_confirmed","buyer_confirmed"]:
        value=getattr(request,key)
        if value is not None:
            state["review"][key]=value
    state["review"]["reviewer"]=request.reviewer
    state["input"]=case.model_dump(mode="json")
    invalidate(state)
    run_analysis(state,"fixed")
    audit(state,"review",f"{request.reviewer}: confirmations saved; {len(state['analysis']['blockers'])} blockers remain.")
    storage.save_case(state)
    return view(state)


@app.post("/api/cases/{case_id}/approve")
def approve(case_id:str,request:ApprovalRequest):
    user=auth.require_role("reviewer", "admin")
    if user:
        request.reviewer=user["name"]
    state=require_case(case_id)
    run_analysis(state,state.get("mode","fixed"))
    if state["analysis"]["blockers"]:
        raise HTTPException(409,{"message":"Resolve every blocking review item before approval","blockers":state["analysis"]["blockers"]})
    digest=hashlib.sha256(json.dumps(state["input"],sort_keys=True).encode()).hexdigest()
    state["approval"]={"user_id":user["id"] if user else None,"tenant_id":user["tenant_id"] if user else "local-demo","role":user["role"] if user else "local-demo","reviewer":request.reviewer,"at":stamp(),"revision":state["revision"],"input_sha256":digest,"scope":"local packet download only"}
    audit(state,"approved",f"{request.reviewer} approved revision{state['revision']} for local download; no filing or sending.")
    storage.save_case(state)
    return view(state)


@app.get("/api/cases/{case_id}/export")
def export(case_id:str):
    state=require_case(case_id)
    if not current_approval(state):
        raise HTTPException(409,"Human approval is required for this current revision")
    audit(state,"exported","Approved packet downloaded locally; no external submission.")
    storage.save_case(state)
    content=packet_zip(view(state),state)
    return Response(content,media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="bakaya-{case_id[:8]}.zip"'})


@app.get("/api/cases/{case_id}/sources/{source_id}")
def get_source(case_id:str,source_id:str):
    source=next((s for s in require_case(case_id)["input"]["sources"] if s["id"]==source_id),None)
    if source is None:
        raise HTTPException(404,"Source not found")
    return source


@app.get("/api/cases/{case_id}/sources/{source_id}/download")
def download_source(case_id:str,source_id:str):
    source=get_source(case_id,source_id)
    if not source.get("stored_name"):
        raise HTTPException(404,"Original source bytes unavailable; extracted evidence remains visible")
    path=storage.upload_dir(case_id)/Path(source["stored_name"]).name
    if not path.is_file():
        raise HTTPException(404,"Original file not found")
    return FileResponse(path,filename=source["file"])


@app.get("/api/cases/{case_id}/agent")
def get_agent(case_id:str):
    return require_case(case_id).get("agent")


@app.post("/api/cases/{case_id}/agent/run")
async def agent_run(case_id:str,request:AgentRequest=AgentRequest()):
    return await advance_agent(case_id,request,True)


@app.post("/api/cases/{case_id}/agent/resume")
async def agent_resume(case_id:str,request:AgentRequest=AgentRequest()):
    return await advance_agent(case_id,request,False)


async def advance_agent(case_id,request,fresh):
    if (request.allow_model_extraction or request.allow_model_planning) and not auth.external_calls_allowed():
        raise HTTPException(403,"External provider calls require an administrator")
    from .agent import LOCKS,advance
    import asyncio
    lock=LOCKS.setdefault(case_id,asyncio.Lock())
    async with lock:
        state=require_case(case_id)
        with neatlogs.trace("prepare-invoice-case", kind="WORKFLOW") as span:
            span.set_attribute("neatlogs.workflow.name", "prepare-invoice-case")
            try:
                state=await advance(state,request,fresh)
                trace_id=span.get_span_context().trace_id
                if trace_id:
                    state["agent"]["trace_id"]=format(trace_id,"032x")
                    storage.save_case(state,expected_revision=state["revision"])
            except storage.ConcurrentCaseUpdate as exc:
                raise HTTPException(409,str(exc)) from exc
            return view(state)


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
