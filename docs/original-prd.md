# Bakaya — PRD (neatHack)

Oct 10, 2026 · @Shubham Sahu

## Summary

Bakaya is an agent that turns an Indian micro or small business's messy receivables records into a filing-ready delayed-payment claim under the MSMED Act. Each claim carries a statutory interest schedule, and every number links back to its source document.

The owner uploads invoices, POs, delivery proofs, bank statements and buyer messages. Bakaya matches payments to invoices and fixes the legal due dates. It computes Section 16 compound interest at 3× the RBI bank rate and checks eligibility. It then outputs an MSME ODR claim packet and a demand letter. Nothing is sent without human approval.

- **Team:** ETL SAPIENS (neatHack, solo to 4)
- **Submission window:** Mon 12 Oct 2026, 7:00–11:55 PM IST
- **Status:** draft PRD; the product name is a working title

## Problem and evidence

Indian small suppliers are owed huge sums. The legal remedy exists, but assembling a correct claim is slow, error-prone work. By 14 Aug 2026, micro and small enterprises had filed **2,56,892 delayed-payment applications worth ₹55,244 crore**. Of that, ₹20,979 crore is still pending, and 16% of cases have been open for over a year ([Crisil](https://intelligence.crisil.com/en/homepage/newsroom/press-releases/2026/08/executed-well-msme-bill-can-be-an-ibc-moment-for-delayed-payments.html)). Indian SMEs wait **73 days** on average to be paid, even though over 82% of invoices carry terms of 30 days or less. That figure comes from about 1.1 lakh MSMEs ([Recordent SME Receivables Report 2026](https://mediabrief.com/recordent-report-highlights-working-capital-stress-for-indian-smes-as-average-overdue-receivables-cross-%E2%82%B93-83-crore/)). Crisil notes that many delays are never formally reported.

**The legal lever** ([mylegalpal](https://mylegalpal.com/articles/how-to-recover-payments-from-clients-in-india-msme-odr/))

- **Section 15:** payment is due within the agreed period, capped at 45 days from acceptance. With no written agreement it is due in 15 days. Goods are deemed accepted if the buyer doesn't object in writing within 15 days.
- **Section 16:** compound interest at 3× the RBI bank rate, with monthly rests, from the due date. It overrides any contract term.
- **Income Tax Act Section 43B(h):** since 1 Apr 2024, a buyer cannot deduct MSE dues that are unpaid past the Section 15 deadline. That gives the supplier leverage in a demand letter.
- **Eligibility:** micro or small only, Udyam-registered *before* the invoice, and manufacturing or services. Traders are excluded.

**Why now:** the MSME ODR portal (odr.msme.gov.in) became the only route for new claims on 15 Oct 2025, and filing is free. Owners now face a new process and have to document the claim themselves. A pending 2026 MSMED amendment Bill would add 90-day mediation, a 75% pre-deposit before a buyer can challenge an award, and recovery as arrears of land revenue. If it passes, these claims become far more valuable.

## Users, buyer and positioning

The user is the owner of a small manufacturer or service firm. The paying channel is the chartered accountant (CA) who already handles their Udyam registration and tax audit.

| Who | Role | What they need | Why they pay |
| --- | --- | --- | --- |
| MSE owner (e.g. a component maker owed ₹8 lakh by a large buyer) | Primary user | A claim they can file today without a lawyer | They recover the dues plus roughly 16–20% statutory interest |
| CA / accounting firm | Channel and repeat buyer | Packets for many clients, consistent and reviewable | A billable service; already tracks 43B(h) in tax audits |
| MSME lawyer / filing service | Secondary buyer | Faster preparation of claims | Cuts drafting time per case |

**Competition** (from public pages; products not tested)

| Player | What it does | Gap Bakaya fills |
| --- | --- | --- |
| [Recordent](https://recordent.com/collection-management) | Credit reports, collections, legal notices, e-arbitration | No evidence reconstruction or statutory interest packet |
| CredFlow-style receivables tools | Payment reminders and dunning | Prevention only; no claim |
| Filing services and law firms ([TaxClue](https://taxclue.in/msme-samadhaan), [LegalBabu](https://www.legalbabu.com/payment-recovery-under-msme/)) | Prepare and file manually | Slow and priced per case; quotes not published |
| Online interest calculators ([corplawupdates](https://www.corplawupdates.in/tools/fee-calculator/msme)) | One-invoice interest maths | No matching, eligibility check or evidence |

**USP:** “Upload your mess, get a claim where every rupee is traced to a document.” Bakaya is the only option we found that reconstructs the claim from raw records. It handles partial payments, TDS deductions and bank-rate changes over time, and leaves anything unresolved visible instead of guessing.

## Goals, non-goals and metrics

For the hackathon, the goal is one complete, correct claim packet from messy synthetic records. The run must show a measured improvement and a recovery from a failed action.

**Goals**

- Go end to end from upload to packet: an approved ODR packet, an interest schedule and a demand letter.
- Use deterministic arithmetic. The model extracts and reasons, but code computes every rupee.
- Link every figure to a source (file, page or line).
- Flag uncertainty explicitly: ambiguous matches stay open instead of being guessed.
- Require human approval before anything leaves the system.

**Non-goals (this build)**

- Filing on the ODR portal automatically, or sending anything to the buyer.
- Medium enterprises, traders, or disputes over quality and contract terms.
- Legal advice or predicting outcomes. Bakaya prepares documents for self-filing.
- Multi-currency or export receivables.

**Success metrics**

| Metric | Hackathon target | Product target |
| --- | --- | --- |
| Invoice–payment match accuracy on eval set | ≥ 95% after fix (baseline reported) | ≥ 98% on real ledgers |
| Interest error vs hand-computed truth | ≤ ₹1 per invoice | ≤ ₹1 per invoice |
| Packet completeness (required fields present) | 100% on eval set | 100% |
| Time from upload to packet | < 5 min for 30 invoices | < 10 min for 200 invoices |
| Flags raised on ambiguous cases | Every planted ambiguity flagged | Reviewer agrees with ≥ 90% of flags |
| Paid validation | 3+ CA or owner conversations, 1 "would pay" | 5 paid pilot packets |

## Agent workflow and requirements

The model reads documents and plans; deterministic code does every calculation. Two loops send the agent back to matching: an ambiguous match, or totals that don't reconcile.

&#91;embedded content: Bakaya agent loop · 8 steps, 3 side exits, 2 loops back to matching\]

A failed rate fetch falls back to a dated table and is flagged on the packet rather than blocking the run. An ineligible claim stops with a reason.

| ID | Requirement | Acceptance |
| --- | --- | --- |
| FR1 | Ingest PDF invoices, scanned images, bank statement CSV/XLSX, WhatsApp .txt export | All four types parse on the eval set |
| FR2 | Extract typed records (Invoice, PO, Delivery, Payment, Message), each field with a source reference | 100% of fields carry file + page/line |
| FR3 | Match payments to invoices: TDS at 194C/194J rates, partials, lump sums; a confidence score; a question when below threshold | ≥ 95% eval accuracy; every planted ambiguity flagged |
| FR4 | Due date = acceptance (delivery, or the objection outcome) + agreed term capped at 45 days; 15 days if no written term | Unit tests on all date rules |
| FR5 | Eligibility: micro/small, manufacturing or services, Udyam date before invoice date | Ineligible cases stop with a stated reason |
| FR6 | Section 16 compound interest, monthly rests, 3× bank rate per rate period; rate fetched with a timestamp | ≤ ₹1 error per invoice vs ground truth |
| FR7 | Verification: claimed + received totals reconcile to the bank statement; otherwise back to matching | No packet marked ready on a mismatch |
| FR8 | Outputs: ODR field sheet, interest schedule (PDF + CSV), demand letter with 43B(h) note, indexed evidence bundle | Every figure links to a source |
| FR9 | Approval gate and audit log of every agent decision | Export disabled until approved |
| FR10 | Buyer lookup via Crustdata (legal name, size), cached, owner confirms | Optional; never used as proof |

## Architecture and sponsor tools

Everything runs as one FastAPI service on the single allowed EC2 instance in us-east-1, with SQLite and temporary uploads. The model is called through its own API, since sponsored AWS credits exclude Bedrock and S3.

&#91;embedded content: Bakaya architecture · one EC2 service, four tools, three sponsor tools\]

The orchestrator decides which tool to call next, but only the interest engine computes rupee amounts. That's why it has the strictest tests.

**Core records:** `Invoice`, `PurchaseOrder`, `Delivery`, `Payment`, `Message`, `Match` (with confidence and reason), `RatePeriod`, `Claim`. Every record carries a `SourceRef` (file, page or line, extracted text).

| Tool | Required? | How Bakaya uses it | Evidence for judges |
| --- | --- | --- | --- |
| neatlogs | Yes | Trace every run: plans, tool calls, cost and latency; find the TDS mis-match and verify the fix | Before/after trace links, observed cost per packet |
| Entire | Yes | Repo connected from commit one; checkpoints for each fix, linked to its coding-agent session | Checkpoint link + ID for the TDS fix, entire-graph output |
| cfo.ai | Yes | Pricing, costs, revenue and runway using neatlogs cost per run | Exported business plan |
| Crustdata | Optional | Buyer company lookup for the demand letter, cached, owner confirms | One enriched buyer in the demo packet |
| AWS ($25) | Optional | One EC2 instance hosting API and app | Live demo URL |

## Evaluation

The judges get numbers, not adjectives: one synthetic eval set, scored before and after a traced fix, plus one deliberately broken run.

**Eval set: 20 synthetic supplier cases**, each with hand-computed ground truth (matched invoices, due dates, interest per invoice, eligibility verdict).

| Planted difficulty | Cases | Correct behaviour |
| --- | --- | --- |
| Clean: one invoice, one late payment | 3 | Exact interest |
| 2% TDS deducted (₹98,000 paid on ₹1,00,000) | 4 | Treat as full payment, not a ₹2,000 short-pay |
| One payment covering several invoices | 3 | Split by buyer's remittance note or oldest-first, flagged |
| Partial payments over months | 3 | Interest on the outstanding balance only |
| Two invoices with the same amount, one payment | 2 | Refuse to guess; ask for remittance detail |
| Buyer objection within 15 days | 2 | Acceptance date moves; due date recomputed |
| Udyam registered after the invoice / trader | 2 | Ineligible, with a stated reason |
| Bank-rate change mid-delay | 1 | Interest computed per rate period |

**Before and after (the neatlogs story):** v1 matches by amount and flags TDS deductions as short-payments, inflating the claim. The traces show the mismatch, and the fix adds TDS recognition (194C/194J rates) plus ledger cross-checks. Report match accuracy, interest error and false short-pay count for both versions, side by side.

**Recovery run (required):** the RBI bank-rate fetch times out or returns an unexpected format. The agent retries once, then falls back to a bundled dated rate table, marks the assumption on the packet and re-verifies when the source responds. A second planted failure is an unreadable scanned challan. The agent asks for a re-upload or alternative proof instead of inventing an acceptance date.

**Hard checks before any packet is marked ready:** the totals reconcile to the bank statement, every interest line points to a rate source, and every invoice has proof of acceptance or is flagged.

## Business model and pricing

The model is a free calculator up front, flat fees per packet, and a monthly CA plan. There is no success fee. All prices are untested hypotheses to model in cfo.ai and check with real buyers.

| Offer | Price (hypothesis) | Who | Includes |
| --- | --- | --- | --- |
| Interest calculator | Free | Any MSE owner | Single-invoice Section 16 maths; captures the lead |
| Claim packet | ₹1,999 per buyer claim | Owner, self-serve | Up to 50 invoices, ODR packet, schedule, demand letter |
| CA plan | ₹4,999/month | CA firms | 10 claim packets/month, client workspaces, white-label export |
| Extra packet | ₹399 | CA plan | Beyond the monthly 10 |

**Why flat fees, not a percentage:** a success fee on recovered dues looks like legal representation. A flat document-preparation fee keeps Bakaya a software tool, and keeps price unrelated to claim size, which is easier for owners to accept.

**Unit economics to model in cfo.ai**

- **Cost per packet:** model inference + OCR + compute. Use the *observed* cost per run from neatlogs traces rather than an estimate.
- **Human support:** minutes per packet for unclear cases, at a fixed hourly cost.
- **Scenarios:** 100, 1,000 and 10,000 packets a month, with CA plan share at 20% / 50%.
- **After credits:** EC2 and model API at list price.
- **Runway:** the cash needed to reach 50 paying CA firms.

**Growth loop:** each demand letter carries a "prepared with Bakaya" line and the 43B(h) warning. Buyers' finance teams see it, and some of them are suppliers too. CAs bring their whole client book.

## Build plan, demo and building in public

Instrument first, build the happy path, then break it on purpose. Submit at 7 PM IST on Monday, not at 11:50.

**Sat 10 Oct: foundation**

- [ ] Before 8:54 AM Sun: claim the AWS access link (it expires 24h after the email)
- [ ] Sign up for neatlogs, Entire (hack.entire.io/neathacks-2026), cfo.ai (cancel billing straight away) and Crustdata (enter the code before email signup)
- [ ] Create a fresh public repo with Entire connected and neatlogs tracing on from the first commit
- [ ] Data model and deterministic interest engine with unit tests
- [ ] Synthetic eval set: 20 cases with ground truth
- [ ] Post #1: the problem plus the ₹55,244 crore figure

**Sun 11 Oct: the agent**

- [ ] Ingest (PDF, image, CSV, chat export) → extraction with source refs
- [ ] Matching, due dates, eligibility, clarifying questions
- [ ] Packet outputs: interest schedule, ODR fields, demand letter
- [ ] Run v1 on the eval set and record the baseline in neatlogs
- [ ] Fix TDS and matching from the traces, re-run, record the numbers; checkpoint in Entire
- [ ] Recovery run: bank-rate fetch failure and an unreadable challan
- [ ] Message 3–5 CAs or owners for willingness to pay
- [ ] Posts #2–#3: the TDS bug trace, before/after numbers

**Mon 12 Oct: business and submission**

- [ ] cfo.ai plan using observed costs per run
- [ ] Crustdata buyer lookup in the packet
- [ ] Record the demo (≤ 3 min)
- [ ] README with traces, Entire checkpoint link and ID, eval table, cfo.ai plan
- [ ] Post #4, then the submission quote-post on X with team, name, project, repo and demo

**Demo script (≤ 3 min)**

1. 0:00 – a supplier owed ₹8 lakh for 140 days, and the ₹55,244 crore national figure.
2. 0:20 – upload a messy folder; the agent plans and extracts, with live trace.
3. 0:50 – the v1 claim wrongly lists a ₹2,000 short-pay; open the neatlogs trace and show why.
4. 1:20 – the fixed run gives correct numbers, with the before/after table on screen.
5. 1:50 – the RBI fetch fails, the agent falls back and flags it; an ambiguous match is left for the user.
6. 2:20 – the approved packet with every rupee clickable to its source.
7. 2:40 – the Entire checkpoint, the cfo.ai plan, and the CA plan pricing.

## Risks, compliance and open questions

The biggest risk is willingness to pay, not technology. Free self-filing means Bakaya must clearly save time or raise recovery.

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Owners won't pay when filing is free | No revenue | Sell to CAs as a billable service; validate with 3–5 calls this weekend |
| Seen as unauthorised legal practice | Regulatory | Position as document preparation for self-filing; no advice, no success fee, a disclaimer on every packet |
| Wrong interest or eligibility | Claim rejected; trust lost | Deterministic engine, ground-truth tests, mandatory human review |
| Sensitive financial data (bank statements, GSTINs) | Privacy breach | Synthetic data in demo and posts; redact before traces; delete after export |
| Bank-rate figure varies between sources (5.50% vs 6.5% seen) | Wrong maths | Fetch from RBI with a timestamp; dated fallback table; flag if stale |
| Rules change (2026 Bill, ODR fields) | Outdated packet | Rules versioned in config with source and date; check odr.msme.gov.in before the demo |
| Demo scope creep | Missed deadline | One buyer, up to 30 invoices, four input types |

**Open questions**

- [ ] Is the product name final? "Bakaya" is a working title.
- [ ] Exact ODR portal form fields and the document formats it accepts
- [ ] Today's RBI bank rate, and its history over the last 24 months
- [ ] Team size and who owns agent, data and demo/posts
- [ ] Does neatHack allow an India-only problem? (Likely yes; confirm on Discord)
- [ ] Pricing reaction from at least 3 CAs
