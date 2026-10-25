# Neatlogs tracing — 11 October 2026

The project key is loaded from the ignored root `.env`; no key is included in source or frontend configuration. Initialization runs in FastAPI lifespan; shutdown drains the SDK. Python performs model calls, so there is no frontend model instrumentation.

## Complete lifecycle and paired evidence

[Controlled replay report](evidence/PAIRED-AGENT-REPLAY.md) · [Public sanitized trace trees](evidence/paired-agent-replay.json)

Actual revisions 233acc9 and 6985522 were replayed against the same synthetic case in isolated data directories. Each trace has 27 spans under one lifecycle root: inventory, ledger analysis, reconciliation, review pause at revision 1, scripted reviewer correction, approval pause at revision 2, explicit scripted approval, resumed packet generation and verified ZIP export. A separate labeled subtree tests an injected local failure and retry without repeating inventory.

- Before trace: `adede6146ac02b223da79587c5c46242`
- After trace: `3af784ca1b8dd9c7bcc69bb7d83fd1e7`

Both exact traces returned successful authenticated readback. Every span resolves to the lifecycle root. The comparison demonstrates redundant physical packet writes **1 → 0**, with identical principal/interest/claim totals, ten checkpoints and valid exports. It does not measure speed, cloud savings or production accuracy. These are rules-driven replays with zero model calls/tokens; zero model inference cost does not mean zero total delivery cost.

These traces use the evidence harness, not an assertion that every historical or deployed run has a continuous root across requests. Named spans preserve state milestones; normalized Neatlogs readback drops custom `bakaya.*` attributes. Local results retain the run IDs and revision checkpoints. The public snapshot excludes prompts, output contents, documents and project/account identifiers. Dashboard guest sharing has not been verified; the public snapshot is the account-free evidence fallback.

## Separate live model evidence

Application trace `45d523b11808755c75601c9114fc81b1` verifies one actual claude-haiku planning/inventory step. Its call returned 358 prompt + 72 completion tokens and gateway-reported USD0.0007898. This is one call, not packet cost or account spend. Diagnostic Doctor trace `9f12d6ec853a4d4ec8b43b8da7c4fb57` is separate. A synthetic structured extraction also returned HTTP200 and 166 tokens; no private records were used.

Upload extraction and agent run/resume requests have individual roots. Manual model spans record timing, actual returned tokens and available gateway cost; tool spans record execution. Health, ordinary CRUD and the frontend are not instrumented. Error messages/stack traces are redacted, and document/prompt/response contents are omitted intentionally. No detections, alerts or automatic evaluations are configured.

## Budget and reproduction

The configured OpenAI-compatible gateway is `https://litellm.vision.aivar.app/v1`, using `claude-haiku` and an ignored key. The provider enforces the owner-confirmed shared USD15/key/30-day budget; remaining balance is unknown. Production public reviewers cannot initiate paid model or buyer-enrichment calls. Planning output is bounded to 256 tokens, extraction to 4096; paid calls never retry automatically. HTTP402/429 requires manual quota action.

Use the [replay report's isolated reproduction instructions](evidence/PAIRED-AGENT-REPLAY.md). The harness refuses existing data directories and paid-provider configuration. Supply only Neatlogs credentials. Never replay into live data or publish its key.

SDK reference: https://docs.neatlogs.com/sdk/python
