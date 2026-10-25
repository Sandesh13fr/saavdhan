# Privacy

This is a prototype. It is not legal advice and has not had a legal review. The open questions at the end must be answered before any real use.

## Data handled

| Data | Where | Notes |
|---|---|---|
| Pasted offer text | Case record (SQLite) | Users are asked to remove names, phone numbers and passport numbers first |
| Uploaded files (PDF, TXT, images; up to 10 files, 15 MB each) | `data/uploads/` | Stored under server-generated names with sha256 hashes |
| Extracted facts and verdict | Case record | Each fact keeps its quote and source reference |
| Audit log | Case record | Up to 1000 events per case |
| Check-in plan | Case record | Aliases only. The UI asks for an alias, not a real name. The itinerary is free text the user writes |
| Check-ins and simulated alerts | Case record | Alerts are simulated; nothing is sent |
| Report packet (ZIP) | Downloaded by the user | Generated on request; not sent anywhere |
| Pattern-map reports | Aggregation store | Phone numbers are HMAC-SHA256 hashed with a secret salt before storage. Offer templates are simhash values. Current data is synthetic |
| Operator accounts | `auth` tables | Scrypt hashes; 8-hour sessions; CLI-provisioned only |

## Synthetic-only demo

- The two demo offers (`bangkok-data-entry`, `dubai-near-miss`) are fictional and labelled "SYNTHETIC DEMO" in the text.
- The pattern map uses synthetic report data labelled "Synthetic data only".
- Demo phone numbers are obviously synthetic (for example +91 90000 00001). They are not checked against any real number list.
- Evaluation offers in `eval/offers/` are written for this project.
- No real recruiter, agency or person is named as a fraud. Agent names in the demos are fictional.

## Retention

- Anonymous cases older than `SAAVDHAN_RETENTION_HOURS` (default 24 hours) are purged. Purges also cap anonymous cases at `SAAVDHAN_ANON_CASE_CAP` (default 200).
- Upload deletion when a case is purged has not been verified; check `backend/storage.py` before relying on it.
- Production limits: 10 cases per tenant and 50 MiB of uploads per tenant (the code refuses new work beyond these limits).
- There is no export or deletion request flow yet.

## Hashing

- Phone numbers: HMAC-SHA256 with `SAAVDHAN_HASH_SALT`. Production refuses to start without a salt of at least 16 characters. The development fallback salt is public in the code and is for local demos only.
- Hashes are not secret if the salt leaks. Treat the salt as a secret.

## No scraping

Saavdhan has no connector to WhatsApp, Telegram or any social platform. Users paste or upload text they already have. Chat exports are user uploads only.

## No automated reporting

Saavdhan never sends a report, complaint or message to any authority. The report packet is downloaded by the user, who decides whether and to whom to give it. The "where to report" text in the packet is marked for verification before use.

## Third parties

- **LLM gateway (opt-in, off by default).** When `SAAVDHAN_ENABLE_LLM=true` and a key is set, the text of the uploaded offer is sent to the configured OpenAI-compatible endpoint. In the project setup this is TokenRouter (`https://api.tokenrouter.com/v1`). If `SAAVDHAN_LLM_BASE_URL` is empty the code uses `https://api.openai.com/v1`.
  - Users must be told before the text is sent. The current in-app privacy note does not yet say this. Copy change is an open item.
  - `.env.example` describes the LLM as OpenAI-only. Update that comment to match the gateway setting.
- **OpenStreetMap tiles (map view).** Map tiles are loaded from OpenStreetMap tile servers. Each tile request discloses the viewer's IP address, browser headers and the map area viewed. Requests do not include report counts, district selections, hashes or documents. The referrer is limited to the origin.
- **geoBoundaries district boundaries.** Local file; no request at runtime.

## DPDP Act 2023 (high level)

The Digital Personal Data Protection Act, 2023 is the relevant Indian law. Saavdhan's design aims at:

- **Notice and consent.** Users should be told what is processed, why and for how long before submitting. Current copy is partial; the LLM disclosure and the family-alert purpose need stating.
- **Purpose limitation.** Data is used to check offers, run the user's own check-in plan and produce the packet. The pattern map is for aggregated, anonymised reporting only.
- **Data minimisation.** Aliases instead of names; hashed phone numbers; short retention; no accounts for users.
- **Rights.** Access, correction, erasure and grievance redressal are not yet built. The app has no request channel.
- **Children.** The users are young people who may be under 18. The Act has extra rules for children's data, including verifiable parental consent. This is not handled.

The sections of the Act and any obligations under it must be confirmed by counsel.

## Open questions for legal review

1. Is Saavdhan a data fiduciary or a processor for the case data, and for the pattern map?
2. Are hashed phone numbers personal data under the Act, given that the salt is held by the operator?
3. How should users under 18 be handled: age check, parental consent, or a different flow?
4. Does the family check-in feature process personal data of third parties (the contacts), and what notice do they need?
5. What is the lawful basis and notice for the LLM gateway, and what contract and cross-border transfer terms apply?
6. What retention period is justified for case data, uploads and the pattern map?
7. What grievance officer, contact channel and breach-notification process are required before a pilot?
8. Can the pattern map be shared with cyber police or placement cells, and under which agreement?
9. Do the "where to report" details in the packet need a legal check before users rely on them?
