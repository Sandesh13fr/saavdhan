# Entire checkpoint capture

Date: 11 October 2026

## Verified state

- Entire CLI 0.11.4 is installed locally.
- Entire is enabled on `main` and syncs checkpoints to `origin`.
- Installed Git hooks are present in `.git/hooks` for `commit-msg`, `prepare-commit-msg`, `post-commit`, `post-rewrite`, and `pre-push`.
- `entire doctor` reports Git hooks OK, Codex hooks installed, hook approval records present, and no stuck sessions.
- Prior checkpoint verification recorded zero saved checkpoints on `main`.
- Sponsor key handling uses the committed custom redaction format from the preceding hook/provenance update.

## New capture

A new tracked Codex session is active for this development change, so the session provenance is now being captured by the trusted Entire/Codex hook path instead of relying only on prior read-only evidence.
