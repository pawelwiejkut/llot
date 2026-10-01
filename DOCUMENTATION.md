# 📚 LLOT - Complete Documentation

> **Detailed documentation for LLOT - Local LLM Ollama Translator**

---

## 📑 Table of Contents

- [🎛️ Features](#-features)
- [🔧 Configuration](#-configuration)
- [🐳 Docker Deployment](#-docker-deployment)
- [🚀 Production & CI](#-production--ci)
- [🌍 Supported Languages](#-supported-languages)
- [🔊 Text-to-Speech](#-text-to-speech-support)
- [🧪 Testing & Quality](#-testing--quality)
- [⚡ Performance](#-performance)
- [🔧 Development](#-development)
- [📚 API Documentation](#-api-documentation)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

---

## 🎛️ Features

### 🌐 **Translation Engine**
- **Real-time translation** as you type
- **38 languages** supported
- **Auto language detection** powered by `langdetect`
- **Multiple tones**: neutral, formal, informal, friendly, technical, poetic
- **Model switching** - use any Ollama-compatible LLM
- **Translation history** stored locally in your browser
- **Alternative suggestions** for better translations
- **Smart refinement** with user constraints

### 🎨 **Modern Interface**
- **Clean, responsive design** inspired by modern translation services
- **Dark/light theme** toggle
- **Mobile-first** responsive layout
- **Keyboard shortcuts** for power users
- **Real-time status** indicators
- **Copy to clipboard** with one click
- **Character counter** and smart layout

### 🔊 **Text-to-Speech**
- Works with **any Wyoming TTS server** (wyoming-piper, wyoming_openai, ...)
- **Voices discovered automatically** from the server
- Speaker button shown only for languages that have a voice
- **In-memory cache** for repeated phrases

### 🛠️ **Technical Excellence**
- **Modern Python** Flask application
- **Clean, refactored codebase** with proper error handling
- **pytest + Playwright test suites** (fake Wyoming TTS server, browser tests)
- **Docker deployment** with multiple configurations
- **Environment-based configuration**
- **Health monitoring** and status checks
- **Detailed logging** for troubleshooting

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` in the project root. The same file is used by
`python run.py` and by `docker compose` (via `env_file`).

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OL_MODEL` | `gemma4:26b` | Default model (users can switch in the UI) |
| `APP_HOST` / `APP_PORT` | `0.0.0.0` / `8080` | Listen address for `run.py`; with Docker, `APP_PORT` is the published host port |
| `FLASK_DEBUG` | `0` | Flask debug mode (never enable on a network-exposed instance) |
| `DEBUG_LOGGING` | `false` | Verbose debug output (may include request text) |
| `WYOMING_TTS_HOST` | – | Wyoming TTS server host; unset disables TTS |
| `WYOMING_TTS_PORT` | `10200` | Wyoming TTS server port |
| `WYOMING_TTS_VOICES` | – | Pin voices per language, e.g. `pl=pl_PL-gosia-medium,en=en_US-lessac-medium` |
| `TRANSLATION_LANGUAGES` | all | Comma-separated language codes to offer |
| `SECRET_KEY` | random | Only used for the debug-mode UI language switcher |

`WYOMING_PIPER_HOST` / `WYOMING_PIPER_PORT` (older names) are still accepted.

### Recommended Models

LLOT works with any Ollama chat model:

| Model | Size | Quality | Think support |
|---|---|---|---|
| `gemma4:26b` | ~18 GB | Excellent | Yes |
| `gemma4:e4b` | ~9 GB | Very good | Yes |
| `gemma3:27b` | ~17 GB | Excellent | No |
| `qwen3:14b` | ~9 GB | Very good | Yes |
| `qwen2.5:14b` | ~9 GB | Good | No |

---

## 🐳 Docker Deployment

| File | What it starts |
|---|---|
| `docker-compose.yml` | LLOT only, using your existing Ollama / TTS servers from `.env` |
| `docker-compose.standalone.yml` | LLOT + Ollama |
| `docker-compose.full.yml` | LLOT + Ollama + Wyoming Piper (voices downloaded on first use) |

```bash
docker compose up -d                                   # standard
docker compose -f docker-compose.full.yml up -d        # everything bundled
docker compose up -d --build                           # after git pull
```

The image runs gunicorn with 2 workers × 4 threads and a 180 s worker timeout
(think-mode requests can take up to 120 s). `.env` is **not** baked into the image;
it is passed at runtime.

---

## 🚀 Production & CI

### Deploying on a Docker host
```bash
scripts/deploy.sh            # or: make deploy
scripts/deploy.sh --pull     # git pull --ff-only first
```
The script runs the unit tests, keeps the running image as `llot:previous`, builds,
starts the container, waits for the Docker healthcheck and `/api/health`, and
**rolls back automatically** if either fails.

### Published images
The `Publish image` workflow pushes multi-arch images to `ghcr.io/pawelwiejkut/llot`
(`latest` from `main`, `sha-…`, and `X.Y.Z` / `X.Y` for `vX.Y.Z` tags). To run one instead
of building locally:
```bash
LLOT_IMAGE=ghcr.io/pawelwiejkut/llot:latest docker compose pull
LLOT_IMAGE=ghcr.io/pawelwiejkut/llot:latest docker compose up -d --no-build
```

### Continuous integration
`.github/workflows/ci.yml` runs on every push and pull request: ruff, unit tests with
coverage, `pip-audit`, Playwright browser tests and a Docker build. Dependabot
(`.github/dependabot.yml`) opens weekly PRs for Python packages, the base image and
GitHub Actions.

### Security notes
- LLOT has **no authentication**. Keep it on a trusted network, or put it behind a
  reverse proxy that adds auth and HTTPS (e.g. Caddy `basic_auth`, Authelia, Traefik
  forward-auth).
- Example Caddyfile:
  ```
  translate.example.com {
      basic_auth {
          alice <bcrypt-hash from `caddy hash-password`>
      }
      reverse_proxy localhost:8080
  }
  ```
- Anyone who can reach LLOT can use your Ollama server through it (any installed model).

---

## 🌍 Supported Languages

**38 languages supported** with smart auto-detection:

### Major Languages
🇺🇸 English • 🇨🇳 中文 (Chinese) • 🇮🇳 हिन्दी (Hindi) • 🇪🇸 Español • 🇫🇷 Français • 🇸🇦 العربية (Arabic)  
🇮🇳 বাংলা (Bengali) • 🇵🇹 Português • 🇷🇺 Русский • 🇵🇰 اردو (Urdu) • 🇮🇩 Bahasa Indonesia  
🇩🇪 Deutsch • 🇯🇵 日本語 • 🇹🇷 Türkçe • 🇰🇷 한국어 • 🇻🇳 Tiếng Việt • 🇮🇳 தமிழ் (Tamil) • 🇹🇭 ไทย

### European Languages  
🇵🇱 Polski • 🇮🇹 Italiano • 🇳🇱 Nederlands • 🇸🇪 Svenska • 🇩🇰 Dansk • 🇳🇴 Norsk • 🇫🇮 Suomi  
🇨🇿 Čeština • 🇸🇰 Slovenčina • 🇭🇺 Magyar • 🇷🇴 Română • 🇧🇬 Български • 🇭🇷 Hrvatski  
🇸🇮 Slovenščina • 🇱🇻 Latviešu • 🇱🇹 Lietuvių • 🇪🇪 Eesti • 🇬🇷 Ελληνικά • 🇲🇹 Malti • 🇮🇪 Gaeilge

**Language filtering available** - configure only the languages you need.

---

## 🔊 Text-to-Speech Support

LLOT talks to TTS servers over the [Wyoming protocol](https://github.com/OHF-Voice/wyoming):

1. On first use it sends `describe` and caches the server's voice list for 5 minutes.
2. For each request it picks a voice whose language matches the target language
   (preferring `medium` quality Piper voices), unless `WYOMING_TTS_VOICES` pins one.
3. It sends `synthesize`, collects audio between `audio-start` and `audio-stop`,
   and returns a WAV file using the sample rate/width/channels reported by the server.

The first request in a new language can take 15-30 s with wyoming-piper while it downloads
the voice; later requests are fast.

### Option A: wyoming-piper (local voices)
```bash
docker run -d -p 10200:10200 -v piper-data:/data rhasspy/wyoming-piper --voice en_US-lessac-medium
echo "WYOMING_TTS_HOST=<server-ip>" >> .env
echo "WYOMING_TTS_PORT=10200" >> .env
```

### Option B: wyoming_openai (OpenAI-compatible TTS, e.g. Speaches)
Point LLOT at the proxy's Wyoming port (default `10300`):
```bash
echo "WYOMING_TTS_HOST=<server-ip>" >> .env
echo "WYOMING_TTS_PORT=10300" >> .env
```

Check what LLOT sees: `curl http://localhost:8080/api/tts/languages`

### Browser fallback
For target languages without a server voice, the front-end uses the Web Speech API with
on-device voices only (`SpeechSynthesisVoice.localService`). Network voices such as Chrome's
"Google …" voices are deliberately skipped because they send the text to a cloud service.
Which languages work therefore depends on the voices installed in the viewer's OS/browser.

---

## 🧪 Testing & Quality

```bash
make install   # creates .venv with app + dev tools and headless Chromium
make lint      # ruff lint + format check
make test      # unit tests with coverage
make audit     # dependency vulnerability scan (pip-audit)
make check     # lint + test + audit (what CI runs, minus browser tests)
make e2e       # Playwright browser tests against a running instance
```

| Suite | What it covers |
|---|---|
| `tests/test_app.py` | API validation (languages, sizes, tone/think), health, errors, redirect, manifest |
| `tests/test_translator.py` | Prompt building and LLM response parsing (Ollama mocked) |
| `tests/test_ollama_client.py` | Ollama client incl. think-mode fallback |
| `tests/test_tts.py` | TTS client against an in-process fake Wyoming server |
| `tests/e2e/test_ui.py` | Browser: no console errors, XSS-safe rendering, default model, speaker visibility, live translate + speak |

Browser tests default to `http://localhost:8080`; point them elsewhere with
`LLOT_URL=http://host:port make e2e`. Tests needing a real Ollama or TTS server skip
themselves when it isn't reachable (`.venv/bin/pytest -m e2e -rs` shows why).

---

## ⚡ Performance

### Benchmarks
- **Page Load**: ~50ms
- **Translation Speed**: 2-15s (model dependent)
- **Memory Usage**: ~200MB (excluding models)
- **TTS Generation**: ~1-3s per sentence

### Optimization Tips
1. **Use faster models** like `gemma4:e4b`, and keep Think mode off for short text
2. **Enable TTS caching** (enabled by default)
3. **Configure language filtering** to reduce options
4. **Use SSD storage** for model loading
5. **Increase RAM** for larger models

---

## 🔧 Development

### Local Development
```bash
# Clone and setup
git clone https://github.com/pawelwiejkut/llot.git
cd llot

# Create .venv with dependencies, dev tools and headless Chromium
make install

# Setup environment
cp .env.example .env

# Run in development mode (Flask dev server, auto-reload with FLASK_DEBUG=1)
FLASK_DEBUG=1 make dev
```

### Code Structure
```
llot/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration management
│   ├── routes/
│   │   ├── main.py           # Web page (/)
│   │   ├── api.py            # REST API
│   │   └── favicon.py        # Icons and manifest
│   ├── services/
│   │   ├── translator.py     # Prompts + translation logic
│   │   ├── ollama_client.py  # Ollama /api/chat client
│   │   ├── tts.py            # Wyoming TTS client
│   │   └── language_detector.py
│   ├── models/language.py    # Languages and tones
│   ├── static/               # CSS / JS (app-modern.js = default UI)
│   ├── templates/            # index-modern.html (the only page)
│   └── translations/         # UI translations (Babel)
├── tests/                    # pytest suite (tests/e2e = Playwright browser tests)
├── scripts/deploy.sh         # Build, deploy, health-check, rollback
└── docker-compose*.yml       # Docker configurations
```

---

## 📚 API Documentation

All POST endpoints accept JSON. Text fields are limited to 10,000 characters
(413 otherwise). `target_lang` must be one of the supported language codes (400 otherwise).
Unknown `tone` values fall back to `neutral`; `think` must be the JSON boolean `true` to enable.

### `POST /api/translate`
```json
{"source_text": "Hello world", "source_lang": "auto", "target_lang": "pl",
 "tone": "neutral", "think": false, "model": "gemma4:26b"}
```
Response: `{"translated_text": "Witaj świecie", "source_lang": "en", "target_lang": "pl"}`
(`source_lang` is the detected language when `auto` was sent). Errors return `{"error": "..."}`
with status 400/413/502; empty input returns `{"error": "EMPTY"}`.

### `POST /api/alternatives`
`{"source_text", "current_translation", "clicked_word", "target_lang", "tone", "think", "model"}`
→ `{"alternatives": ["...", ...]}` (max 6)

### `POST /api/refine`
`{"source_text", "current_translation", "target_lang", "tone", "enforced_phrases": [...], "replacements": [{"from": "...", "to": "..."}]}`
→ `{"translated": "...", "faithful": true}`

### `POST /api/tts`
`{"text": "Witaj świecie", "language": "pl"}` → `audio/wav`.
Status 404 when the server has no voice for the language, 502 on TTS server errors,
503 when TTS is not configured.

### `GET /api/tts/languages`
`{"enabled": true, "languages": ["pl"]}`

### `GET /api/models`
`{"models": ["gemma4:26b", ...]}` (chat-capable models only; embedding models are hidden)

### `GET /api/health`
```json
{"ollama": {"status": "ok", "models": ["..."]}, "tts": {"status": "ok"}, "overall": "ok"}
```
`overall` is `warning` when only TTS is down or disabled.

---

## 🐛 Troubleshooting

### Common Issues

**Translation not working?**
- ✅ Ollama on the same host as Docker? `OLLAMA_HOST=http://host.docker.internal:11434`, and Ollama
  must listen on all interfaces (it binds to 127.0.0.1 by default): set `OLLAMA_HOST=0.0.0.0` in
  Ollama's own environment (e.g. `systemctl edit ollama`) and restart it
- ✅ Check Ollama server is running: `curl http://localhost:11434/api/tags`
- ✅ Verify model is available: `ollama list`
- ✅ Check LLOT logs: `docker compose logs llot`

**TTS not working?**
- ✅ Check which languages have voices: `curl http://localhost:8080/api/tts/languages`
- ✅ Check `WYOMING_TTS_HOST` / `WYOMING_TTS_PORT` in `.env` (wyoming-piper uses 10200, wyoming_openai 10300)
- ✅ Test the API: `curl -X POST http://localhost:8080/api/tts -H 'Content-Type: application/json' -d '{"text":"test","language":"en"}' -o test.wav`
- ✅ After changing `.env`, recreate the container: `docker compose up -d`

**UI issues?**
- ✅ Clear browser cache and refresh
- ✅ Check browser console for JavaScript errors
- ✅ Verify all static assets are loading

**Performance issues?**
- ✅ Use smaller, faster models (e.g., `gemma4:e4b`)
- ✅ Increase system RAM
- ✅ Check available disk space
- ✅ Monitor system resources

### Debug Mode
```bash
# Enable detailed logging (logs go to `docker compose logs llot`)
echo "DEBUG_LOGGING=true" >> .env

# Recreate the container so it picks up .env changes
docker compose up -d
```

`FLASK_DEBUG=1` only affects `make dev` and enables the interactive Werkzeug debugger;
never use it on an instance reachable from other machines.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
- Use the issue template
- Include screenshots if UI-related
- Provide environment details
- Add reproduction steps

### ✨ Feature Requests  
- Check existing issues first
- Explain the use case
- Consider implementation complexity
- Provide mockups if UI-related

### 🔧 Code Contributions
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run test suite: `make test`
5. Submit pull request

### 🌐 Translations
Help translate LLOT interface:
1. Copy `app/translations/messages.pot`
2. Create new language folder
3. Translate strings using poedit or manually
4. Submit as pull request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Ollama](https://ollama.com)** - For making local LLM deployment simple
- **[Wyoming](https://github.com/OHF-Voice/wyoming)** / **[Piper](https://github.com/rhasspy/wyoming-piper)** - For local TTS
- **[Flask](https://flask.palletsprojects.com)** - For the robust web framework
- **[langdetect](https://github.com/Mimino666/langdetect)** - For language detection
- **Self-hosting community** - For inspiring privacy-first solutions