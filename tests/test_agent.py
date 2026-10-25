import asyncio

import pytest
from fastapi.testclient import TestClient

from backend import storage
from backend.main import app


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(storage,"DATA_DIR",tmp_path)
    return TestClient(app)


def resolve(client,case):
    return client.patch(f"/api/cases/{case['id']}/review",json={"reviewer":"Reviewer","rate_confirmed":True,"buyer_confirmed":True,"resolutions":[{"payment_id":"PAY-003","source_id":"REMIT-003","reason":"Confirmed exact remittance","allocations":[{"invoice_id":"INV-004","amount":"150000"}]}]})


def test_agent_executes_real_tools_and_persists_reviewer_wait(client):
    case=client.post("/api/cases/demo").json()
    result=client.post(f"/api/cases/{case['id']}/agent/run",json={}).json()
    agent=result["agent"]
    assert agent["status"]=="waiting_review"
    assert [s["tool"] for s in agent["steps"]]==["inventory_evidence","analyze_ledger","verify_reconciliation","request_review"]
    assert len(agent["checkpoints"])==4
    assert any(q["code"]=="ambiguous_payment" for q in agent["waiting_questions"])
    saved=storage.get_case(case["id"])["agent"]
    assert saved==agent
    unchanged=client.post(f"/api/cases/{case['id']}/agent/resume",json={}).json()["agent"]
    assert unchanged["steps"]==agent["steps"]
    assert client.get(f"/api/cases/{case['id']}/export").status_code==409


def test_step_budget_resumes_at_checkpoint(client):
    case=client.post("/api/cases/demo").json()
    first=client.post(f"/api/cases/{case['id']}/agent/run",json={"max_steps":1}).json()["agent"]
    assert first["status"]=="paused_budget" and first["next_tool"]=="analyze_ledger"
    second=client.post(f"/api/cases/{case['id']}/agent/resume",json={"max_steps":1}).json()["agent"]
    assert second["run_id"]==first["run_id"]
    assert [s["tool"] for s in second["steps"]]==["inventory_evidence","analyze_ledger"]


def test_failed_local_tool_recovers_once_from_saved_checkpoint(client):
    case=client.post("/api/cases/demo").json()
    first=client.post(f"/api/cases/{case['id']}/agent/run",json={"simulate_tool_failure":True}).json()["agent"]
    assert first["status"]=="recoverable_failure"
    assert first["steps"][-1]["status"]=="failed"
    assert "SIMULATED" in first["steps"][-1]["summary"]
    resumed=client.post(f"/api/cases/{case['id']}/agent/resume",json={"simulate_tool_failure":True}).json()["agent"]
    assert resumed["status"]=="waiting_review"
    assert resumed["attempts"]["verify_reconciliation"]==2
    assert [s["status"] for s in resumed["steps"] if s["tool"]=="verify_reconciliation"]==["failed","completed"]


def test_review_then_human_approval_then_packet_build(client):
    case=client.post("/api/cases/demo").json()
    client.post(f"/api/cases/{case['id']}/agent/run",json={})
    assert resolve(client,case).json()["status"]=="ready"
    waited=client.post(f"/api/cases/{case['id']}/agent/resume",json={}).json()
    assert waited["agent"]["status"]=="waiting_approval"
    assert waited["approval"] is None
    assert any(s["tool"]=="refresh_checkpoint" for s in waited["agent"]["steps"])
    client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Reviewer"})
    final=client.post(f"/api/cases/{case['id']}/agent/resume",json={}).json()
    assert final["agent"]["status"]=="complete"
    assert final["agent"]["packet"]["bytes"]>1000
    assert not list(storage.upload_dir(case["id"]).glob("approved-packet-*.zip"))
    assert client.get(final["agent"]["packet"]["download_url"]).status_code==200


def test_agent_blocks_paid_extraction_when_not_opted_in(client,monkeypatch):
    from backend import agent
    case=client.post("/api/cases/demo").json()
    state=storage.get_case(case["id"])
    state["input"]["sources"][0]["status"]="unstructured_review"
    storage.save_case(state)
    calls=[]
    async def no_call(*args):
        calls.append(args)
        raise AssertionError("Should not call provider")
    monkeypatch.setattr(agent,"provider_available",lambda:True)
    monkeypatch.setattr(agent,"extract_records",no_call)
    result=client.post(f"/api/cases/{case['id']}/agent/run",json={}).json()
    assert not calls and result["agent"]["model_attempts"]==0


def test_paid_extraction_failure_has_no_automatic_retry(client,monkeypatch):
    from backend import agent
    case=client.post("/api/cases/demo").json()
    state=storage.get_case(case["id"])
    state["input"]["sources"][0]["status"]="unstructured_review"
    storage.save_case(state)
    calls=[]
    async def fail(*args):
        calls.append(args[1])
        raise ValueError("provider quota")
    monkeypatch.setattr(agent,"provider_available",lambda:True)
    monkeypatch.setattr(agent,"extract_records",fail)
    result=client.post(f"/api/cases/{case['id']}/agent/run",json={"allow_model_extraction":True}).json()
    assert len(calls)==1
    assert result["agent"]["model_attempts"]==1
    assert result["agent"]["status"]=="waiting_review"
    client.post(f"/api/cases/{case['id']}/agent/resume",json={"allow_model_extraction":True})
    assert len(calls)==1


def test_optimistic_checkpoint_rejects_concurrent_financial_edit(client):
    case=client.post("/api/cases/demo").json()
    earlier=storage.get_case(case["id"])
    changed=storage.get_case(case["id"])
    changed["revision"]+=1
    storage.save_case(changed)
    with pytest.raises(storage.ConcurrentCaseUpdate):
        storage.save_case(earlier,expected_revision=earlier["revision"])


def test_agent_rejects_unbounded_step_request(client):
    case=client.post("/api/cases/demo").json()
    assert client.post(f"/api/cases/{case['id']}/agent/run",json={"max_steps":100}).status_code==422
