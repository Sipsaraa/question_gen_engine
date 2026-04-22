.PHONY: help up down build logs logs-tail shell-generator dev-setup lint test clean verify-gen

# Color highlighting for terminal output
GREEN = \033[0;32m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}'

# Docker Compose Commands
up: ## Start the Question Gen Engine local docker environment
	docker compose up -d

up-build: ## Build and start the Question Gen Engine environment
	docker compose up --build -d

down: ## Stop the Question Gen Engine environment
	docker compose down

build: ## Build the docker images
	docker compose build

logs: ## View the logs
	docker compose logs -f

shell: ## Open a bash shell in the engine container
	docker compose exec qt-engine bash

# Local Development Commands
dev-setup: ## Set up local dev environment with uv
	uv sync
	@echo "${GREEN}Environment synced! Use 'uv run' or activate .venv.${NC}"

lint: ## Check code style
	uv run flake8 src/ tests/

test: ## Run tests
	uv run pytest -v

docs-serve: ## Serve documentation locally
	uv run mkdocs serve

docs-build: ## Build documentation site
	uv run mkdocs build

clean: ## Clean up caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
