"""Deterministic extractor used when the LLM is disabled.

Phase 1 stub: returns an empty Offer. The extraction lane adds regex/heuristics.
"""
from __future__ import annotations

from .models import Offer, SourceRef


def extract(sources: list[SourceRef]) -> Offer:
    return Offer(source_ids=[s.id for s in sources])
