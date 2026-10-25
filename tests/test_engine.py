from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.engine import add_month, analyze, due_dates, interest_schedule, money
from backend.evaluation import evaluate, reference_interest
from backend.fixtures import demo_case, sourced
from backend.models import Invoice, Payment, RatePeriod, Allocation, PurchaseOrder


def rates(start=date(2026,1,1),end=date(2027,1,1),rate="6.5"):
    return [RatePeriod(start=start,end=end,bank_rate=Decimal(rate),source="fixture",source_refs=["RATES"])]


def invoice(**changes):
    defaults=dict(id="I1",number="I1",date=date(2026,1,1),delivery_date=date(2026,1,1),amount=Decimal(100000))
    return Invoice(**(defaults|changes))


@pytest.mark.parametrize("term,due",[(None,"2026-01-16"),(0,"2026-01-01"),(30,"2026-01-31"),(60,"2026-02-15")])
def test_due_dates_and_next_day_interest(term,due):
    actual,start=due_dates(invoice(written_term_days=term))
    assert str(actual)==due
    assert (start-actual).days==1


def test_timely_objection_moves_acceptance():
    inv=invoice(objection_date=date(2026,1,16),objection_resolved_date=date(2026,2,1),written_term_days=30)
    assert due_dates(inv)==(date(2026,3,3),date(2026,3,4))


def test_late_objection_does_not_move_acceptance():
    inv=invoice(objection_date=date(2026,1,17),objection_resolved_date=date(2026,2,1))
    assert due_dates(inv)[0]==date(2026,1,16)


def test_unresolved_objection_fails_closed():
    with pytest.raises(ValueError,match="unresolved"):
        due_dates(invoice(objection_date=date(2026,1,10)))


def test_missing_acceptance_never_uses_invoice_date():
    with pytest.raises(ValueError,match="Acceptance"):
        due_dates(invoice(delivery_date=None))


def test_closed_form_two_month_compounding():
    # Jan1–Feb1:31days; Feb1–Mar1:28days. Independently hand-expanded.
    result,principal,_=interest_schedule(Decimal(100000),date(2026,1,1),date(2026,2,28),[],rates())
    first=Decimal(100000)*Decimal(".195")*31/365
    expected=first+(Decimal(100000)+first)*Decimal(".195")*28/365
    assert abs(result-expected)<Decimal(".00000000000000000001")
    assert principal==100000


def test_partial_payment_split_and_monthly_rest():
    result,principal,_=interest_schedule(Decimal(100000),date(2026,1,1),date(2026,2,28),[(date(2026,1,16),Decimal(30000))],rates())
    first=(Decimal(100000)*15+Decimal(70000)*16)*Decimal(".195")/365
    expected=first+(Decimal(70000)+first)*Decimal(".195")*28/365
    assert abs(result-expected)<Decimal(".00000000000000000001")
    assert principal==70000


def test_dated_rate_change_inside_rest_does_not_reset_compounding():
    periods=rates(end=date(2026,1,16),rate="6.5")+rates(start=date(2026,1,16),rate="5.5")
    result,_,rows=interest_schedule(Decimal(100000),date(2026,1,1),date(2026,1,31),[],periods)
    expected=Decimal(100000)*(Decimal(".195")*15+Decimal(".165")*16)/365
    assert abs(result-expected)<Decimal(".00000000000000000001")
    assert [r["days"] for r in rows]==[15,16]


@pytest.mark.parametrize("periods",[rates(end=date(2026,1,10)),rates()+rates()])
def test_rate_gaps_or_overlap_block(periods):
    with pytest.raises(ValueError,match="unique"):
        interest_schedule(Decimal(100),date(2026,1,1),date(2026,1,31),[],periods)


def test_payment_on_interest_start_has_no_principal_interest():
    interest,principal,_=interest_schedule(Decimal(100000),date(2026,1,1),date(2026,1,31),[(date(2026,1,1),Decimal(100000))],rates())
    assert interest==0 and principal==0


def test_unpaid_interest_remains_after_principal_paid():
    interest,principal,_=interest_schedule(Decimal(100000),date(2026,1,1),date(2026,2,28),[(date(2026,2,1),Decimal(100000))],rates())
    first=Decimal(100000)*Decimal(".195")*31/365
    expected=first+first*Decimal(".195")*28/365
    assert abs(interest-expected)<Decimal(".00000000000000000001") and principal==0


def test_month_anchor_recovers_after_february():
    assert add_month(date(2024,1,31),1)==date(2024,2,29)
    assert add_month(date(2024,1,31),2)==date(2024,3,31)


def test_all_evaluation_cases_agree_with_independent_daily_oracle():
    report=evaluate()
    assert report["fixed"]["matching_accuracy"]==100
    assert Decimal(report["fixed"]["max_interest_error"])<=Decimal(".01")
    assert report["fixed"]["ambiguities_flagged"]==2
    assert report["baseline"]["false_short_payments"]==4


def test_two_percent_shortfall_without_proof_is_never_tds():
    case=demo_case()
    case.payments[0].tds_amount=Decimal(0)
    case.payments[0].tds_evidence_source=None
    result=analyze(case)
    assert result["totals"]["tds_recognized"]=="0.00"
    assert result["invoices"][0]["outstanding"]=="2000.00"


def test_missing_tds_proof_blocks_credit():
    case=demo_case()
    case.payments[0].tds_evidence_source=None
    result=analyze(case)
    assert any(b["code"]=="tds_evidence" for b in result["blockers"])
    assert not any(m["payment_id"]=="PAY-001" for m in result["matches"])


def test_tampered_tds_amount_cannot_borrow_unrelated_certificate():
    case=demo_case()
    case.payments[0].tds_amount=Decimal(1000)
    result=analyze(case)
    assert any(b["code"]=="tds_document_mismatch" for b in result["blockers"])


def test_duplicate_amounts_refuse_guess_and_conserve_ledger():
    result=analyze(demo_case())
    assert any(b["code"]=="ambiguous_payment" for b in result["blockers"])
    total=result["totals"]
    assert Decimal(total["invoiced"])==Decimal(total["principal"])+Decimal(total["allocated_bank"])+Decimal(total["tds_recognized"])
    assert Decimal(total["bank_received"])==Decimal(total["allocated_bank"])+Decimal(total["unallocated"])


def test_amount_only_candidate_requires_confirmation():
    case=demo_case()
    case.payments=case.payments[:1]
    case.payments[0].amount=Decimal(100000)
    case.payments[0].tds_amount=Decimal(0)
    case.payments[0].invoice_ids=[]
    case.payments[0].reference="Bank transfer"
    result=analyze(case)
    assert any(b["code"]=="payment_confirmation" for b in result["blockers"])


def test_overpayment_and_bank_mismatch_block_approval():
    case=demo_case()
    case.payments[1].amount=Decimal(300000)
    result=analyze(case)
    assert {"overpayment","bank_mismatch"}<= {b["code"] for b in result["blockers"]}


def test_field_provenance_is_required():
    case=demo_case()
    case.invoices[0].field_sources.pop("delivery_date")
    result=analyze(case)
    assert any(b["code"]=="missing_field_provenance" for b in result["blockers"])


def test_registration_after_contract_requires_review_not_definitive_rejection():
    case=demo_case()
    case.supplier.udyam_date=date(2026,4,25)
    result=analyze(case)
    assert any(b["code"]=="registration_review" for b in result["blockers"])


def test_conflicting_po_terms_and_date_are_blocked():
    case=demo_case()
    case.purchase_orders=[sourced(PurchaseOrder,"DOC-001",id="PO1",number="PO1",invoice_id="INV-001",date=date(2026,4,21),written_term_days=45)]
    result=analyze(case)
    assert any(b["code"]=="conflicting_linked_evidence" for b in result["blockers"])


def test_not_yet_due_invoice_cannot_be_approved_as_delayed_payment():
    case=demo_case()
    case.as_of=date(2026,6,2)
    result=analyze(case,{"rate_confirmed":True,"buyer_confirmed":True})
    assert any(b["code"]=="not_overdue" for b in result["blockers"])


@pytest.mark.parametrize("amount",["NaN","Infinity","-1","0","1.001"])
def test_invalid_money_rejected(amount):
    with pytest.raises(ValidationError):
        invoice(amount=Decimal(amount))
