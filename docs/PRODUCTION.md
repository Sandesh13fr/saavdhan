# Bakaya controlled deployment and validation

This is a single-instance deployment package, not proof of a deployed or professionally validated service. Authentication and tenant checks must pass the current security tests before public deployment. Existing demo cases stay in the reserved local-demo tenant; never assign legacy evidence to a new customer automatically.

## Hosting

The container builds the React interface, runs one FastAPI worker as user 10001, installs local English Tesseract, and serves through Caddy. Only the proxy publishes ports 80/443. Persistent evidence and SQLite live in deploy/data; certificate state persists in named volumes. The app has a read-only root filesystem, a bounded temporary filesystem, dropped capabilities, memory/CPU limits, and a health check. Access logs are disabled to avoid recording case URLs. See [Caddy HTTPS requirements](https://caddyserver.com/docs/automatic-https).

AWS inspection on 2026-10-11 confirmed us-east-1 access and the shared Hackathon_VPC. The first encrypted launch omitted KmsKeyId and immediately terminated with Client.InvalidKMSKey.InvalidState; default-key inspection was denied by the account policy. The owner subsequently approved a synthetic-data demo on default unencrypted EBS. One dedicated t3.small with standard CPU credits, IMDSv2 and a 16 GB gp3 volume is running; unrelated shared resources were untouched. Backend installation and HTTPS verification are in progress. Real financial documents are excluded by the demo operating policy, not an automatic document classifier. See [AWS usage rules](AWS-USAGE.md).

Local Docker verification passed health, unauthenticated rejection, wrong-origin login and missing-CSRF rejection, cross-tenant rejection, secure cookie flags, actual PNG/PDF OCR uploads, and encrypted backup/restore with fourteen verified files and byte-identical originals. Its isolated test container/volume were removed; live data was untouched. This local evidence does not replace deployed HTTPS checks.

Before launch, supply an owned DNS name and a dedicated authorized server. Stay within the provider's EC2/us-east-1/VPC grant and $25 budget; do not create NAT gateways, load balancers, or unrelated services. Existing shared infrastructure costs are outside this application's estimate. Estimate instance, encrypted EBS, public IPv4, traffic and backup destination costs for the actual usage duration before creation. Set burstable instances to standard CPU credits, require IMDSv2, use encrypted persistent EBS for real financial documents, scope the security group to 80/443 plus an explicitly authorized administrative path, and do not expose 8000. See [EC2 security](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security.html).

On a dedicated Linux Docker host:

1. Put this checkout at /opt/bakaya. Copy deploy/production.env.example to deploy/production.env; set the domain, API keys only if needed, and a new backup key. Keep production.env mode 600 and outside version control.
2. Create deploy/data owned by uid/gid 10001. Point the domain A record to the server; open 80/443.
3. In deploy, run `docker compose --env-file production.env config --quiet`, then `docker compose --env-file production.env build`, and `docker compose --env-file production.env up -d`.
4. Provision each authorized account with `docker compose --env-file production.env exec app python -m backend.auth create-user --email EMAIL --name NAME --tenant TENANT --role reviewer`. The password prompt is interactive; never put passwords in command arguments. A distinct tenant identifies each organization.
5. Check HTTPS, health, cookie flags, sign-in/out, two-tenant evidence isolation, approval/export and rejection of unauthenticated/cross-origin writes against the deployed URL. A successful build alone does not pass these checks.
6. Install the backup service/timer from deploy into /etc/systemd/system after inspecting the fixed /opt/bakaya path. Make deploy/backup.sh executable, reload systemd and enable bakaya-backup.timer. Confirm a backup and restore drill before allowing real uploads.

## Encrypted backups

`scripts/backup.py` uses SQLite's [online backup API](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup), checks database integrity, packages data files including original uploads with a SHA-256/size manifest, and authenticates/encrypts the archive with [Fernet](https://cryptography.io/en/latest/fernet/). It refuses symlinks, existing outputs, output inside live data, oversized archives, unsafe restore paths, hash mismatches, and restoration into an existing directory. Restores stage and verify first, then rename into a new isolated directory. It never replaces the running database.

The 128 MB in-memory backup limit is deliberate and fits the bounded pilot container; use a streaming storage backup service before the dataset grows beyond it. Keep the encryption key outside the data directory and keep a separate offline copy. Same-host backups cannot survive loss of the host: copy encrypted archives to an independently controlled destination and verify retrieval. No destination or off-host transfer has been configured.

The daily timer runs at 02:30 UTC (08:00 IST), stops the application writer briefly, performs the backup, and restarts it even on failure. This maintenance window keeps database and file evidence consistent. Fourteen-day cleanup is restricted to the dedicated backup directory. Daily backups imply an intended recovery point up to 24 hours; no measured recovery-time guarantee exists. Monitor the service failure state; the timer alone is not a notification service.

Manual drill, using an environment-held BAKAYA_BACKUP_KEY:

```
python scripts/backup.py create data artifacts/backup-drill.enc
python scripts/backup.py restore artifacts/backup-drill.enc artifacts/restored-drill
```

Run create only in a maintenance window with application writers stopped. Inspect restored case counts, accounts and uploaded bytes in isolation before a human schedules an actual switch. Do not point the app at the drill directory unintentionally. Tests exercise encryption, complete restoration, corruption rejection, manifest tampering and no-overwrite behavior.

## OCR

Set BAKAYA_OCR_ENABLED=true to enable local Tesseract; TESSERACT_CMD can name its executable. The Docker package includes Tesseract/English. On Windows an existing standard Program Files installation is recognized. No external OCR provider or paid API is called.

Uploads remain capped at 15 MB; PDFs are capped at 50 pages; OCR renders a scanned page at 216 DPI, caps images at 20 million pixels and gives each Tesseract subprocess 30 seconds. Searchable PDF pages retain native text extraction. OCR text carries the original upload hash and PDF page provenance; it enters unstructured_review and never directly creates invoices, payments or dates. Errors/no text preserve ocr_unavailable. An owner must verify the original, extraction and all money/date facts. A readable string is not a quality guarantee.

Verified 2026-10-11 with local Tesseract 5.4: a clearly labeled synthetic invoice PNG and image-only PDF recovered invoice TEST-123 and amount INR 10000. Original SHA-256 and page provenance were retained, no structured facts were automatically asserted. A real public CORD receipt (dim, wrinkled, Indonesian) failed to recover all five visible expected monetary amounts: 0/5. The OCR lane remained in review with no records. This failure means the present OCR is unsuitable for unattended document processing; require searchable evidence or manually checked structured facts for difficult scans. See root-generated ignored artifacts/validation provenance/result files for that reference sample.

## Real document and professional validation protocol

No CA/customer sign-off has been obtained. Public receipt OCR is a technical reference, not MSME eligibility, interest, tax or filing validation. AI-generated samples remain explicitly synthetic. Do not substitute model output for an independent reviewer.

For a controlled pilot, obtain the document owner's written permission and retention choice. Supply anonymized original invoice, purchase order, delivery/acceptance record, bank receipt/statement, relevant TDS certificate, Udyam history, disputed correspondence and an authoritative dated rate history. Keep originals out of Git, public screenshots, traces and public model prompts. Share only the minimum necessary with a model provider after owner consent.

Have a qualified reviewer independently prepare expected invoice dates/amounts, due dates, payment allocations, TDS treatment, eligibility assumptions, disputed items and interest calculation. Record each expected fact with a source/page and mark uncertain facts unresolved before running Bakaya. Use at least one clean and one deliberately ambiguous case, including a partial payment and a scan requiring correction. This is an acceptance plan, not an asserted sample-size sufficiency.

Acceptance gates:

- Every material money/date fact agrees with the original and independent worksheet, or blocks approval with an explicit unresolved discrepancy.
- Conservation holds: allocated cash/TDS totals do not exceed verified sources, and residual balances match independently.
- Wrong/ambiguous allocation, missing evidence, corrected facts and changed input invalidate approval until reviewed again.
- Another tenant cannot list, read, change, download or infer the case/evidence. Public URLs and traces reveal no source contents.
- Restored backup contains identical original bytes and usable records/accounts; corrupted backups are rejected.
- Reviewer explicitly approves the current revision; exports are inspected and no portal filing or notice is sent automatically.

Reviewer record template: reviewer name and qualification; organization; permission reference; dataset hash list; independent worksheet reference; each discrepancy and resolution; unresolved exclusions; exact app commit/version; review date; accepted scope; signature or recorded approval. Until this is completed, describe the platform as a prototype with tested engineering controls, not a professionally validated claim engine.

## Vercel frontend and AWS backend split

The frontend project is bakayaai in the owner's Vercel team. The verified reserved domain is https://bakayaai-sandesh.vercel.app; bakayaai.vercel.app was already assigned elsewhere. Production login origin is this exact frontend URL. Until the approved synthetic AWS backend passes deployment checks, frontend/vercel.json routes API requests to an explicit HTTP503 maintenance endpoint; no local demo or account data is published.

After the synthetic backend passes deployed checks, replace only the first rewrite with https://BACKEND_HOST/api/:path*. Use the Caddy backend HTTPS hostname in BAKAYA_DOMAIN and BAKAYA_ALLOWED_HOSTS (plus 127.0.0.1 for health), and keep BAKAYA_PUBLIC_ORIGIN as the Vercel frontend URL. Cookies have no Domain attribute so the proxy response binds them to the frontend. Test through the Vercel origin: sign-in/out, CSRF, cookie flags, uploads, two-tenant isolation and exports. Do not replace the temporary endpoint until the authenticated backend passes checks. Preview Vercel deployments retain Vercel protection; the public production shell exposes no claim data.

Authentication is implemented and tested with server-provisioned viewer/editor/reviewer/admin accounts, salted scrypt hashes, revocable eight-hour HttpOnly sessions, CSRF tokens, account/IP login throttling and server-bound reviewer attribution. CLI password reset revokes active sessions. Legacy local demo cases are not adopted by customer tenants. No self-signup, MFA or email recovery is implemented; independent security review is still required before sensitive customer use.


## Live synthetic deployment — 11 October 2026

Frontend: https://bakayaai-sandesh.vercel.app. AWS backend: https://3-93-34-52.sslip.io. Certificate validation, reviewer login, secure cookie, authenticated cases, logout and session revocation passed. The dedicated t3.small uses 16 GB unencrypted gp3 under explicit owner approval; synthetic data only. Daily encrypted backups are active; one downloaded off-host archive restored successfully. Automated off-host transfer, professional sign-off and sensitive-document production readiness remain pending. Stop the instance after the event; stop/start changes its public IP and requires updating the backend hostname and frontend rewrite.

Login details are in the ignored local artifacts/deploy/operator-access.txt; never publish that file. Live browser inspection was unavailable, so deployed UI visual QA remains pending.


## Public demo hardening — 11 October 2026

Paid model/Crustdata requests require an administrator; the public reviewer can prepare, review and export synthetic packets using local tools. Production tenants are limited to ten cases, fifty MiB of original upload reservations, one hundred sources per case and one thousand audit events per case. Failed upload reservations require operator review; no evidence/audit is silently deleted. Five active sessions per account bound session growth. Client-supplied original-byte metadata is ignored; ingestion assigns hashes. Approvals record actual account/tenant/role. Unknown environment names fail startup rather than enabling anonymous access. Derived agent packet copies are not stored repeatedly; export builds the ZIP on demand. These controls do not distinguish individual people sharing the public demo account.

Live hardening verification passed through the Vercel origin: public reviewer external_calls_allowed=false; model planning and Crustdata requests rejected with HTTP403 without provider calls; logout revoked access; unauthenticated responses retain no-store. AWS image rebuilt and healthy; Vercel frontend deployment READY.
