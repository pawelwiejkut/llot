# 🌐 LLOT - Local LLM Ollama Translator

> **Privacy-first, self-hosted translation service powered by local LLMs**

**No data leaves your network.** **No API keys required.** **100% offline translation** using your own Ollama models.

![LLOT Screenshot](https://img.shields.io/badge/Self--Hosted-100%25-green?style=for-the-badge&logo=docker)
![Languages](https://img.shields.io/badge/Languages-40%2B-blue?style=for-the-badge)
![Privacy](https://img.shields.io/badge/Privacy-First-red?style=for-the-badge&logo=shield)

---

## 🚀 Why LLOT?

**Perfect for self-hosters who value privacy and control:**

- 🔒 **Complete Privacy** - All translations happen locally on your hardware
- 🏠 **Self-Hosted** - Deploy on your homelab, VPS, or any server you control
- 🌍 **40+ Languages** - Interface supports major world languages + European languages
- ⚡ **Real-time Translation** - Instant translation as you type
- 🎯 **Smart Language Detection** - Automatically detects source language
- 🔧 **Tone Control** - Formal, informal, technical, or poetic translations
- 📝 **Interactive Refinement** - Click any word to get alternative translations
- 📚 **Translation History** - Keep track of your recent translations
- 🐳 **Docker Ready** - One-command deployment with Docker Compose
- 🎨 **Modern UI** - Responsive design that works on all devices

---

## 📋 Prerequisites

- **Ollama** installed and running (with translation models like `gemma2`, `llama3`, `mistral`)
- **Docker & Docker Compose** (recommended) OR **Python 3.8+**
- **2GB+ RAM** (depends on your chosen model)

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

**The fastest way to get up and running:**

```bash
# Clone and start
git clone https://github.com/yourusername/llot.git
cd llot
docker-compose up -d

# Access at http://localhost:8080
```

**That's it!** LLOT will automatically connect to your Ollama instance.

### Option 2: Manual Installation

**For more control over your setup:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/llot.git
cd llot

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (optional)
cp .env.example .env
# Edit .env if needed

# 5. Run
python run.py
```

---

## ⚙️ Configuration

Create `.env` file for custom settings:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OL_MODEL=gemma3:27b                   # Your preferred model

# App Settings  
APP_HOST=0.0.0.0
APP_PORT=8080

# Production Settings
FLASK_ENV=production
FLASK_DEBUG=0

# Language Configuration
# Optional: Limit available translation languages (comma-separated)
# If not set, all 40+ supported languages will be available
TRANSLATION_LANGUAGES=en,es,fr,de,pl,it,pt
```

### Language Settings

- **Interface Language**: Automatically detected from browser's Accept-Language header in production mode
- **Debug Mode**: Manual language selector available when `FLASK_DEBUG=1` 
- **Translation Languages**: Configurable via `TRANSLATION_LANGUAGES` environment variable

### 🤖 Recommended Setup

**Preferred configuration for best results:**

- **Model**: `gemma3:27b` for optimal translation quality
- **Hardware**: RTX 3090 or similar GPU recommended  
- **Memory**: 32GB+ RAM for smooth performance

**Quick setup:**
```bash
ollama pull gemma3:27b
```

---

## 🏆 Why Self-Hosters Love LLOT

### ✅ **Privacy First**
- **100% Local Processing** - Your translations never leave your server
- **No API Keys Required** - No external service dependencies  
- **No Data Collection** - Zero telemetry, zero tracking
- **Offline Capable** - Works without internet after setup

### ⚡ **Performance & Efficiency**
- **Lightning Fast** - Sub-second translations with local LLMs
- **Resource Friendly** - Optimized for home server hardware  
- **Memory Efficient** - Translation history stored in browser localStorage
- **Docker Ready** - One-command deployment with compose

### 🛠️ **Self-Hosted Friendly**
- **Modern Architecture** - Clean Flask app with proper separation
- **Easy Configuration** - Simple `.env` file setup
- **Reverse Proxy Ready** - Works behind nginx/traefik/caddy
- **Health Checks** - Built-in monitoring endpoints
- **Auto-Updates** - Git pull and rebuild workflow

> 💬 **r/selfhosted approved!** Join the discussion and share your setup!

---

## 🌍 Supported Languages

**Interface available in 40+ languages including:**

### 🌍 Major World Languages
🇬🇧 English • 🇨🇳 中文 • 🇮🇳 हिन्दी • 🇪🇸 Español • 🇫🇷 Français • 🇸🇦 العربية • 🇧🇩 বাংলা • 🇵🇹 Português • 🇷🇺 Русский • 🇵🇰 اردو • 🇮🇩 Indonesia • 🇩🇪 Deutsch • 🇯🇵 日本語 • 🇹🇷 Türkçe • 🇰🇷 한국어 • 🇻🇳 Tiếng Việt

### 🇪🇺 European Languages  
🇵🇱 Polski • 🇮🇹 Italiano • 🇳🇱 Nederlands • 🇸🇪 Svenska • 🇩🇰 Dansk • 🇳🇴 Norsk • 🇫🇮 Suomi • 🇨🇿 Čeština • 🇸🇰 Slovenčina • 🇭🇺 Magyar • 🇷🇴 Română • 🇧🇬 Български • 🇭🇷 Hrvatski • 🇸🇮 Slovenščina • 🇱🇻 Latviešu • 🇱🇹 Lietuvių • 🇪🇪 Eesti • 🇬🇷 Ελληνικά • 🇲🇹 Malti • 🇮🇪 Gaeilge

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```yaml
# docker-compose.yml included in repo
version: '3.8'

services:
  llot:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434  # For Docker Desktop
      # - OLLAMA_HOST=http://172.17.0.1:11434         # For Linux Docker
    restart: unless-stopped
```

### Using Docker

```bash
# Build and run
docker build -t llot .
docker run -d \
  --name llot \
  -p 8080:8080 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --restart unless-stopped \
  llot
```

---

## 🏗️ Architecture

**Modern, maintainable Flask application:**

```
llot/
├── app/
│   ├── models/           # Data models (languages, history)
│   ├── services/         # Business logic (translation, ollama client)
│   ├── routes/           # API endpoints and web routes
│   ├── templates/        # HTML templates with i18n
│   ├── static/           # CSS, JavaScript, assets
│   └── translations/     # 40+ language translations
├── tests/                # Unit tests
├── docker-compose.yml    # Easy deployment
├── Dockerfile           # Container definition
└── requirements.txt     # Python dependencies
```

**Key Technologies:**
- **Flask** with modern Blueprint architecture
- **Flask-Babel** for internationalization
- **Ollama API** for local LLM communication
- **SQLite** for lightweight data storage (history)
- **Docker** for easy deployment

---

## 🔧 Development

**Contributing or customizing:**

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
make test
# or
pytest tests/ -v

# Run development server
make dev
# or  
python run.py

# Lint and format
make lint
make format
```

### Adding New Languages

1. Add language to `app/config.py`:
```python
LANGUAGES = {
    'your_lang': 'Your Language Name',
    # ...
}
```

2. Create translation files:
```bash
mkdir -p app/translations/your_lang/LC_MESSAGES/
cp app/translations/en/LC_MESSAGES/messages.po app/translations/your_lang/LC_MESSAGES/
# Translate the file
```

3. Add JavaScript translations to `app/static/js/app.js`

---

## 🔒 Privacy & Security

**Why LLOT is perfect for privacy-conscious users:**

- ✅ **No external API calls** - Everything runs locally
- ✅ **No data collection** - We don't store, log, or transmit your translations  
- ✅ **No telemetry** - Zero tracking or analytics
- ✅ **No internet required** - Works completely offline
- ✅ **You control the models** - Use any Ollama-compatible model
- ✅ **Self-hosted** - Your server, your rules
- ✅ **Open source** - Inspect every line of code

**Perfect for:**
- 🏢 **Corporate environments** with strict data policies
- 🏠 **Home users** who value privacy
- 🌐 **Air-gapped networks** without internet access
- 🏥 **Healthcare/Legal** with sensitive documents
- 🎓 **Educational institutions** with student privacy requirements

---

## 📊 API Reference

**RESTful API for integration:**

```bash
# Translate text
POST /api/translate
{
  "source_text": "Hello world",
  "source_lang": "en", 
  "target_lang": "es",
  "tone": "neutral"
}

# Get alternative translations
POST /api/alternatives
{
  "source_text": "Hello world",
  "current_translation": "Hola mundo", 
  "clicked_word": "mundo",
  "target_lang": "es"
}

# Save to history
POST /api/history/save
{
  "source_text": "Hello",
  "translated": "Hola",
  "target_lang": "es" 
}
```

---

## 🤝 Community & Support

**Join the self-hosted community:**

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/llot/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/llot/discussions)
- 🗨️ **Chat**: [Discord Server](#) or [Matrix Room](#)
- 📖 **Wiki**: [Documentation](https://github.com/yourusername/llot/wiki)

**Contributing:**
- PRs welcome for new languages, features, or bug fixes
- See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- Join our monthly community calls

---

## 📝 License

**MIT License** - Use commercially, modify freely, share with attribution.

See [LICENSE](LICENSE) for full details.

---

## ⭐ Star History

**If LLOT helps you maintain privacy while translating, consider starring the repo!**

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/llot&type=Date)](https://github.com/yourusername/llot/stargazers)

---

**🚀 Ready to translate privately? [Get started now](#-quick-start)**