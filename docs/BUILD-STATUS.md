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

## Still Bakaya code (replaced in phase 1–2)

- `backend/engine.py` interest/TDS engine, `backend/evaluation.py`, invoice models,
  invoice routes and UI. Env vars still `BAKAYA_*`.

## Works / simulated / known limits

Filled as phases land.
