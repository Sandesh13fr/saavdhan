"""Deterministic offer rules. Python decides; extractor output is only evidence.

Each rule returns hit / clear / unknown; unknown means the offer lacked the facts to decide.
"""
from __future__ import annotations

import re

from .models import FieldValue, Offer, RuleHit

MEA = "https://www.mea.gov.in/overseas-employment.htm"
EMIGRATE = "https://emigrate.gov.in"

# Fee cap reported in MEA advisory (Rs 30,000 + 18% GST). Verify current figure before release.
FEE_CAP_INR = 30000 * 1.18

RULES = [
    {"id": "R1_TOURIST_VISA", "severity": "critical", "source": MEA},
    {"id": "R2_RA_NOT_LISTED", "severity": "high", "source": EMIGRATE},
    {"id": "R3_NO_RC_NUMBER", "severity": "high", "source": EMIGRATE},
    {"id": "R4_FEE_OVER_CAP", "severity": "high", "source": MEA},
    {"id": "R5_NO_TRIPARTITE_CONTRACT", "severity": "high", "source": MEA},
    {"id": "R6_HIGH_RISK_CORRIDOR", "severity": "critical", "source": MEA},
    {"id": "R7_INFORMAL_CHANNEL_ONLY", "severity": "medium", "source": MEA},
    {"id": "R8_NO_RECEIPT", "severity": "medium", "source": MEA},
    {"id": "R9_PBBY_MISSING", "severity": "info", "source": MEA},
    {"id": "H1_SALARY_ANOMALY", "severity": "medium", "source": "heuristic", "heuristic": True},
    {"id": "H2_PASSPORT_HANDOVER", "severity": "high", "source": "heuristic", "heuristic": True},
    {"id": "H3_PRESSURE", "severity": "low", "source": "heuristic", "heuristic": True},
]


# Configurable lists (lower-case). Matched as whole words, case-insensitive.
HIGH_RISK_COUNTRIES = {"thailand", "myanmar", "cambodia", "laos"}
HIGH_RISK_ROLES = ["data entry", "customer support", "customer service", "it", "digital marketing",
                   "online marketing", "chat support", "call centre", "call center", "typing"]
INFORMAL_CHANNELS = {"whatsapp", "telegram", "instagram", "facebook"}

# APPROXIMATE FX to INR, for the H1 heuristic only. Not a rate source.
APPROX_FX_TO_INR = {"INR": 1, "AED": 22.7, "SAR": 22.2, "QAR": 22.9, "OMR": 216, "KWD": 270, "USD": 83,
                    "THB": 2.3, "MYR": 18, "SGD": 62, "EUR": 90, "JPY": 0.55}
# Rough monthly INR reference by role keyword (heuristic, tune with data).
SALARY_REFERENCE_INR = {"data entry": 40000, "customer support": 50000, "default": 150000}
SALARY_ANOMALY_FACTOR = 2

_META = {r["id"]: r for r in RULES}


def _val(f: FieldValue) -> str | None:
    v = (f.value or "").strip()
    return v or None


def _vals(fs: list[FieldValue]) -> list[str]:
    return [v.lower() for f in fs if (v := _val(f))]


def _num(f: FieldValue) -> float | None:
    v = _val(f)
    if v is None:
        return None
    try:
        return float(v.replace(",", ""))
    except ValueError:
        return None


def _word_in(needle: str, text: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", text, re.I) is not None


def _hit(rid: str, status: str, evidence: list[FieldValue], severity: str | None = None) -> RuleHit:
    m = _META[rid]
    return RuleHit(rule_id=rid, severity=severity or m["severity"], status=status,
                   evidence=[e for e in evidence if _val(e)], explanation_key=f"rule.{rid}.{status}",
                   rule_source_url=m["source"], heuristic=m.get("heuristic", False))


def _salary_inr(o: Offer) -> float | None:
    amt, cur = _num(o.salary_amount), (_val(o.salary_currency) or "").upper()
    return amt * APPROX_FX_TO_INR[cur] if amt is not None and cur in APPROX_FX_TO_INR else None


def run_rules(offer: Offer, ra_match: dict | None = None) -> list[RuleHit]:
    """`ra_match` comes from ra_lookup.lookup(); None means the list was not consulted."""
    o, out = offer, []
    add = lambda *a, **k: out.append(_hit(*a, **k))  # noqa: E731

    # R1
    visa = (_val(o.visa_type) or "").lower()
    add("R1_TOURIST_VISA", "hit" if visa in ("tourist", "visit") else "clear" if visa in ("employment", "work") else "unknown", [o.visa_type])

    # R2
    ra = ra_match.get("status") if ra_match else None
    has_agent = _val(o.agent_name) or _val(o.agent_rc_number)
    ev = [o.agent_name, o.agent_rc_number]
    if not has_agent or ra not in ("listed", "not_listed", "unregistered_list"):
        add("R2_RA_NOT_LISTED", "unknown", ev)
    elif ra == "listed":
        add("R2_RA_NOT_LISTED", "clear", ev)
    else:
        add("R2_RA_NOT_LISTED", "hit", ev, "critical" if ra == "unregistered_list" else None)

    # R3
    add("R3_NO_RC_NUMBER", "clear" if _val(o.agent_rc_number) else "hit", [o.agent_rc_number])

    # R4
    fee = _num(o.fees_demanded_inr)
    add("R4_FEE_OVER_CAP", "unknown" if fee is None else "hit" if fee > FEE_CAP_INR else "clear", [o.fees_demanded_inr])

    # R5
    sigs = set(_vals(o.contract_signatories))
    if not (_val(o.role_title) or _val(o.employer_name) or _val(o.destination_country)):
        s5 = "unknown"
    elif (_val(o.contract_mentioned) or "").lower() == "yes" and {"employer", "agent", "worker"} <= sigs:
        s5 = "clear"
    else:
        s5 = "hit"
    add("R5_NO_TRIPARTITE_CONTRACT", s5, [o.contract_mentioned, *o.contract_signatories])

    # R6
    places = [o.destination_country, *o.transit_countries]
    names = [v.lower() for v in (_val(p) or "" for p in places) if v]
    role = (_val(o.role_title) or "").lower()
    if not names:
        s6 = "unknown"
    elif not set(names) & HIGH_RISK_COUNTRIES:
        s6 = "clear"
    elif not role:
        s6 = "unknown"
    else:
        s6 = "hit" if any(_word_in(r, role) for r in HIGH_RISK_ROLES) else "clear"
    add("R6_HIGH_RISK_CORRIDOR", s6, [*places, o.role_title])

    # R7
    ch = set(_vals(o.agent_channels))
    s7 = "unknown" if not ch else "clear" if "office_address" in ch else "hit" if ch <= INFORMAL_CHANNELS else "clear"
    add("R7_INFORMAL_CHANNEL_ONLY", s7, o.agent_channels)

    # R8
    receipt = (_val(o.receipt_promised) or "").lower()
    add("R8_NO_RECEIPT", "hit" if fee and fee > 0 and receipt != "yes" else "clear", [o.fees_demanded_inr, o.receipt_promised])

    # R9
    add("R9_PBBY_MISSING", "clear" if (_val(o.pbby_insurance_mentioned) or "").lower() == "yes" else "hit", [o.pbby_insurance_mentioned])

    # H1
    inr = _salary_inr(o)
    ref = next((v for k, v in SALARY_REFERENCE_INR.items() if k != "default" and role and _word_in(k, role)),
               SALARY_REFERENCE_INR["default"])
    add("H1_SALARY_ANOMALY", "unknown" if inr is None else "hit" if inr > SALARY_ANOMALY_FACTOR * ref else "clear",
        [o.salary_amount, o.salary_currency, o.role_title])

    # H2
    ph = (_val(o.passport_handover_requested) or "").lower()
    add("H2_PASSPORT_HANDOVER", "hit" if ph == "yes" else "clear" if ph == "no" else "unknown", [o.passport_handover_requested])

    # H3
    add("H3_PRESSURE", "hit" if _vals(o.urgency_language) else "clear", o.urgency_language)
    return out
