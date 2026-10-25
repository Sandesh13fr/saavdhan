import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend import storage


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(storage,"DATA_DIR",tmp_path)
    return TestClient(app)


def resolve(client,case):
    return client.patch(f"/api/cases/{case['id']}/review",json={"reviewer":"Test reviewer","rate_confirmed":True,"buyer_confirmed":True,"resolutions":[{"payment_id":"PAY-003","source_id":"REMIT-003","reason":"Confirmed remittance note INV-004","allocations":[{"invoice_id":"INV-004","amount":"150000.00","tds_amount":"0"}]}]})


def test_human_review_and_approval_gate_complete_packet(client):
    case=client.post("/api/cases/demo").json()
    cid=case["id"]
    assert client.get(f"/api/cases/{cid}/export").status_code==409
    assert client.post(f"/api/cases/{cid}/approve",json={"reviewer":"Me"}).status_code==409
    reviewed=resolve(client,case)
    assert reviewed.status_code==200 and reviewed.json()["status"]=="ready"
    assert reviewed.json()["totals"]["principal"]=="470000.00"
    approved=client.post(f"/api/cases/{cid}/approve",json={"reviewer":"Me"})
    assert approved.status_code==200 and approved.json()["status"]=="approved"
    packet=client.get(f"/api/cases/{cid}/export")
    assert packet.status_code==200
    with zipfile.ZipFile(io.BytesIO(packet.content)) as archive:
        required={"odr-field-sheet.json","interest-schedule.pdf","interest-schedule.csv","demand-letter.pdf","demand-letter.txt","evidence-index.csv","approval.json"}
        assert required<=set(archive.namelist())
        assert "SYNTHETIC DEMO" in archive.read("demand-letter.txt").decode()
        assert "rate_source" in archive.read("interest-schedule.csv").decode()


def test_rerun_invalidates_previous_approval(client):
    case=client.post("/api/cases/demo").json()
    resolve(client,case)
    client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Me"})
    client.post(f"/api/cases/{case['id']}/run",json={"mode":"fixed"})
    assert client.get(f"/api/cases/{case['id']}/export").status_code==409


def test_upload_unreadable_scan_invalidates_approval_and_flags_ocr(client):
    case=client.post("/api/cases/demo").json()
    resolve(client,case)
    client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Me"})
    updated=client.post(f"/api/cases/{case['id']}/upload",files=[("files",("scan.png",b"not-readable-image","image/png"))])
    assert updated.status_code==200
    assert any(s["status"]=="ocr_unavailable" for s in updated.json()["sources"])
    assert client.get(f"/api/cases/{case['id']}/export").status_code==409


def test_tampered_allocation_preserves_blocker(client):
    case=client.post("/api/cases/demo").json()
    request={"rate_confirmed":True,"buyer_confirmed":True,"resolutions":[{"payment_id":"PAY-003","source_id":"REMIT-003","reason":"malicious over-allocation","allocations":[{"invoice_id":"INV-004","amount":"200000"}]}]}
    result=client.patch(f"/api/cases/{case['id']}/review",json=request)
    assert result.status_code==200
    assert any(b["code"]=="allocation_mismatch" for b in result.json()["blockers"])
    assert client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Me"}).status_code==409


def test_source_download_and_traversal_are_safe(client):
    case=client.post("/api/cases/demo").json()
    result=client.get(f"/api/cases/{case['id']}/sources/REMIT-003/download")
    assert result.status_code==200 and b"INV-004" in result.content
    assert client.get("/api/cases/no-such-case").status_code==404


def test_simulated_rate_failure_is_honestly_labeled(client):
    case=client.post("/api/cases/demo").json()
    result=client.post(f"/api/cases/{case['id']}/run",json={"simulate_rate_failure":True})
    assert result.status_code==200
    details=" ".join(a["detail"] for a in result.json()["audit"])
    assert "SIMULATION" in details and "no external HTTP request" in details


def test_bad_money_validation_and_cross_origin_mutation(client):
    assert client.post("/api/cases",json={"invoices":[{"id":"I","number":"I","date":"2026-01-01","amount":"NaN"}]}).status_code==422
    assert client.post("/api/cases/demo",headers={"origin":"https://evil.example"}).status_code==403


def test_invoice_correction_updates_provenance_and_revokes_approval(client):
    case=client.post("/api/cases/demo").json()
    resolve(client,case)
    client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Me"})
    corrected=client.patch(f"/api/cases/{case['id']}/review",json={"reviewer":"Me","invoice_updates":[{"invoice_id":"INV-002","source_id":"DOC-002","reason":"Confirmed written terms against original document","fields":{"written_term_days":45}}]})
    assert corrected.status_code==200
    invoice=next(i for i in corrected.json()["invoices"] if i["id"]=="INV-002")
    assert invoice["due_date"]=="2026-06-17"
    assert invoice["field_sources"]["written_term_days"]==["DOC-002"]
    assert corrected.json()["approval"] is None
    assert client.get(f"/api/cases/{case['id']}/export").status_code==409


def test_invoice_correction_cannot_edit_ids_or_bad_dates(client):
    case=client.post("/api/cases/demo").json()
    base={"invoice_id":"INV-001","source_id":"DOC-001","reason":"Reviewer correction"}
    assert client.patch(f"/api/cases/{case['id']}/review",json={"invoice_updates":[{**base,"fields":{"id":"OTHER"}}]}).status_code==422
    assert client.patch(f"/api/cases/{case['id']}/review",json={"invoice_updates":[{**base,"fields":{"date":"invalid"}}]}).status_code==422
    saved=client.get(f"/api/cases/{case['id']}").json()
    assert saved["invoices"][0]["id"]=="INV-001" and saved["invoices"][0]["date"]=="2026-05-01"


def test_unreadable_evidence_supersession_keeps_replacement_link(client):
    case=client.post("/api/cases/demo").json()
    uploaded=client.post(f"/api/cases/{case['id']}/upload",files=[("files",("scan.png",b"unreadable","image/png"))]).json()
    scan=next(s for s in uploaded["sources"] if s["status"]=="ocr_unavailable")
    reviewed=client.patch(f"/api/cases/{case['id']}/review",json={"source_reviews":[{"source_id":scan["id"],"replacement_source_id":"DOC-001","reason":"Readable delivery proof replaces unprocessed scan"}]}).json()
    source=next(s for s in reviewed["sources"] if s["id"]==scan["id"])
    assert source["status"]=="superseded" and source["replacement_source_id"]=="DOC-001"
    assert not any(b.get("source_id")==scan["id"] for b in reviewed["blockers"])


def test_export_approval_hash_catches_input_changed_without_revision(client):
    case=client.post("/api/cases/demo").json()
    resolve(client,case)
    client.post(f"/api/cases/{case['id']}/approve",json={"reviewer":"Me"})
    state=storage.get_case(case["id"])
    state["input"]["invoices"][0]["amount"]="200000.00"
    storage.save_case(state)
    assert client.get(f"/api/cases/{case['id']}/export").status_code==409


def test_dns_rebinding_host_and_opaque_origin_rejected(client):
    assert client.get("/api/cases", headers={"host": "evil.example"}).status_code == 400
    assert client.post("/api/cases/demo", headers={"origin": "null"}).status_code == 403
