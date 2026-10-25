# Controlled paired agent replay

[Inspect the public sanitized trace trees and run comparison](paired-agent-replay.json). This snapshot includes actual readback names, parent IDs, timestamps and timing metrics, plus local run/checkpoint results; no project keys, prompts or uploaded documents are included.

On 11 October 2026, the same synthetic fixture and API sequence were run against actual Git revisions 233acc9 (before) and 6985522 (after) in separate temporary checkouts/data directories. This is a controlled replay performed now, not historical runtime measurements. Both revisions contain other changes; the targeted packet-write removal is verified by their backend/agent.py diff. The before implementation wrote an unused approved ZIP beside source uploads; the after implementation keeps checkpoint metadata and regenerates the approved packet on export.

| Verified result | Before 233acc9 | After 6985522 |
| --- | --- | --- |
| Redundant packet files written | 1 | 0 |
| Valid approved ZIP export | Yes | Yes |
| Principal | INR 470,000.00 | INR 470,000.00 |
| Interest | INR 40,777.36 | INR 40,777.36 |
| Total | INR 510,777.36 | INR 510,777.36 |
| Lifecycle checkpoints | 10 | 10 |
| Model calls/tokens | 0 / 0 | 0 / 0 |
| Neatlogs readback spans | 27 | 27 |

The redundant file was not included as a nested export member even before the fix. This evidence supports removing an unnecessary disk write, not a claim of changed financial accuracy, measured cloud savings, or a faster agent. ZIP byte lengths differ because serialization/timestamps differ. No total delivery-cost measurement was made; zero model inference applies only to these rules-driven runs.

Exact Neatlogs trace readback returned HTTP 200 with success and 27 spans per trace:

- Before: adede6146ac02b223da79587c5c46242
- After: 3af784ca1b8dd9c7bcc69bb7d83fd1e7

Each trace has a real lifecycle root spanning tool execution, scripted source-backed human review, explicit scripted approval, resumed packet generation, valid ZIP export, and a separately labeled simulated local failure/retry. Every span shares the trace ID and resolves through its parent chain to that root. Explicit named checkpoint spans show waiting review at revision 1, waiting approval at revision 2, then completion at revision 2. Retry reconciliation executes twice under the simulation subtree; inventory is not repeated. These are synthetic QA reviewer inputs, not professional validation or observed customer decisions.

The key-authenticated readback route is `https://ingest.neatlogs.com/api/traces/v3/TRACE_ID`, using the project key in the x-api-key header. This is an authenticated API endpoint, not a verified public dashboard sharing link. Open the trace IDs in the account's Neatlogs interface; guest access is not established. Normalized readback exposes names, parent IDs, timestamps and counts but drops custom bakaya.* root attributes. The local replay JSON separately preserves run ID, revision checkpoints and zero-provider-call metrics; do not claim those custom fields appeared in dashboard readback.

Reproduction: export each exact Git revision into a temporary checkout, set BAKAYA_DATA_DIR to a new nonexistent directory outside live data, BAKAYA_ENV=local, BAKAYA_ENABLE_LLM=false, and explicitly blank LITELLM_API_KEY/OPENAI_API_KEY/CRUSTDATA_API_KEY. Supply only the Neatlogs key through the environment. From that checkout run the workspace Python interpreter with the current `scripts/trace_agent_replay.py REVISION ABSOLUTE_OUTPUT_DIRECTORY`. The harness refuses existing data directories or paid-provider configuration, asserts the complete lifecycle/export and trace tree, and reads back the exact trace. Restore nothing into live data.

Ignored evidence files are under artifacts/evidence/paired-replay: per-revision result JSON, exact trace readback JSON, approved synthetic packets and comparison.json. The separate actual browser recording is artifacts/evidence/agent-lifecycle.webm. No API keys or real documents are in the tracked report.
