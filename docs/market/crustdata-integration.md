# Crustdata connection — 11 October 2026

The supplied API key is stored in ignored local `.env` and local Codex MCP configuration. Neither is committed. Official endpoint: https://mcp.crustdata.com/mcp (Bearer authentication), verified from https://mcp.crustdata.com/.

Authenticated initialization and tool discovery returned HTTP200. Free credit balance check succeeded and reported account balance5200 credits, spent_this_call0. The user explicitly sets the working ceiling at500 CREDITS; do not raise it without authorization. Account balance does not override this ceiling. No billable lookup, watcher or enrichment was performed in this verification.

The tool's price table reports company enrich v2 at2credits/company and identify v2 free, as of its published pricing snapshot. Recheck before usage. Limit fields and company count, record provider-reported usage, cache results and stop paid operations on unknown/error cost. No USD conversion is assumed. The provider-side500 limit is user-reported, not independently confirmed by balance data.

This connects the development MCP, not yet the Bakaya buyer-enrichment UI. Enrichment must remain optional and require owner confirmation; company data is not legal identity, Udyam eligibility, registration or tax evidence.

## Application lookup completed — 11 October 2026

Optional buyer context is available as a collapsed section in the claim workspace. A user supplies one company domain and explicitly confirms the lookup. Credentials remain server-side. The returned company summary records provider, company identifier, retrieval time and reported credit cost; it never changes claim facts, eligibility, calculations or approval.

The backend checks current provider pricing, reserves 2 credits before a lookup, caches results by domain and enforces a cumulative 500-credit ceiling in the local database. Cached lookups cost zero. Failed or unverified calls retain their reservation and stop further paid lookups for review. This conservative ledger covers this installation only; teammates' external calls are not visible to it. Do not reset or replace the database to bypass the cap.

Live verification used 2 credits for schema inspection and 2 for the application lookup: 4 credits consumed and 4/500 reserved locally. Stripe was used as a public company example, not as a real synthetic-case buyer. Eight focused tests passed; frontend build passed. No other paid company lookup was made.

Entire checkpoint evidence is verified separately. cfo model creation remains blocked by unavailable tools/login. The repository was verified public on 11 October, following the user's visibility change.
