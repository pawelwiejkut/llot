#!/usr/bin/env python3
"""
LLOT - Local LLM Ollama Translator
Main application entry point
"""

import os
import sys
from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    config = Config()
    print(f"Starting llot on http://{config.LISTEN_HOST}:{config.LISTEN_PORT}")
    print(f"Ollama: {config.OLLAMA_HOST}")
    print(f"Model: {config.DEFAULT_MODEL}")
    
    try:
        debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
        app.run(
            host=config.LISTEN_HOST, 
            port=config.LISTEN_PORT,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)