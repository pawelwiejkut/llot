---
name: verify
description: Verify a change to LLOT end-to-end - lint, unit tests, dependency audit, rebuild the container and run the Playwright browser tests against it. Use after any code change, before telling the user something works.
---

# Verify a LLOT change

Run from the repo root. Stop and fix at the first failure; report real output, not a summary guess.

1. Static checks and unit tests:
   ```bash
   make lint
   make test
   ```
2. If `requirements*.txt` changed: `make audit`.
3. If anything under `app/` changed, rebuild and restart the local instance, then wait for it to be healthy:
   ```bash
   docker compose up -d --build
   docker inspect -f '{{.State.Health.Status}}' llot   # repeat until "healthy"
   curl -s http://localhost:8080/api/health
   ```
4. Browser tests against the running instance (includes a live translate + speaker smoke test that
   skips itself when Ollama or TTS is unavailable):
   ```bash
   make e2e
   ```
   Read skip reasons with `.venv/bin/pytest -m e2e -rs`.
5. For a front-end bug that the suite doesn't cover, add a test to `tests/e2e/test_ui.py` that reproduces
   it (use `page.route` to stub API responses so the test is deterministic), watch it fail, then fix.

If `.venv` is missing, run `make install` first (creates it and installs headless Chromium).
