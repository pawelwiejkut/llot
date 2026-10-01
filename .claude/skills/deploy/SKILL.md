---
name: deploy
description: Deploy the current LLOT code to the local Docker host (container "llot", port 8080) with health check and automatic rollback. Use when the user asks to deploy, release, update or restart the running instance.
---

# Deploy LLOT locally

1. Make sure the change is verified (see the `verify` skill) — at least `make lint test`.
2. Deploy:
   ```bash
   scripts/deploy.sh            # tests, build, up -d, health check, rollback on failure
   scripts/deploy.sh --pull     # git pull --ff-only first
   ```
   The script tags the running image `llot:previous` before building and restores it automatically
   if the container doesn't become healthy or `/api/health` reports `error`.
3. Confirm:
   ```bash
   curl -s http://localhost:8080/api/health
   docker logs --tail 20 llot
   ```
4. Report to the user what was deployed (commit, health status, TTS languages from
   `curl -s http://localhost:8080/api/tts/languages`).

Notes
- Config comes from `.env` via `env_file`; editing `.env` requires `docker compose up -d` (recreate).
- Published images: the `Publish image` GitHub workflow pushes `ghcr.io/pawelwiejkut/llot`. To run one
  instead of building: `LLOT_IMAGE=ghcr.io/pawelwiejkut/llot:latest docker compose pull && docker compose up -d --no-build`.
- Low disk space breaks builds; check `df -h /` and `docker system df` if a build fails.
