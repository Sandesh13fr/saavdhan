"""Bounded analysis pipeline: sources -> extract -> validate -> rules -> verdict.

No autonomous tool choice and no external calls beyond the opt-in extractor.
The deterministic extractor always runs. When the LLM also runs, rules are evaluated on
both offers and each rule keeps the more severe status, so model output can add a red flag
but never remove one.
"""
from __future__ import annotations

from . import extract_fallback
from .models import RuleHit, SourceRef
from .providers import extract_offer
from .rules import run_rules
from .verdict import decide

RA_LIST_DATE = "not loaded"  # set from ra_lookup once the MEA list is parsed

_RANK = {"hit": 2, "unknown": 1, "clear": 0}
_SEV = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def _stricter(a: RuleHit, b: RuleHit) -> RuleHit:
    if (_RANK[b.status], _SEV[b.severity]) > (_RANK[a.status], _SEV[a.severity]):
        return b
    return a


async def analyze(state: dict) -> dict:
    sources = [SourceRef.model_validate(s) for s in state["sources"]]
    errors = []
    fallback = extract_fallback.extract(sources)
    hits = run_rules(fallback, None)
    offer, method = fallback, "fallback"
    try:
        llm = await extract_offer(sources)
    except ValueError as exc:
        llm = None
        errors.append(str(exc))
    if llm is not None:
        offer, method = llm, "llm"
        hits = [_stricter(a, b) for a, b in zip(hits, run_rules(llm, None))]
    verdict = decide(hits, RA_LIST_DATE)
    if state.get("ingest_truncated"):
        errors.append("Part of the document was not checked.")
        if verdict.level == "NO_RED_FLAGS_FOUND":
            verdict.level = "VERIFY_FIRST"
            verdict.next_steps_key = "next.VERIFY_FIRST"
    return {"offer": offer.model_dump(mode="json"), "fallback_offer": fallback.model_dump(mode="json") if llm else None,
            "verdict": verdict.model_dump(mode="json"), "extraction_method": method, "errors": errors}
