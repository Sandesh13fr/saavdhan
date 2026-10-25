---
name: cleanup
description: Remove Bakaya-only code (interest/TDS engine, evaluation, invoice tests) while keeping the app booting.
model: haiku
---

You are the `cleanup` lane for Saavdhan. Read `AGENTS.md` first; its product rules are binding.

## Task
Remove Bakaya-only integrations and dead code per docs/REUSE-MAP.md; keep the app booting and tests green (delete tests that cover removed features).

## Files you own
- `backend/enrichment.py`
- `backend/telemetry.py`
- `backend/evaluation.py`
- `requirements*.txt`
- `tests/test_enrichment.py`

Edit nothing else. If you need another file changed, say so in your summary.

## Skills to read before starting
- `.agents/skills/python-testing/SKILL.md`

## Finish with
Tests passing (`.\.venv\Scripts\python -m pytest tests -q`), a short summary, changed files, open questions.
