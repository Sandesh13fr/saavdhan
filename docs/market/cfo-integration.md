# cfo.ai model — 11 October 2026

[Open the anonymous read-only judge model](https://app.cfo.ai/s/D9U0WKRrog83poBC) · [Owner page](https://app.cfo.ai/s/p_AQGWpgYkOTYzMzUxMTgtNWY4OC00ZGEzLTlkMDEtYjExYjZiMDI4ZDRmDWRlZmF1bHRfbGF5ZXI)

## Saved model and verified outputs

The cfo page contains editable unit economics, a monthly revenue/burn/runway table and clear basis disclosures. Its actual spreadsheet export downloaded successfully earlier; two sheets and expected contribution values were checked. That earlier export predates the updated owner cash/cost inputs below and must be regenerated for current values.

The owner supplied **INR30,000 opening cash and INR20,000 monthly fixed costs**. These are owner-provided inputs, not independently validated records; no cost breakdown is asserted. They replace the earlier illustrative cash/cost inputs. Pricing, refund/fee rates, delivery costs and demand remain unvalidated planning assumptions.

| Scenario | Monthly demand | Gross revenue INR | Contribution base/stress INR | Stress burn INR | Conditional runway months |
| --- | --- | ---: | ---: | ---: | ---: |
| Main | Zero-demand placeholder, not observed zero sales | 0 | 0 / 0 | 20,000 | 1.5 |
| Illustrative Demand — Not Actuals | Invented 10 self-serve packets, 2 ten-packet bundles, 5 extras | 31,983 | 25,833.85 / 9,383.85 | 10,616.15 | 2.825883 |

The illustrative scenario inherits owner-provided cash/costs from Main; its demand remains separate. Base contribution exceeds fixed costs by INR5,833.85; base burn is zero, so no finite base runway is asserted. Runway is a static opening-cash/positive-burn sensitivity, not a cash-flow forecast or an observed business survival period. Past displayed months are also modeled placeholders, not historical actuals. No FX assumption is used.

Per-packet base/stress contribution remains INR1,769.05/1,299.05 for self-serve, INR344.905/−125.095 for a fully used monthly bundle and INR249.05/−220.95 for extras. High delivery costs make bundle/extra packets loss-making before fixed costs. Net receipts = gross price × (1 − refund rate − payment fee rate); contribution = net receipts − delivery cost.

Changelog 280107–280110 records the owner cash/cost updates, removal of superseded scenario rules and revised disclosures. Both scenarios were independently read back: ten rows × 24 months, 240 populated cells, complete calculation/delivery coverage and zero formula errors. Main returns cash 30,000/costs 20,000/runway 1.5; the shared illustrative scenario returns the same inputs and runway 2.8258832062470853. Floating-point display differences are immaterial at currency rounding.

## Guest access

The owner-authorized cfo share receipt confirms anonymous identity access, READ permission, one linked Bakaya page in the illustrative scenario and no expiry. Anonymous HTTP returns 200 without a login redirect; rendered guest values still require a browser check. The share points to the live illustrative scenario, not a snapshot, so the updated saved values are included. Deactivating the link stops new follows; removal of already-granted access is a separate operation according to cfo. No other workspace pages were shared.

## Boundaries

No bank connection, purchase, billing change, notification or private claim-document transfer was performed. The financial model is founder planning, separate from claim eligibility/approval/export. The local workbook remains a separate planning artifact, not a cfo export.

One observed claude-haiku planning call used 358 prompt + 72 completion tokens and provider-reported USD0.0007898. This is one call, not a whole packet cost. The shared allowance is USD15/key/30 days; remaining balance is unknown. Owner demand measurements and professional/customer validation remain pending.

## Public fallback snapshot

[Download the current cfo readback CSV](../evidence/cfo-runway.csv). This sanitized snapshot contains the exact saved MCP values for Main and the illustrative scenario, including owner cash/cost inputs and conditional runway. It is an MCP calculated-readback snapshot, **not a native cfo Excel export**. Revenue/burn arithmetic and both runway ratios have independent self-checks. Once pushed to public GitHub, this file is accessible without a cfo account. The earlier native spreadsheet download is stale relative to these inputs; refreshing it timed out, so no fresh native export is claimed.
