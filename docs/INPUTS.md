# Preparing input records

The local parser reads structured CSV/XLSX rows. Each row must have `record_type`; dates must be `YYYY-MM-DD`, and money must use plain decimal numbers. Blank columns are ignored. The first sheet of an XLSX file uses the same column names. Preserve actual source records alongside these reviewed transcriptions.

Files in `samples/` form a small, fictional, complete input set. Create a new claim with any fictional party profile, upload all five sample CSV files, and review the results. They overwrite the manually entered supplier/buyer profile with the sourced sample rows. Sample rates are synthetic and must never be used for a real claim.

| Record type | Required columns | Additional supported columns |
|---|---|---|
| supplier | name, category, activity, udyam_number, udyam_date | address |
| buyer | name | address |
| invoice | id, number, date, amount | buyer, contract_date, delivery_date, acceptance_date, written_term_days, objection_date, objection_resolved_date |
| payment | id, date, amount | reference, invoice_ids (separate IDs with `|`), tds_amount, tds_section, tds_evidence_source |
| purchase_order | id, number, invoice_id, date | written_term_days |
| delivery | id, invoice_id, date | accepted (true/false) |
| bank_control | amount | Total relevant buyer receipts, including future-dated rows if included in the uploaded statement |
| rate | start, end, bank_rate, source | synthetic (true/false), fetched_at |

Rate `end` is exclusive. Bank Rate is a percentage, so use `6.50` rather than `0.065`. These are review inputs, not automatically fetched RBI history. Provide complete, non-overlapping periods covering the claim. `written_term_days` is blank when there is no written agreement.

Invoice IDs must match across payments, purchase orders and delivery records. Duplicate identifiers fail validation. Contradictory contract/terms/delivery facts block approval. Matching by amount alone needs confirmation, and a payment covering several invoices requires explicit evidence-backed allocations (the current browser form supports one invoice per ambiguous receipt; complex allocations can be entered through the documented API).

## PDFs, text exports and scans

Text-searchable PDFs are read page by page; `.txt` messages are retained with line references. Without the optional model adapter, these are supporting evidence rather than automatic typed invoice extraction. Images and image-only PDFs are marked as needing OCR/readable alternatives. To replace an unreadable source, upload readable evidence and record the replacement and reason in the review screen. The original remains in the audit/evidence record as superseded.

With `BAKAYA_ENABLE_LLM=true` and `OPENAI_API_KEY`, PDF/text extraction can propose typed facts. The adapter checks source quotes and record types, and the source remains pending human review. This path is implemented and locally validated but has not made a paid live call. Source quoting alone does not prove correct interpretation.

## Deductions and limitations

TDS requires an explicit certificate/remittance document, its source ID, a documented section and matching amounts. A two-percent difference alone is not sufficient. Source IDs are visible in the evidence drawer; the review API can classify reviewed documents as `tds_certificate` or `remittance_note`. Complex TDS/partial-payment preparation may require typed API input; do not guess or weaken the evidence gate to force approval.

The exact current ODR portal form has not been verified. The exported field sheet is a generic preparation worksheet, not a certified portal upload format. Review registration, acceptance, appropriations and interest conventions professionally before real use.
