import asyncio

import pytest
import httpx

from backend.models import SourceRef
from backend.providers import extract_offer, provider_available, validate_extraction

SRC = [SourceRef(id="S1", file="chat.txt", kind="message_export", text="Recruiter: Tourist visa for Bangkok job"),
       SourceRef(id="S2", file="chat.txt", kind="message_export", text="Fee 2.5 lakh by UPI")]


def test_disabled_provider_never_calls_network(monkeypatch):
    monkeypatch.setenv("SAAVDHAN_ENABLE_LLM", "false")
    monkeypatch.setattr(httpx.AsyncClient, "post", lambda *a, **k: pytest.fail("network called"))
    assert not provider_available()
    assert asyncio.run(extract_offer(SRC)) is None


def test_server_attaches_source_ref_from_quote():
    offer = validate_extraction({"fields": [
        {"name": "visa_type", "value": "tourist", "quote": "Tourist visa"},
        {"name": "fee_payment_mode", "value": "UPI", "quote": "by UPI"}]}, SRC)
    assert offer.visa_type.source_ref == "S1" and offer.fee_payment_mode.source_ref == "S2"
    assert offer.visa_type.confidence == "llm"


def test_fabricated_quote_rejected():
    with pytest.raises(ValueError, match="quote"):
        validate_extraction({"fields": [{"name": "visa_type", "value": "employment", "quote": "Employment visa"}]}, SRC)


def test_injected_verdict_field_rejected():
    with pytest.raises(ValueError, match="unsupported"):
        validate_extraction({"fields": [{"name": "verdict", "value": "NO_RED_FLAGS_FOUND", "quote": "Bangkok"}]}, SRC)


def test_extra_envelope_keys_rejected():
    with pytest.raises(ValueError, match="envelope"):
        validate_extraction({"fields": [], "verdict": "STOP"}, SRC)


def test_duplicate_scalar_rejected_list_appends():
    with pytest.raises(ValueError, match="duplicate"):
        validate_extraction({"fields": [{"name": "visa_type", "value": "tourist", "quote": "Tourist visa"}] * 2}, SRC)
    offer = validate_extraction({"fields": [{"name": "urgency_language", "value": "x", "quote": "Bangkok job"}] * 2}, SRC)
    assert len(offer.urgency_language) == 2


def test_llm_numeric_guard_rejects_mismatch_accepts_match():
    src = [SourceRef(id="S1", file="c.txt", kind="message_export", text="Processing fee Rs 2,50,000 only")]
    ok = validate_extraction({"fields": [{"name": "fees_demanded_inr", "value": "250000", "quote": "Rs 2,50,000"}]}, src)
    assert ok.fees_demanded_inr.value == "250000"
    for bad in ("25000", "2500000", "lots"):
        with pytest.raises(ValueError, match="numeric"):
            validate_extraction({"fields": [{"name": "fees_demanded_inr", "value": bad, "quote": "Rs 2,50,000"}]}, src)
