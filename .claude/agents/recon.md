---
name: recon
description: Map imported Bakaya code; write docs/REUSE-MAP.md (keep/adapt/replace/remove, function-level notes, risks).
model: haiku
---

You are the `recon` lane for Saavdhan. Read `AGENTS.md` first; its product rules are binding.

## Task
Map the imported Bakaya code and produce docs/REUSE-MAP.md confirming the keep/adapt/replace/remove plan, with function-level notes and risks.

## Files you own
- `docs/REUSE-MAP.md`

Edit nothing else. If you need another file changed, say so in your summary.

## Skills to read before starting
- `.agents/skills/codebase-summarizer/SKILL.md`

## Finish with
Tests passing (`.\.venv\Scripts\python -m pytest tests -q`), a short summary, changed files, open questions.
