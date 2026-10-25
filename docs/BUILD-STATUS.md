# Build status — 11 October 2026

Bakaya is a working **trusted local receivables-preparation prototype**, not a deployed financial/legal service. Python/FastAPI, Pydantic, SQLite and Decimal power a React/TypeScript workspace.

## Implemented

- CSV/XLSX, searchable PDF/text ingestion with original files, hashes and page/line references. Hashes verify stored bytes, not authenticity.
- Source-quoted typed model proposals; live synthetic extraction validated through the OpenAI-compatible gateway using claude-haiku.
- Invoice/payment/TDS allocations, ambiguity blockers, control-total reconciliation and disclosed interest conventions with reviewer-supplied dated rates.
- Bounded planning, persistent steps/revisions, attempt limits, recoverable errors and reviewer waits. Deterministic mode is labeled.
- Source-backed corrections invalidate approval; current-revision human approval gates PDF/CSV/evidence ZIP export. Nothing is sent or filed.
- Ledger-first workspace, evidence review, collapsed secondary tools, accessible Radix dialogs and self-hosted fonts.

## Recorded verification

Latest pre-release snapshot: **94 backend tests freshly pass on 11 October**, frontend build passes; desktop/mobile allocation → confirmation → approval → ZIP download and tablet overflow checked, with no observed runtime errors. Export PDFs were visually inspected in earlier validation. Revalidate final changes; these are recorded snapshots.

Eight new Crustdata tests are included. Consent and cached buyer lookup passed browser checks at 1440/768/390 widths; the cached call consumed zero new credits. The local ledger shows 4 consumed / 4 reserved of the 500-credit ceiling. GitHub push/PR test-and-build validation has been added; remote CI passed for release commit `e0ab49f` (GitHub run 38123570935).

A live four-tool model-planned run saved eight checkpoints and reached reviewer wait; state survived restart. A separate deterministic injected failure resumed with inventory executed once and one failed step retained. This was not a real provider outage or mid-call crash test.

Twenty synthetic fixtures: deliberate baseline 14/20 versus corrected matcher 20/20; false TDS short-payments 4 → 0 and planted ambiguities 0/2 → 2/2. This is fixture performance, not customer accuracy or legal certification.

Neatlogs application trace `45d523b11808755c75601c9114fc81b1`: successful workflow/model/inventory spans. One planning call reported 430 tokens / USD0.0007898; team total/remaining balance unknown. Entire saved remote checkpoint linkage, one-line attribution and isolated Git-assisted rollback passed; native Entire session resume restored conversation but **did not roll code back**.

## Remaining gates

| Area | Current truth / next action |
| --- | --- |
| cfo.ai | Model created, values/formulas read back, browser opened and actual spreadsheet export verified. [Current integration status](market/cfo-integration.md). |
| Crustdata | Authenticated; optional buyer enrichment implemented and browser-verified under the 500-credit ceiling. [Current integration status](market/crustdata-integration.md). |
| Public evidence | Repository PUBLIC verified; final guest-link checks, progress post, narrated video and submission pending. |
| Docker / AWS | Docker image built. Dedicated encrypted AWS launch immediately terminated with InvalidKMSKey.InvalidState; provider action required. |
| Real documents | Clean synthetic image/PDF OCR verified; difficult public receipt recovered 0/5 expected monetary amounts. Customer/professional validation pending. |
| Legal / rates / portal | Rate-history fetch/cache, actual portal schema/fees and qualified eligibility/interest review pending. |
| Production | Authentication/roles, tenant isolation, CSRF, throttling, encrypted backup/restore implemented and tested. Deployed backend, off-host backups, retention/deletion, monitoring, malware controls, policy and independent review remain pending. |
| Market | No CA/customer interviews or paid pilots; pricing and demand are hypotheses. |

See [judging evidence](JUDGING-EVIDENCE.md), [release package](RELEASE-PACKAGE.md) and [manual steps](MANUAL-STEPS.md). No completion percentage is a measured production-readiness score.


## Live synthetic deployment — 11 October 2026

Frontend: https://bakayaai-sandesh.vercel.app. AWS backend: https://3-93-34-52.sslip.io. Certificate validation, reviewer login, secure cookie, authenticated cases, logout and session revocation passed. The dedicated t3.small uses 16 GB unencrypted gp3 under explicit owner approval; synthetic data only. Daily encrypted backups are active; one downloaded off-host archive restored successfully. Automated off-host transfer, professional sign-off and sensitive-document production readiness remain pending. Stop the instance after the event; stop/start changes its public IP and requires updating the backend hostname and frontend rewrite.

Login details are in the ignored local artifacts/deploy/operator-access.txt; never publish that file. Live browser inspection was unavailable, so deployed UI visual QA remains pending.
