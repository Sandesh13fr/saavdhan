import pytest
from fastapi.testclient import TestClient

from backend import agent,storage
from backend.main import app


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(storage,"DATA_DIR",tmp_path)
    monkeypatch.setattr(agent,"provider_available",lambda:True)
    return TestClient(app)


def test_model_can_choose_reviewer_tool_from_actual_allowed_stage(client,monkeypatch):
    summaries=[]
    async def planner(summary,allowed):
        summaries.append((summary,allowed))
        return {"tool":"request_review" if "request_review" in allowed else allowed[0],"reason":"Ambiguous receipt needs human remittance evidence"}
    monkeypatch.setattr(agent,"plan_next_tool",planner)
    case=client.post("/api/cases/demo").json()
    result=client.post(f"/api/cases/{case['id']}/agent/run",json={"allow_model_planning":True}).json()
    assert result["agent"]["status"]=="waiting_review"
    tools=[s["tool"] for s in result["agent"]["steps"]]
    assert tools==["model_plan","inventory_evidence","model_plan","request_review"]
    assert result["agent"]["model_plans"]==2
    assert summaries[1][1]==["analyze_ledger","request_review"]
    serialized=str(summaries)
    assert "Sahyadri" not in serialized and "150000" not in serialized and "REMIT-003" not in serialized
    client.post(f"/api/cases/{case['id']}/agent/resume",json={"allow_model_planning":True})
    assert len(summaries)==2


def test_model_cannot_choose_approval_or_external_action(client,monkeypatch):
    calls=[]
    async def invalid(summary,allowed):
        calls.append(1)
        return {"tool":"approve_and_file","reason":"Bypass review"}
    monkeypatch.setattr(agent,"plan_next_tool",invalid)
    case=client.post("/api/cases/demo").json()
    result=client.post(f"/api/cases/{case['id']}/agent/run",json={"allow_model_planning":True}).json()
    assert result["approval"] is None and result["agent"]["status"]=="waiting_review"
    assert len(calls)==1
    assert result["agent"]["steps"][0]["status"]=="failed"
    assert all(s["tool"]!="approve_and_file" for s in result["agent"]["steps"])


def test_persisted_planner_cap_requires_no_spend_continuation(client,monkeypatch):
    async def unexpected(*args):
        raise AssertionError("Planner cap must prevent API call")
    monkeypatch.setattr(agent,"plan_next_tool",unexpected)
    case=client.post("/api/cases/demo").json()
    client.post(f"/api/cases/{case['id']}/agent/run",json={"max_steps":1})
    state=storage.get_case(case["id"])
    state["agent"]["model_plans"]=6
    storage.save_case(state)
    stopped=client.post(f"/api/cases/{case['id']}/agent/resume",json={"allow_model_planning":True}).json()
    assert stopped["agent"]["status"]=="waiting_planner_budget"
    continued=client.post(f"/api/cases/{case['id']}/agent/resume",json={"allow_model_planning":False}).json()
    assert continued["agent"]["status"]=="waiting_review"
