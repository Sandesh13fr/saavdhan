# Skills used

Installed: 498 skills in `.agents/skills/` (none in `.claude/skills/`, `.codex/skills/` or `skills/`).
They are not committed (`.agents/` is gitignored). Only the skills below apply; the rest
(marketing, other frameworks, blockchain, game dev...) are unrelated to this build.

| Workstream | Skills | Why |
|---|---|---|
| Rules engine, safety net, cleanup | `python-testing`, `python` | pytest positive/negative test per rule |
| Extraction | `structured-output-extractor`, `guardrails-safety-filter-builder` | JSON-schema LLM output; prompt-injection handling for untrusted documents |
| Backend API | `fastapi-python` | New `/api/offers` routes |
| Frontend | `react`, `typescript`, `vite`, `responsive-design`, `accessibility-a11y`, `ui-ux-pro-max` | Mobile-first rebuild of `frontend/src` |
| i18n | `internationalization-i18n`, `i18n-frontend-implementer`, `localization-l10n` | en/hi/mr strings and toggle |
| Evaluation | `evaluation-harness`, `data-seeding-fixtures-builder` | Labelled synthetic set, per-rule precision/recall |
| Security review | `threat-model-generator`, `security-pr-checklist-skill`, `secrets-scanner`, `pii-redaction-logging-policy-builder`, `input-validation-sanitization-auditor` | Reviewer lane checklist |
| Privacy | `data-retention-archiving-planner` | Upload retention period |
| Docs | `readme-best-practices`, `technical-writing`, `mermaid-diagram-generator` | README, ARCHITECTURE diagrams |
| Deploy | `docker`, `dockerfile-optimizer`, `github-actions-pipeline-creator` | Single Docker service; CI incl. "safe"-wording grep |
| Deck | `slides`; built-in `anthropic-skills:pptx` | Content for the IIT Bombay template |

## Conflicts

- Any skill advice to label content "safe" / "verified safe" is overridden by the
  product rule: never output "safe" or an equivalent.
- `web-scraping` / `scrapy-web-scraping` / `beautifulsoup-parsing` are not used for
  social platforms (no WhatsApp/Telegram/social scraping). The MEA RA list is parsed
  from PDFs the user downloads.
