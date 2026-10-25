from __future__ import annotations

from datetime import date as Date, datetime, timezone, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_refs: list[str] = Field(default_factory=list)
    field_sources: dict[str, list[str]] = Field(default_factory=dict)


class SourceRef(BaseModel):
    id: str
    file: str
    kind: str
    status: str = "parsed"
    page: int | None = None
    line: int | None = None
    text: str = ""

    @field_validator("text")
    @classmethod
    def bounded_source_text(cls,value):
        import os
        if os.getenv("BAKAYA_ENV", "local") != "local" and len(value)>200000:
            raise ValueError("Evidence source exceeds 200000 characters")
        return value

    sha256: str = ""
    stored_name: str | None = None
    replacement_source_id: str | None = None


class Supplier(Record):
    name: str = ""
    category: Literal["micro", "small", "medium", "unknown"] = "unknown"
    activity: Literal["manufacturing", "services", "trading", "unknown"] = "unknown"
    udyam_number: str = ""
    udyam_date: Date | None = None
    address: str = ""


class Buyer(Record):
    name: str = ""
    address: str = ""


class Invoice(Record):
    id: str
    number: str
    date: Date
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    buyer: str = ""
    delivery_date: Date | None = None
    acceptance_date: Date | None = None
    written_term_days: int | None = Field(default=None, ge=0, le=3650)
    contract_date: Date | None = None
    objection_date: Date | None = None
    objection_resolved_date: Date | None = None


class PurchaseOrder(Record):
    id: str
    number: str
    invoice_id: str
    date: Date
    written_term_days: int | None = Field(default=None, ge=0)


class Delivery(Record):
    id: str
    invoice_id: str
    date: Date
    accepted: bool = False


class Message(Record):
    id: str
    date: Date | None = None
    text: str
    invoice_ids: list[str] = Field(default_factory=list)


class Allocation(Record):
    invoice_id: str
    amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    tds_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=18, decimal_places=2)


class Payment(Record):
    id: str
    date: Date
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    reference: str = ""
    invoice_ids: list[str] = Field(default_factory=list)
    allocations: list[Allocation] = Field(default_factory=list)
    tds_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=18, decimal_places=2)
    tds_evidence_source: str | None = None
    tds_section: str | None = None


class RatePeriod(Record):
    start: Date
    end: Date
    bank_rate: Decimal = Field(gt=0, le=30)
    source: str
    fetched_at: str | None = None
    synthetic: bool = False

    @model_validator(mode="after")
    def ordered(self):
        if self.end <= self.start:
            raise ValueError("Rate end must be after start (end is exclusive)")
        return self


class CaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = "Untitled receivables case"
    supplier: Supplier = Field(default_factory=Supplier)
    buyer: Buyer = Field(default_factory=Buyer)
    as_of: Date = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=5, minutes=30))).date())
    invoices: list[Invoice] = Field(default_factory=list, max_length=200)
    payments: list[Payment] = Field(default_factory=list, max_length=1000)
    purchase_orders: list[PurchaseOrder] = Field(default_factory=list)
    deliveries: list[Delivery] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)
    rates: list[RatePeriod] = Field(default_factory=list, max_length=100)
    sources: list[SourceRef] = Field(default_factory=list,max_length=100)
    bank_total: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def unique_ids(self):
        for label, records in [("invoice", self.invoices), ("payment", self.payments), ("source", self.sources)]:
            ids = [r.id for r in records]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate {label} IDs")
        return self


class RunRequest(BaseModel):
    mode: Literal["fixed", "baseline"] = "fixed"
    simulate_rate_failure: bool = False


class Resolution(BaseModel):
    payment_id: str
    allocations: list[Allocation]
    reason: str = Field(min_length=5)
    source_id: str


class InvoiceCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invoice_id: str
    source_id: str
    reason: str = Field(min_length=5)
    fields: dict[str, str | int | None]

    @model_validator(mode="after")
    def editable_fields(self):
        allowed={"number","date","amount","buyer","delivery_date","acceptance_date","contract_date","written_term_days","objection_date","objection_resolved_date"}
        if not self.fields or not set(self.fields)<=allowed:
            raise ValueError("Invoice correction may edit only documented invoice facts; IDs/provenance cannot be changed directly")
        return self


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer: str = Field(default="Local reviewer", min_length=1)
    rate_confirmed: bool | None = None
    buyer_confirmed: bool | None = None
    resolutions: list[Resolution] = Field(default_factory=list)
    source_reviews: list[dict[str, str]] = Field(default_factory=list)
    invoice_updates: list[InvoiceCorrection] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    reviewer: str = Field(min_length=1)


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_steps: int = Field(default=8, ge=1, le=12)
    allow_model_extraction: bool = False
    allow_model_planning: bool = False
    simulate_tool_failure: bool = False

