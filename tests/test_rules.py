"""Rule tests: synthetic offers only."""
import pytest

from backend.models import FieldValue, Offer
from backend.rules import FEE_CAP_INR, run_rules
from backend.verdict import decide


def fv(v):
    return FieldValue(value=v, quote=f"q:{v}")


def fvs(*vs):
    return [fv(v) for v in vs]


def offer(**kw):
    return Offer(**{k: (v if isinstance(v, list) else fv(v)) for k, v in kw.items()})


def get(o, rid, ra=None):
    return next(h for h in run_rules(o, ra) if h.rule_id == rid)


LISTED = {"status": "listed", "list_date": "2025-01-01", "evidence": "row"}

# (rule, offer kwargs, expected status, ra_match)
CASES = [
    ("R1_TOURIST_VISA", dict(visa_type="tourist"), "hit", None),
    ("R1_TOURIST_VISA", dict(visa_type="visit"), "hit", None),
    ("R1_TOURIST_VISA", dict(visa_type="employment"), "clear", None),
    ("R1_TOURIST_VISA", dict(visa_type="unknown"), "unknown", None),
    ("R1_TOURIST_VISA", {}, "unknown", None),
    ("R2_RA_NOT_LISTED", dict(agent_name="X Overseas"), "hit", {"status": "not_listed"}),
    ("R2_RA_NOT_LISTED", dict(agent_rc_number="B-1"), "clear", LISTED),
    ("R2_RA_NOT_LISTED", dict(agent_name="X"), "unknown", None),
    ("R2_RA_NOT_LISTED", dict(agent_name="X"), "unknown", {"status": "unknown"}),
    ("R2_RA_NOT_LISTED", {}, "unknown", LISTED),
    ("R3_NO_RC_NUMBER", {}, "hit", None),
    ("R3_NO_RC_NUMBER", dict(agent_rc_number="B-1"), "clear", None),
    ("R4_FEE_OVER_CAP", dict(fees_demanded_inr="250000"), "hit", None),
    ("R4_FEE_OVER_CAP", dict(fees_demanded_inr=str(int(FEE_CAP_INR))), "clear", None),
    ("R4_FEE_OVER_CAP", {}, "unknown", None),
    ("R4_FEE_OVER_CAP", dict(fees_demanded_inr="lakh"), "unknown", None),
    ("R5_NO_TRIPARTITE_CONTRACT", dict(role_title="cook"), "hit", None),
    ("R5_NO_TRIPARTITE_CONTRACT", dict(role_title="cook", contract_mentioned="yes",
                                       contract_signatories=fvs("employer", "worker")), "hit", None),
    ("R5_NO_TRIPARTITE_CONTRACT", dict(role_title="cook", contract_mentioned="yes",
                                       contract_signatories=fvs("employer", "agent", "worker")), "clear", None),
    ("R5_NO_TRIPARTITE_CONTRACT", {}, "unknown", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="Thailand", role_title="Data Entry operator"), "hit", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="UAE", transit_countries=fvs("Myanmar"),
                                   role_title="customer support"), "hit", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="Thailand", role_title="kitchen helper"), "clear", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="Thailand", role_title="IT support"), "hit", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="Saudi Arabia", role_title="data entry"), "clear", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(destination_country="Thailand"), "unknown", None),
    ("R6_HIGH_RISK_CORRIDOR", dict(role_title="data entry"), "unknown", None),
    ("R7_INFORMAL_CHANNEL_ONLY", dict(agent_channels=fvs("whatsapp", "telegram")), "hit", None),
    ("R7_INFORMAL_CHANNEL_ONLY", dict(agent_channels=fvs("whatsapp", "office_address")), "clear", None),
    ("R7_INFORMAL_CHANNEL_ONLY", {}, "unknown", None),
    ("R8_NO_RECEIPT", dict(fees_demanded_inr="20000"), "hit", None),
    ("R8_NO_RECEIPT", dict(fees_demanded_inr="20000", receipt_promised="no"), "hit", None),
    ("R8_NO_RECEIPT", dict(fees_demanded_inr="20000", receipt_promised="yes"), "clear", None),
    ("R8_NO_RECEIPT", {}, "clear", None),
    ("R9_PBBY_MISSING", {}, "hit", None),
    ("R9_PBBY_MISSING", dict(pbby_insurance_mentioned="yes"), "clear", None),
    ("H1_SALARY_ANOMALY", dict(role_title="data entry", salary_amount="150000", salary_currency="INR"), "hit", None),
    ("H1_SALARY_ANOMALY", dict(role_title="data entry", salary_amount="50000", salary_currency="INR"), "clear", None),
    ("H1_SALARY_ANOMALY", dict(role_title="cook", salary_amount="3000", salary_currency="AED"), "clear", None),
    ("H1_SALARY_ANOMALY", dict(salary_amount="3000"), "unknown", None),
    ("H1_SALARY_ANOMALY", dict(salary_amount="3000", salary_currency="XYZ"), "unknown", None),
    ("H2_PASSPORT_HANDOVER", dict(passport_handover_requested="yes"), "hit", None),
    ("H2_PASSPORT_HANDOVER", dict(passport_handover_requested="no"), "clear", None),
    ("H2_PASSPORT_HANDOVER", {}, "unknown", None),
    ("H3_PRESSURE", dict(urgency_language=fvs("pay today or lose the seat")), "hit", None),
    ("H3_PRESSURE", {}, "clear", None),
]


@pytest.mark.parametrize("rid,kw,expected,ra", CASES)
def test_rule(rid, kw, expected, ra):
    assert get(offer(**kw), rid, ra).status == expected


def test_r2_unregistered_list_is_critical():
    h = get(offer(agent_name="X"), "R2_RA_NOT_LISTED", {"status": "unregistered_list"})
    assert (h.status, h.severity) == ("hit", "critical")
    assert get(offer(agent_name="X"), "R2_RA_NOT_LISTED", {"status": "not_listed"}).severity == "high"


def test_shape_and_metadata():
    hits = run_rules(Offer(), None)
    assert len(hits) == 12
    for h in hits:
        assert h.explanation_key == f"rule.{h.rule_id}.{h.status}"
        assert h.rule_source_url
    assert {h.rule_id for h in hits if h.heuristic} == {"H1_SALARY_ANOMALY", "H2_PASSPORT_HANDOVER", "H3_PRESSURE"}


def test_evidence_carries_used_fields():
    assert [e.value for e in get(offer(visa_type="tourist"), "R1_TOURIST_VISA").evidence] == ["tourist"]


def test_verdict_bangkok_stop():
    o = offer(destination_country="Thailand", role_title="data entry", visa_type="tourist")
    assert decide(run_rules(o, None), "2025-01-01").level == "STOP"


def test_verdict_compliant_no_red_flags():
    o = offer(agent_name="A Overseas", agent_rc_number="B-1", visa_type="employment", role_title="electrician",
              employer_name="Gulf Co", destination_country="Saudi Arabia", fees_demanded_inr="20000",
              receipt_promised="yes", contract_mentioned="yes", pbby_insurance_mentioned="yes",
              passport_handover_requested="no", salary_amount="2000", salary_currency="SAR",
              contract_signatories=fvs("employer", "agent", "worker"),
              agent_channels=fvs("phone", "office_address"))
    assert decide(run_rules(o, LISTED), "2025-01-01").level == "NO_RED_FLAGS_FOUND"


def test_verdict_empty_offer_not_clear():
    assert decide(run_rules(Offer(), None), "2025-01-01").level != "NO_RED_FLAGS_FOUND"


def test_verdict_unregistered_list_stop():
    v = decide(run_rules(offer(agent_name="X"), {"status": "unregistered_list"}), "2025-01-01")
    assert v.level == "STOP"
