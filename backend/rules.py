"""Deterministic offer rules. Python decides; extractor output is only evidence.

Phase 1 stub: every rule reports `unknown`. The rules-engine lane implements the checks.
"""
from __future__ import annotations

from .models import Offer, RuleHit

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


def run_rules(offer: Offer, ra_match: dict | None = None) -> list[RuleHit]:
    """`ra_match` comes from ra_lookup.lookup(); None means the list was not consulted."""
    return [RuleHit(rule_id=r["id"], severity=r["severity"], status="unknown", evidence=[],
                    explanation_key=f"rule.{r['id']}.unknown", rule_source_url=r["source"],
                    heuristic=r.get("heuristic", False)) for r in RULES]
