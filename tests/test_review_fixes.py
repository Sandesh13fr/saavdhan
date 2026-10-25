"""Review regressions. All offers and contact details are synthetic."""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend import agent, ingest, main, storage
from backend.extract_fallback import extract
from backend.models import SourceRef, Verdict
from backend.rules import run_rules


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    main._hits.clear()
    return TestClient(main.app)


def test_body_limit_before_reading_and_optional_length(client, monkeypatch):
    def unread_body():
        pytest.fail("Oversized body must be rejected before reading")
        yield b"SYNTHETIC"

    assert client.post("/api/offers", content=unread_body(), headers={
        "Content-Length": str(160 * 1024 * 1024 + 1),
        "Content-Type": "multipart/form-data; boundary=synthetic",
    }).status_code == 413
    monkeypatch.setenv("SAAVDHAN_MAX_BODY_MB", "1")
    assert client.post("/api/offers", content=unread_body(), headers={
        "Content-Length": str(1024 * 1024 + 1),
    }).status_code == 413
    assert client.post("/api/offers", data={"text": "SYNTHETIC offer"}).status_code == 200
    assert client.post("/api/offers", content=iter([b"text=SYNTHETIC+offer"]), headers={
        "Content-Type": "application/x-www-form-urlencoded",
    }).status_code == 200
    assert client.post("/api/offers", files=[
        ("files", (f"synthetic-{i}.txt", b"SYNTHETIC offer")) for i in range(11)
    ]).status_code == 400


def test_ingest_runs_outside_event_loop(client, monkeypatch):
    original = main.ingest_bytes
    calls = []

    def worker_ingest(name, data):
        with pytest.raises(RuntimeError, match="no running event loop"):
            asyncio.get_running_loop()
        calls.append(name)
        return original(name, data)

    monkeypatch.setattr(main, "ingest_bytes", worker_ingest)
    assert client.post("/api/offers", data={"text": "SYNTHETIC offer"}).status_code == 200
    assert calls == ["pasted-offer.txt"]


@pytest.mark.parametrize("route", ["analyze", "safety-plan", "checkin", "advance-clock", "packet"])
@pytest.mark.parametrize("conflict", [False, True])
def test_mutations_increment_revision_and_reject_lost_updates(client, monkeypatch, route, conflict):
    case = client.post("/api/demo/offers/bangkok-data-entry").json()
    cid = case["id"]
    plan = {"traveller_alias": "SYNTHETIC traveller", "contacts": [
        {"alias": "SYNTHETIC family", "channel": "SYNTHETIC demo inbox"}]}
    assert client.post(f"/api/offers/{cid}/safety-plan", json=plan).status_code == 200
    assert client.post(f"/api/offers/{cid}/analyze").status_code == 200
    before = storage.get_case(cid)
    original = storage.save_case
    calls = []

    def checked_save(state, expected_revision=None):
        calls.append(expected_revision)
        assert expected_revision == before["revision"]
        assert state["revision"] == expected_revision + 1
        if conflict:
            concurrent = storage.get_case(cid)
            concurrent["revision"] += 1
            main.audit(concurrent, "concurrent", "SYNTHETIC concurrent update")
            original(concurrent, expected_revision=expected_revision)
        original(state, expected_revision=expected_revision)

    monkeypatch.setattr(storage, "save_case", checked_save)
    if route == "packet":
        response = client.get(f"/api/offers/{cid}/packet")
    elif route == "advance-clock":
        response = client.post("/api/demo/advance-clock", json={"case_id": cid, "hours": 30})
    else:
        response = client.post(f"/api/offers/{cid}/{route}", json=plan if route == "safety-plan" else {"note": "SYNTHETIC check-in"})
    assert calls == [before["revision"]]
    assert response.status_code == (409 if conflict else 200)
    stored = storage.get_case(cid)
    assert stored["revision"] == before["revision"] + 1
    assert stored["audit"][-1]["action"] == ("concurrent" if conflict else {
        "analyze": "analyzed", "safety-plan": "safety_plan", "checkin": "checkin",
        "advance-clock": "demo_clock", "packet": "packet",
    }[route])
    if conflict:
        assert response.json()["detail"] == "Case changed; reload and try again"
    elif route != "packet":
        assert response.json()["revision"] == stored["revision"]


@pytest.mark.parametrize("context", ["Our office is in", "Address:", "Headquarters:", "Based in", "कार्यालय", "ऑफिस", "पत्ता"])
@pytest.mark.parametrize("place", ["Dubai", "U.A.E."])
def test_office_country_is_not_destination_and_r6_sees_route(context, place):
    text = f"SYNTHETIC {context} {place}.\nData entry job in Myanmar. Employment visa."
    source = SourceRef(id="SYNTHETIC", file="synthetic.txt", kind="message_export", text=text)
    offer = extract([source])
    assert offer.destination_country.value == "Myanmar"
    assert [place.value for place in offer.transit_countries] == ["United Arab Emirates"]
    assert all(place.quote in text for place in [offer.destination_country, *offer.transit_countries])
    assert next(hit for hit in run_rules(offer, None) if hit.rule_id == "R6_HIGH_RISK_CORRIDOR").status == "hit"
    # Countries without an explicit transit label also remain rule evidence.
    other = extract([source.model_copy(update={"text": "SYNTHETIC Data entry job in Dubai.\nMyanmar."})])
    assert [place.value for place in other.transit_countries] == ["Myanmar"]
    assert next(hit for hit in run_rules(other, None) if hit.rule_id == "R6_HIGH_RISK_CORRIDOR").status == "hit"
    office_only = extract([source.model_copy(update={"text": f"SYNTHETIC {context} {place}."})])
    assert office_only.destination_country.value is None
    assert [place.value for place in office_only.transit_countries] == ["United Arab Emirates"]


@pytest.mark.parametrize("text", [
    "SYNTHETIC Salary INR 50000 per month processing fee INR 250000.",
    "SYNTHETIC Processing fee INR 250000 salary INR 50000 per month.",
    "SYNTHETIC Salary 50000 per month processing fee 250000.",
])
def test_each_amount_follows_its_own_label(text):
    offer = extract([SourceRef(id="SYNTHETIC", file="synthetic.txt", kind="message_export", text=text)])
    assert offer.salary_amount.value == "50000"
    assert offer.fees_demanded_inr.value == "250000"
    assert offer.salary_amount.quote in text and offer.fees_demanded_inr.quote in text


@pytest.mark.parametrize("kind", ["txt", "png", "pdf"])
@pytest.mark.parametrize("level", ["NO_RED_FLAGS_FOUND", "VERIFY_FIRST", "STOP"])
def test_truncation_warns_and_long_lines_are_checked(client, monkeypatch, kind, level):
    text = "SYNTHETIC " + "x " * 3000 + "Tourist visa for data entry in Myanmar. Fee INR 250000. " + "x " * 50000
    data = text.encode("utf-8")
    if kind == "png":
        monkeypatch.setattr(ingest, "ocr_image", lambda data: text)
        data = b"SYNTHETIC image placeholder"
    elif kind == "pdf":
        monkeypatch.setattr("pypdf.PdfReader", lambda data: SimpleNamespace(
            pages=[SimpleNamespace(extract_text=lambda: text)]))
        data = b"SYNTHETIC PDF placeholder"
    case = client.post("/api/offers", files={"files": (f"synthetic.{kind}", data)}).json()
    assert storage.get_case(case["id"])["ingest_truncated"] is True
    assert "Only the first 100,000 characters were checked." in case["audit"][-1]["detail"]
    assert max(len(source["text"]) for source in case["sources"]) == 100000
    monkeypatch.setattr(agent, "decide", lambda hits, date: Verdict(
        level=level, rule_hits=hits, ra_list_date=date, next_steps_key=f"next.{level}"))
    result = client.post(f"/api/offers/{case['id']}/analyze").json()["analysis"]
    assert result["offer"]["visa_type"]["value"] == "tourist"
    assert result["offer"]["fees_demanded_inr"]["value"] == "250000"
    assert result["verdict"]["level"] == ("VERIFY_FIRST" if level == "NO_RED_FLAGS_FOUND" else level)
    assert result["verdict"]["next_steps_key"] == f"next.{result['verdict']['level']}"
    assert "Part of the document was not checked." in result["errors"]


def test_get_persists_new_alerts_once(client):
    case = client.post("/api/offers", data={"text": "SYNTHETIC offer"}).json()
    cid = case["id"]
    client.post(f"/api/offers/{cid}/safety-plan", json={
        "traveller_alias": "SYNTHETIC traveller", "contacts": [
            {"alias": "SYNTHETIC family", "channel": "SYNTHETIC demo inbox"}]})
    state = storage.get_case(cid)
    state["safety"]["plan"]["last_checkin"] = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    storage.save_case(state)
    response = client.get(f"/api/offers/{cid}").json()
    assert response["revision"] == state["revision"] + 1
    assert len(response["safety"]["alerts"]) == 1
    assert storage.get_case(cid)["safety"]["alerts"] == response["safety"]["alerts"]
    again = client.get(f"/api/offers/{cid}").json()
    assert again["revision"] == response["revision"]
    assert again["safety"]["alerts"] == response["safety"]["alerts"]


def test_anonymous_retention_applies_on_read_and_preserves_tenants(client, monkeypatch):
    monkeypatch.setenv("SAAVDHAN_RETENTION_HOURS", "2")
    case = client.post("/api/offers", data={"text": "SYNTHETIC expired offer"}).json()
    fresh = client.post("/api/offers", data={"text": "SYNTHETIC current offer"}).json()
    state = storage.get_case(case["id"])
    state["created_at"] = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    storage.save_case(state)
    token = storage.TENANT.set("SYNTHETIC-tenant")
    try:
        storage.save_case({**state, "id": "SYNTHETIC-tenant-case"})
    finally:
        storage.TENANT.reset(token)
    assert client.get(f"/api/offers/{case['id']}").status_code == 404
    assert storage.get_case(case["id"]) is None
    assert not (storage.DATA_DIR / "uploads" / case["id"]).exists()
    assert client.get(f"/api/offers/{fresh['id']}").status_code == 200
    token = storage.TENANT.set("SYNTHETIC-tenant")
    try:
        assert main.require_case("SYNTHETIC-tenant-case")["id"] == "SYNTHETIC-tenant-case"
    finally:
        storage.TENANT.reset(token)
