# Entire evidence verification — 11 October 2026

Read-only checks performed against the local Bakaya repository and origin:

- `entire status`: enabled on main, Codex integration present, checkpoint sync target origin.
- `entire doctor`: Git hooks OK; Codex hooks installed; hook approval records PRESENT; no stuck sessions found.
- `entire checkpoint list`: zero saved checkpoints on main.
- `entire checkpoint list --pending --json`: two task-completion records, both with empty checkpoint ID and metadata directory. These are pending activity, not persistent commit-linked evidence.
- `git for-each-ref` for local/remote Entire refs: none returned.
- `git ls-remote origin` for Entire checkpoint refs/branches: none returned.
- Status reports session attribution/tracking divergence after Git history movement; do not present attribution totals as reliable.

Verdict: hook installation and user approval are verified. Persistent checkpoint creation, linkage to a Bakaya commit and remote synchronization remain unverified. No checkpoint ID or URL can truthfully be supplied yet.

Next evidence required: a real development change captured through the approved hooks, a saved checkpoint ID, its linked commit, and successful remote readback. Before capturing session transcripts, verify secret redaction because credentials appeared in the conversation; do not publish raw session data. This verification did not modify sessions, condense/discard history, change Git refs or create checkpoints.

## Completed checkpoint verification — 11 October 2026

- Saved checkpoint: `01M4KRBT9GY4SCGC3WR3NXRGTR`.
- Linked main commit: `0958d0e` (`Link agent commits automatically for checkpoint evidence`), with an Entire-Checkpoint trailer.
- Local checkpoint ref: `refs/entire/checkpoints/TR/01M4KRBT9GY4SCGC3WR3NXRGTR`.
- Local and origin ref object IDs both: `da34ac5436932b9cd457da37beac6be3da33615e`.
- Normal Git push reported one checkpoint ref pushed successfully. Exact remote readback matched the local object.
- Entire metadata readback reports one root Codex session and two stored subagent transcripts. This checkpoint is marked logs-only: it proves stored development context linked to a commit, not independently measured file attribution or a rollback experiment.
- Ten stored files (12,259,101 bytes) were scanned for locally configured KEY/TOKEN values and supplied gateway/Crustdata key patterns before push; zero matches. This is a bounded text check, not a guarantee against all sensitive data formats.

Cause of previous stalls: the prepare-commit-msg hook awaited confirmation in a hidden Windows controlling terminal. `commit_linking: always` resolves that prompt for the authorized agent commits. Custom redaction rules protect the two supplied key formats; default scanner remains enabled. Redaction behavior follows https://github.com/entireio/cli/blob/main/docs/security-and-privacy.md.

Verdict: installed/trusted hooks, permanent saved context, commit linkage and remote synchronization are now verified. Repository remains private. No public checkpoint page or recovery/rollback experiment was verified.

## Attribution and rollback tests — 11 October 2026

`entire blame .entire/settings.json --json` identifies line15 as AI, Codex, checkpoint `01M4KRBT9GY4SCGC3WR3NXRGTR`, session `01a12590-dc17-7413-9dad-86cc358ad23f`, commit `0958d0ed57ed6daea46206accadb421926bb2c5b`. Older unlinked lines are labeled human even though this build was agent-assisted. PASS for the tested linked line; this is commit/checkpoint attribution, not independent proof of authorship for every file.

Rollback test used an isolated clone under ignored `artifacts/qa/entire-rollback-test`, a dedicated branch and separate CODEX_HOME. A later test commit added `ROLLBACK_TEST_MUTATION` to the capture document. Native `entire session resume --force` restored the saved session transcript, but retained the later commit and marker, both when already on the branch and when switching from main. Native automatic code rollback therefore did NOT pass this test; no code-restoration claim is made for that command. Interactive agent launch was declined on the second run; the first launch could not run without a terminal.

Explicit Git rollback to the checkpoint-linked commit `0958d0e` passed: HEAD matched, the document matched committed bytes after Windows newline normalization, mutation was absent, and checkout was clean. Main workspace HEAD remained `d6d89c9` during this test and was not reset. No remote rollback or force push occurred. Session-log restoration and Git-assisted code rollback are verified separately.
