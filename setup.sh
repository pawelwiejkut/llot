#!/bin/bash
# LLOT Setup Script
# Helps you configure LLOT for your environment

set -e

CONFIG_FILE=".llot_setup.conf"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to save configuration
save_config() {
    cat > "$CONFIG_FILE" << EOF
# LLOT Setup Configuration - Auto-generated
OLLAMA_CHOICE=$1
OLLAMA_HOST=$2
OLLAMA_PORT=$3
MODEL_NAME=$4
PIPER_HOST=$5
PIPER_PORT=$6
LANGUAGE_CODES=$7
LAST_UPDATED=$(date)
EOF
    echo "💾 Configuration saved to $CONFIG_FILE"
}

# Function to check for previous configuration
check_previous_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
        echo "🌐 LLOT - Local LLM Ollama Translator Setup"
        echo "=========================================="
        echo ""
        echo "📂 Found previous configuration from: $LAST_UPDATED"
        echo "   • Ollama choice: $OLLAMA_CHOICE"
        echo "   • Model: $MODEL_NAME"
        [[ -n "$OLLAMA_HOST" ]] && echo "   • Ollama: $OLLAMA_HOST:$OLLAMA_PORT"
        [[ -n "$PIPER_HOST" ]] && echo "   • Wyoming Piper: $PIPER_HOST:$PIPER_PORT"
        [[ -n "$LANGUAGE_CODES" ]] && echo "   • Languages: $LANGUAGE_CODES"
        echo ""
        read -p "Use previous configuration? (y/n): " use_previous
        if [[ $use_previous == "y" || $use_previous == "Y" ]]; then
            return 0
        else
            echo "Starting fresh configuration..."
            echo ""
            return 1
        fi
    else
        echo "🌐 LLOT - Local LLM Ollama Translator Setup"
        echo "=========================================="
        echo ""
        return 1
    fi
}

# Check for previous configuration at startup
if check_previous_config; then
    ollama_choice=$OLLAMA_CHOICE
    ollama_host=$OLLAMA_HOST
    ollama_port=$OLLAMA_PORT
    model_name=$MODEL_NAME
    piper_host=$PIPER_HOST
    piper_port=$PIPER_PORT
    language_codes=$LANGUAGE_CODES
    
    # Set up compose file based on previous choice
    case $ollama_choice in
        1) compose_file="docker-compose.local.yml" ;;
        2) compose_file="docker-compose.standalone.yml" ;;
        3) compose_file="docker-compose.full.yml" ;;
    esac
    
    # Skip to environment file creation
    skip_config=true
else
    skip_config=false
fi

# Check prerequisites only if not using previous config
if [[ $skip_config == false ]]; then
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
fi

# Ask about Ollama (skip if using previous config)
if [[ $skip_config == false ]]; then
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
fi # End of skip_config check

# Ask about Wyoming Piper if not already included (skip if using previous config)
if [[ $skip_config == false ]] && [[ $ollama_choice != "3" ]]; then
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

# Ask about model preference (skip if using previous config)
if [[ $skip_config == false ]]; then
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
fi # End of skip_config check for model

# Ask about language limitations (skip if using previous config)
if [[ $skip_config == false ]]; then
echo "🌍 Language Configuration"
echo "========================="
echo "By default, LLOT supports 40+ translation languages."
echo "Would you like to limit available languages to improve performance?"
echo ""
read -p "Limit languages? (y/n): " limit_languages

if [[ $limit_languages == "y" || $limit_languages == "Y" ]]; then
    read -p "Enter language codes (default: en,de,pl,cs): " language_codes
    language_codes=${language_codes:-"en,de,pl,cs"}
    echo "✅ Limited to languages: $language_codes"
else
    language_codes=""
    echo "✅ All 40+ languages will be available"
fi
echo ""
fi # End of skip_config check for languages

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
${language_codes:+TRANSLATION_LANGUAGES=$language_codes}
${language_codes:+# Remove the # above to activate language limitation}
EOF

echo "✅ Created .env file"

# Save current configuration
save_config "$ollama_choice" "$ollama_host" "$ollama_port" "$model_name" "$piper_host" "$piper_port" "$language_codes"
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
if [[ -n "$language_codes" ]]; then
    echo "  • Languages: $language_codes"
else
    echo "  • Languages: All 40+ supported"
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