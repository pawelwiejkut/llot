# 🚀 LLOT Quick Start Guide

**Get LLOT running in under 2 minutes!**

## 🎯 Choose Your Setup

### Option 1: I already have Ollama running (Recommended)

```bash
git clone https://github.com/yourusername/llot.git
cd llot
docker-compose up -d
```

**Done!** Open http://localhost:8080

---

### Option 2: I need everything (LLOT + Ollama)

```bash
git clone https://github.com/yourusername/llot.git
cd llot
docker-compose -f docker-compose.standalone.yml up -d

# Wait for Ollama to start, then pull a model
docker exec llot-ollama ollama pull gemma2:9b
```

**Done!** Open http://localhost:8080

---

### Option 3: Manual installation (Python)

```bash
git clone https://github.com/yourusername/llot.git
cd llot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Done!** Open http://localhost:8080

---

## 🤖 Recommended First Steps

1. **Install a good translation model:**
   ```bash
   ollama pull gemma2:9b  # Balanced performance
   # or
   ollama pull llama3:8b  # Alternative
   ```

2. **Test translation:**
   - Type "Hello world" in the source box
   - Select target language
   - Watch it translate automatically!

3. **Try interactive features:**
   - Click any word in the result for alternatives
   - Use the language swap button
   - Check out different tones

---

## 🔧 Troubleshooting

**LLOT can't connect to Ollama?**

- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Linux users: Edit `.env` and set `OLLAMA_HOST=http://172.17.0.1:11434`
- Windows/Mac: Should work with default settings

**Translation is slow?**

- Try a smaller model: `ollama pull gemma2:2b`
- Check if your model is loaded: `ollama ps`

**Need help?**

- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/llot/issues)

---

**🎉 That's it! Happy translating!**