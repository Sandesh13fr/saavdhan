"""Bounded, checkpointed tool planner. Never approves, files, or sends.

This is a rules-driven orchestrator around actual tools, with optional quoted
model extraction. It does not portray the rules planner as an LLM planner.
Each tool checkpoint persists in SQLite; paid extraction has zero automatic
retries and is opt-in. Recoverable local tool failures retry once on resume.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import neatlogs

from . import storage
from .engine import analyze
from .exports import packet_zip
from .models import CaseInput, AgentRequest
from .providers import provider_available, extract_records, plan_next_tool

LOCKS: dict[str,asyncio.Lock] = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def new_agent(state):
    return {"run_id":uuid.uuid4().hex,"planner":"deterministic bounded tool planner; optional model extraction",
            "status":"running","started_at":now(),"updated_at":now(),"input_revision":state["revision"],
            "next_tool":"inventory_evidence","steps":[],"checkpoints":[],"waiting_questions":[],
            "flags":{},"attempts":{},"max_total_steps":30,"model_attempts":0,"model_plans":0,"max_model_plans":6,"packet":None}


def select_tool(state, request):
    agent=state["agent"]
    flags=agent["flags"]
    if not flags.get("inventory"):
        return "inventory_evidence"
    pending=[s for s in state["input"]["sources"] if s["status"]=="unstructured_review" and s.get("text") and s["id"] not in flags.get("extraction_attempted",[])]
    if pending and request.allow_model_extraction and provider_available() and agent["model_attempts"]<3:
        return "extract_source"
    if not flags.get("ledger"):
        return "analyze_ledger"
    if not flags.get("reconciliation"):
        return "verify_reconciliation"
    if state["analysis"]["blockers"]:
        return "request_review"
    if not state["approval"]:
        return "request_approval"
    if not flags.get("packet"):
        return "build_local_packet"
    return None


def record_step(state,tool,status,summary,**extra):
    agent=state["agent"]
    step={"number":len(agent["steps"])+1,"tool":tool,"status":status,"summary":summary,"at":now(),**extra}
    agent["steps"].append(step)
    agent["updated_at"]=step["at"]
    state["audit"].append({"at":step["at"],"action":"agent_"+tool,"detail":summary})
    agent["checkpoints"].append({"step":step["number"],"revision":state["revision"],"at":step["at"],"tool":tool,"status":status})


async def choose_with_model(state,request,recommended):
    """The model can choose only tools whose deterministic preconditions hold."""
    agent=state["agent"]
    if not request.allow_model_planning or agent["flags"].get("planner_unavailable") or not provider_available():
        return recommended
    if agent.get("model_plans",0)>=agent.get("max_model_plans",6):
        agent["status"]="waiting_planner_budget"
        agent["waiting_questions"]=[{"code":"planner_budget","question":"Six model plans reached. Resume with model planning disabled to continue deterministic tools without further model spend."}]
        return None
    allowed=[recommended]
    if recommended in {"extract_source","analyze_ledger","verify_reconciliation"} and state["analysis"]["blockers"]:
        allowed.append("request_review")
    if recommended=="extract_source":
        allowed.append("analyze_ledger")
    summary={"goal":"Prepare an evidence-backed delayed-payment packet; pause for uncertainty or human approval; never file or send.",
             "source_count":len(state["input"]["sources"]),"invoice_count":len(state["input"]["invoices"]),"payment_count":len(state["input"]["payments"]),
             "unreadable_sources":sum(s["status"] in {"ocr_unavailable","parse_error"} for s in state["input"]["sources"]),
             "blocker_codes":sorted(set(b["code"] for b in state["analysis"]["blockers"])),"human_approval_present":bool(state["approval"]),
             "completed_tools":[s["tool"] for s in agent["steps"] if s["status"]=="completed"],"recommended_tool":recommended}
    agent["model_plans"]=agent.get("model_plans",0)+1
    storage.save_case(state,expected_revision=state["revision"])
    try:
        decision=await plan_next_tool(summary,allowed)
        if decision is None:
            raise ValueError("Model planner unavailable")
        if set(decision)!={"tool","reason"} or decision["tool"] not in allowed or not isinstance(decision["reason"],str):
            raise ValueError("Model proposed a tool outside current preconditions")
        agent["planner"]="bounded model tool selection with deterministic financial/approval guards"
        record_step(state,"model_plan","completed",f"Model selected {decision['tool']}: {decision['reason'][:240]}",allowed_tools=allowed,selected_tool=decision["tool"])
        return decision["tool"]
    except ValueError:
        # A failed model plan is not automatically retried. Rules tools can
        # continue without spending again during this run.
        agent["flags"]["planner_unavailable"]=True
        record_step(state,"model_plan","failed","Model planner unavailable or rejected; continuing the deterministic tool choice, no paid planning retry.")
        return recommended


async def execute_tool(state,tool,request):
    agent=state["agent"]
    flags=agent["flags"]
    if request.simulate_tool_failure and tool=="verify_reconciliation" and not flags.get("failure_injected"):
        flags["failure_injected"]=True
        raise RuntimeError("SIMULATED local reconciliation tool failure; no external call made")
    if tool=="inventory_evidence":
        sources=state["input"]["sources"]
        readable=sum(s["status"] not in {"ocr_unavailable","parse_error"} for s in sources)
        flags["inventory"]=True
        return f"Inventoried {len(sources)} evidence references; {readable} readable, {len(sources)-readable} require replacement. No missing facts inferred."
    if tool=="extract_source":
        source=next(s for s in state["input"]["sources"] if s["status"]=="unstructured_review" and s.get("text") and s["id"] not in flags.get("extraction_attempted",[]))
        flags.setdefault("extraction_attempted",[]).append(source["id"])
        agent["model_attempts"]+=1
        # Mark the attempt BEFORE calling. The next persisted checkpoint on
        # failure prevents a paid retry being selected automatically.
        storage.save_case(state,expected_revision=state["revision"])
        try:
            proposed=await extract_records(source["text"],source["id"])
            if not proposed:
                raise ValueError("Model extraction unavailable; readable source needs manual structured extraction")
            from .main import merge_records, apply_linked_facts
            candidate=json.loads(json.dumps(state["input"]))
            merge_records(candidate,proposed)
            checked=apply_linked_facts(CaseInput.model_validate(candidate))
            state["input"]=checked.model_dump(mode="json")
            extracted_source=next(s for s in state["input"]["sources"] if s["id"]==source["id"])
            extracted_source["status"]="extracted_needs_review"
            state["revision"]+=1
            state["approval"]=None
            state["review"]={"buyer_confirmed":False,"rate_confirmed":False}
            agent["input_revision"]=state["revision"]
            count=sum(len(v) if isinstance(v,list) else 1 for v in proposed.values())
            return f"Quoted typed extraction proposed {count} records from {source['id']}; human source review required. Paid tool not automatically retried."
        except Exception as exc:
            # No raw source text, model payload, credentials, or HTTP bodies in
            # audit/telemetry. Failure continues to deterministic checks.
            agent.setdefault("extraction_errors",[]).append({"source_id":source["id"],"message":"Extraction failed validation or provider call; use manual structured records."})
            return f"Extraction attempt for {source['id']} failed ({type(exc).__name__}); no records accepted, no paid retry. Supply verified structured records."
    if tool=="analyze_ledger":
        case=CaseInput.model_validate(state["input"])
        state["analysis"]=analyze(case,state["review"],"fixed")
        state["mode"]="fixed"
        flags["ledger"]=True
        result=state["analysis"]
        return f"Deterministic tools produced {len(result['matches'])} matches and {len(result['schedule'])} interest segments; {len(result['blockers'])} blockers. Rates, evidence and eligibility remain reviewable."
    if tool=="verify_reconciliation":
        totals=state["analysis"]["totals"]
        principal_identity=Decimal(totals["invoiced"])==Decimal(totals["principal"])+Decimal(totals["allocated_bank"])+Decimal(totals["tds_recognized"])
        receipt_identity=Decimal(totals["bank_received"])==Decimal(totals["allocated_bank"])+Decimal(totals["unallocated"])
        if not principal_identity or not receipt_identity:
            raise ValueError("Independent money-conservation check failed; no packet prepared")
        flags["reconciliation"]=True
        return f"Independent Decimal conservation checks pass. Unallocated bank receipts: INR {totals['unallocated']}; unresolved allocation still blocks approval."
    if tool=="request_review":
        agent["status"]="waiting_review"
        agent["waiting_questions"]=[{"id":b["id"],"code":b["code"],"question":b["question"],"source_id":b.get("source_id"),"payment_id":b.get("payment_id"),"candidates":b.get("candidates",[])} for b in state["analysis"]["blockers"]]
        return f"Stopped for {len(agent['waiting_questions'])} blocking reviewer decisions. No blocker waived and no approval issued."
    if tool=="request_approval":
        agent["status"]="waiting_approval"
        agent["waiting_questions"]=[{"id":"human-approval","code":"approval","question":"Review figures and evidence, then explicitly approve this revision for local download."}]
        return "Evidence checks complete; waiting for explicit human approval. No packet leaves this local service."
    if tool=="build_local_packet":
        from .main import current_approval,view
        if not current_approval(state):
            raise ValueError("Current human approval required before packet build")
        content=packet_zip(view(state),state)
        name="approved-packet-"+str(state["revision"])+".zip"
        # Export regenerates the approved packet; checkpoint metadata needs no duplicate file.
        flags["packet"]=True
        agent["packet"]={"filename":name,"bytes":len(content),"revision":state["revision"],"download_url":f"/api/cases/{state['id']}/export"}
        agent["status"]="complete"
        agent["waiting_questions"]=[]
        return f"Built {len(content)}byte approved packet locally; synthetic DEMO marking retained; nothing filed or sent."
    raise ValueError("Unknown tool")


async def advance(state,request:AgentRequest,fresh=False):
    expected_revision=state["revision"]
    if fresh or not state.get("agent"):
        state["agent"]=new_agent(state)
    agent=state["agent"]
    revision_changed=agent["input_revision"]!=state["revision"]
    if revision_changed:
        attempted=agent["flags"].get("extraction_attempted",[])
        previous_flags=agent["flags"]
        agent["flags"]={"extraction_attempted":attempted,**{key:previous_flags[key] for key in ("planner_unavailable","failure_injected") if key in previous_flags}}
        agent["input_revision"]=state["revision"]
        agent["packet"]=None
        record_step(state,"refresh_checkpoint","completed","Case revision changed after human review/upload; tools will recompute against current evidence.")
    # Repeated resume without a decision does not burn steps or create a loop.
    if agent["status"]=="waiting_review" and state["analysis"]["blockers"] and not revision_changed:
        return state
    if agent["status"]=="waiting_approval" and not state["approval"] and agent["flags"].get("ledger"):
        return state
    agent["status"]="running"
    agent["waiting_questions"]=[]
    for _ in range(request.max_steps):
        slots=2 if request.allow_model_planning and provider_available() and not agent["flags"].get("planner_unavailable") else 1
        if len(agent["steps"])+slots>agent["max_total_steps"]:
            agent["status"]="budget_exhausted"
            agent["next_tool"]=None
            break
        tool=select_tool(state,request)
        agent["next_tool"]=tool
        if tool is None:
            agent["status"]="complete"
            break
        tool=await choose_with_model(state,request,tool)
        if tool is None:
            break
        attempts=agent["attempts"].get(tool,0)
        if agent.get("failed_tool")==tool and attempts>=2:
            agent["status"]="failed"
            agent["waiting_questions"]=[{"code":"tool_failure","question":"Local tool failed twice. Inspect evidence or start a new bounded run after fixing the cause."}]
            break
        agent["attempts"][tool]=attempts+1
        try:
            with neatlogs.trace(tool,kind="TOOL") as span:
                span.set_attribute("neatlogs.tool.name",tool)
                span.set_attribute("bakaya.invoice_count",len(state["input"]["invoices"]))
                span.set_attribute("bakaya.source_count",len(state["input"]["sources"]))
                summary=await execute_tool(state,tool,request)
                span.set_attribute("bakaya.tool_status","completed")
            agent.pop("failed_tool",None)
            record_step(state,tool,"completed",summary)
        except Exception as exc:
            agent["failed_tool"]=tool
            agent["status"]="recoverable_failure" if attempts==0 else "failed"
            # Local deterministic exception only; no source/credential body.
            summary=str(exc) if tool=="verify_reconciliation" else f"{tool} failed ({type(exc).__name__}); no external action occurred."
            record_step(state,tool,"failed",summary)
            agent["waiting_questions"]=[{"code":"tool_failure","question":"Resume once to retry this local tool from the saved checkpoint."}]
        agent["next_tool"]=select_tool(state,request)
        storage.save_case(state,expected_revision=expected_revision)
        expected_revision=state["revision"]
        if agent["status"]!="running":
            break
    if agent["status"]=="running":
        agent["status"]="paused_budget"
        agent["next_tool"]=select_tool(state,request)
    storage.save_case(state,expected_revision=expected_revision)
    return state
