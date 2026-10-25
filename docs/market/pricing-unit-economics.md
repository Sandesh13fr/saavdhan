# Pricing hypotheses and unit economics

**Draft 10 October 2026. Nothing here is measured cost, observed willingness to pay or a forecast.** The accompanying CSV contains illustrative sensitivity arithmetic. All prices originate in the supplied PRD and need validation.

## Proposed packages and the value metric

Charge per **buyer claim packet**: one supplier entity, one buyer legal entity, one defined invoice bundle and one approved evidence version. This tracks a completed preparation job better than seats or percentage of recovered money. Define regeneration, new evidence, page limits and refunds before sale so users are not surprised.

| Hypothesis | Price | Proposed scope | Validation needed |
|---|---|---|---|
| Calculator | Free | One invoice, user-entered dates/rate assumptions; estimate visible without mandatory email | Does qualified packet demand follow? Gate current rate coverage and legal ambiguity honestly. |
| Self-serve packet | ₹1,999 per buyer claim | Up to 50 invoices; source index, interest schedule, draft letter and provisional field sheet | Page/OCR ceiling, revisions, support minutes, taxes and refund terms. Do not promise representation. |
| CA monthly | ₹4,999/month | 10 packets; proposed client workspaces and branding | Do not sell unimplemented features. Validate repeat monthly case frequency and authority to upload each client's data. |
| CA extra packet | ₹399 | Same supported scope after monthly allowance | Full-utilization contribution margin, costly cases and retry abuse. |

Keep accuracy, source visibility, deletion control and human approval in every tier. Premium features can be usage, collaboration or branding; do not make essential error checks an upsell. Start monthly/pay-per-packet; defer annual contracts until repeat demand is observed. A flat fee clarifies billing but is not proof of regulatory compliance.

The CA bundle is a large discount: at 10 used packets revenue is ₹499.90/packet, versus ₹1,999 one-off. At 2 used it is ₹2,499.50/packet, so low-volume firms may prefer one-off purchases. At 20 used, revenue=(₹4,999+10×₹399) /20=₹449.45/packet. If account sharing, intensive support or complex evidence raises service cost, the extra-packet price is especially vulnerable.

## Model definitions

```
N = completed billed packets / month (exclude tests, failed jobs, free calculator)
s = fraction of N fulfilled under CA subscriptions (packet share, NOT account share)
u = used included packets per active CA account, 1..10
CA accounts = N*s/u  (continuous planning approximation; operational counts are integers)
Revenue = N*(1-s)*1999 + CA_accounts*4999 + extra_packets*399
Net revenue after refund provision = Revenue*(1-refund_fraction)
Payment costs = Revenue*payment_fee_fraction
Variable delivery cost = N*(inference+OCR+variable_compute+support_minutes*hourly_cost/60)
Contribution = Net revenue - Payment costs - Variable delivery cost
Operating result = Contribution - fixed_infrastructure - fixed_tools - payroll - legal/security - marketing
```

No GST is treated as revenue. Model assumes listed prices are **exclusive of applicable tax**, subject to founder/CA decision; inclusive pricing would reduce net revenue. Payment fees on tax, fixed transaction fees, chargebacks and tax-credit recovery are not modeled. Referral rewards, vendor minimums, foreign-exchange spread and data-egress need separate inputs if introduced. Do not double-count fixed EC2 cost in variable compute.

## Editable assumption register

| Input | Illustrative base | Stress | Source / replacement |
|---|---:|---:|---|
| Inference INR/packet |20|60|Assumption; replace with neatlogs measured billable cost including retries |
| OCR INR/packet |5|20|Assumption; measure pages and actual provider bill |
| Variable compute/storage INR/packet |5|20|Assumption; separate attributable usage from fixed hosting |
| Support minutes/packet |10|30|Assumption; time observed correction/review support, including failures |
| Loaded support INR/hour |600|1,000|Assumption; founder opportunity cost is not zero |
| Total variable delivery INR/packet |130|600|Derived from above |
| Refund provision |3%|3%|Assumption, not observed refund rate |
| Payment fee |2%|2%|Assumption, not quoted gateway rate |
| Fixed infrastructure/month |4,000|4,000|Placeholder, not AWS quote; excludes tools/payroll/legal/marketing |
| CA allowance used |10|10|Conservative full use for unit margin; separate utilization research required |
| CA packet share |20%/50%|20%/50%|Scenario, not market mix |
| Monthly volume |100/1,000/10,000|same|Scenario, not capacity or demand claim |

The CSV enumerates both cost cases, all three volumes and both CA shares. At 100 packets and 50% CA share, gross revenue is ₹124,945; base contribution before fixed costs is ₹105,697.75; stress contribution is ₹58,697.75. Those attractive blended numbers hide an important negative: a fully-used CA bundle has ₹474.905 retained after modeled refunds/fees per packet. At ₹600 delivery cost it loses ₹125.095/packet before fixed costs. A ₹399 add-on leaves ₹379.05 before delivery cost and loses ₹220.95 in the stress case. Do not use blended direct-sales margin to conceal an unviable subscription.

For a target 70% contribution margin after modeled refunds and fees, maximum delivery cost is 25% of gross selling price: ₹499.75 one-off, ₹124.975 per fully-used CA packet, ₹99.75 per extra packet. The illustrative ₹130 base already misses that target on CA included packets and extras. Remedies to test are better automation, bounded scope, fewer included packets, higher add-on price or separately priced human help—not unsupported “AI costs are near zero.”

## Measurement before cfo.ai import

Record one row per run: run ID, model/provider/version, input/output tokens, OCR pages, retries, cached work, infrastructure allocation method, currency/date/rate, cost source, successful/failed status, support minutes and case size. Report median and 90th percentile **cost per successfully delivered packet**, allocating failed-run costs across successes. Keep synthetic-evaluation cost separate from paid workload estimates. Record sponsor-covered actual cash cost AND undiscounted list-price cost. Free credits are temporary financing, not zero underlying cost.

## Acquisition, retention and runway

No ARPC, CAC, churn, LTV or cash balance is measured. CA list ARPC ₹4,999 is a package price, not observed blended ARPC. Keep transactional owner cohorts separate from recurring CA cohorts. A single recovered claim does not create a recurring customer.

Blended CAC=(sales+marketing cash spend+allocated loaded founder/staff time+tools+content+partner fees)/new paying customers. Track CA account CAC separately from one-off packet CAC. CAC payback=CA CAC/monthly CA contribution, when contribution is positive. A rough recurring LTV=monthly ARPC×gross-margin fraction/monthly account churn; do not compute an empirical LTV from a tiny new cohort or apply subscription churn to one-off buyers.

Illustrative 50 CA-firm milestone: MRR=50×4,999=₹249,950; annualized run-rate=₹2,999,400, **not booked annual revenue**. At 10 packets each, 500 packets/month need 83.3 support hours at 10 minutes each, or 250 hours at 30 minutes. One small team cannot assume the high-volume scenarios are operable.

Goal-based acquisition budget example: target 50 retained accounts, assumed ₹5,000 CAC and 80% annual retention gives(50×5,000) /0.8=₹312,500; add 15% experiment buffer=₹359,375. This is a sensitivity example, **not authorized spend** or an inferred funded budget. Model CAC ₹2,000–₹10,000 and retention 60%–90% before approval.

Runway requires starting cash and a dated monthly cash-flow model. Minimum cash to milestone=max cumulative cash deficit before milestone + desired reserve; each month include product payroll, legal review, security, fixed vendors, acquisition, support, payment timing and tax. Sponsor credit face value is not cash available to pay salaries. Cash balance, founder compensation, vendor plans and ramp timing are missing; therefore no defensible months-of-runway number can be supplied yet.

## Research protocol

1. Observe three to five permissioned CA/owner workflows for initial qualitative learning. Ask about the last actual disputed/unpaid invoice, evidence gathered, hours, existing adviser, current spend, who approves and how often cases recur. Avoid leading with a promised recovery.
2. Show a synthetic sample packet and ask the reviewer to check a source, identify an ambiguity and explain whether they could use the export. Record confusion and completion time.
3. Ask willingness at randomized initial prices (e.g. ₹999/₹1,999/₹2,999 packet; ₹2,999/₹4,999/₹7,999 CA) across separate prospects; do not repeatedly reduce price until one says yes. These are candidate research levels, not public offers.
4. Capture paid pilot acceptance, payment, completion, refund and repeat request separately. “Would pay” is not a sale. Target five paid pilot packets only after scope/legal/privacy review and user-authorized outreach.
5. Use the four Van Westendorp questions only when a materially larger qualified sample is available; three friendly calls cannot establish an optimal price. Feature ranking can test source links vs saved time vs client workspaces vs branding without fake statistical confidence.

Research log fields: date, pseudonymous segment, recent case frequency, preparation time, existing method, price shown, exact response, next action, consent, paid amount, refund and repeat usage. No interviews or outreach were performed for this draft.
