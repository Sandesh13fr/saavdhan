# Judging evidence — current snapshot, 11 October 2026

The [official event page](https://neatlogs.com/hackathon), fetched live with Firecrawl on 11 October, weights five categories. These are **weights, not a predicted score**. Mandatory sponsors are Neatlogs, Entire and cfo.ai. The cfo business plan must cover pricing, costs, revenue and runway. Submission requires a public repository with event-period commits and an accessible demo; public updates should be tagged #neatHack.

| Criterion | Weight | Verified evidence | Remaining evidence |
| --- | ---: | --- | --- |
| The agent | 30% | Bounded planning; deterministic Decimal verification; saved checkpoints/reviewer wait; restart persistence; separately injected recovery without repeated inventory; revision-bound approval/export. | Complete local lifecycle recorded; final narrated presentation and release checks at submitted SHA remain pending. |
| Sponsor use | 25% | Real model request; finalized Neatlogs application trace; Entire permanent checkpoints, attribution and remote readback. | Full lifecycle and paired revision trace readbacks completed; cfo owner inputs/readback and anonymous READ sharing completed with a public CSV fallback. Native anonymous cfo rendering and fresh native Excel export remain unchecked. |
| Demo | 20% | Desktop/mobile approval/export checks; synthetic inputs; [script](RELEASE-PACKAGE.md). | Actual final video and accessible URL. |
| Building in public | 15% | Dated event-period commits; repository PUBLIC, verified on 11 October. | Verify public source/commits; honest public progress update and URL. Private pushes alone are insufficient. |
| Usefulness/originality | 10% | Specific evidence-preparation/reconciliation workflow and attributed legal/competitor research. | Real user/professional validation remains unavailable; synthetic case only. |

## Evidence register

| Evidence | Exact scope / limitation |
| --- | --- |
| Tests / UI | Fresh 99 backend tests pass on 11 October; frontend build and desktop/mobile review/export plus tablet overflow passed. Revalidate final changes; do not advertise an evergreen test count. |
| Complete local lifecycle | [Recorded browser workflow](assets/agent-lifecycle.webm) and [compact evidence](evidence/agent-lifecycle.json): same goal/run ID, ten checkpoints, reviewer pause, revision 1→2, approval pause, packet completion and actual ZIP download. Scripted human UI inputs on synthetic records; zero paid calls. Not an LLM-planned run or Neatlogs trace, and separate from injected-failure recovery. |
| Live agent | Run `2557a200a4cb48abaa05f4c74ee9e214`: four tools/eight saved checkpoints/reviewer wait, retained after restart. No extraction or export within that run. |
| Extraction | Separate real claude-haiku synthetic buyer proposal passed source-quote/type validation. Initial structured-output call: HTTP200, 166 tokens. Not legal correctness. |
| Recovery | Run `12f1bf9b0cb84c8093b8e59f540afffe`: injected reconciliation failure, same-run resume, inventory once, failed step retained. Deterministic/local, not provider outage. |
| Neatlogs | [Complete paired lifecycle evidence](evidence/PAIRED-AGENT-REPLAY.md), [sanitized trace trees](evidence/paired-agent-replay.json): before `adede6146ac02b223da79587c5c46242`, after `3af784ca1b8dd9c7bcc69bb7d83fd1e7`; exact API readback success, 27 spans each, common root, review/approval state markers, packet export and separately labeled injected recovery. Zero LLM calls in these controlled replays; earlier actual model trace `45d523b11808755c75601c9114fc81b1` is separate. Public dashboard access remains unverified. |
| Cost | One call: 358 prompt + 72 completion tokens, reported USD0.0007898. Not total spend or packet cost. User cap USD15/shared key/30 days; remaining unknown. |
| Entire | Checkpoint `01M4KRBT9GY4SCGC3WR3NXRGTR` linked `0958d0e`, remote object matches; latest UI checkpoint `01M4KYXAQ24EBCG4NE32TZQA0H` linked `ad4a7ab`. [Detailed evidence](ENTIRE-EVIDENCE.md). |
| Attribution / rollback | Tested .entire/settings.json line15 attributes to Codex/checkpoint/commit. Native resume restored logs but did not restore code; explicit Git rollback passed in isolated clone only. |
| cfo.ai | [Read-only judge model](https://app.cfo.ai/s/D9U0WKRrog83poBC): pricing/unit costs, revenue/burn/runway, owner cash INR30,000 and fixed costs INR20,000 monthly; zero formula errors in both 240-cell scenarios. Zero-demand placeholder runway 1.5 months; hypothetical stress demand 2.83 months. Anonymous READ sharing settings and unauthenticated HTTP200 verified; logged-in browser values verified. [Public fallback CSV](evidence/cfo-runway.csv) needs no cfo account. Fresh native Excel export remains unverified. [Status](market/cfo-integration.md). |
| Crustdata | Authentication/free balance verified; optional app enrichment implemented and browser-verified with consent at 1440/768/390; cached lookup spent zero new credits; local ledger 4 consumed / 4 reserved of 500. [Current status](market/crustdata-integration.md). Not identity/eligibility proof. |
| AWS | STS identity verified. Default-encrypted provisioning failed even without an explicit KmsKeyId. Owner-approved synthetic Vercel/AWS deployment is live on unencrypted EBS; HTTPS/authenticated API checks passed. Credit balance and sensitive-document production readiness are unverified. |
| Actual revision comparison | [Paired traces and measurements](evidence/PAIRED-AGENT-REPLAY.md): redundant packet writes 1→0 between actual revisions 233acc9/6985522 with identical monetary totals, ten checkpoints and valid exports. Controlled replay now, not historical speed, cost or accuracy evidence. |
| Synthetic comparison | 20 fixtures: deliberately flawed baseline 14/20 vs corrected 20/20; false TDS 4→0, ambiguity 0/2→2/2. Not production accuracy or a trace-based historical improvement. |
| Production controls | Authentication/tenant authorization tests and local Docker build/run verified. Daily encrypted backups are active; one downloaded off-host archive restored. Automated off-host transfer remains pending. Synthetic deployment HTTPS/authenticated checks passed. Synthetic OCR passes; CORD public receipt amounts extracted 0/5. Professional signoff is pending. |
| Research | [Market documents](market/README.md): source-backed research and pricing hypotheses; no CA interviews, paid demand or recovery outcome claimed. |

The first MVP is the baseline; describe event-period changes using actual diffs. Sponsor logos/configuration do not substitute for useful workflows. No raw private evidence, public post, filing or billing action is part of this ledger.

## Final release evidence

Record the final SHA and tests/build; attach redacted before/after traces when available, actual recovery evidence, Entire checkpoint, cfo plan/export and video/repository/public-update URLs. Verify guest access. Missing artifacts stay pending. See [milestones](HACKATHON-MILESTONES.md) and [submission package](RELEASE-PACKAGE.md).


## Live synthetic deployment — 11 October 2026

Frontend: https://bakayaai-sandesh.vercel.app. AWS backend: https://3-93-34-52.sslip.io. Certificate validation, reviewer login, secure cookie, authenticated cases, logout and session revocation passed. The dedicated t3.small uses 16 GB unencrypted gp3 under explicit owner approval; synthetic data only. Daily encrypted backups are active; one downloaded off-host archive restored successfully. Automated off-host transfer, professional sign-off and sensitive-document production readiness remain pending. Stop the instance after the event; stop/start changes its public IP and requires updating the backend hostname and frontend rewrite.

Login details are in the ignored local artifacts/deploy/operator-access.txt; never publish that file. Live browser inspection was unavailable, so deployed UI visual QA remains pending.
