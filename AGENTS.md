# AGENTS.md

Guide for AI coding agents working on LLOT. Human-facing docs: `README.md`, `DOCUMENTATION.md`.

## What this is

LLOT is a self-hosted translation web app: Flask backend + one vanilla-JS page. Translation is done by
a local LLM through **Ollama** (`/api/chat`); optional text-to-speech goes through any **Wyoming**
protocol TTS server (wyoming-piper, wyoming_openai, ...). No database, no accounts: translation history
lives in the browser's localStorage.

## Layout

```
app/
  __init__.py              create_app(): config, Babel, logging, blueprints
  config.py                Config class; reads .env; ALL_LANGUAGES (38 codes)
  routes/api.py            REST API (/api/translate, /alternatives, /refine, /tts, /tts/languages, /health, /models)
  routes/main.py           "/" page + debug-only /set_language/<code>
  routes/favicon.py        icon routes (inline base64)
  services/translator.py   prompt building + parsing for translate / alternatives / refine
  services/ollama_client.py  thin requests client for Ollama /api/chat (think-mode fallback)
  services/tts.py          Wyoming TTS client: voice discovery (describe), synthesis, WAV building
  services/language_detector.py  langdetect wrapper (seeded, base codes)
  models/language.py       LanguageService, tones (TONE_VALUES is the allowlist)
  templates/index-modern.html  the only page
  static/js/app-modern.js  all front-end logic (classes: LLOTApp, DropdownManager, TranslationManager,
                           UIManager, HistoryManager, TTSManager, TTSPlayer, ...)
  static/css/style-modern.css
  translations/            Flask-Babel catalogs for the UI (.po/.mo)
tests/                     pytest unit tests (+ fake Wyoming server in test_tts.py)
tests/e2e/                 Playwright browser tests (marker `e2e`, need a running instance)
scripts/deploy.sh          build + docker compose up + health check + rollback
```

## Commands

Dev environment lives in `.venv` (create with `make install`; it also installs headless Chromium).

| Task | Command |
|---|---|
| Unit tests (+coverage) | `make test` or `.venv/bin/pytest` |
| Browser tests | `make e2e` (needs LLOT running; `LLOT_URL` defaults to `http://localhost:8080`) |
| Lint + format check | `make lint` (ruff) |
| Auto-fix + format | `make format` |
| Dependency CVE scan | `make audit` (pip-audit) |
| All CI checks except e2e | `make check` |
| Run locally | `make dev` (Flask, reads `.env`) |
| Deploy on this host | `make deploy` (= `scripts/deploy.sh`) |

There is no JS build step or JS test runner; check JS syntax with
`node --check app/static/js/app-modern.js` if Node is available, and cover behaviour with `tests/e2e`.

## Conventions

- Python 3.11+ (image runs 3.13). Formatting and lint: ruff (`pyproject.toml`, line length 110).
- Pin exact versions in `requirements.txt` (runtime) and `requirements-dev.txt` (tools); run `make audit` after changes.
- API input is untrusted: use `_str()` / `_common_params()` in `routes/api.py`; validate languages against
  `ALL_LANGUAGES`, tones against `LanguageService.TONE_VALUES`; respect `MAX_TEXT_LENGTH`.
- Never inject model output or user text into HTML unescaped: use `escapeHtml()` in JS, or `textContent`.
- Don't log user text at INFO level (privacy-first product). Use `logger.debug` for payloads.
- Logging goes to stderr (`docker logs`); no log files.
- TTS: server voices first; otherwise `BrowserVoices` (Web Speech API) with `localService` voices only,
  never network voices (privacy). Both paths must start inside the click handler synchronously (Safari).
- TTS: never hard-code voice names. Voices come from the server's `describe`; per-language overrides via
  `WYOMING_TTS_VOICES`. Old env names `WYOMING_PIPER_HOST/PORT` must keep working.
- Front-end persistence keys: `llot-model-choice` (explicit model choice only), `llot-tone`, `llot-think`,
  `llot-theme`, `llot-history`. Don't auto-persist defaults.
- UI strings in templates go through `_()`; after adding strings run `make extract-strings update-translations`.

## Gotchas

- `AsyncTcpClient` from `wyoming` connects in `__aenter__`; `tts.py` calls `connect()` itself, so don't
  wrap it in `async with`.
- Ollama API: only `/api/chat`, `/api/tags`, `/api/show`. Model capabilities from `/api/show` are cached
  10 min per worker; `think` is only sent to models reporting `thinking` (and a 400 "does not support
  thinking" is retried without it for servers that don't report capabilities). Alternatives/refine use
  structured outputs (`format` = JSON schema in `translator.py`); keep the regex JSON fallback.
- gunicorn runs 2 workers x 4 threads with `--timeout 180` because think-mode requests can take ~120 s.
  In-memory caches (`tts_cache`, voice list) are per worker.
- `.env` is **not** baked into the Docker image (`.dockerignore`); compose passes it via `env_file`.
  After editing `.env`, recreate the container (`docker compose up -d`), a restart is not enough.
- Safari needs `play()` inside the click gesture: `TTSPlayer.unlock()` must run synchronously in the
  click handler before any `await`.
- `tests/` read the developer's `.env` through `load_dotenv`; tests that depend on TTS/Ollama env must set
  or clear those variables with `monkeypatch`.

## Before you finish a change

1. `make lint` and `make test` pass.
2. Front-end change: run `make e2e` against a rebuilt instance (`docker compose up -d --build`).
3. Docs: update `README.md` / `DOCUMENTATION.md` when behaviour, config or API changes.
