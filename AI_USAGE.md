# AI usage log

Hack for Social Cause 2027 requires teams to disclose how AI tools were used and to estimate the share of work they produced. This log is kept current by the lead and is the source for the disclosure on slide 7 of the deck.

| Date | Tool / model | Work | Human review |
|---|---|---|---|
| 2026-10-25 | Claude Code (Opus 5.5, lead) | Phase 0: imported the Bakaya engine (same author), removed Bakaya-only integrations, wrote AGENTS.md, subagent definitions, build status | Sandesh to review |
| 2026-10-25 | Claude Code lead + recon subagent (Haiku 5.5) | Phase 1: REUSE-MAP, Offer schema, offer routes, pipeline, test rewrite | Sandesh to review |
| 2026-10-25 | Claude Code lead (Opus 5.5) with subagents (Sonnet and Haiku 5.5) | Phase 2: lanes for rules engine, multilingual fallback extractor and LLM numeric guard, check-in net, i18n copy (en, hi, mr), six-screen frontend, pattern map and map view | Sandesh to review; Hindi and Marathi copy pending native review |
| 2026-10-25 | Codex CLI (0.162.1) | Phase 2: 40 synthetic labelled offers in `eval/offers/`; Leaflet map and district boundary handling | Sandesh to review; boundaries from geoBoundaries (ODbL) |
| 2026-10-25 | Claude Code lead + QA and reviewer subagents (Sonnet and Haiku 5.5) | Phase 3: evaluation harness and report (`eval/run_eval.py`, `eval/REPORT.md`), security review, fixes for review findings, anonymous retention and rate limit | Sandesh to review; evaluation caveat stated in the report |
| 2026-10-25 | Claude Code docs subagent (Haiku 5.5) | Phase 4 docs: README, architecture, rules, privacy, demo script, deck outline, this log. Removed Bakaya-specific `docs/PRODUCTION.md` and `backend/README.md` | Sandesh to review; open items listed in each document |

## Human work that remains

Humans must still do all of the following before submission:

- Confirm the live Stage 1 deadline on the MY Bharat portal. The guidelines and the build plan give different dates.
- Apply the IIT Bombay deck template; name the deck `Maharashtra_<TeamName>_Deck.pdf` and keep it at 10 MB or less.
- Native review of all Hindi and Marathi copy (`frontend/src/i18n/REVIEW.md`).
- Verify the MEA fee cap (Rs 30,000 + 18% GST) against the current official figure, and fix the matching copy.
- Verify each rule's MEA source passage and the problem-statement links, which were taken from the brief and not re-checked in the docs pass.
- Load the MEA active recruiting agent list and confirm the list date appears on every verdict.
- Run the LLM path live through the chosen gateway (the last attempt returned HTTP 401) and update the privacy notice with the disclosure.
- Legal review of the DPDP Act 2023 open questions in `docs/PRIVACY.md`.
- Team member details, team name, college details and self-certifications (Annexure 1) are entered by humans only. No agent handles them.
- Sign-off on every verdict and check-in wording.
- Final upload and submission on the portal by the team lead.

## Estimated AI share of code and documentation

**Estimate: 90 to 95 per cent** of the repository's code and documentation was drafted by AI tools (Claude Code subagents and Codex CLI), under human direction and review.

Method: estimate by the team from the commit history (`git log`), the agent-lane records in `docs/BUILD-STATUS.md` and the review findings. It is not a tool-measured figure. Every change was reviewed and tested by a human before it was committed. Re-estimate at feature freeze (27 October 2026, 12:00 IST) and update slide 7 of the deck to match.
