# Rules

Source of truth: `backend/rules.py` (ids, severities, sources, constants) and `backend/verdict.py` (verdict logic). The English copy for each rule is in `frontend/src/i18n/en.json`.

## Status semantics

Every rule returns one status:

- **hit**: the offer shows the point Saavdhan checks. Shown as "Point to check".
- **clear**: the offer shows the opposite. Shown as "Nothing found".
- **unknown**: the offer does not say, or the fact needed to decide is missing. Shown as "Not stated". Unknown is never treated as clear.

Not mentioned counts as a hit for R3, R7, R8 and R9 (for example, no RC number or no receipt promise). R8 is clear when no fee is asked.

## The 12 rules

Links are the constants in `rules.py`: the MEA overseas-employment page (https://www.mea.gov.in/overseas-employment.htm) and eMigrate (https://emigrate.gov.in). The specific passage for each rule is not yet pinned in the repository (see open items).

| ID | Severity | Check (plain English) | Hit | Clear | Unknown | Source |
|---|---|---|---|---|---|---|
| R1_TOURIST_VISA | critical | Is the visa a tourist or visit visa? Work needs a work/employment visa. | visa is tourist or visit | visa is employment or work | visa not stated | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R2_RA_NOT_LISTED | high (critical if the agent is on an unregistered list) | Is the named agent on MEA's active recruiting agent list? | agent not on the list, or on an unregistered list | agent on the list | no agent named, or list not consulted | [eMigrate](https://emigrate.gov.in) |
| R3_NO_RC_NUMBER | high | Does the offer show an agent RC number? | no RC number | RC number present | not applicable: missing RC counts as hit | [eMigrate](https://emigrate.gov.in) |
| R4_FEE_OVER_CAP | high | Is the fee demanded above the MEA cap, Rs 30,000 + 18% GST (Rs 35,400)? | fee above the cap | fee within the cap | no fee amount stated | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R5_NO_TRIPARTITE_CONTRACT | high | Does the offer say the employer, the agent and the worker all sign one contract? | no contract mentioned, or a signatory is missing | all three named as signatories and a contract mentioned | no role, employer or destination at all | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R6_HIGH_RISK_CORRIDOR | critical | Does the route (Thailand, Myanmar, Cambodia, Laos) combine with a high-risk role (data entry, IT, customer support, digital or online marketing, chat support, call centre, typing)? | destination or transit is a listed country and the role matches a listed role | no listed country, or listed country but role does not match | no role stated, or no destination | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R7_INFORMAL_CHANNEL_ONLY | medium | Is the agent reachable only through chat apps (WhatsApp, Telegram, Instagram, Facebook)? | only informal channels listed | an office address, email, website or other channel listed | no channel stated | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R8_NO_RECEIPT | medium | If a fee is asked, is a receipt promised? | fee asked and no receipt promised | receipt promised, or no fee asked | not applicable (no unknown state) | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| R9_PBBY_MISSING | info | Is PBBY (Pravasi Bharatiya Bima Yojana) insurance mentioned? Information only. | not mentioned | mentioned | not applicable | [MEA](https://www.mea.gov.in/overseas-employment.htm) |
| H1_SALARY_ANOMALY | medium (heuristic) | Is the monthly salary, converted with approximate exchange rates, more than twice a rough reference for the role? | above 2 times the reference | within range | no salary stated | Heuristic |
| H2_PASSPORT_HANDOVER | high (heuristic) | Does the offer ask you to hand over or keep your passport? | yes | the offer says no | not stated | Heuristic |
| H3_PRESSURE | low (heuristic) | Does the offer use urgency language ("only 2 seats left", "confirm today")? | urgency phrase present | no urgency phrase | not applicable | Heuristic |

Heuristic rules (H1 to H3) carry `heuristic: true`. The app labels them "Warning sign, not a rule".

## Verdict logic

From `backend/verdict.py`:

1. Any **critical** hit gives `STOP`.
2. Otherwise, any **high** hit, or three or more unknowns on the key rules (R1, R2, R5), gives `VERIFY_FIRST`.
3. Otherwise, if the recruiter-list date is not a valid date (for example, the list is not loaded), gives `VERIFY_FIRST`.
4. Otherwise, `NO_RED_FLAGS_FOUND`.

Medium, low and info hits are shown but do not change the level. Heuristic hits follow their listed severity.

Best-verdict text (en): "No red flags found. Confirm with the Protector of Emigrants before paying anything." The app never gives an all-clear beyond this text.

## Fee cap caveat

`FEE_CAP_INR = 30000 * 1.18` (Rs 35,400) in `rules.py` is the MEA figure as reported in advisories. **Verify the current official figure before release.** Two places must change together: the constant and the copy in `en.json`, `hi.json` and `mr.json`, which currently hard-codes "Rs 30,000 + 18% GST". The fee is compared with the total including GST as stated in the offer.

## Configurable lists

Lists and constants that can be tuned, all in `backend/rules.py` unless stated:

- `HIGH_RISK_COUNTRIES`: thailand, myanmar, cambodia, laos.
- `HIGH_RISK_ROLES`: data entry, customer support, customer service, IT, digital marketing, online marketing, chat support, call centre, call center, typing.
- `INFORMAL_CHANNELS`: whatsapp, telegram, instagram, facebook.
- `APPROX_FX_TO_INR`: approximate exchange rates for H1 only. Not a rate source.
- `SALARY_REFERENCE_INR` and `SALARY_ANOMALY_FACTOR`: rough references for H1, to be tuned with data.
- `FEE_CAP_INR`: see the fee cap caveat.
- `KEY_UNKNOWN_RULES` in `backend/verdict.py`: rules whose unknowns count toward `VERIFY_FIRST`.
- Country and role extraction vocabularies: `backend/extract_fallback.py`.

## Known limitations

- R2 needs the MEA recruiter list, which is not loaded in this build. Without it R2 is unknown and the verdict cannot be `NO_RED_FLAGS_FOUND`.
- R6 stays unknown when no role is extracted, so a high-risk corridor alone cannot give `STOP`. In the evaluation this caused 10 of 13 verdict misses (see [eval/REPORT.md](../eval/REPORT.md)). Whether that is correct is a product decision still open.
- The fallback extractor was tuned on the 40 synthetic offers used to score it.

## Open items

- Pin the exact MEA passage for each rule and add it to the rule source.
- Each rule needs a positive and a negative test and a cited source, or the `heuristic` label (AGENTS rule). Confirm coverage in `tests/test_rules.py`.
