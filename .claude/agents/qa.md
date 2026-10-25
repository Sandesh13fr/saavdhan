---
name: qa
description: Synthetic evaluation set and harness; run full test suite; report failures.
model: haiku
---

You are the `qa` lane for Saavdhan. Read `AGENTS.md` first; its product rules are binding.

## Task
Build the synthetic evaluation harness (per-rule precision/recall, verdict confusion matrix, extraction field accuracy LLM vs fallback, median analysis time); run full test suite; report failures to the lead. Results are labelled synthetic.

## Files you own
- `eval/**`
- `tests/conftest.py`

Edit nothing else. If you need another file changed, say so in your summary.

## Skills to read before starting
- `.agents/skills/evaluation-harness/SKILL.md`
- `.agents/skills/python-testing/SKILL.md`

## Finish with
Tests passing (`.\.venv\Scripts\python -m pytest tests -q`), a short summary, changed files, open questions.
