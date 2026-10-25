import asyncio
import pytest
import httpx
from backend import providers
from backend import storage


@pytest.fixture(autouse=True)
def isolated_usage_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
from backend.providers import extract_records, provider_available, validate_extraction


def test_disabled_provider_never_calls_network(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("BAKAYA_ENABLE_LLM", "false")
    assert not provider_available()
    assert asyncio.run(extract_records("confidential document", "source-1")) is None


def test_gateway_configuration_and_quoted_response(monkeypatch):
    monkeypatch.setenv("BAKAYA_ENABLE_LLM", "true")
    monkeypatch.setenv("LITELLM_API_KEY", "test-gateway-key")
    monkeypatch.setenv("BAKAYA_LLM_BASE_URL", "https://gateway.example/v1/")
    monkeypatch.setenv("BAKAYA_OPENAI_MODEL", "claude-haiku")
    import json
    def handle(request):
        assert str(request.url) == "https://gateway.example/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-gateway-key"
        body = json.loads(request.content)
        assert body["model"] == "claude-haiku"
        assert body["max_tokens"] == 4096
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"records": [{"kind": "buyer", "fields": [
                {"name": "name", "value": "Acme", "quote": "Buyer: Acme"}]}]})}}],
            "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80}})
    original = httpx.AsyncClient
    monkeypatch.setattr(providers.httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(handle), **kwargs))
    assert asyncio.run(extract_records("Buyer: Acme", "TEST"))["buyer"]["name"] == "Acme"


def test_gateway_budget_failure_is_not_retried(monkeypatch):
    monkeypatch.setenv("BAKAYA_ENABLE_LLM", "true")
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")
    attempts = []
    def handle(request):
        attempts.append(request)
        return httpx.Response(429, json={"error": {"message": "budget exceeded"}})
    original = httpx.AsyncClient
    monkeypatch.setattr(providers.httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(handle), **kwargs))
    with pytest.raises(ValueError, match="budget unavailable"):
        asyncio.run(extract_records("Buyer: Acme", "TEST"))
    assert len(attempts) == 1


@pytest.mark.parametrize("tool,accepted", [("request_review", True), ("approve_and_file", False)])
def test_model_planner_enforces_server_tool_allowlist(monkeypatch, tool, accepted):
    import json
    monkeypatch.setenv("BAKAYA_ENABLE_LLM", "true")
    monkeypatch.setenv("LITELLM_API_KEY", "test-key")
    def handle(request):
        body = json.loads(request.content)
        assert body["max_tokens"] == 256
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"tool": tool, "reason": "Missing evidence requires review."})}}]})
    original = httpx.AsyncClient
    monkeypatch.setattr(providers.httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(handle), **kwargs))
    call = providers.plan_next_tool({"blocker_count": 1}, ["request_review", "analyze_ledger"])
    if accepted:
        assert asyncio.run(call)["tool"] == "request_review"
    else:
        with pytest.raises(ValueError, match="invalid tool"):
            asyncio.run(call)


def test_fabricated_quote_rejected():
    payload = {"records": [{"kind": "buyer", "fields": [{"name": "name", "value": "Buyer", "quote": "Made up buyer"}]}]}
    with pytest.raises(ValueError, match="quote"):
        validate_extraction(payload, "Actual buyer: Acme", "source-1")


def test_server_attaches_provenance():
    payload = {"records": [{"kind": "buyer", "fields": [{"name": "name", "value": "Acme", "quote": "Buyer: Acme"}]}]}
    result = validate_extraction(payload, "Buyer: Acme", "source-1")
    assert result["buyer"]["source_refs"] == ["source-1"]
    assert result["buyer"]["field_sources"]["name"] == ["source-1"]


def test_injected_approval_field_rejected():
    payload = {"records": [{"kind": "buyer", "fields": [{"name": "approved", "value": "true", "quote": "approved"}]}]}
    with pytest.raises(ValueError, match="invalid"):
        validate_extraction(payload, "approved", "source-1")


def test_incomplete_invoice_rejected():
    payload = {"records": [{"kind": "invoices", "fields": [{"name": "number", "value": "INV-1", "quote": "INV-1"}]}]}
    with pytest.raises(ValueError, match="typed validation"):
        validate_extraction(payload, "INV-1", "source-1")


def test_amount_cannot_disagree_with_quote():
    payload = {"records": [{"kind": "invoices", "fields": [{"name": "amount", "value": "200000", "quote": "Total INR 100,000"}]}]}
    with pytest.raises(ValueError, match="numeric value"):
        validate_extraction(payload, "Total INR 100,000", "source-1")
