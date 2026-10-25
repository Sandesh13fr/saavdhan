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

## Phase 3 — evaluation and review (25 Oct)

- Eval harness `eval/run_eval.py` -> `eval/REPORT.md`. Fallback extractor on the 40 synthetic offers:
  baseline 27/40 verdicts; after fixes 40/40, macro rule F1 0.948, field accuracy 0.880, median 2.3 ms.
  The extractor was tuned on this same set, so scores are optimistic (stated in the report).
- Security review: 1 critical, 4 high, 5 medium. Fixed: LLM can only add red flags (rules run on
  both extractors, stricter status wins) + quote/value validation; injection-skip removed; no best
  verdict without a real recruiter-list date; pasted-text and line caps; anonymous retention (24h),
  eviction and per-IP rate limit; demo clock limited to demo cases in production; HMAC phone hashes
  with required production salt. Reviewer re-verified: SIGN-OFF, no critical findings. Its two
  follow-ups also fixed: anonymous upload budget recomputed from disk (purge frees space);
  uvicorn --proxy-headers so rate limit and login throttle see real client IPs.
- Demo officer: `scripts/seed_demo_officer.py` (password only in gitignored `.env`).
- Browser-checked: Bangkok STOP, check-in plan, missed check-in, family alert, pattern map (36
  districts, one hash across 5 districts).
- Copy reworded after review (no "MEA high-risk list" claim; fee cap stated; list date in R2 copy).

## Phase 4 — deployed (26 Oct)

- Live demo: **https://saavdhan.onrender.com** (Render free Docker web service, Singapore, auto-deploy
  from `main`). Verified live: health ok with OCR (eng+hin+mar); Bangkok demo STOP (R1, R3, R4, R5, R6,
  R7, R8, R9, H1, H3 hit); near-miss VERIFY_FIRST; packet ZIP 200; pattern map 401 anonymous and 200
  for the demo officer; cross-origin POST 403. Recruiter list not loaded, so R2 stays unknown.
- Free plan: sleeps when idle (~1 min cold start); disk resets on restart (demo officer re-created).
- Docs lane: README, ARCHITECTURE, RULES, PRIVACY, DEMO-SCRIPT, DECK-OUTLINE, AI_USAGE, DEPLOY.

- Codex lanes (26 Oct): 22 synthetic-data screenshots (`docs/screenshots/`, capture script in
  `tools/screenshots/`); second code review found 11 issues (4 high: unbounded multipart body, blocking
  OCR in async route, lost updates without revision checks, office-city hiding a high-risk route) —
  all fixed with 40 regression tests. 209 tests pass; eval unchanged (40/40 on the tuning set).
- Rule titles for R2 and H2 made neutral ("Agent on MEA's active list?", "Who keeps your passport?").

- Frontend rebuilt (26 Oct) to match the 14 mock screens and identity board (paper/ink/alert red,
  Archivo + Noto Sans Devanagari + IBM Plex Mono, S-mark logo, board verdict language). Flow: home →
  submit (stepper, tabs) → review extracted facts → result → evidence → check-in setup → check-in →
  family alert → help; institution login → tile-less pattern map → pattern detail. Map screens lazy-loaded.
  Deliberate differences from the mocks listed in `design/REVIEW.md`. 32 synthetic screenshots re-captured.
- OpenFreeMap basemap not merged (mock shows a tile-less map); branch `lane/openfreemap` kept.
- OpenRouter configured as the optional LLM gateway (off by default and in production).

## Known gaps

- R2 shows "dated not loaded" until the MEA RA list is parsed.
- Anonymous visitors share one tenant with a 10-case cap in production: replace with retention
  + per-client limits before public deploy.
- RA list not loaded (`ra_list_date: "not loaded"`) until codex-ra-list lane parses MEA PDFs.
- README, docs/PRODUCTION.md, backend/README.md still describe Bakaya (docs lane).

## Works / simulated / known limits

Filled as phases land.

- Open from review (deploy lane): narrow FORWARDED_ALLOW_IPS to the proxy; per-account
  login lockout per account; docs/PRODUCTION.md still Bakaya text; LLM sends offer text to a third party
  (TokenRouter) — disclose in privacy copy; up to 10 files x 500 lines per case.
- TokenRouter key returns 401 (quota exhausted); LLM path untested live. `eval/run_eval.py --llm` once fixed.
- Fee cap Rs 30,000 + 18% GST is as reported; verify against the current official figure.
