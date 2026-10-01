@AGENTS.md

## Claude Code specifics

- Project skills live in `.claude/skills/`: `verify` (full check of a change incl. browser test) and
  `deploy` (ship to the local Docker host). Prefer them over ad-hoc command sequences.
- Shared permissions are in `.claude/settings.json`; personal overrides go in `.claude/settings.local.json`
  (git-ignored).
- The production instance on this host is the `llot` container on port 8080, configured from `.env`.
  Treat `.env` as the user's config: edit it only when asked, never commit it.
- Commit or push only when the user asks.
