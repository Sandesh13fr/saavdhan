# Phase 2 contracts (lead-owned)

Lanes code against these. Changing one needs the lead.

## Offer field values (LLM and fallback extractor must emit the same)

Every `FieldValue` has `value` (string or null), `quote` (verbatim source text), `source_ref`
(set by server), `confidence` (`llm` | `fallback`; never read by rules).

| Field | Normalised `value` |
|---|---|
| visa_type | `employment` `work` `tourist` `visit` `unknown` |
| destination_country, transit_countries[] | English country name: `Thailand`, `Myanmar`, `Cambodia`, `Laos`, `United Arab Emirates`, `Saudi Arabia`, ... |
| role_title | lower-case role as stated, e.g. `data entry`, `customer support`, `electrician` |
| fees_demanded_inr | integer rupees, digits only: `250000` (from "2.5 lakh", "Rs 2,50,000", "अडीच लाख", "२.५ लाख") |
| salary_amount | number, digits and optional `.`: `120000`; `salary_currency` ISO code `INR` `AED` `THB` `USD` `SAR` ... |
| fee_payment_mode | `upi` `cash` `bank_transfer` `card` `crypto` `other` |
| receipt_promised, contract_mentioned, pbby_insurance_mentioned, passport_handover_requested | `yes` or `no` (null = not mentioned) |
| contract_signatories[] | `employer` `agent` `worker` |
| agent_channels[] | `whatsapp` `telegram` `instagram` `facebook` `email` `website` `phone` `office_address` |
| agent_phones[] | digits with leading `+` country code when given: `+919000000001` |
| agent_rc_number | as written, trimmed |
| urgency_language[] | the urgency phrase itself |

## RA lookup result (`ra_match` argument of `rules.run_rules`)

`None` = list not consulted. Otherwise
`{"status": "listed" | "not_listed" | "unregistered_list" | "unknown", "list_date": "YYYY-MM-DD", "evidence": "<row or reason>"}`.

## Rule semantics (rules.py)

- `explanation_key` = `rule.<RULE_ID>.<status>`; `next_steps_key` = `next.<LEVEL>`.
- R1: tourist/visit -> hit; employment/work -> clear; absent/unknown -> unknown.
- R2: needs agent name or RC and `ra_match`; `unregistered_list` -> hit with severity critical; `not_listed` -> hit;
  `listed` -> clear; else unknown.
- R3, R7, R8, R9: "not mentioned" counts as hit (R8 only when a fee is demanded; otherwise clear).
- R5: hit when no contract is mentioned or signatories lack any of employer/agent/worker; clear when all three;
  unknown only when the offer has no role, employer and destination at all.
- Heuristics (H1–H3) carry `heuristic: true`.
- Verdict (verdict.py, done): any critical hit -> STOP; else any high hit or 3+ unknowns on R1/R2/R5 -> VERIFY_FIRST;
  else NO_RED_FLAGS_FOUND.

## API (backend/main.py)

Case view (`GET /api/offers/{id}` and every mutation):
```
{id, created_at, demo, revision, sources[], audit[],
 analysis: null | {offer, verdict: {level, rule_hits[], ra_list_date, next_steps_key}, extraction_method: "llm"|"fallback", errors[]},
 safety: null | {plan: SafetyPlan, checkins: [{at, note}], status: "ok"|"due"|"missed", next_due, now,
                 alerts: [{to_alias, channel, at, message_key: "family.alert_body", simulated: true}]}}
```
- `POST /api/offers` multipart: `files` (0–10) and/or `text` -> view
- `POST /api/demo/offers/{bangkok-data-entry|dubai-near-miss}` -> view (synthetic)
- `POST /api/offers/{id}/analyze` -> view
- `GET /api/offers/{id}/packet` -> ZIP
- `POST /api/offers/{id}/safety-plan` JSON SafetyPlan (`traveller_alias`, `contacts[1..2]{alias,channel}`, `itinerary[]`, `checkin_interval_hours`) -> view
- `POST /api/offers/{id}/checkin` JSON `{note}` -> view
- `POST /api/demo/advance-clock` JSON `{case_id, hours}` -> view (demo only; moves the case's simulated clock)
- `GET /api/reports/map` (login) -> `MapData` (`frontend/src/features/map/types.ts`)
- `GET /api/meta` -> `{app, version, ra_list_date, fee_cap_inr, rules[{id,severity,source,heuristic}]}`
- Auth: `POST /api/auth/login {email,password}` -> `{csrf_token,...}`; send `X-CSRF-Token` on mutations when signed in.

## i18n keys

Files: `frontend/src/i18n/{en,hi,mr}.json`, flat keys, `{name}` placeholders. Missing key -> English -> key.

```
app.name app.tagline app.synthetic_badge lang.en lang.hi lang.mr
nav.check nav.verdict nav.safety nav.family nav.map nav.limits
check.title check.intro check.paste_label check.paste_placeholder check.upload_label check.submit
check.demo_title check.demo_scam check.demo_near_miss check.privacy_note check.analyzing
verdict.title verdict.STOP.title verdict.STOP.body verdict.VERIFY_FIRST.title verdict.VERIFY_FIRST.body
verdict.NO_RED_FLAGS_FOUND.title verdict.NO_RED_FLAGS_FOUND.body verdict.ra_list_date({date})
verdict.quote_label verdict.source_label verdict.rule_source verdict.heuristic_badge
verdict.status.hit verdict.status.clear verdict.status.unknown verdict.method.llm verdict.method.fallback
verdict.download_packet verdict.make_safety_plan verdict.facts_title verdict.not_found
severity.critical severity.high severity.medium severity.low severity.info
rule.<ID>.title rule.<ID>.hit rule.<ID>.clear rule.<ID>.unknown   (for all 12 rule ids)
next.STOP next.VERIFY_FIRST next.NO_RED_FLAGS_FOUND
safety.title safety.intro safety.traveller_alias safety.contact_alias safety.contact_channel safety.add_contact
safety.itinerary safety.itinerary_placeholder safety.interval_hours safety.save safety.checkin safety.checkin_note
safety.status.ok safety.status.due safety.status.missed safety.next_due({time}) safety.last_checkin({time})
safety.demo_advance safety.simulated_note
family.title family.alert_title family.alert_body({alias}) family.open_packet family.no_alerts family.simulated_badge
map.title map.login_required map.email map.password map.sign_in map.sign_out map.synthetic_badge
map.repeated_agents map.repeated_templates map.districts map.reports
limits.title limits.what_it_does limits.what_it_does_not limits.not_legal_advice limits.no_auto_report
limits.sources_title limits.helplines_title limits.verify_contacts
error.generic error.network common.loading common.back common.close
```
`verdict.NO_RED_FLAGS_FOUND.body` (en) is exactly: "No red flags found. Confirm with the Protector of Emigrants before paying anything."
No string may say "safe" or an equivalent (सुरक्षित, सुरक्षीत, "no risk", "guaranteed").
Never call a named person or agency a fraud; state facts ("not found on MEA's active recruiting agent list dated {date}").
