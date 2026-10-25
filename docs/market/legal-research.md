# Legal research and corrections for Bakaya

**Research date: 2026-10-10. Draft engineering and marketing research; review required before real claims.** The software can prepare a review packet. It should not decide contested legal entitlement or guarantee portal acceptance.

## Corrections that affect the build

| PRD statement | Finding | Product decision |
|---|---|---|
| Interest starts “from the due date” | Section 16 says appointed day, or the date immediately following the agreed date. Section 15 and 16 are reproduced in the official NBCC judgment, pp. 18–19. | Store last payment date and first interest date separately; payment on deadline attracts no late interest. |
| Registered before invoice = eligible; later registration = ineligible | This is too simple. Older cases consider registration, contract and supply dates. NBCC (2025) questioned prior registration as a condition to Section 18 and referred the issue to a larger bench. | Gather registration history, contract/PO, supply and invoice dates. Late or uncertain registration becomes **needs legal review**, not an automatic entitlement or final rejection. |
| RBI Bank Rate 5.50% or 6.5% | RBI notification of 7 October 2026 raises Bank Rate from 5.50% to **5.75% immediately**. | Current 3× nominal input = **17.25%**. Historical periods need their historical rates. Do not use repo rate or current rate for an entire old debt. |
| 75% pre-deposit is a prospective 2026 reform | Section 19 already contains a 75% deposit condition for a non-supplier applicant seeking to set aside an award/decree/order. | Remove “new benefit” claim. Do not equate deposit with recovery guaranteed to the supplier. |
| ₹55,244 crore / 2,56,892 as at August 2026 | Official Ministry Annual Report 2025–26 reports **2,56,892 applications / ₹55,244.31 crore up to 31 December 2025**. | Use that exact date and distinguish applications from resolved cases or recovered money. |
| Only new-claim route is ODR from 15 October 2025 | Confirmed by the Ministry's Annual Report 2025–26, section 1.7.1. | Link official ODR portal; label generated field sheet as provisional until current form is checked. |
| Filing is free | Universal current fee schedule not verified; official ODR guideline link failed to download. Portal access, a government filing fee and later ADR/representation costs are distinct. | Do not publish “entire process free.” Confirm applicable institution/state rules manually. |
| Always put a 43B(h) warning in letters | Historic 1961 Act provision is verified, but CBDT now provides the Income-tax Act 2025 and 2026 transition guidance. | Default to neutral optional tax note requiring CA review, tax-year selection and current statutory mapping. |
| Recognize 2% TDS by amount and clear principal | A matching amount is evidence of a possible deduction, not proof it is valid TDS or credited to the supplier. | Require certificate/tax-credit/ledger evidence and approval; otherwise leave the difference unresolved. No universal 194C/194J rate assumption. |
| Flat fee means no unauthorized legal-practice issue | Fee structure alone cannot settle the regulatory question. | Obtain legal review of scope, disclaimers, notices, referral model and representation boundaries. |

## Date rules: distinguish law from arithmetic conventions

The statutory rule is acceptance/deemed acceptance based, not invoice-date based. Section 2(b) defines appointed day after expiry of fifteen days from acceptance or deemed acceptance. A written objection concerning acceptance within fifteen days changes the acceptance analysis to the date that objection is removed; silence does not invent documentary proof. With a written agreement, the agreed payment period cannot exceed 45 days from acceptance/deemed acceptance. With no written agreement, payment is required before appointed day.

Engineering convention for review: if acceptance is 1 January, no written term gives a last payment date of 16 January and first interest date of 17 January. A 30-day written period gives last payment date 31 January and interest starts 1 February. These examples apply ordinary date addition and need sign-off on boundary counting. Missing acceptance evidence or unresolved objection must block “ready” status. A 60-day contract cannot simply retain a 60-day statutory deadline.

Separate confirmed statutory monthly compounding from unresolved implementation choices: calendar-month vs anniversary rests; actual/365 vs another day-count convention; leap years; odd-day prorating; rounding timing; allocation of partial payments between principal and interest; tax deductions, credit notes, returns and disputed adjustments. Neither an AI nor a test fixture makes a chosen convention legally authoritative. Show the convention and rate segments on every schedule. An unsupported fallback can create an **estimate / review required**, never a silently verified statutory amount.

## Registration and scope

NBCC (India) Ltd. v State of West Bengal, **2025 INSC 54,10 January 2025**, is available from the Supreme Court. Its analysis differs from the prior-registration readings of Silpi Industries and Mahakali Foods; its conclusion in paragraphs 29–30 refers the appeal to a three-judge bench. Some secondary pages describe this as a final blanket rule. That omits the reference and is unsuitable for a binary eligibility engine. The current larger-bench disposition was not verified in this research; retain it as a blocking question for real filings.

Official Ministry material restricts delayed-payment provisions to micro/small manufacturing or service enterprises and excludes trading activities with NIC 45/46/47. Medium businesses are outside this MVP. Do not deny all remedies to those outside scope; distinguish **unsupported by Bakaya** from **has no legal remedy**. Mixed activities, historic registrations (EM-II/UAM/Udyam/UAP), migration, enterprise reclassification and registration after contract deserve human review. RAMP's ODR scheme page mentions Udyam and UAP; portal onboarding eligibility and substantive statutory entitlement should not be conflated.

Current Ministry classification page states revised thresholds from 1 April 2025: micro investment ≤₹2.5 crore AND turnover ≤₹10 crore; small ≤₹25 crore AND ≤₹100 crore; medium ≤₹125 crore AND ≤₹500 crore. Date-specific classification and transition rules matter; a current certificate alone may not answer a historic supply question.

## Tax and demand-letter treatment

The official 1961 Act Section 43B page and CBDT September 2024 tax-audit webinar support actual-payment deduction treatment for covered MSE liabilities beyond Section 15 deadlines, effective AY 2024–25. It is not a fine payable to the supplier or proof that this buyer has an immediate tax liability. The return-filing-date relaxation applicable to other Section 43B clauses does not automatically apply to (h). Interest deductibility under MSMED Section 23 is a separate point.

The official Income-tax Act 2025 hub now publishes transition guidance. Search indexed official Bill text identifies a corresponding rule at Section 37(2) (g), but the enacted Act PDF returned 404 and its dynamic section page did not expose the text here. **Do not certify that mapping from a Bill alone.** A CA must check enacted/current text, commencement, tax-year applicability and savings for older years before a letter uses the successor citation. Until then use: “Delayed payment may have tax consequences under the applicable income-tax provisions. Please obtain advice for the relevant tax year.” The business should be able to omit this optional note.

## Portal and amendment verification

The ODR homepage was discoverable in official indexed content, but live fetch returned 502. No logged-in form was accessed; no case was created. Required fields, limits, allowed attachments, declarations, digital signatures, institution selection, state process and fees remain **unverified**. The exported document must say “claim-preparation field sheet — verify against current portal.” A human approval inside Bakaya is not a government acknowledgment.

The Ministry's orders listing, indexed as checked today, labels a **draft** Micro, Small and Medium Enterprises Development (Amendment) Act, 2026 with publication date 21 September 2026. This is not evidence of passage, assent or commencement. Keep mediation/recovery changes out of the operative rules until Gazette text and effective dates are checked.

## Source register

All accessed 2026-10-10. Dates below are source/effective dates, not inferred dates of legislation.

| ID | Primary source | Date and access quality | Used for |
|---|---|---|---|
| L1 | [India Code MSMED Act](https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf) | Act 2006; indexed document found; direct fetch timed out | Canonical law reference; sections 15/16 additionally read in L2 |
| L2 | [Supreme Court NBCC judgment](https://api.sci.gov.in/supremecourt/2022/24558/24558_2022_12_1501_58501_Judgement_10-Jan-2025.pdf) | 2025-01-10; PDF downloaded and text extracted; local `sources/nbcc-2025.pdf` | Sections 15/16 pp.18–19; registration reasoning and paras 29–30 pp.42–43 |
| L3 | [RBI Bank Rate notification](https://www.rbi.org.in/scripts/NotificationUser.aspx?Id=13728&Mode=0) | 2026-10-07; full page read | Bank Rate 5.75%, effective immediately |
| L4 | [RBI current rates](https://www.rbi.org.in/) | Website updated 2026-10-10; full page read | Current Bank Rate corroboration; not complete historical table |
| L5 | [MSME Annual Report 2025–26](https://msme.gov.in/sites/default/files/MSMEANNUALREPORT2025-26ENGLISH_0.pdf) | Section 1.7.1, printed p.8; official indexed excerpt read | 2025-12-31 statistics; ODR switch |
| L6 | [Ministry delayed-payment guidance](https://ramp.msme.gov.in/ramp/pdf-documents/scheme-guidelines/msefc.pdf) | Undated guidance references Haryana 2021; official indexed text read | Trading exclusions; Section 19 already requires 75%; state procedure nuance |
| L7 | [Ministry classification](https://www.msme.gov.in/ministry/about-us/details/Title%3DWhat%27s-MSME-IzMzITMtQWa) | Effective 2025-04-01; official indexed text read | Current thresholds |
| L8 | [Income Tax Section 43B historic text](https://www.incometaxindia.gov.in/w/section-43b-39) | Page identifies 1961 Act, 2023 version; official text read | Clause(h) amendment and effective date; not proof of all current 2026 tax law |
| L9 | [CBDT tax-audit webinar](https://www.incometax.gov.in/iec/foportal/sites/default/files/2024-09/Webinar%20PPT%20for%203CA-3CD_3CB-3CD_13.09.2024.pdf) | 2024-09-13; official indexed text read | AY 2024–25 applicability |
| L10 | [CBDT 2025 Act and transition hub](https://www.incometaxindia.gov.in/en/income-tax-act-202511) | Current hub read; Act body inaccessible | Need for enacted successor text and tax-year review |
| L11 | [MSME ODR](https://odr.msme.gov.in/) | Live 502; indexed homepage available | Public route only; current form and fees unresolved |
| L12 | [ODR scheme](https://ramp.msme.gov.in/ramp/index.php/RAMP-initiative/mse-odr/mse-odr-scheme) | Official indexed text read | Scheme scope includes Udyam and UAP |
| L13 | [Ministry draft orders](https://www.msme.gov.in/documents/orders-and-notices?page=1) | Indexed listing states draft 2026 amendment, published 2026-09-21; live body empty | Do not treat draft as enacted |

## Review queue before real claims

1. Lawyer: reconcile current Supreme Court/larger-bench position and registration/supply timing; limitation, acknowledgments, jurisdiction and contract objections.
2. Lawyer/accountant: approve monthly-rest convention, rounding, partial-payment allocation and valid TDS evidence.
3. CA: enacted 2025 tax successor, year-specific applicability, exemptions and neutral letter wording.
4. Operator: capture dated current ODR field/attachment/fee checklist without submitting a claim.
5. Engineer/reviewer: collect official effective-dated rate history for every claim period; distinguish stale cache from verified coverage.
6. Founder/counsel: privacy, retention, subprocessor exposure, notice drafting and the boundary between software assistance and regulated professional services.
