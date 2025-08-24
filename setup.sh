#!/bin/bash
# LLOT Setup Script
# Helps you configure LLOT for your environment

set -e

echo "🌐 LLOT - Local LLM Ollama Translator Setup"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Ask about Ollama
echo "📡 Ollama Configuration"
echo "======================"
echo "LLOT needs access to an Ollama server for translation."
echo ""
echo "Choose your Ollama setup:"
echo "1) I have Ollama running on another server (URL required)"
echo "2) I want to install Ollama locally with Docker"
echo "3) I want the complete setup (Ollama + Wyoming Piper TTS)"
echo ""
read -p "Enter your choice (1-3): " ollama_choice

case $ollama_choice in
    1)
        echo ""
        echo "🔗 External Ollama Configuration"
        echo "================================"
        read -p "Enter your Ollama server IP/hostname: " ollama_host
        read -p "Enter Ollama port (default 11434): " ollama_port
        ollama_port=${ollama_port:-11434}
        
        if [[ -z "$ollama_host" ]]; then
            echo "❌ Ollama host cannot be empty"
            exit 1
        fi
        
        ollama_url="http://$ollama_host:$ollama_port"
        
        # Create local docker-compose with external Ollama
        cat > docker-compose.local.yml << EOF
version: '3.8'

services:
  llot:
    build: .
    container_name: llot
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_HOST=$ollama_url
      - OL_MODEL=\${OL_MODEL:-gemma3:27b}
      - APP_HOST=0.0.0.0
      - APP_PORT=8080
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    restart: unless-stopped
    networks:
      - llot-network

networks:
  llot-network:
    driver: bridge
EOF
        
        compose_file="docker-compose.local.yml"
        echo "✅ Created configuration for external Ollama: $ollama_host:$ollama_port"
        ;;
        
    2)
        echo ""
        echo "🐳 Local Ollama Installation"
        echo "============================"
        echo "This will install Ollama in a Docker container."
        compose_file="docker-compose.standalone.yml"
        echo "✅ Will use local Ollama installation"
        ;;
        
    3)
        echo ""
        echo "🚀 Complete Installation"
        echo "========================"
        echo "This will install both Ollama and Wyoming Piper TTS locally."
        compose_file="docker-compose.full.yml"
        echo "✅ Will use complete local installation"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""

# Ask about Wyoming Piper if not already included
if [[ $ollama_choice != "3" ]]; then
    echo "🔊 Wyoming Piper TTS (Optional)"
    echo "==============================="
    echo "Would you like text-to-speech functionality?"
    echo ""
    read -p "Do you have a Wyoming Piper server? (y/n): " has_piper
    
    if [[ $has_piper == "y" || $has_piper == "Y" ]]; then
        read -p "Enter Wyoming Piper server IP/hostname: " piper_host
        read -p "Enter Wyoming Piper port (default 10200): " piper_port
        piper_port=${piper_port:-10200}
        
        # Add Wyoming Piper configuration to .env file (handled later)
        echo "ℹ️  Wyoming Piper will be configured in .env file"
        
        echo "✅ Configured Wyoming Piper TTS: $piper_host:$piper_port"
    else
        echo "ℹ️  TTS will be disabled (no audio playback)"
    fi
    echo ""
fi

# Ask about model preference
echo "🤖 Model Configuration"
echo "======================"
echo "Which Gemma3 model would you like to use for translation?"
echo "1) gemma3:27b (best quality)"
echo "2) gemma3:12b (balanced performance)"  
echo "3) gemma3:4b (multimodal support)"
echo "4) gemma3:1b (lightweight)"
echo "5) Custom model"
echo ""
read -p "Enter your choice (1-5): " model_choice

case $model_choice in
    1) model_name="gemma3:27b" ;;
    2) model_name="gemma3:12b" ;;
    3) model_name="gemma3:4b" ;;
    4) model_name="gemma3:1b" ;;
    5) 
        read -p "Enter your custom model name: " model_name
        if [[ -z "$model_name" ]]; then
            echo "❌ Model name cannot be empty"
            exit 1
        fi
        ;;
    *) 
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Update compose file with chosen model
if [[ $ollama_choice == "1" ]]; then
    sed -i.bak "s/OL_MODEL:-gemma3:27b}/OL_MODEL:-$model_name}/" docker-compose.local.yml
    rm docker-compose.local.yml.bak
fi

echo "✅ Model configured: $model_name"
echo ""

# Create .env file
echo "📝 Creating environment configuration..."
cat > .env << EOF
# LLOT Configuration
OLLAMA_HOST=${ollama_url:-http://ollama:11434}
OL_MODEL=$model_name
APP_HOST=0.0.0.0
APP_PORT=8080
FLASK_ENV=production
FLASK_DEBUG=0

# Optional: Wyoming Piper TTS
${piper_host:+WYOMING_PIPER_HOST=$piper_host}
${piper_port:+WYOMING_PIPER_PORT=$piper_port}

# Optional: Limit available languages (comma-separated)
# TRANSLATION_LANGUAGES=en,de,pl,es,fr
EOF

echo "✅ Created .env file"
echo ""

# Final summary and startup
echo "🎉 Setup Complete!"
echo "=================="
echo "Configuration:"
echo "  • Compose file: $compose_file"
echo "  • Ollama model: $model_name"
if [[ -n "$ollama_host" ]]; then
    echo "  • Ollama server: $ollama_host:$ollama_port"
fi
if [[ -n "$piper_host" ]]; then
    echo "  • Wyoming Piper: $piper_host:$piper_port"
fi
echo ""

read -p "Would you like to start LLOT now? (y/n): " start_now

if [[ $start_now == "y" || $start_now == "Y" ]]; then
    echo ""
    echo "🚀 Starting LLOT..."
    docker-compose -f $compose_file up -d
    
    echo ""
    echo "✅ LLOT is starting up!"
    echo "📍 Access LLOT at: http://localhost:8080"
    echo ""
    
    if [[ $ollama_choice == "2" || $ollama_choice == "3" ]]; then
        echo "⏳ Note: First startup may take several minutes while Ollama downloads the model."
        echo "📚 To download the model manually:"
        echo "   docker exec llot-ollama ollama pull $model_name"
    fi
    
    echo ""
    echo "📋 Useful commands:"
    echo "   • View logs: docker-compose -f $compose_file logs -f"
    echo "   • Stop LLOT: docker-compose -f $compose_file down"
    echo "   • Update LLOT: git pull && docker-compose -f $compose_file up -d --build"
else
    echo ""
    echo "✅ Setup complete! Start LLOT later with:"
    echo "   docker-compose -f $compose_file up -d"
fi

echo ""
echo "📖 For more information, see README.md"
echo "🐛 Issues? Visit: https://github.com/pawelwiejkut/llot/issues"