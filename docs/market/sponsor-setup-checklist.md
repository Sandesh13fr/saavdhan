# Sponsor and submission checklist — 11 October 2026

Current rules verified with a live Firecrawl fetch of the [official event page](https://neatlogs.com/hackathon) on 11 October. This replaces the original PRD-only checklist; expiry dates and account-specific balances still require their own evidence.

| Sponsor | Current evidence | Remaining / limits |
| --- | --- | --- |
| Neatlogs — mandatory | Finalized actual application trace with workflow/model/inventory spans. | Final redacted demonstration/comparison; do not imply every historical run was traced. |
| Entire — mandatory | Saved remote checkpoints, commit linkage and tested attribution. | Native session resume failed code rollback; Git-assisted isolated rollback passed. [Evidence](../ENTIRE-EVIDENCE.md). |
| cfo.ai — mandatory | OAuth/discovery succeeded previously; user has signed in; workspace shows Loading while model access is investigated. | Useful plan/write/readback/export pending. Must cover pricing, costs, revenue and runway with assumptions. [Status](cfo-integration.md). |
| Crustdata — optional | Authentication/free credit check verified. | Consented app enrichment implemented/browser-verified; cached lookup zero new credits, local ledger 4 consumed / 4 reserved of 500; user's working cap 500 credits remains despite advertised 5,000 event credits. [Status](crustdata-integration.md). |
| AWS — optional | STS identity verified only. | Current event page allows EC2, Lambda, IAM roles and load balancers in us-east-1, USD25/team for eligible first 350 checked-in teams; excludes Bedrock. No deployment/credit-balance verification. |
| LiteLLM — resource | Real claude-haiku requests/extraction/planning. | Page advertises USD20/team, but use user's stricter shared USD15/key/30-day cap; remaining unknown. |

Official cfo onboarding page says a card is required and immediate cancellation avoids billing. Account owner must review their actual billing/settings and handle any changes; no account cancellation, bank connection or purchase was performed by Bakaya.

## Final handoff

- [x] Supplied secrets kept local; repository public state verified on 11 October; bounded publication scan found no configured keys/patterns.
- [x] Neatlogs application proof and Entire checkpoint proof recorded.
- [ ] Actual cfo model/export verified, not merely prepared CSV inputs.
- [ ] Final code SHA/tests/build/demo and guest-access links reconciled.
- [ ] Narrated demo and honest #neatHack public progress URLs supplied.
- [ ] User checks Discord cutoff and quotes official neatlogs submission post with team/name/project/publicrepo/demo.
- [ ] User retains submission confirmation and later reviews account renewals/resources/retention.

Submission opens **12 October, 19:00 IST**; **23:55 IST is planned close**, final cutoff on Discord. See [release package](../RELEASE-PACKAGE.md), [milestones](../HACKATHON-MILESTONES.md) and [manual steps](../MANUAL-STEPS.md). Nothing has been posted/submitted by this document.
