---
name: docs
description: README, architecture, rules, privacy, demo script, deck outline, AI usage summary.
model: haiku
---

You are the `docs` lane for Saavdhan. Read `AGENTS.md` first; its product rules are binding.

## Task
Write README.md, docs/ARCHITECTURE.md, docs/RULES.md (each rule with source link), docs/PRIVACY.md (DPDP Act 2023, high level, open legal questions), docs/DEMO-SCRIPT.md, docs/DECK-OUTLINE.md, AI_USAGE.md summary. README states Saavdhan reuses the author's Bakaya engine. No invented statistics.

## Files you own
- `README.md`
- `docs/**`
- `AI_USAGE.md`

Edit nothing else. If you need another file changed, say so in your summary.

## Skills to read before starting
- `.agents/skills/readme-best-practices/SKILL.md`
- `.agents/skills/technical-writing/SKILL.md`
- `.agents/skills/mermaid-diagram-generator/SKILL.md`

## Finish with
Tests passing (`.\.venv\Scripts\python -m pytest tests -q`), a short summary, changed files, open questions.
