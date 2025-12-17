.PHONY: help install install-dev clean lint format type-check test test-cov pre-commit run-cli run-gui

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)概念マップ採点統合システム - 開発コマンド$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install core dependencies
	@echo "$(BLUE)Installing core dependencies...$(NC)"
	pip install -e .

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt
	@echo "$(GREEN)Development dependencies installed!$(NC)"
	@echo "$(YELLOW)Run 'make pre-commit-install' to set up git hooks$(NC)"

install-all: ## Install all dependencies (including optional)
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	pip install -e ".[all,dev]"
	pip install -r requirements-dev.txt

clean: ## Clean up build artifacts and cache
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build dist 2>/dev/null || true
	@echo "$(GREEN)Cleaned!$(NC)"

lint: ## Run linter (ruff)
	@echo "$(BLUE)Running ruff linter...$(NC)"
	ruff check .

lint-fix: ## Run linter with auto-fix
	@echo "$(BLUE)Running ruff linter with auto-fix...$(NC)"
	ruff check --fix .

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code with ruff...$(NC)"
	ruff format .

format-check: ## Check code formatting without modifying
	@echo "$(BLUE)Checking code formatting...$(NC)"
	ruff format --check .

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running mypy type checker...$(NC)"
	mypy concept_map_system

security: ## Run security checks (bandit)
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r concept_map_system -c pyproject.toml

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest --cov=concept_map_system --cov-report=html --cov-report=term-missing

test-verbose: ## Run tests in verbose mode
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	pytest -v

pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

pre-commit-run: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit on all files...$(NC)"
	pre-commit run --all-files

check: lint format-check type-check test ## Run all checks (lint, format, type-check, test)
	@echo "$(GREEN)All checks passed!$(NC)"

ci: ## Run CI checks (format-check, lint, type-check, test, security)
	@echo "$(BLUE)Running CI checks...$(NC)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) test
	@$(MAKE) security
	@echo "$(GREEN)CI checks passed!$(NC)"

run-cli: ## Run CLI interface
	@echo "$(BLUE)Running CLI (use --help for options)...$(NC)"
	python -m concept_map_system cli --list

run-gui: ## Run GUI interface
	@echo "$(BLUE)Running GUI...$(NC)"
	python -m concept_map_system gui

build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	python -m build

publish-test: build ## Publish to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	@echo "$(RED)Publishing to PyPI...$(NC)"
	python -m twine upload dist/*

dev: ## Set up complete development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@$(MAKE) install-dev
	@$(MAKE) pre-commit-install
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@$(MAKE) help

watch: ## Watch for changes and run tests
	@echo "$(BLUE)Watching for changes...$(NC)"
	pytest-watch

coverage-html: test-cov ## Generate and open HTML coverage report
	@echo "$(BLUE)Opening coverage report...$(NC)"
	open htmlcov/index.html || xdg-open htmlcov/index.html 2>/dev/null

list-algorithms: ## List available scoring algorithms
	@echo "$(BLUE)Available algorithms:$(NC)"
	python -m concept_map_system cli --list

example: ## Run example scoring
	@echo "$(BLUE)Running example scoring...$(NC)"
	@echo "$(YELLOW)Usage: make example MASTER=path/to/master.csv STUDENT=path/to/student.csv$(NC)"
	@if [ -z "$(MASTER)" ] || [ -z "$(STUDENT)" ]; then \
		echo "$(RED)Error: MASTER and STUDENT variables required$(NC)"; \
		echo "Example: make example MASTER=master.csv STUDENT=student.csv"; \
		exit 1; \
	fi
	python -m concept_map_system cli -a mcclure $(MASTER) $(STUDENT)
