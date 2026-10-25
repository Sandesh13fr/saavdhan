"""Optional company context, kept outside claim facts and approval."""
import json
import os
import re
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from . import storage


def database():
    conn = storage.connect()
    conn.execute("CREATE TABLE IF NOT EXISTS enrichment_budget (id INTEGER PRIMARY KEY, reserved INTEGER NOT NULL, blocked INTEGER NOT NULL)")
    conn.execute("INSERT OR IGNORE INTO enrichment_budget VALUES (1,0,0)")
    conn.execute("CREATE TABLE IF NOT EXISTS buyer_context (domain TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS case_context (case_id TEXT PRIMARY KEY, domain TEXT NOT NULL)")
    conn.commit()
    return conn


def read(case_id):
    with database() as conn:
        row = conn.execute("SELECT payload FROM buyer_context JOIN case_context USING(domain) WHERE case_id=?", (case_id,)).fetchone()
        reserved, blocked = conn.execute("SELECT reserved,blocked FROM enrichment_budget WHERE id=1").fetchone()
    return {"result": json.loads(row[0]) if row else None, "credits_reserved": reserved, "credit_limit": 500, "blocked": bool(blocked), "configured": bool(os.getenv("CRUSTDATA_API_KEY"))}


def tool(name, arguments):
    headers = {"Authorization": "Bearer " + os.environ["CRUSTDATA_API_KEY"], "Accept": "application/json, text/event-stream"}
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        def rpc(body):
            response = client.post("https://mcp.crustdata.com/mcp", headers=headers, json=body)
            response.raise_for_status()
            if response.headers.get("mcp-session-id"):
                headers["mcp-session-id"] = response.headers["mcp-session-id"]
            text = response.text
            if text.startswith("event:") or text.startswith("data:"):
                text = next(line[6:] for line in text.splitlines() if line.startswith("data: "))
            return json.loads(text)
        rpc({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"bakaya","version":"0.1"}}})
        result = rpc({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":name,"arguments":arguments}})
    if "error" in result or result.get("result", {}).get("isError"):
        raise ValueError("Provider rejected lookup")
    return "\n".join(c["text"] for c in result["result"].get("content", []) if c.get("type") == "text")


def lookup(case_id, domain):
    domain = domain.strip().lower()
    if len(domain) > 253 or not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
        raise HTTPException(422, "Enter a company domain only, such as stripe.com")
    if not os.getenv("CRUSTDATA_API_KEY"):
        raise HTTPException(503, "Crustdata is not configured")
    # Reserve before network I/O; uncertain calls retain their reservation and stop spending.
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        cached = conn.execute("SELECT payload FROM buyer_context WHERE domain=?", (domain,)).fetchone()
        if cached:
            conn.execute("INSERT OR REPLACE INTO case_context VALUES (?,?)", (case_id,domain))
            return read_result(cached[0], True)
        reserved, blocked = conn.execute("SELECT reserved,blocked FROM enrichment_budget WHERE id=1").fetchone()
        if blocked or reserved + 2 > 500:
            raise HTTPException(409, "Crustdata spending stopped: budget exhausted or an earlier cost needs review")
        conn.execute("UPDATE enrichment_budget SET reserved=reserved+2 WHERE id=1")
    try:
        prices = tool("crustdata_credit_costs", {})
        if not re.search(r"`crustdata_company_enrich_v2`\s*\|\s*Any field groups\s*\|\s*2 credits / company", prices):
            raise ValueError("Price changed")
        identified = tool("crustdata_company_identify_v2", {"params":{"domains":[domain]}})
        matches = json.loads(identified.split("\n\n_credits:")[0])[0]["matches"]
        if len(matches) != 1:
            raise ValueError("Company is missing or ambiguous")
        company_id = matches[0]["company_data"]["crustdata_company_id"]
        text = tool("crustdata_company_enrich_v2", {"params":{"crustdata_company_ids":[company_id],"fields":["basic_info"]}})
        cost = re.search(r"_credits: spent ([0-9.]+) this call", text)
        if not cost or float(cost[1]) not in (0, 2):
            raise ValueError("Unverified cost")
        enriched = json.loads(text.split("\n\n_credits:")[0])[0]["matches"]
        if len(enriched) != 1 or enriched[0]["company_data"]["crustdata_company_id"] != company_id:
            raise ValueError("Unverified company response")
        basic = enriched[0]["company_data"]["basic_info"]
        context = {key: basic.get(key) for key in ("name","primary_domain","description","company_type","year_founded")}
        payload = {"domain":domain,"company_id":company_id,"retrieved_at":datetime.now(timezone.utc).isoformat(),"provider":"Crustdata","credits":float(cost[1]),"context":context,"notice":"Company context only. Confirm against your own records; this is not identity or eligibility proof."}
        with database() as conn:
            conn.execute("INSERT OR REPLACE INTO buyer_context VALUES (?,?)", (domain,json.dumps(payload)))
            conn.execute("INSERT OR REPLACE INTO case_context VALUES (?,?)", (case_id,domain))
        return read_result(json.dumps(payload), False)
    except Exception:
        with database() as conn:
            conn.execute("UPDATE enrichment_budget SET blocked=1 WHERE id=1")
        raise HTTPException(502, "Lookup could not be verified. Paid lookups stopped for review; no automatic retry.") from None


def read_result(payload, cached):
    return {"result":json.loads(payload),"cached":cached,"spent_this_call":0 if cached else json.loads(payload)["credits"]}
