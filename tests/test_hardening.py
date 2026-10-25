"""Regressions for the Phase 3 security review."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from backend import agent, main, storage
from backend.models import FieldValue, Offer
from backend.verdict import decide
from backend.rules import run_rules


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    main._hits.clear()
    return TestClient(main.app)


def test_no_all_clear_without_real_recruiter_list_date():
    clean = Offer(**{k: FieldValue(value=v, quote=v) for k, v in dict(
        visa_type="employment", agent_name="Example (fictional)", agent_rc_number="B-0000/DEMO", destination_country="Japan",
        role_title="welder", employer_name="Example KK", fees_demanded_inr="20000", receipt_promised="yes",
        contract_mentioned="yes", pbby_insurance_mentioned="yes", passport_handover_requested="no").items()},
        contract_signatories=[FieldValue(value=s, quote=s) for s in ("employer", "agent", "worker")],
        agent_channels=[FieldValue(value="office_address", quote="Office")])
    listed = {"status": "listed", "list_date": "2026-04-08", "evidence": "x"}
    assert decide(run_rules(clean, listed), "2026-04-08").level == "NO_RED_FLAGS_FOUND"
    assert decide(run_rules(clean, listed), "not loaded").level == "VERIFY_FIRST"


def test_llm_can_add_but_never_remove_red_flags(monkeypatch):
    async def lying_llm(sources):
        return Offer(visa_type=FieldValue(value="employment", quote="Tourist visa for Bangkok data entry"))
    monkeypatch.setattr(agent, "extract_offer", lying_llm)
    state = {"sources": [{"id": "S1", "file": "x.txt", "kind": "message_export", "text": "Tourist visa for Bangkok data entry"}]}
    result = asyncio.run(agent.analyze(state))
    r1 = next(h for h in result["verdict"]["rule_hits"] if h["rule_id"] == "R1_TOURIST_VISA")
    assert r1["status"] == "hit" and result["verdict"]["level"] == "STOP"


def test_demo_clock_refused_for_real_cases_in_production(client, monkeypatch):
    cid = client.post("/api/offers", data={"text": "job offer"}).json()["id"]
    client.post(f"/api/offers/{cid}/safety-plan", json={"traveller_alias": "A", "contacts": [{"alias": "B", "channel": "C"}]})
    monkeypatch.setenv("SAAVDHAN_ENV", "production")
    monkeypatch.setenv("SAAVDHAN_PUBLIC_ORIGIN", "https://testserver")
    assert client.post("/api/demo/advance-clock", json={"case_id": cid, "hours": 30}).status_code == 404


def test_rate_limit_and_text_cap(client, monkeypatch):
    monkeypatch.setattr(main, "RATE_MAX", 3)
    assert client.post("/api/offers", data={"text": "x" * 50001}).status_code == 413
    for _ in range(2):
        assert client.post("/api/offers", data={"text": "x"}).status_code == 200
    assert client.post("/api/offers", data={"text": "x"}).status_code == 429


def test_line_sources_capped(client):
    case = client.post("/api/offers", data={"text": "a\n" * 5000}).json()
    assert len(case["sources"]) <= 502


def test_anonymous_cases_expire_and_evict(client, monkeypatch):
    first = client.post("/api/offers", data={"text": "x"}).json()["id"]
    monkeypatch.setenv("SAAVDHAN_ANON_CASE_CAP", "2")
    client.post("/api/offers", data={"text": "y"})
    client.post("/api/offers", data={"text": "z"})
    assert client.get(f"/api/offers/{first}").status_code == 404
    assert storage.purge_anonymous(0, 100) == 2  # age 0h: everything left is expired


def test_anonymous_upload_budget_is_freed_by_purge(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setenv("SAAVDHAN_ENV", "production")
    monkeypatch.setenv("SAAVDHAN_ANON_UPLOAD_MB", "1")
    storage.save_case({"id": "old", "created_at": "2000-01-01T00:00:00+00:00", "audit": []})
    (storage.upload_dir("old") / "f.txt").write_bytes(b"x" * 900_000)
    with pytest.raises(storage.TenantCapacityExceeded):
        storage.reserve_upload_bytes(200_000)
    storage.purge_anonymous(24, 100)
    storage.reserve_upload_bytes(200_000)  # space is back


def test_demo_officer_bootstrap_from_env(tmp_path, monkeypatch):
    from backend import auth
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setenv("SAAVDHAN_DEMO_OFFICER_PASSWORD", "a demo password 123")
    main.bootstrap_demo_officer()
    main.bootstrap_demo_officer()  # idempotent
    token, identity = auth.login("officer@saavdhan.example", "a demo password 123")
    assert identity["user"]["role"] == "viewer"
