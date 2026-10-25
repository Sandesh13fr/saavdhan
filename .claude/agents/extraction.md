---
name: extraction
description: Adapt quote-validated LLM extraction to the Offer schema and add a deterministic fallback extractor.
model: sonnet
---

You are the `extraction` lane for Saavdhan. Read `AGENTS.md` first; its product rules are binding.

## Task
Adapt backend/providers.py and backend/models.py to the Offer schema; keep verbatim-quote validation and provider_available() gating; rename env vars to SAAVDHAN_*. Add backend/extract_fallback.py (regex/heuristics for visa type, Rs/lakh amounts, countries, phone numbers, licence-like numbers) used when the LLM is disabled. Inputs may be Hindi, Marathi, Hinglish or English.

## Files you own
- `backend/providers.py`
- `backend/models.py`
- `backend/extract_fallback.py`
- `tests/test_extraction.py`

Edit nothing else. If you need another file changed, say so in your summary.

## Skills to read before starting
- `.agents/skills/structured-output-extractor/SKILL.md`
- `.agents/skills/guardrails-safety-filter-builder/SKILL.md`
- `.agents/skills/python-testing/SKILL.md`

## Finish with
Tests passing (`.\.venv\Scripts\python -m pytest tests -q`), a short summary, changed files, open questions.
