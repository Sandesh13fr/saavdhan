# Hackathon milestones — 11 October 2026

The [official event page](https://neatlogs.com/hackathon) was fetched live with Firecrawl on 11 October. Submission opens **12 October, 19:00 IST**; **23:55 IST is the planned close**, with the final cutoff announced on [Discord](https://neatlogs.com/discord). Aim for opening. Submit by quoting the official neatlogs X post with team/name, project, public repository and demo; recheck live instructions before publishing.

| Milestone | Current evidence / remaining action | Owner |
| --- | --- | --- |
| Core agent | Bounded model planning, deterministic calculations, persistent steps, reviewer wait, revision-bound approval and export implemented. Recorded 99-test snapshot; revalidate final changes. | Builder |
| Interface | A ledger workspace + B evidence review; secondary tools collapsed; dialog focus and desktop/mobile export/tablet overflow checks passed. | Builder |
| Neatlogs | [Controlled full-lifecycle paired traces](evidence/PAIRED-AGENT-REPLAY.md) read back successfully: 27 spans each, tool ancestry, review/approval states, export and injected recovery verified. Actual revision comparison eliminates one redundant packet write with identical totals. [Public safe readback](evidence/paired-agent-replay.json); dashboard guest sharing unverified. | Complete for demonstrated scope |
| Entire | Saved/pushed checkpoints, linked-file attribution and isolated Git rollback verified. Native session resume did not restore code. [Evidence](ENTIRE-EVIDENCE.md). | Complete for demonstrated scope |
| cfo.ai | [Read-only judge model](https://app.cfo.ai/s/D9U0WKRrog83poBC), owner cash INR30,000/fixed costs INR20,000 monthly and separate hypothetical demand scenario saved/read back; zero formula errors. Conditional runway 1.5/2.83 months. Anonymous READ sharing enabled; [public CSV fallback](evidence/cfo-runway.csv) provides account-free values. Fresh native spreadsheet export remains unverified. [Status](market/cfo-integration.md). | Complete for model and public fallback |
| Crustdata | Auth/free balance check verified; optional consented buyer enrichment implemented and browser-verified at desktop 1440/tablet 768/mobile 390. Cached lookup spent zero new credits. Local ledger 4 consumed / 4 reserved of 500. [Status](market/crustdata-integration.md). | Builder |
| Public repository | Repository PUBLIC, verified by coordinating builder on 11 October. All 248 Git objects/local refs scanned for configured keys and supplied key patterns with zero matches; final release/guest link checks still required. | User, then builder |
| Building in public | Private commits are not public progress. Publish an honest dated update tagged #neatHack and preserve its URL; do not backdate. | User |
| Demo | [Local lifecycle recording](assets/agent-lifecycle.webm) and [compact evidence](evidence/agent-lifecycle.json) prepared: same goal/run ID, ten checkpoints, reviewer pause, revision 1→2, approval pause and packet completion. Scripted human inputs, synthetic records, zero paid calls; separate injected recovery. Final narrated three-minute presentation/upload remains pending. | User / builder capture |
| Release verification | 99 tests pass; auth/tenant tests and local Docker build/run verified. Revalidate CI for the final pushed SHA. Final submitted SHA and safe guest-access links still required. | Builder |
| Submit | Fill release links, confirm official post/Discord cutoff, quote official post and retain permalink/confirmation. | User |

No visibility change, public post or submission is implied by this checklist. Authentication/tenant tests and Docker are verified. Synthetic Vercel/AWS hosting is live after owner-approved unencrypted EBS; AWS default-encrypted provisioning failed even without KmsKeyId. Daily encrypted backups are active and one downloaded off-host archive restored; automated off-host transfer remains pending. OCR synthetic scans pass but CORD receipt amount extraction is 0/5. Professional signoff remains pending. See [manual steps](MANUAL-STEPS.md).


## Live synthetic deployment — 11 October 2026

Frontend: https://bakayaai-sandesh.vercel.app. AWS backend: https://3-93-34-52.sslip.io. Certificate validation, reviewer login, secure cookie, authenticated cases, logout and session revocation passed. The dedicated t3.small uses 16 GB unencrypted gp3 under explicit owner approval; synthetic data only. Daily encrypted backups are active; one downloaded off-host archive restored successfully. Automated off-host transfer, professional sign-off and sensitive-document production readiness remain pending. Stop the instance after the event; stop/start changes its public IP and requires updating the backend hostname and frontend rewrite.

Login details are in the ignored local artifacts/deploy/operator-access.txt; never publish that file. Live browser inspection was unavailable, so deployed UI visual QA remains pending.
