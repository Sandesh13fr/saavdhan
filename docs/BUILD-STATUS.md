# Build status — 25 October 2026

Deadline: Stage 1 submission closes 27 Oct 2026. Feature freeze 27 Oct 12:00 IST.

## Phase 0 — workspace (done except blocking inputs)

- Bakaya imported without history (`3af9901`, source commit `ccb2d9c`), same author.
- Bakaya-only integrations removed (`2e75ab2`): Crustdata, neatlogs (telemetry is a no-op),
  `.entire/`, docs/market, docs/evidence, sample CSVs, Vercel config.
- 91 inherited tests pass; frontend builds.
- AGENTS.md, CLAUDE.md, AI_USAGE.md, LICENSE (MIT, pending confirmation), 10 subagent
  definitions in `.claude/agents/`, docs/SKILLS-USED.md.

Toolchain: Python 3.12.6, Node 24.11.1, codex-cli 0.162.1, gh 2.94.0 (logged in as
Sandesh13fr), Docker present, Tesseract 5.4.0 at `C:\Program Files\Tesseract-OCR`
(not on PATH; only `eng` language data — `hin`/`mar` missing).

## Phase 1 — stripped app boots (done)

- Invoice engine, evaluation, invoice models/routes/tests removed. Env vars now `SAAVDHAN_*`.
- `backend/models.py`: Offer (FieldValue with verbatim quote + server-attached source_ref),
  RuleHit, Verdict, SafetyPlan, Contact, CheckIn, Report.
- Routes: `POST /api/offers` (files and/or pasted text), `POST /api/offers/{id}/analyze`,
  `GET /api/offers/{id}`, `GET /api/offers/{id}/packet`, sources, `POST /api/demo/offers/{name}`,
  `GET /api/meta`, `GET /api/health`. Offer check is anonymous; only `/api/reports/*` needs login.
- Pipeline `backend/agent.py`: LLM extractor (opt-in, quote-validated) else fallback -> rules -> verdict.
  Model tool planner removed.
- Stubs for phase 2 lanes: `rules.py` (all rules `unknown`), `extract_fallback.py` (empty Offer),
  `verdict.py` logic is real. Stub analysis therefore always returns VERIFY_FIRST.
- Packet ZIP: offer copy, facts CSV, rule checks CSV, where-to-report (marked verify before use), PDF summary.
- CI: pytest, frontend build, grep that fails on "safe" / "सुरक्षित" in app code.
- 37 tests pass (real Tesseract OCR test included). OCR languages via `SAAVDHAN_OCR_LANGS`.
- Removed a hard-coded Bakaya demo login from `App.tsx` (it was already public in the Bakaya repo).

## Phase 2 — lanes merged (25 Oct)

- rules-engine: all 12 rules, 56 tests. extraction: multilingual fallback extractor (en/hi/mr/Hinglish,
  lakh/अडीच/Devanagari digits), LLM numeric guard. safety-net: plan, check-ins, simulated clock,
  idempotent simulated family alerts, itinerary in packet. i18n: 149 keys en/hi/mr (all flagged for
  native review, see frontend/src/i18n/REVIEW.md). frontend: 6 mobile-first screens.
  codex-eval-data: 40 synthetic labelled offers (eval/offers). codex-map: Leaflet map + geoBoundaries
  ADM2 (ODbL). Pattern-map backend: salted phone hashes, simhash templates, synthetic only.
- Browser check: Bangkok demo -> STOP with quotes and sources; near-miss demo -> VERIFY_FIRST (API test).
- LLM provider: TokenRouter (OpenAI-compatible, `https://api.tokenrouter.com/v1`), configured in `.env`.
  Live call blocked: key quota exhausted (HTTP 401). Fallback extractor runs meanwhile.

## Known gaps

- Pattern map needs a provisioned officer account (`python -m backend.auth create-user`); none exists yet.
- R2 shows "dated not loaded" until the MEA RA list is parsed.
- Anonymous visitors share one tenant with a 10-case cap in production: replace with retention
  + per-client limits before public deploy.
- RA list not loaded (`ra_list_date: "not loaded"`) until codex-ra-list lane parses MEA PDFs.
- README, docs/PRODUCTION.md, backend/README.md still describe Bakaya (docs lane).

## Works / simulated / known limits

Filled as phases land.
