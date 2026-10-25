"""Verdict from rule hits. Unknown is never treated as clear. There is no all-clear level."""
from __future__ import annotations

import re

from .models import RuleHit, Verdict

KEY_UNKNOWN_RULES = {"R1_TOURIST_VISA", "R2_RA_NOT_LISTED", "R5_NO_TRIPARTITE_CONTRACT"}


def decide(hits: list[RuleHit], ra_list_date: str) -> Verdict:
    hit = [h for h in hits if h.status == "hit"]
    unknown_key = sum(1 for h in hits if h.status == "unknown" and h.rule_id in KEY_UNKNOWN_RULES)
    if any(h.severity == "critical" for h in hit):
        level = "STOP"
    elif any(h.severity == "high" for h in hit) or unknown_key >= 3:
        level = "VERIFY_FIRST"
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ra_list_date or ""):
        level = "VERIFY_FIRST"  # recruiter list not consulted: never show the best verdict
    else:
        level = "NO_RED_FLAGS_FOUND"
    return Verdict(level=level, rule_hits=hits, ra_list_date=ra_list_date, next_steps_key=f"next.{level}")
