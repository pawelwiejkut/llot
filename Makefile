.PHONY: help setup-env install dev prod deploy audit test e2e lint format check clean clean-docker status logs pull-model docker docker-standalone docker-full docker-down extract-strings update-translations compile-translations

help:		## Show this help
	@echo "🌐 LLOT - Local LLM Ollama Translator"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 🚀 Quick Start Commands
docker:		## Start with Docker Compose (requires existing Ollama)
	docker compose up -d
	@echo "✅ LLOT started! Open http://localhost:8080"

docker-standalone:	## Start with bundled Ollama (complete setup)
	docker compose -f docker-compose.standalone.yml up -d
	@echo "⏳ Starting Ollama... This may take a minute"
	@echo "📥 Don't forget to pull a model: make pull-model"

docker-full:	## Start bundled Ollama + Wyoming Piper TTS + LLOT
	docker compose -f docker-compose.full.yml up -d

docker-down:	## Stop all Docker services
	docker compose down
	docker compose -f docker-compose.standalone.yml down
	docker compose -f docker-compose.full.yml down

pull-model:	## Pull recommended translation model
	@if [ -x "$$(command -v ollama)" ]; then \
		echo "📥 Pulling gemma4:26b model..."; \
		ollama pull gemma4:26b; \
	else \
		echo "📥 Pulling model via Docker..."; \
		docker exec llot-ollama ollama pull gemma4:26b; \
	fi

# 🔧 Development Commands  
VENV ?= .venv
BIN := $(VENV)/bin

setup-env install:	## Create .venv with app + dev tools and a headless browser for e2e tests
	python3 -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -r requirements-dev.txt
	$(BIN)/playwright install --with-deps chromium
	@echo "✅ Dev environment ready in $(VENV)"

dev:		## Run development server
	$(BIN)/python run.py

prod:		## Run production server with gunicorn
	$(BIN)/gunicorn -w 2 --threads 4 --timeout 180 -b 0.0.0.0:8080 wsgi:app

deploy:		## Build, deploy with docker compose, health-check, auto-rollback
	scripts/deploy.sh

audit:		## Check dependencies for known vulnerabilities
	$(BIN)/pip-audit -r requirements.txt

# 🧪 Testing & Quality
test:		## Run unit tests with coverage
	$(BIN)/pytest --cov --cov-report=term-missing

e2e:		## Run browser tests against a running instance (LLOT_URL, default http://localhost:8080)
	$(BIN)/pytest -m e2e

lint:		## Lint and check formatting with ruff
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

format:		## Auto-fix lint issues and format with ruff
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

check: lint test audit	## Everything CI runs except e2e

# 🧹 Cleanup
clean:		## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	@echo "🧹 Cache cleaned!"

clean-docker:	## Clean up Docker containers and images
	docker compose down --rmi all --volumes --remove-orphans
	docker compose -f docker-compose.standalone.yml down --rmi all --volumes --remove-orphans
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
	docker compose logs -f llot

# 🌍 Translation Management  
extract-strings:	## Extract translatable strings (requires babel)
	$(BIN)/pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot app

update-translations:	## Update translation files (requires babel)
	$(BIN)/pybabel update -i app/translations/messages.pot -d app/translations

compile-translations:	## Compile .po files to .mo
	$(BIN)/pybabel compile -d app/translations