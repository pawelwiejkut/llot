.PHONY: help install run test clean dev prod docker docker-standalone docker-down setup-env

help:		## Show this help
	@echo "🌐 LLOT - Local LLM Ollama Translator"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 🚀 Quick Start Commands
docker:		## Start with Docker Compose (requires existing Ollama)
	docker-compose up -d
	@echo "✅ LLOT started! Open http://localhost:8080"

docker-standalone:	## Start with bundled Ollama (complete setup)
	docker-compose -f docker-compose.standalone.yml up -d
	@echo "⏳ Starting Ollama... This may take a minute"
	@echo "📥 Don't forget to pull a model: make pull-model"

docker-down:	## Stop all Docker services
	docker-compose down
	docker-compose -f docker-compose.standalone.yml down

pull-model:	## Pull recommended translation model
	@if [ -x "$$(command -v ollama)" ]; then \
		echo "📥 Pulling gemma2:9b model..."; \
		ollama pull gemma2:9b; \
	else \
		echo "📥 Pulling model via Docker..."; \
		docker exec llot-ollama ollama pull gemma2:9b; \
	fi

# 🔧 Development Commands  
setup-env:	## Setup development environment
	python3 -m venv venv
	@echo "📦 Virtual environment created!"
	@echo "🔧 Activate with: source venv/bin/activate"
	@echo "📥 Then run: make install"

install:	## Install Python dependencies
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

dev:		## Run development server
	@echo "🚀 Starting development server..."
	python run.py

prod:		## Run production server with gunicorn
	gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app

# 🧪 Testing & Quality
test:		## Run tests
	pytest tests/ -v

lint:		## Lint code with flake8 (if installed)
	@command -v flake8 >/dev/null 2>&1 && flake8 app/ tests/ || echo "💡 Install flake8 for linting: pip install flake8"

format:		## Format code with black (if installed)
	@command -v black >/dev/null 2>&1 && black app/ tests/ || echo "💡 Install black for formatting: pip install black"

# 🧹 Cleanup
clean:		## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	@echo "🧹 Cache cleaned!"

clean-docker:	## Clean up Docker containers and images
	docker-compose down --rmi all --volumes --remove-orphans
	docker-compose -f docker-compose.standalone.yml down --rmi all --volumes --remove-orphans
	@echo "🧹 Docker cleaned!"

# 📊 Info Commands
status:		## Show service status
	@echo "🔍 LLOT Service Status:"
	@if [ "$$(docker ps -q -f name=llot)" ]; then \
		echo "✅ LLOT container is running"; \
		echo "🌐 Web UI: http://localhost:8080"; \
	else \
		echo "❌ LLOT container not running"; \
	fi
	@if [ "$$(docker ps -q -f name=llot-ollama)" ]; then \
		echo "✅ Ollama container is running"; \
	elif [ -x "$$(command -v ollama)" ] && [ "$$(pgrep ollama)" ]; then \
		echo "✅ Ollama is running (host)"; \
	else \
		echo "❌ Ollama not detected"; \
	fi

logs:		## Show application logs
	docker-compose logs -f llot

# 🌍 Translation Management  
extract-strings:	## Extract translatable strings (requires babel)
	@command -v pybabel >/dev/null 2>&1 && pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot . || echo "💡 Install babel: pip install Flask-Babel"

update-translations:	## Update translation files (requires babel)
	@command -v pybabel >/dev/null 2>&1 && pybabel update -i app/translations/messages.pot -d app/translations || echo "💡 Install babel: pip install Flask-Babel"