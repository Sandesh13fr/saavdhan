"""Content-free tracing for document extraction; no financial records exported."""
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import sqlite3

import neatlogs
from . import storage


def record_usage(span, model, response, body):
    """Record gateway-reported usage, never estimate unavailable dollar costs."""
    usage = body.get("usage", {})
    cost = None
    try:
        value = Decimal(response.headers.get("x-litellm-response-cost", ""))
        if value.is_finite() and value >= 0:
            cost = str(value)
            span.set_attribute("bakaya.gateway_cost_usd", float(value))
    except InvalidOperation:
        pass
    counts = {}
    for field, label in (("prompt_tokens", "prompt"), ("completion_tokens", "completion"), ("total_tokens", "total")):
        count = usage.get(field)
        if isinstance(count, int) and count >= 0:
            span.set_attribute(f"neatlogs.llm.token_count.{label}", count)
            counts[field] = count
    try:
        with storage.connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS model_usage (id TEXT PRIMARY KEY, at TEXT, model TEXT, prompt_tokens INTEGER, completion_tokens INTEGER, cost_usd TEXT)")
            conn.execute("INSERT INTO model_usage VALUES (?,?,?,?,?,?)", (
                uuid.uuid4().hex, datetime.now(timezone.utc).isoformat(), model,
                counts.get("prompt_tokens"), counts.get("completion_tokens"), cost))
    except sqlite3.Error:
        # Telemetry persistence must not change extraction/approval behavior.
        pass


def redact_errors(item, *, context=None):
    # Route errors may contain uploaded filenames or validation excerpts.
    for event in item.get("events", []):
        attrs = event.get("attributes", {})
        for key in ("exception.message", "exception.stacktrace"):
            if key in attrs:
                attrs[key] = "[redacted]"
    return item


def initialize():
    neatlogs.init(
        api_key=os.getenv("NEATLOGS_API_KEY"),
        endpoint="https://ingest.neatlogs.com",
        workflow_name="invoice-document-extraction",
        register_shutdown_handlers=False,
        mask=redact_errors,
    )


def shutdown():
    neatlogs.shutdown()
