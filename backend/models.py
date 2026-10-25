"""Saavdhan domain models. Extractors fill Offer; Python rules decide RuleHit and Verdict."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceRef(BaseModel):
    id: str
    file: str
    kind: str
    status: str = "parsed"
    page: int | None = None
    line: int | None = None
    text: str = ""
    sha256: str = ""
    stored_name: str | None = None

    @field_validator("text")
    @classmethod
    def bounded_source_text(cls, value):
        if os.getenv("SAAVDHAN_ENV", "local") != "local" and len(value) > 200000:
            raise ValueError("Source exceeds 200000 characters")
        return value


class FieldValue(BaseModel):
    """One extracted fact. `quote` is verbatim source text; `source_ref` is attached by the server."""
    model_config = ConfigDict(extra="forbid")
    value: str | None = None
    quote: str = ""
    source_ref: str | None = None
    # Extractor's own label (llm / fallback); never read by rules or verdict.
    confidence: str | None = None


def _f():
    return Field(default_factory=FieldValue)


class Offer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_ids: list[str] = Field(default_factory=list)
    agent_name: FieldValue = _f()
    agent_rc_number: FieldValue = _f()
    agent_phones: list[FieldValue] = Field(default_factory=list)
    agent_channels: list[FieldValue] = Field(default_factory=list)
    employer_name: FieldValue = _f()
    destination_country: FieldValue = _f()
    transit_countries: list[FieldValue] = Field(default_factory=list)
    visa_type: FieldValue = _f()  # employment|work|tourist|visit|unknown
    role_title: FieldValue = _f()
    salary_amount: FieldValue = _f()
    salary_currency: FieldValue = _f()
    fees_demanded_inr: FieldValue = _f()
    fee_payment_mode: FieldValue = _f()
    receipt_promised: FieldValue = _f()
    contract_mentioned: FieldValue = _f()
    contract_signatories: list[FieldValue] = Field(default_factory=list)
    pbby_insurance_mentioned: FieldValue = _f()
    passport_handover_requested: FieldValue = _f()
    urgency_language: list[FieldValue] = Field(default_factory=list)


LIST_FIELDS = {name for name, f in Offer.model_fields.items() if name != "source_ids" and f.annotation == list[FieldValue]}
SCALAR_FIELDS = {name for name in Offer.model_fields if name not in LIST_FIELDS | {"source_ids"}}

Severity = Literal["critical", "high", "medium", "low", "info"]


class RuleHit(BaseModel):
    rule_id: str
    severity: Severity
    status: Literal["hit", "clear", "unknown"]
    evidence: list[FieldValue] = Field(default_factory=list)
    explanation_key: str
    rule_source_url: str
    heuristic: bool = False


class Verdict(BaseModel):
    level: Literal["STOP", "VERIFY_FIRST", "NO_RED_FLAGS_FOUND"]
    rule_hits: list[RuleHit]
    ra_list_date: str
    next_steps_key: str


class Contact(BaseModel):
    alias: str = Field(min_length=1, max_length=60)
    channel: str = Field(min_length=1, max_length=120)


class SafetyPlan(BaseModel):
    traveller_alias: str = Field(min_length=1, max_length=60)
    contacts: list[Contact] = Field(min_length=1, max_length=2)
    itinerary: list[str] = Field(default_factory=list, max_length=20)
    checkin_interval_hours: int = Field(default=24, ge=1, le=168)
    last_checkin: datetime | None = None


class CheckIn(BaseModel):
    at: datetime
    note: str = Field(default="", max_length=280)


class Report(BaseModel):
    district: str
    agent_phone_hash: str
    offer_template_hash: str
    created_at: datetime
