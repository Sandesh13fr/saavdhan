# Backend behavior

`backend.main:app` serves the API and a built `frontend/dist` from one origin.
This is a local document-preparation service. Reviewer names are audit entries,
not authenticated identities; public deployment requires authentication and
access isolation. SQLite and original evidence remain in `data/` locally.

## Calculation and review

The Decimal engine uses actual/365 daily accrual and calendar-month anniversary
rests anchored to the interest start. It does not round intermediate amounts.
Payment credits reduce principal at the start of their date. The as-of date is
inclusive. Payments are assumed principal-first; unpaid accrued interest
continues after principal settlement. This appropriation and rest convention
must be reviewed for real claims; the Act itself does not specify every numeric
implementation detail.

Acceptance requires delivery/acceptance proof. Timely written objections require
a resolution date. Written payment terms cap at45 days; without a written term,
the deadline is acceptance+15 days. Interest starts the following day. Registration
after contract/invoice raises legal review rather than a definitive exclusion.
Trading and medium-enterprise cases stop in this limited workflow.

TDS credits need a readable certificate/remittance source identifying the invoice,
section and explicit deduction amount. A98% bank receipt never proves TDS by
itself. Amount-only matches require reviewer confirmation. Conflicting linked
POs/deliveries, missing field provenance, unknown IDs, overpayment, rate gaps and
unallocated receipts block approval. Financial inputs are typed and money is
serialized as decimal strings.

## API

- `POST /api/cases` creates a JSON `CaseInput`; `POST /api/cases/demo` creates
  fictional source records and synthetic rates.
- `POST /api/cases/{id}/upload` accepts multipart `files`; CSV/XLSX support
  explicit `record_type` rows and ISO dates. PDF preserves page text; images
  visibly report that OCR is unavailable. TXT preserves chat lines as evidence.
  Optional configured model extraction makes quoted typed proposals, capped at
  three calls per upload; proposals require human source review.
- `POST /api/cases/{id}/run` runs deterministic checks. The optional rate-failure
  scenario is explicitly simulated; it performs no RBI network fetch.
- `PATCH /api/cases/{id}/review` accepts buyer/rate confirmations, explicit payment
  `resolutions`, `invoice_updates` with typed documented fields, and `source_reviews`.
  Unreadable evidence requires a readable `replacement_source_id` and reason.
  The original source remains indexed with its replacement link.
- `POST /api/cases/{id}/approve` requires every blocker resolved. A SHA256 input
  digest and revision bind approval to those inputs. Uploads, corrections and
  reruns invalidate approval. Export verifies the current input digest.
- `GET /api/cases/{id}/export` downloads the approved ZIP: full PDF/CSV interest
  schedule, worksheet, demand letter, reconciliation, evidence index, original
  evidence and audit. Synthetic rates retain `DEMO - NOT FOR FILING` markings.
  Current ODR portal field schema is not asserted as verified.

## Bounded agent

`POST /api/cases/{id}/agent/run` starts a persisted run; `/agent/resume` resumes;
`GET /api/cases/{id}/agent` returns its saved state. Each request executes at most
12 tools (default8), and the run caps at30 recorded steps. Each tool checkpoint
is persisted. Tools inventory evidence, optionally extract quoted records,
analyze the ledger, independently verify money conservation, ask for review,
wait for explicit human approval, and build an approved local packet.

Default planning is an openly labeled deterministic tool planner. Explicit
`allow_model_planning:true` uses a configured model to choose among only
server-eligible tools from aggregate counts and blocker codes. It cannot approve,
file, send or do financial arithmetic. Six model plans per run and three source
extractions per run are persisted caps. Provider failures trigger no automatic
paid retry. The planner falls back to deterministic selection on a rejected or
unavailable model response; reaching the planning cap pauses until the user
resumes with model planning disabled. The configured gateway's account budget
is separate from these call caps.

`simulate_tool_failure:true` plants a local reconciliation-tool failure. Resume
retries that local tool once from its saved checkpoint; a second failure stops.
Source extraction attempts persist before the paid call, preventing automatic
repetition after a process interruption. Concurrent financial edits during a
tool run fail the optimistic revision check instead of overwriting reviewer work.
Unchanged review waits do not loop or spend further calls.

## Evaluation

`python -m backend.evaluation` regenerates20 fictional cases and measured results
under `backend/evaluation_data/`. Matching/due dates are explicit fixture labels.
Interest truth uses an independent day-by-day Decimal oracle and is supported
by closed-form hand calculations in tests. It is not20 independently certified
legal ground-truth claims. Baseline deliberately ignores TDS and guesses duplicate
payments; it cannot be approved. Current fixed matching is20/20 versus14/20;
false short payments4→0 and planted ambiguities flagged0/2→2/2. This narrow set
does not measure production accuracy or OCR performance.
