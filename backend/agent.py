"""Bounded analysis pipeline: sources -> extract -> validate -> rules -> verdict.

No autonomous tool choice and no external calls beyond the opt-in extractor.
"""
from __future__ import annotations

from . import extract_fallback
from .models import SourceRef
from .providers import extract_offer
from .rules import run_rules
from .verdict import decide

RA_LIST_DATE = "not loaded"  # set from ra_lookup once the MEA list is parsed


async def analyze(state: dict) -> dict:
    sources = [SourceRef.model_validate(s) for s in state["sources"]]
    offer, errors = None, []
    try:
        offer = await extract_offer(sources)
    except ValueError as exc:
        errors.append(str(exc))
    method = "llm" if offer else "fallback"
    if offer is None:
        offer = extract_fallback.extract(sources)
    verdict = decide(run_rules(offer, None), RA_LIST_DATE)
    return {"offer": offer.model_dump(mode="json"), "verdict": verdict.model_dump(mode="json"),
            "extraction_method": method, "errors": errors}
