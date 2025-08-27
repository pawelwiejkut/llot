# 🌐 LLOT - Local LLM Ollama Translator

> **Privacy-first AI translation service powered by local LLM models**  
> ✨ No API keys • No cloud services • No data collection • 100% self-hosted ✨

[![Self-Hosted](https://img.shields.io/badge/Self--Hosted-100%25-green?style=for-the-badge&logo=docker)](https://github.com/pawelwiejkut/llot)
[![Languages](https://img.shields.io/badge/Languages-65%2B-blue?style=for-the-badge)](https://github.com/pawelwiejkut/llot)
[![Privacy](https://img.shields.io/badge/Privacy-First-red?style=for-the-badge&logo=shield)](https://github.com/pawelwiejkut/llot)
[![Modern UI](https://img.shields.io/badge/Modern-UI-purple?style=for-the-badge)](https://github.com/pawelwiejkut/llot)

---

## 📸 Modern Interface

### 🎨 Light Mode
![LLOT Main Interface](docs/images/main-interface.png)
*Clean, intuitive interface with real-time translation*

![LLOT Translation Result](docs/images/translation-result.png)
*Translation in action - powered by local AI models*

### 🌙 Dark Mode  
![LLOT Dark Mode](docs/images/dark-mode.png)
*Beautiful dark theme for comfortable nighttime use*

### 📱 Mobile Responsive
![LLOT Mobile Interface](docs/images/mobile-interface.png)
*Perfect mobile experience - translate on any device*

---

## ✨ Why Choose LLOT?

| 🔒 **Complete Privacy** | ⚡ **Lightning Performance** | 🏠 **Homelab Perfect** |
|:---:|:---:|:---:|
| Your data never leaves your network | Instant translation with local AI | Docker deployment in under 5 minutes |
| No cloud APIs or tracking | Real-time as-you-type translation | Uses your existing Ollama server |
| Zero external dependencies | Smart language auto-detection | Lightweight Python Flask app |

| 🌍 **65+ Languages** | 🔊 **Neural TTS** | 🎛️ **Full Control** |
|:---:|:---:|:---:|
| Major world languages supported | High-quality speech synthesis | Choose your AI models |
| Auto language detection | 20+ TTS voices via Wyoming Piper | Configurable tone & style |
| Custom language filtering | Crystal-clear pronunciation | Your hardware, your rules |

---

## 🚀 Quick Start

### 🎯 Option 1: Use Your Existing Ollama Server
```bash
git clone https://github.com/pawelwiejkut/llot.git
cd llot

# Configure your Ollama server
echo "OLLAMA_HOST=http://your-ollama-server:11434" > .env
echo "OL_MODEL=llama3.2:3b" >> .env  # or your preferred model

# Start LLOT
docker-compose up -d

# Access at http://localhost:8080
```

### 🔧 Option 2: Complete Local Setup
```bash
git clone https://github.com/pawelwiejkut/llot.git
cd llot

# Includes Ollama + Wyoming Piper TTS
docker-compose -f docker-compose.full.yml up -d

# Access at http://localhost:8080
```

### ⚙️ Option 3: Native Installation
```bash
git clone https://github.com/pawelwiejkut/llot.git
cd llot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit your settings

# Run application
python run.py
```

---

## 🎛️ Features

### 🌐 **Translation Engine**
- **Real-time translation** as you type
- **65+ languages** supported
- **Auto language detection** powered by `langdetect`
- **Multiple tones**: neutral, formal, informal, friendly, technical, poetic
- **Model switching** - use any Ollama-compatible LLM
- **Translation history** with quick recall
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
- **High-quality neural TTS** via Wyoming Piper
- **20+ language voices** with natural pronunciation
- **Source and target** text playback
- **Caching system** for improved performance

### 🛠️ **Technical Excellence**
- **Modern Python** Flask application
- **Clean, refactored codebase** with proper error handling
- **Comprehensive test suite** with automated UI testing
- **Docker deployment** with multiple configurations
- **Environment-based configuration**
- **Health monitoring** and status checks
- **Detailed logging** for troubleshooting

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OL_MODEL=llama3.2:3b

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8080
FLASK_DEBUG=0

# TTS Configuration (optional)
WYOMING_PIPER_HOST=localhost
WYOMING_PIPER_PORT=10200

# Language Filtering (optional)
TRANSLATION_LANGUAGES=en,de,fr,es,it,pt,pl,ru,zh,ja,ko,ar,hi

# Debug Settings
DEBUG_LOGGING=false
```

### Supported Models

LLOT works with any Ollama-compatible model. Recommended models:

| Model | Size | Speed | Quality | Best For |
|-------|------|--------|---------|----------|
| `llama3.2:3b` | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | Fast translation |
| `llama3.1:8b` | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐ | Balanced performance |
| `gemma2:9b` | 5.4GB | ⚡⚡ | ⭐⭐⭐⭐ | High quality |
| `qwen2.5:14b` | 8.2GB | ⚡ | ⭐⭐⭐⭐⭐ | Professional use |

---

## 🐳 Docker Deployment

### Standard Setup (Use Existing Ollama)
```yaml
version: '3.8'
services:
  llot:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_HOST=http://your-ollama-server:11434
      - OL_MODEL=llama3.2:3b
    volumes:
      - ./logs:/app/logs
```

### Full Setup (Includes Ollama + TTS)
```bash
# Launches everything you need
docker-compose -f docker-compose.full.yml up -d
```

---

## 🌍 Supported Languages

**65+ languages supported** with smart auto-detection:

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

### Supported TTS Languages
- **English** (US) - Multiple voices
- **German** (DE) - Professional quality  
- **French** (FR) - Natural pronunciation
- **Spanish** (ES) - Clear articulation
- **Portuguese** (BR) - Brazilian accent
- **Polish** (PL) - Native speaker quality
- **And 15+ more languages**

### TTS Setup
```bash
# Install Wyoming Piper (if not using Docker)
pip install wyoming-piper

# Start TTS service
wyoming-piper --voice pl_PL-darkman-medium --port 10200

# Configure LLOT
echo "WYOMING_PIPER_HOST=localhost" >> .env
echo "WYOMING_PIPER_PORT=10200" >> .env
```

---

## 🧪 Testing & Quality

### Comprehensive Test Suite
```bash
# Unit tests
python -m pytest tests/ -v

# Comprehensive UI tests
python tests/comprehensive_app_tests.py

# Generate test reports
python tests/comprehensive_app_tests_extended.py
```

### Test Coverage
- ✅ **API Endpoints** - All translation, history, TTS endpoints
- ✅ **UI Functionality** - Language selection, dark mode, mobile responsive
- ✅ **Error Handling** - Empty inputs, server errors, timeouts
- ✅ **Performance** - Translation speed, page load times
- ✅ **Accessibility** - Keyboard navigation, screen readers

---

## ⚡ Performance

### Benchmarks
- **Page Load**: ~50ms
- **Translation Speed**: 2-15s (model dependent)
- **Memory Usage**: ~200MB (excluding models)
- **TTS Generation**: ~1-3s per sentence

### Optimization Tips
1. **Use faster models** like `llama3.2:3b` for speed
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

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run in development mode
export FLASK_DEBUG=1
python run.py
```

### Code Structure
```
llot/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Configuration management
│   ├── routes/               # API and web routes
│   │   ├── main.py          # Main web routes
│   │   ├── api.py           # Translation API
│   │   └── favicon.py       # Static asset routes
│   ├── services/            # Business logic
│   │   ├── translator.py    # Translation service
│   │   ├── ollama_client.py # Ollama API client
│   │   └── language_detector.py # Language detection
│   ├── models/              # Data models
│   │   ├── history.py       # Translation history
│   │   └── language.py      # Language definitions
│   ├── static/              # Frontend assets
│   │   ├── css/style-modern.css # Modern UI styles
│   │   └── js/app-modern.js  # Modern UI JavaScript
│   └── templates/           # Jinja2 templates
│       ├── index-modern.html # Modern UI template
│       └── backup/          # Classic UI backup
├── tests/                   # Test suites
├── docs/                    # Documentation
└── docker-compose.yml      # Docker configuration
```

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
4. Run test suite: `python -m pytest`
5. Submit pull request

### 🌐 Translations
Help translate LLOT interface:
1. Copy `app/translations/messages.pot`
2. Create new language folder
3. Translate strings using poedit or manually
4. Submit as pull request

---

## 📚 API Documentation

### Translation Endpoint
```bash
POST /api/translate
Content-Type: application/json

{
  "source_text": "Hello world",
  "source_lang": "en",    # or "auto"
  "target_lang": "pl", 
  "tone": "neutral"       # optional
}

# Response
{
  "translated_text": "Witaj świecie",
  "source_lang": "en",
  "target_lang": "pl"
}
```

### Text-to-Speech Endpoint
```bash
POST /api/tts
Content-Type: application/json

{
  "text": "Witaj świecie",
  "language": "pl"
}

# Response: audio/wav binary data
```

### Health Check
```bash
GET /api/health

# Response
{
  "ollama": {"status": "ok", "models": [...]},
  "tts": {"status": "ok"},
  "overall": "ok"
}
```

---

## 🐛 Troubleshooting

### Common Issues

**Translation not working?**
- ✅ Check Ollama server is running: `curl http://localhost:11434/api/tags`
- ✅ Verify model is available: `ollama list`
- ✅ Check LLOT logs: `docker-compose logs llot`

**TTS not working?**
- ✅ Verify Wyoming Piper is running: `curl http://localhost:10200`
- ✅ Check TTS configuration in `.env`
- ✅ Test direct API: `curl -X POST http://localhost:8080/api/tts -d '{"text":"test","language":"en"}'`

**UI issues?**
- ✅ Clear browser cache and refresh
- ✅ Check browser console for JavaScript errors
- ✅ Verify all static assets are loading

**Performance issues?**
- ✅ Use smaller, faster models (e.g., `llama3.2:3b`)
- ✅ Increase system RAM
- ✅ Check available disk space
- ✅ Monitor system resources

### Debug Mode
```bash
# Enable detailed logging
echo "DEBUG_LOGGING=true" >> .env
echo "FLASK_DEBUG=1" >> .env

# Restart application
docker-compose restart
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Support the Project

If LLOT helps you achieve translation privacy and independence:

- ⭐ **Star this repository** 
- 🐛 **Report issues** to help improve quality
- 🔧 **Contribute code** or documentation
- 🌍 **Share with the self-hosting community**

---

## 🙏 Acknowledgments

- **[Ollama](https://ollama.com)** - For making local LLM deployment simple
- **[Wyoming Piper](https://github.com/rhasspy/wyoming-piper)** - For excellent local TTS
- **[Flask](https://flask.palletsprojects.com)** - For the robust web framework
- **[langdetect](https://github.com/Mimino666/langdetect)** - For language detection
- **Self-hosting community** - For inspiring privacy-first solutions

---

<div align="center">

**🏠 Made for Self-Hosters, by Self-Hosters**

**🔒 Your Data • 🏠 Your Network • ⚡ Your Speed**

[🚀 Get Started](#-quick-start) • [📖 Documentation](#-api-documentation) • [🐛 Issues](https://github.com/pawelwiejkut/llot/issues) • [💬 Discussions](https://github.com/pawelwiejkut/llot/discussions)

</div>