# Saavdhan fallback extraction evaluation

> **Synthetic evaluation set of 40 offers written for this project. Not real-world accuracy. The fallback extractor was tuned on this same set after the first run (27/40), so these scores are optimistic; a held-out set is needed for an honest estimate.**

- Date: 2026-10-26
- Git commit: `5510a06`
- Extractor mode: `fallback`
- Offers: 40; LLM fallbacks on ValueError: 0

## Headline

- Verdict accuracy: 1.000
- Macro rule F1: 0.948
- Field accuracy: 0.880
- Median analysis time: 2.58 ms (p95 3.67 ms)

## Verdict confusion matrix (rows expected, columns predicted)

| expected \ predicted | STOP | VERIFY_FIRST | NO_RED_FLAGS_FOUND |
|---|---|---|---|
| STOP | 20 | 0 | 0 |
| VERIFY_FIRST | 0 | 5 | 0 |
| NO_RED_FLAGS_FOUND | 0 | 0 | 15 |

## Per-rule precision, recall and F1

| rule | TP | FP | FN | TN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|
| R1_TOURIST_VISA | 7 | 0 | 0 | 33 | 1.000 | 1.000 | 1.000 |
| R2_RA_NOT_LISTED | 9 | 0 | 5 | 26 | 1.000 | 0.643 | 0.783 |
| R3_NO_RC_NUMBER | 14 | 0 | 0 | 26 | 1.000 | 1.000 | 1.000 |
| R4_FEE_OVER_CAP | 15 | 0 | 0 | 25 | 1.000 | 1.000 | 1.000 |
| R5_NO_TRIPARTITE_CONTRACT | 14 | 0 | 0 | 26 | 1.000 | 1.000 | 1.000 |
| R6_HIGH_RISK_CORRIDOR | 19 | 0 | 1 | 20 | 1.000 | 0.950 | 0.974 |
| R7_INFORMAL_CHANNEL_ONLY | 11 | 0 | 0 | 29 | 1.000 | 1.000 | 1.000 |
| R8_NO_RECEIPT | 10 | 0 | 0 | 30 | 1.000 | 1.000 | 1.000 |
| R9_PBBY_MISSING | 13 | 0 | 1 | 26 | 1.000 | 0.929 | 0.963 |
| H1_SALARY_ANOMALY | 5 | 0 | 0 | 35 | 1.000 | 1.000 | 1.000 |
| H2_PASSPORT_HANDOVER | 4 | 0 | 2 | 34 | 1.000 | 0.667 | 0.800 |
| H3_PRESSURE | 6 | 0 | 2 | 32 | 1.000 | 0.750 | 0.857 |

Macro F1 (rules with any truth or prediction): 0.948

## Extraction field accuracy

| field | correct | total | accuracy |
|---|---|---|---|
| agent_rc_number | 40 | 40 | 1.000 |
| destination_country | 34 | 40 | 0.850 |
| fees_demanded_inr | 39 | 40 | 0.975 |
| role_title | 23 | 40 | 0.575 |
| visa_type | 40 | 40 | 1.000 |
| **overall** | 176 | 200 | 0.880 |

| language | correct | total | accuracy |
|---|---|---|---|
| en | 46 | 50 | 0.920 |
| hi | 53 | 60 | 0.883 |
| hinglish | 43 | 50 | 0.860 |
| mr | 34 | 40 | 0.850 |

## Analysis time

- Median: 2.58 ms
- p95: 3.67 ms

Time covers extraction, rules and verdict; ingest is excluded.

## Misclassified offers

None.

## Definitions

- A rule prediction is a hit when its status is `hit`; ground truth is membership in `expected.rule_hits`.
- F1 = 2TP / (2TP + FP + FN); undefined (excluded from macro) when there is no truth and no prediction.
- Field match: casefold and strip; numeric fields compare as numbers; expected null requires a null prediction.

## Likely causes

Judgement per wrong verdict (13 of 40). No eval label was found to be wrong; every miss below is a code-side gap in the fallback extractor, except the one rule-semantics note at the end. Backend code and eval/offers were not edited.

| id | lang | expected to predicted | field / rule | judgement | snippet |
|---|---|---|---|---|---|
| 004 | en | STOP to VERIFY_FIRST | R6 unknown; role_title None (expected `IT`) | extractor gap: ROLES has no IT / high-risk role vocabulary | "Laos IT role for Example Cloud Employer" |
| 005 | en | STOP to VERIFY_FIRST | R2 false hit: agent_name = `Recruitment`; R6 unknown (role None); R7 clear (should be hit) | extractor gap x3: AGENT_NAME matches the bare word "Recruitment"; `office_address` channel from a negated mention; no chat-role match | "Recruitment is only on Telegram and WhatsApp, no office address" / "Thailand chat support vacancy" |
| 008 | hi-mix | STOP to VERIFY_FIRST | R6 clear (role `technician`, expected `IT`) | extractor gap: role keeps the trailing noun and drops the IT modifier | "IT technician ka role" |
| 010 | hinglish | STOP to VERIFY_FIRST | R4 clear (fee 30001, expected 35401); R6 unknown (role None) | extractor gap: takes the first amount (pre-GST) not the stated total; no "chat support" role in Cambodia clause | "rounded payable total Rs 35,401" |
| 012 | hi | STOP to VERIFY_FIRST | R6 unknown (role None); R5 false hit; R8 false hit | extractor gap: "ग्राहक सहायता" not in ROLES; negation is applied to the whole letter, so the later "नहीं" flips contract_mentioned and receipt_promised to "no" | "बीमा का विवरण नहीं दिया गया है" |
| 013 | hi | STOP to VERIFY_FIRST | R6 unknown (role None); R7 clear (should be hit); R4 fee 400000 (expected 450000) | extractor gap x3: "आईटी" not a role; bare "कार्यालय" counted as office_address despite "नहीं"; "साढ़े चार लाख" not parsed | "संपर्क केवल Telegram; कार्यालय नहीं" |
| 014 | hi | STOP to VERIFY_FIRST | R6 unknown (role None); R7 clear (should be hit) | extractor gap: "डिजिटल मार्केटिंग" not a known role; same negated-office bug | "बातचीत केवल WhatsApp पर है, कार्यालय नहीं" |
| 015 | hi | STOP to VERIFY_FIRST | R2 unknown and R3 false hit (RC None); R6 clear; role_title captures a whole clause | extractor gap: RC_LABEL has लायसेंस but not लाइसेंस, so the licence number is dropped; role span runs to the next sentence | "लाइसेंस DEMO-RA-015" / "आईटी तकनीशियन। रोजगार वीज़ा" |
| 018 | mr | STOP to VERIFY_FIRST | R6 unknown (role None, expected "online marketing"); R5, R8, R9 false hits | extractor gap: Marathi role missing; a negation elsewhere in the letter ("नाही") flips contract, receipt and PBBY to "no" | "नोंदणी क्रमांक पत्रात दिलेला नाही" |
| 020 | mr | STOP to VERIFY_FIRST | R4 unknown (fee None, expected 200000); R6 unknown (role None) | extractor gap: "दोन लाख रुपये" not parsed; "आयटी" not a role | "दोन लाख रुपये रोख आजच भरा" |
| 025 | en (legit) | VERIFY_FIRST to NO_RED_FLAGS_FOUND | R4 clear (fee 30001, expected 35401 incl. GST) | extractor gap, same as 010: pre-GST base taken over the stated total. Label is correct: the cap is applied to total INR incl. GST (CONTRACTS.md). Also role "technician" vs expected "HVAC technician" | "rounded total payable Rs 35,401" |
| 032 | hi (legit) | NO_RED_FLAGS_FOUND to VERIFY_FIRST | R3 false hit (RC None, expected DEMO-RA-032) | extractor gap: लाइसेंस label variant missing from RC_LABEL. Label is correct | "लाइसेंस DEMO-RA-032" |
| 034 | hi (legit) | NO_RED_FLAGS_FOUND to VERIFY_FIRST | R3 false hit (RC None, expected DEMO-RA-034) | extractor gap, same as 032. Label is correct | "लाइसेंस DEMO-RA-034" |

Also note: RC is missed for 031 and 035 in the same way; their verdicts stay correct, so they are not in the misses table.

### Cross-cutting causes (by count of misses affected)

1. **Negation scope (5 misses: 005, 012, 018, plus 013, 014 via office_address).** `_yes_no` applies NEGATION to the whole text unit, and CHANNELS match a bare `\baddress\b` or `कार्यालय` even after "no" / "नहीं". Judgement: extractor gap. Fix belongs in `backend/extract_fallback.py`, not in the labels.
2. **Role vocabulary (10 misses: 004, 005, 008, 010, 012, 013, 014, 015, 018, 020).** ROLES lacks the high-risk roles that rules.py R6 needs (IT, chat support, digital marketing, online marketing, Devanagari/Marathi forms). Without a role, R6 is unknown, so STOP becomes VERIFY_FIRST. Judgement: extractor gap.
3. **Fee base versus total (010, 025, plus 013 and 020 unparsed).** The fee is the first amount in the clause, not the total including GST. Judgement: extractor gap.
4. **RC label spelling (015, 032, 034, plus 031 and 035 field misses).** Judgement: extractor gap, one-word fix to RC_LABEL.

### Rule-semantics note (not a miss; for the lead)

R6 returns unknown when no role is extracted (`elif not role: s6 = "unknown"`). A critical corridor match with no role therefore cannot produce STOP, which drives the 10 STOP-to-VERIFY misses. This matches the current rule code and no label is wrong under it. Whether a high-risk corridor should hit without a role is a product decision for the lead, not a QA finding.
