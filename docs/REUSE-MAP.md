# Reuse map: Bakaya code imported into Saavdhan

Status: 2026-10-25, recon lane. Scope: `backend/*.py`, `frontend/src/App.tsx`, `tests/*.py`.
Decisions follow the plan: keep / adapt / replace / remove.

## Snapshot warning

- `backend/models.py` was rewritten in place at 23:06:19 by another edit. It now holds the Saavdhan
  schema (`Offer`, `FieldValue`, `RuleHit`, `Verdict`, `SafetyPlan`, `CheckIn`, `Report`). The Bakaya
  classes (`CaseInput`, `Invoice`, `Payment`, ...) are gone.
- The Bakaya modules that import those classes were not updated. `engine.py`, `main.py`, `agent.py`,
  `providers.py`, `ingest.py`, `exports.py`, `fixtures.py`, `evaluation.py` all fail at import.
- Current test result: `.\.venv\Scripts\python -m pytest tests -q` fails at collection (8 errors,
  0 tests run). Example: `ImportError: cannot import name 'CaseInput' from 'backend.models'`.
- This map describes the Bakaya versions read at session start (`models.py` was 192 lines then).

## 1. Decision summary

| File | Decision | Saavdhan target |
|---|---|---|
| `ingest.py` | keep (drop CSV/XLSX invoice row parsing) | `ingest.py`: PDF text, TXT, image OCR, SourceRef + sha256 |
| `storage.py` | keep | SQLite case store with revision CAS |
| `auth.py` | keep, scoped | only to gate the authority pattern-map view (see open Q1) |
| `main.py` | keep middleware and helpers; adapt routes | security headers, session guard, upload limits, `audit()` kept |
| `providers.py` | adapt | quote-validated extraction into new `Offer` schema |
| `models.py` | adapt (already partly replaced) | `Offer`, `RuleHit`, `Verdict`, `SafetyPlan`, `CheckIn`, `Report` |
| `exports.py` | adapt | `pdf_bytes`, `csv_bytes`, zip writer kept; family report packet |
| `agent.py` | adapt (shrink) | bounded pipeline: ingest -> extract -> validate -> rules -> verdict |
| `fixtures.py` | adapt | synthetic demo offers, labelled FICTIONAL |
| `main.py` routes | adapt | check/intake/report routes |
| `App.tsx` | adapt + replace | keep shell, api helper, evidence viewer; replace ledger/review UI |
| `engine.py` | replace -> `rules.py` + `verdict.py` | rules return `RuleHit`; verdict is pure Python |
| `evaluation.py` | remove | invoice interest oracle |
| `evaluation_data/` | remove | invoice results and cases |
| `telemetry.py` | keep (no-op shim) | call sites in agent/providers/main stay; rename `bakaya.*` attributes |
| invoice tests | remove or rewrite | see section 4 |

## 2. Function-level notes

### `engine.py` (replace)

| Symbol | Survives? | Notes |
|---|---|---|
| `ZERO`, `CENT` | no | Decimal constants; only if money rules need them |
| `RULES_SOURCE` | no | URL constant imported by `exports.py`; rules.py gets its own `rule_source_url` per rule |
| `CONVENTION` | no | Actual/365 text imported by `exports.py` |
| `money()` | maybe | Decimal quantize helper; keep a copy only if fee comparison needs it |
| `add_month()` | no | interest rest arithmetic |
| `due_dates()` | no | invoice acceptance/term logic |
| `interest_schedule()` | no | interest engine |
| `analyze()` | no | replace with `rules.evaluate(offer, ra_list) -> list[RuleHit]` and `verdict.decide(hits) -> Verdict`. Keep its fail-closed idea: missing evidence -> status `unknown`, never `clear` |

### `agent.py` (adapt)

| Symbol | Survives? | Notes |
|---|---|---|
| `LOCKS` | keep | per-case `asyncio.Lock` |
| `now()` | keep | timestamp helper |
| `new_agent()` | adapt | keep run_id, checkpoints, step budget; drop invoice flags (`ledger`, `reconciliation`, `packet`) |
| `select_tool()` | adapt | fixed order: ingest, extract (opt-in), validate, rules, verdict |
| `record_step()` | keep | writes audit + checkpoint |
| `choose_with_model()` | remove (recommended) | model choosing tools conflicts with a fixed pipeline; AGENTS rule 4 makes it a risk |
| `execute_tool()` | adapt | `inventory_evidence` -> ingest; `extract_source` keep; `analyze_ledger` -> rules+verdict; `verify_reconciliation` drop; `request_review`/`request_approval`/`build_local_packet` -> adapt to report review |
| `advance()` | keep | resume, one retry on local failure, CAS revision check, bounded steps |

Note: `execute_tool` imports `merge_records` and `apply_linked_facts` from `main` inside the function
(circular import). Move merge logic to a shared module before deleting Bakaya code.

### `providers.py` (adapt)

| Symbol | Survives? | Notes |
|---|---|---|
| `KINDS` | replace | map to `Offer` fields, not invoice record kinds |
| `SCHEMA` | adapt | JSON schema for `Offer` fields: name, value, quote |
| `provider_available()` | keep | env gate; rename `BAKAYA_ENABLE_LLM` -> `SAAVDHAN_` |
| `_normalize()` | keep | whitespace-normalized quote check |
| `validate_extraction()` | keep, adapt | quote-substring check, server-attached `source_ref`, typed validation. Replace the amount/TDS/term numeric checks with a fee-amount check |
| `extract_records()` | keep transport, rewrite prompt | 402/429 no automatic retry, 40k char cap, `response_format` strict JSON |
| `plan_next_tool()` | remove | goes with `choose_with_model()` |

### `storage.py` (keep)

| Symbol | Survives? | Notes |
|---|---|---|
| `TENANT` | keep or drop | ContextVar tenant; drop if single-tenant |
| `DATA_DIR` | keep | rename env `BAKAYA_DATA_DIR`; `bakaya.sqlite3` filename also changes |
| `ClosingConnection`, `connect()` | keep | closes sqlite on `with` exit; cases table; tenant migration can go with `TENANT` |
| `ConcurrentCaseUpdate` | keep | revision CAS |
| `TenantCapacityExceeded` | keep or drop | production caps (10 cases, 50 MiB) |
| `reserve_upload_bytes()` | adapt | upload budget; production-only |
| `save_case()` | keep | `BEGIN IMMEDIATE`, expected_revision check, audit cap |
| `get_case()`, `list_cases()` | keep | payload JSON per case |
| `upload_dir()` | keep | server-generated IDs only |

### `auth.py` (keep, scoped)

| Symbol | Survives? | Notes |
|---|---|---|
| `USER`, `SESSION_SECONDS` | keep | ContextVar and 8h session |
| `production()` | keep | env gate; rename `BAKAYA_ENV` |
| `database()` | keep | users, sessions, login_attempts tables |
| `password_hash()` | keep | scrypt, n=16384 |
| `provision()` | keep | CLI-created accounts only |
| `public_user()`, `session()` | keep | session digest lookup with expiry |
| `login()` | keep | per-email and per-IP throttling |
| `external_calls_allowed()` | keep | gate for paid LLM calls (admin-only in production) |
| `require_role()`, `reset_password()`, `__main__` | keep | role gate; password reset revokes sessions; operator CLI |

### `ingest.py` (keep, drop invoice parsing)

| Symbol | Survives? | Notes |
|---|---|---|
| `MAX_FILE_BYTES` | keep | 15 MB |
| `ALLOWED` | adapt | drop `.csv`, `.xlsx`; keep pdf, txt, png, jpg, jpeg, webp, tif, tiff |
| `tesseract_command()`, `ocr_available()`, `ocr_image()` | keep | opt-in via env; hard-coded Windows path fallback; 20M pixel cap, 30 s timeout |
| `parse_date()` | adapt | strict ISO; needed for the recruiter-list date (rule 3) |
| `parse_money()` | adapt | strict decimal for `fees_demanded_inr` |
| `row_record()` | remove | CSV/XLSX row typing (plan) |
| `ingest_bytes()` | adapt | keep PDF page split, image OCR, TXT lines, status flags. Remove csv/xlsx branch. Return contract `(sources, extracted, errors)` is used by `main.upload` |

### `main.py` (keep middleware, adapt routes)

| Symbol | Survives? | Notes |
|---|---|---|
| `lifespan()` | keep | env validation (rename prefix); HTTPS origin check in production |
| `TRUSTED_HOSTS` + `TrustedHostMiddleware` | keep | DNS rebinding defence |
| `session_guard()` | keep | origin check, CSRF, viewer read-only, `/api` auth gate. Needs an allowlist for public check routes (risk 4) |
| `security_headers()` | keep | CSP, nosniff, DENY frames, no-referrer, HSTS in production |
| `auth_me()`, `auth_login()`, `auth_logout()` | keep if auth kept | |
| `tenant_capacity_error()` | keep | 413 handler |
| `stamp()`, `audit()`, `require_case()` | keep | audit log; 404 helper |
| `invalidate()` | keep | revision bump + clears approval |
| `current_approval()` | keep | hash of input bound to revision |
| `run_analysis()` | replace | calls rules/verdict |
| `view()` | adapt | report view; keep `status`, `audit`, `revision` |
| `create()` | adapt | drop manual party-profile logic; keep user-statement source for intake |
| `health()` | keep | rename service and env keys; drop `external_submission` if not needed |
| `cases()`, `new_case()` | adapt | likely single-check flow instead of case list |
| `new_demo()` | adapt | synthetic offers; drop evaluation call |
| `evaluation()` | remove | |
| `get_case()` | keep | |
| `merge_records()` | keep, move | used by upload and agent; move to shared module |
| `apply_linked_facts()` | remove | PO/delivery linking |
| `upload()` | keep | limits: 30 files per request, 100 sources, 3 model calls |
| `run()` | remove | invoice mode and simulated rate failure |
| `review()` | adapt | keep reviewer confirmation; drop invoice_updates, resolutions, source_reviews |
| `approve()` | adapt | human confirmation before report download |
| `export()` | adapt | family report packet |
| `get_source()`, `download_source()` | keep | path traversal guarded by `Path(...).name` |
| `get_agent()`, `agent_run()`, `agent_resume()` | keep | routes |
| `advance_agent()` | keep | per-case lock, CAS, trace span |
| static frontend block | keep | `is_relative_to` guard; API 404 for `/api/` |

### `models.py` (adapt; already partly replaced)

| Bakaya class | Decision | Saavdhan equivalent (current file) |
|---|---|---|
| `Record` | keep pattern | `extra="forbid"`; `FieldValue` now carries `quote` and `source_ref` |
| `SourceRef` | keep | now `sha256`, `stored_name`, bounded text (`SAAVDHAN_ENV`) |
| `Supplier`, `Buyer`, `Invoice`, `PurchaseOrder`, `Delivery`, `Message`, `Allocation`, `Payment`, `RatePeriod` | remove | invoice domain |
| `CaseInput` | replace | `Offer` (intake) |
| `RunRequest`, `Resolution`, `InvoiceCorrection` | remove | invoice actions |
| `ReviewRequest` | adapt | reviewer confirmations only |
| `ApprovalRequest` | keep | |
| `AgentRequest` | keep | bounded `max_steps` pattern; drop planning flags |
| (new) `Offer`, `FieldValue`, `RuleHit`, `Verdict`, `Contact`, `SafetyPlan`, `CheckIn`, `Report`, `LIST_FIELDS`, `SCALAR_FIELDS` | new | already present |

### `exports.py` (adapt)

| Symbol | Survives? | Notes |
|---|---|---|
| `csv_bytes()` | keep | formula-injection guard (`=+-@`) |
| `pdf_bytes()` | keep | title says "Bakaya"; change default |
| `packet_zip()` | adapt | keep README (no-filing notice), evidence index, audit.json, approval.json, evidence copy. Remove demand letter, ODR sheet, interest PDF and CSVs. The letter text makes MSMED and tax claims; do not carry into the report |

### `fixtures.py` (adapt)

| Symbol | Survives? | Notes |
|---|---|---|
| `ref()` | keep | SourceRef factory |
| `sourced()` | adapt | uses `field_sources`; move to `FieldValue` |
| `demo_case()` | replace | synthetic offers, marked FICTIONAL |
| `evaluation_cases()` | remove | invoice scenarios |

### `evaluation.py` (remove)

| Symbol | Notes |
|---|---|
| `reference_interest()` | interest oracle; invoice only |
| `evaluate()` | invoice metrics; `main.new_demo` and `GET /api/evaluation` call it |
| `main()` | writes `evaluation_data/` |

### `telemetry.py` (keep)

| Symbol | Notes |
|---|---|
| `_Span`, `trace()`, `span()`, `record_usage()` | no-op. Keep; rename `bakaya.*` attribute keys |

### `frontend/src/App.tsx` (adapt + replace)

| Symbol | Decision | Notes |
|---|---|---|
| `api()`, `json()` | keep | CSRF header, 401 event, error detail parsing. Rename event `bakaya:session-expired` |
| `rupees()`, `date()`, `list()` | keep | INR format for fee amounts; date copy "Awaiting evidence" changes |
| `statusLabel` | replace | verdict labels |
| `needsReview()`, `sourceStatus()` | keep, edit | status list |
| `App()` | adapt | keep auth bootstrap, `perform()`, `openSource()`, nav/Dialog shell. Drop invoice state (`resolutions`, `invoiceEdits`, `sourceReviews`, `selectedInvoiceId`) |
| `loadDemo()` | adapt | synthetic demo |
| `selectCase()`, `uploadFiles()` | adapt | |
| `saveReview()`, `approve()`, `download()` | adapt | report download; file name `Bakaya-...` |
| `refs()`, `Badge`, `Empty` | keep | "View source" link; UI atoms |
| `invoiceLedger()`, `selectedRecordPanel()`, `reviewDecisions()`, `InvoiceCorrection()` | remove or replace | invoice UI |
| `activityTable()` | keep | audit log |
| `evidenceWorkspace()` | keep | source viewer; drop invoice/payment linking |
| `SourceReferences()` | keep | field-to-source list |
| `NewClaimModal()` | replace | Offer intake form. Keep Dialog and file input |
| `SignIn()` | keep only if auth kept | **remove the hard-coded demo login** (risk 2) |

File input `accept` lists `.csv,.xlsx` in two places; drop both.

## 3. Invoice-concept dependencies that break when `engine.py` is deleted

| Location | Dependency | Break point |
|---|---|---|
| `exports.py:15` | `from .engine import CONVENTION, RULES_SOURCE` | breaks on delete |
| `main.py:19` | `from .engine import analyze` | breaks on delete |
| `agent.py:20` | `from .engine import analyze` | breaks on delete |
| `evaluation.py:10` | `from .engine import analyze, money` | removed with evaluation.py |
| `fixtures.py:5` | imports Invoice, Payment, Supplier, Buyer, RatePeriod, Allocation | already broken by models.py rewrite |
| `ingest.py:18` | imports Invoice, Payment, SourceRef, Supplier, Buyer, RatePeriod, Message, PurchaseOrder, Delivery, Allocation | already broken |
| `providers.py:19`, `KINDS` | Buyer, Delivery, Invoice, Message, Payment, PurchaseOrder, Supplier | already broken |
| `main.py:23`, `agent.py:22` | `CaseInput`, `RunRequest`, `ReviewRequest`, `AgentRequest` | `CaseInput` already gone |
| `main.py:create()/view()` | `case.supplier`, `case.sources`, `state["input"]["invoices"]`, `state["analysis"]` | state schema changes with new models |
| `main.py:merge_records()` | `supplier`, `buyer`, `bank_total` keys | must move before agent imports it |
| `storage.py` | state keys `input`, `analysis`, `review`, `approval`, `agent` | generic JSON; keep the CAS on `revision` |
| `scripts/backup.py` | none (stdlib + cryptography only) | safe; test expects `bakaya.sqlite3` literal |
| `frontend/App.tsx` | response keys `invoices`, `payments`, `matches`, `schedule`, `totals`, `blockers`, `rules` | UI must follow the new view shape |
| `pyproject`/`requirements.txt` | `openpyxl` only used by XLSX path | can drop after XLSX removal; `reportlab`, `pypdf`, `Pillow`, `pypdfium2` still used |

## 4. Test map

| Test file | Decision | Notes |
|---|---|---|
| `conftest.py` | keep | rename `BAKAYA_ENABLE_LLM` and key env vars |
| `test_auth.py` | keep | session, CSRF, expiry, throttling, reset, cookie, headers, capacity, env fail-closed. Rewrite the review payload fixtures (lines ~41, `INV-004`) and `kind='invoice'` |
| `test_ingest.py` | partial | keep `test_searchable_pdf_preserves_page_text_pending_review`, `test_image_flags_missing_ocr_never_invents_date`, `test_whatsapp_text_preserves_line_provenance` (rename to user-uploaded text export). Remove `test_csv_typed_records_have_line_provenance`, `test_xlsx_payment_extracts_without_date_guessing`. Keep the idea of `test_ambiguous_date_is_parse_error_not_guess` for the Offer date parser |
| `test_ocr.py` | keep | all four tests survive. Rewrite `synthetic_scan()` text (it says "INVOICE") and the `"10000"` / `"TEST-123"` assertions |
| `test_provider.py` | partial | keep: `test_disabled_provider_never_calls_network`, `test_gateway_configuration_and_quoted_response`, `test_gateway_budget_failure_is_not_retried`, `test_fabricated_quote_rejected`, `test_server_attaches_provenance`, `test_injected_approval_field_rejected`. Rewrite: `test_incomplete_invoice_rejected`, `test_amount_cannot_disagree_with_quote` (fee amount). Remove: `test_model_planner_enforces_server_tool_allowlist` (parametrized) |
| `test_backup.py` | keep | `scripts/backup.py` has no backend import. Rename `bakaya.sqlite3` literals in the test and backup manifest |
| `test_engine.py` | remove | all 20+ tests are interest, due-date, TDS, allocation. Replace with rules tests: each rule needs a positive and a negative test with a cited source URL or a `heuristic` label (AGENTS) |
| `test_agent.py` | rewrite | keep the bounded-run tests: `test_step_budget_resumes_at_checkpoint`, `test_failed_local_tool_recovers_once_from_saved_checkpoint`, `test_optimistic_checkpoint_rejects_concurrent_financial_edit`, `test_agent_rejects_unbounded_step_request`, `test_paid_extraction_failure_has_no_automatic_retry`, `test_agent_blocks_paid_extraction_when_not_opted_in`. Remove the TDS/approval packet tests |
| `test_agent_planner.py` | remove | goes with model planning |
| `test_api.py` | rewrite | keep: `test_source_download_and_traversal_are_safe`, `test_dns_rebinding_host_and_opaque_origin_rejected`, `test_bad_money_validation_and_cross_origin_mutation` (fee field), `test_export_approval_hash_catches_input_changed_without_revision` (concept). Remove invoice correction, allocation, rate-failure and supersession tests |

Coverage gap: no test yet for `rules.py` / `verdict.py` (new), or for the Offer schema. Both are needed before the replacement lands.

## 5. Risks

1. **Repo does not import right now.** `models.py` was rewritten mid-session and the Bakaya modules were not moved with it. Pytest collection fails. Assign one owner for the cut-over and do not merge partial states.
2. **Hard-coded demo login in `App.tsx` `SignIn()`.** A password literal is shipped in the frontend bundle for two Vercel hostnames. That breaks AGENTS rule 6 and the no-secrets rule. Remove it. If it was live, rotate it. The value is not repeated here.
3. **Circular import and hidden coupling.** `agent.py` imports `main.merge_records` and `main.apply_linked_facts` inside `execute_tool`. Move these to a shared module first, or the agent breaks when `main.py` is reworked.
4. **Auth gate on all `/api/*` in production.** `session_guard` returns 401 for every `/api/` path except three. A public check route will either fail or lead someone to weaken the gate. Add an explicit allowlist and tests for it.
5. **Extraction is only quote-checked.** `validate_extraction` proves the quote is in the source, not that the field means what the model says. Rules must treat extracted values as unverified, and the "models never set verdicts" rule (AGENTS 4) holds only by convention until the planner is removed.
6. **Legal and tax text in the packet.** `exports.py` letter cites MSMED and Income-tax sections and asserts a claim. Do not carry it over; it conflicts with AGENTS rules 2 and 7 (verifiable facts only).
7. **Naming drift.** `BAKAYA_` env vars (storage, ingest, auth, main, providers), `bakaya.sqlite3`, `bakaya:session-expired`, `Bakaya-*.zip`, `bakaya.case`, and telemetry keys still use the old name. AGENTS requires `SAAVDHAN_`. Decide on a migration path for existing local data.
8. **Chat-export handling.** The TXT path labels a pasted chat export as `message_export` evidence. Keep it as a user upload only, with no connectors or scraping (AGENTS 7).

## 6. Open questions

- Q1. Does Saavdhan need login at all? The plan keeps `auth.py` "only for the authority pattern-map view". If the checker is public, `auth.py` and `SignIn()` can go, and risk 4 mostly disappears.
- Q2. Keep `TENANT` and the upload budget, or go single-user? The current code is multi-tenant by design.
- Q3. Is the Bakaya SQLite file to be migrated, or a fresh Saavdhan DB with the new name?
- Q4. Should `ALLOWED` keep image OCR at all, given the OCR path is opt-in and depends on a Windows-only fallback path?
- Q5. Is a model planner wanted at all? Recommendation: remove.
