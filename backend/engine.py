"""Deterministic rules. Rates and allocations are inputs, never model guesses.

Convention: actual/365 simple accrual within calendar-month anniversary rests;
unrounded accrued interest capitalizes at each rest. Payments credit principal
at the START of their date. As-of is inclusive. Money rounds only for display.
The Act specifies monthly rests, not a complete computational convention;
reviewers must confirm this convention and appropriation before real filing.
"""
from __future__ import annotations

import calendar
import re
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, localcontext

from .models import CaseInput, Invoice, RatePeriod

ZERO = Decimal("0")
CENT = Decimal("0.01")
RULES_SOURCE = "https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf"
CONVENTION = "Actual/365; monthly anniversary rests; principal-first payments at start of payment date; as-of inclusive; no intermediate rounding. Unpaid capitalized interest continues after principal settlement."


def money(value: Decimal | str | int) -> str:
    return str(Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP))


def add_month(anchor: date, n: int) -> date:
    month = anchor.month - 1 + n
    year, month = anchor.year + month // 12, month % 12 + 1
    return date(year, month, min(anchor.day, calendar.monthrange(year, month)[1]))


def due_dates(invoice: Invoice) -> tuple[date, date]:
    acceptance = invoice.acceptance_date or invoice.delivery_date
    if acceptance is None:
        raise ValueError("Acceptance or delivery evidence is required")
    if acceptance < invoice.date:
        raise ValueError("Acceptance before invoice date requires professional review")
    if invoice.objection_date:
        if not invoice.delivery_date:
            raise ValueError("Delivery date required to assess objection timing")
        if invoice.objection_date < invoice.delivery_date:
            raise ValueError("Objection cannot precede delivery")
        if invoice.objection_date <= invoice.delivery_date + timedelta(days=15):
            if not invoice.objection_resolved_date:
                raise ValueError("Timely written objection unresolved: acceptance cannot be assumed")
            if invoice.objection_resolved_date < invoice.objection_date:
                raise ValueError("Objection resolution cannot precede objection")
            acceptance = invoice.objection_resolved_date
    days = 15 if invoice.written_term_days is None else min(invoice.written_term_days, 45)
    due = acceptance + timedelta(days=days)
    return due, due + timedelta(days=1)


def interest_schedule(amount: Decimal, start: date, as_of: date,
                      credits: list[tuple[date, Decimal]], rates: list[RatePeriod], invoice_id: str = ""):
    """Return full-precision interest, principal, and display schedule.

    Rate periods are [start,end). Gaps and overlaps fail closed, including
    dates where only capitalized interest remains outstanding.
    """
    with localcontext() as ctx:
        ctx.prec = 36
        principal, capitalized, accrued = amount, ZERO, ZERO
        stop = as_of + timedelta(days=1)
        principal -= sum((v for d, v in credits if d <= start), ZERO)
        if principal < ZERO:
            raise ValueError("Credits exceed invoice principal")
        if start >= stop:
            remaining = amount - sum((v for d, v in credits if d <= as_of), ZERO)
            if remaining < ZERO:
                raise ValueError("Credits exceed invoice principal")
            return ZERO, remaining, []
        changes = {start, stop}
        changes.update(d for d, _ in credits if start < d < stop)
        for rate in rates:
            changes.update(d for d in [rate.start, rate.end] if start < d < stop)
        rests, n = set(), 1
        while add_month(start, n) < stop:
            rests.add(add_month(start, n))
            n += 1
        changes.update(rests)
        ordered = sorted(changes)
        rows = []
        for left, right in zip(ordered, ordered[1:]):
            if left != start:
                principal -= sum((v for d, v in credits if d == left), ZERO)
            if principal < ZERO:
                raise ValueError("Credits exceed invoice principal")
            if left in rests:
                capitalized += accrued
                accrued = ZERO
            covering = [r for r in rates if r.start <= left and r.end >= right]
            if len(covering) != 1:
                raise ValueError(f"Rate coverage must be unique for {left} to {right}")
            rate = covering[0]
            annual = rate.bank_rate * 3
            increment = (principal + capitalized) * annual / 100 * Decimal((right-left).days) / 365
            accrued += increment
            rows.append({"invoice_id": invoice_id, "start": str(left), "end": str(right),
                         "days": (right-left).days, "principal": money(principal),
                         "capitalized_interest": money(capitalized), "bank_rate": str(rate.bank_rate),
                         "annual_rate": str(annual), "interest": money(increment),
                         "interest_exact": str(increment), "rate_source": rate.source,
                         "rate_source_refs": rate.source_refs, "rest": left in rests,
                         "source_refs": rate.source_refs})
        return capitalized + accrued, principal, rows


def analyze(case: CaseInput, review: dict | None = None, mode: str = "fixed") -> dict:
    review = review or {}
    sources = {s.id: s for s in case.sources}
    blockers, warnings, matches, results, schedule = [], [], [], [], []

    def block(code, message, **extra):
        blockers.append({"id": f"{code}-{len(blockers)+1}", "code": code, "message": message,
                         "question": message, "severity": "blocking", **extra})

    def provenance(record, label, required=()):
        if not record.source_refs or any(s not in sources for s in record.source_refs):
            block("missing_provenance", f"{label}: valid source references are required.")
        for field in required:
            refs = record.field_sources.get(field, [])
            if not refs or any(s not in sources for s in refs):
                block("missing_field_provenance", f"{label}: source for {field} is missing.")

    if not case.invoices:
        block("no_invoices", "Add at least one invoice with its evidence.")
    if not case.supplier.name or not case.buyer.name:
        block("missing_parties", "Supplier and buyer legal names are required.")
    provenance(case.supplier, "Supplier", ("category", "activity", "udyam_date"))
    provenance(case.buyer, "Buyer", ("name",))
    if case.supplier.category not in {"micro", "small"}:
        block("ineligible", "Only micro and small enterprises are in this preparation workflow.")
    if case.supplier.activity not in {"manufacturing", "services"}:
        block("ineligible", "Trading or unknown activity needs separate legal assessment; this workflow stops.")
    if not case.supplier.udyam_date or not case.supplier.udyam_number:
        block("registration", "Udyam registration number and date evidence are required.")
    if not review.get("buyer_confirmed"):
        block("buyer_confirmation", "Confirm the buyer's legal name and address before approval.")
    if not review.get("rate_confirmed"):
        block("rate_confirmation", "Confirm dated rates and the interest/payment convention. Synthetic rates produce a DEMO packet only.")
    if any(r.synthetic for r in case.rates):
        warnings.append("Synthetic bank rates: illustrative DEMO packet; replace with verified RBI history before real filing.")
    if mode == "baseline":
        block("baseline_only", "Baseline demonstrates the deliberately flawed matcher and cannot be approved.")
    warnings.append("Eligibility is a conservative preparation screen, subject to contract/supply facts and legal review.")
    for source in case.sources:
        if source.status in {"ocr_unavailable", "parse_error", "unstructured_review", "extracted_needs_review"}:
            block("unreadable_evidence" if source.status != "unstructured_review" else "unstructured_evidence",
                  f"{source.file}: {source.status.replace('_', ' ')}. Supply structured records with references or readable alternative proof.", source_id=source.id)

    invoices = {i.id: i for i in case.invoices}
    credited = {i.id: ZERO for i in case.invoices}
    credits = {i.id: [] for i in case.invoices}
    bank = sum((p.amount for p in case.payments if p.date <= case.as_of), ZERO)
    all_bank = sum((p.amount for p in case.payments), ZERO)
    tds, allocated_bank = ZERO, ZERO
    for payment in sorted(case.payments, key=lambda p: (p.date, p.id)):
        provenance(payment, payment.id, ("amount", "date"))
        if payment.date > case.as_of:
            warnings.append(f"{payment.id} is after as-of and excluded from balances.")
            continue
        allocation_list = [a.model_dump() for a in payment.allocations]
        reason, confidence = "Explicit remittance allocation", 1.0
        if not allocation_list:
            candidates = payment.invoice_ids or [i.id for i in case.invoices if i.number.lower() in payment.reference.lower()]
            if mode == "baseline":
                candidates = [i.id for i in case.invoices if credited[i.id] < i.amount][:1]
                reason, confidence = "Baseline: first open invoice; TDS ignored", 0.3
            if len(candidates) == 1 and candidates[0] in invoices:
                allocation_list = [{"invoice_id": candidates[0], "amount": payment.amount,
                                    "tds_amount": ZERO if mode == "baseline" else payment.tds_amount}]
                reason = "Invoice reference in payment evidence" if mode == "fixed" else reason
                confidence = 0.98 if mode == "fixed" else confidence
            elif not candidates:
                candidates = [i.id for i in case.invoices if i.amount - credited[i.id] == payment.amount]
                if len(candidates) == 1:
                    block("payment_confirmation", f"{payment.id}: amount-only match to {candidates[0]} is below confidence threshold; confirm remittance evidence.", payment_id=payment.id, candidates=candidates, confidence=0.85)
                    continue
            if not allocation_list:
                block("ambiguous_payment", f"{payment.id}: choose invoices and amounts from remittance evidence; no allocation guessed.",
                      payment_id=payment.id, candidates=candidates or list(invoices))
                continue
        if mode == "baseline":
            for item in allocation_list:
                item["tds_amount"] = ZERO
        if sum((Decimal(a["amount"]) for a in allocation_list), ZERO) != payment.amount:
            block("allocation_mismatch", f"{payment.id}: allocations must equal the bank receipt.", payment_id=payment.id)
            continue
        bad = False
        local_credits = {}
        local_tds = ZERO
        for item in allocation_list:
            iid = item["invoice_id"]
            if iid not in invoices:
                block("unknown_invoice", f"{payment.id}: unknown invoice {iid}.", payment_id=payment.id)
                bad = True
                continue
            cash, tax = Decimal(item["amount"]), Decimal(item.get("tds_amount", 0))
            if tax:
                evidence = sources.get(payment.tds_evidence_source or "")
                if not evidence or evidence.kind not in {"tds_certificate", "remittance_note"} or "tds" not in evidence.text.lower():
                    block("tds_evidence", f"{payment.id}: TDS credit needs explicit certificate/remittance evidence; a 2% difference is insufficient.", payment_id=payment.id)
                    bad = True
                if payment.tds_section not in {"194C", "194J"}:
                    block("tds_section", f"{payment.id}: confirm the TDS section from evidence.", payment_id=payment.id)
                    bad = True
                if evidence:
                    documented = re.findall(r"\bTDS\s*(?:amount\s*[:=]?\s*)?(?:(?:INR|Rs\.?|₹)\s*)?([\d,]+(?:\.\d{1,2})?)", evidence.text, flags=re.I)
                    if tax not in [Decimal(value.replace(",", "")) for value in documented] or invoices[iid].number.lower() not in evidence.text.lower() or (payment.tds_section or "").lower() not in evidence.text.lower():
                        block("tds_document_mismatch", f"{payment.id}: certificate/remittance text must explicitly identify the invoice, section and claimed TDS amount.", payment_id=payment.id)
                        bad = True
            local_credits[iid] = local_credits.get(iid, ZERO) + cash + tax
            local_tds += tax
        if payment.tds_amount != local_tds and mode == "fixed":
            block("tds_mismatch", f"{payment.id}: TDS allocations must reconcile to the documented TDS amount.", payment_id=payment.id)
            bad = True
        for iid, value in local_credits.items():
            if value + credited[iid] > invoices[iid].amount:
                block("overpayment", f"{payment.id}: credits exceed {iid}; review appropriation or refund.", payment_id=payment.id)
                bad = True
        if bad:
            continue
        for item in allocation_list:
            iid = item["invoice_id"]
            cash, tax = Decimal(item["amount"]), Decimal(item.get("tds_amount", 0))
            credited[iid] += cash + tax
            credits[iid].append((payment.date, cash + tax))
            matches.append({"payment_id": payment.id, "invoice_id": iid, "amount": money(cash), "tds_amount": money(tax),
                            "confidence": confidence, "reason": reason,
                            "source_refs": list(dict.fromkeys(payment.source_refs + ([payment.tds_evidence_source] if tax else [])))})
        allocated_bank += payment.amount
        tds += local_tds
    if case.bank_total is None:
        block("bank_total", "Confirm total relevant buyer credits from the bank statement for reconciliation.")
    elif case.bank_total != all_bank:
        block("bank_mismatch", "Bank statement control total does not equal extracted payment total.")
    if bank != allocated_bank:
        block("reconciliation", "Unallocated bank credits remain. Resolve payment matches before export.")

    interest_total, principal_total = ZERO, ZERO
    for invoice in case.invoices:
        provenance(invoice, invoice.id, ("amount", "date"))
        if invoice.date > case.as_of:
            block("future_invoice", f"{invoice.id}: invoice is after as-of date.", invoice_id=invoice.id)
        if invoice.buyer and invoice.buyer.casefold().strip()!=case.buyer.name.casefold().strip():
            block("buyer_mismatch", f"{invoice.id}: buyer identity differs from the single-buyer case. Confirm or separate the claim.", invoice_id=invoice.id)
        pos=[p for p in case.purchase_orders if p.invoice_id==invoice.id]
        deliveries=[d for d in case.deliveries if d.invoice_id==invoice.id]
        if len(pos)>1 or len(deliveries)>1:
            block("conflicting_linked_evidence", f"{invoice.id}: multiple PO/delivery records need explicit consolidation before calculation.", invoice_id=invoice.id)
        for po in pos:
            provenance(po,po.id,("date","invoice_id"))
            if (invoice.contract_date and invoice.contract_date!=po.date) or (invoice.written_term_days is not None and po.written_term_days is not None and invoice.written_term_days!=po.written_term_days):
                block("conflicting_linked_evidence", f"{invoice.id}: invoice and PO contract date/terms disagree.", invoice_id=invoice.id)
        for delivery in deliveries:
            provenance(delivery,delivery.id,("date","invoice_id"))
            if invoice.delivery_date and invoice.delivery_date!=delivery.date:
                block("conflicting_linked_evidence", f"{invoice.id}: delivery evidence dates disagree.", invoice_id=invoice.id)
        if case.supplier.udyam_date:
            if case.supplier.udyam_date >= invoice.date:
                block("registration_review", f"{invoice.id}: registration was not before invoice date; eligibility requires legal review, not automatic rejection.", invoice_id=invoice.id)
            if invoice.contract_date is None:
                block("contract_date", f"{invoice.id}: contract/PO date evidence is required for registration eligibility.", invoice_id=invoice.id)
            elif case.supplier.udyam_date > invoice.contract_date:
                block("registration_review", f"{invoice.id}: contract predates registration; eligibility requires legal assessment of registration/contract/supply facts.", invoice_id=invoice.id)
        acceptance_field = "acceptance_date" if invoice.acceptance_date else "delivery_date"
        provenance(invoice, invoice.id, (acceptance_field, "contract_date"))
        if invoice.written_term_days is not None:
            provenance(invoice, invoice.id, ("written_term_days",))
        if invoice.objection_date:
            provenance(invoice, invoice.id, ("objection_date",))
            if invoice.objection_resolved_date:
                provenance(invoice, invoice.id, ("objection_resolved_date",))
        result = invoice.model_dump(mode="json")
        result.update(due_date=None, interest_start=None, outstanding=money(invoice.amount-credited[invoice.id]), interest="0.00")
        amount_interest = ZERO
        try:
            due, start = due_dates(invoice)
            result.update(due_date=str(due), interest_start=str(start))
            if due >= case.as_of:
                block("not_overdue", f"{invoice.id}: payment deadline has not passed as of {case.as_of}; exclude it from a delayed-payment claim or choose the correct calculation date.", invoice_id=invoice.id)
            amount_interest, remaining, rows = interest_schedule(invoice.amount, start, case.as_of, credits[invoice.id], case.rates, invoice.id)
            for row in rows:
                row["source_refs"] = list(dict.fromkeys(invoice.source_refs + row["source_refs"] + [ref for m in matches if m["invoice_id"] == invoice.id for ref in m["source_refs"]]))
            schedule.extend(rows)
            result.update(outstanding=money(remaining), interest=money(amount_interest))
        except ValueError as exc:
            block("calculation", f"{invoice.id}: {exc}", invoice_id=invoice.id)
        result["total"] = money(Decimal(result["outstanding"]) + amount_interest)
        principal_total += Decimal(result["outstanding"])
        interest_total += amount_interest
        results.append(result)
    for rate in case.rates:
        if not rate.source or not rate.source_refs or any(ref not in sources for ref in rate.source_refs):
            block("rate_provenance", "Every dated bank-rate period must link to a source record.")
    total_invoiced = sum((i.amount for i in case.invoices), ZERO)
    identity = total_invoiced - principal_total - allocated_bank - tds
    if identity != ZERO:
        block("ledger_mismatch", "Invoice principal does not reconcile to allocated bank receipts and evidenced TDS.")
    return {"status": "review_required" if blockers else "ready", "invoices": results,
            "payments": [p.model_dump(mode="json") for p in case.payments], "matches": matches,
            "blockers": blockers, "warnings": warnings, "schedule": schedule, "convention": CONVENTION,
            "totals": {"invoiced": money(total_invoiced), "bank_received": money(bank), "allocated_bank": money(allocated_bank),
                       "tds_recognized": money(tds), "principal": money(principal_total), "interest": money(interest_total),
                       "total": money(principal_total + interest_total), "unallocated": money(bank-allocated_bank), "reconciliation_difference": money(identity)},
            "rate_status": "synthetic_confirmed" if review.get("rate_confirmed") and any(r.synthetic for r in case.rates) else "synthetic_unconfirmed" if any(r.synthetic for r in case.rates) else "reviewed" if review.get("rate_confirmed") else "unconfirmed",
            "rules": {"version": "2026-10-10-local-mvp", "source": RULES_SOURCE,
                      "due_date": "Acceptance + written terms capped at45 days; absent writing +15 days. Interest starts next day.",
                      "registration": "Registration after invoice/contract requires legal review; this preparation workflow blocks automatic approval, not a definitive rejection."}}
