.PHONY: all lint format test typecheck coverage clean help

# Default target
all: lint format test coverage

# Run ruff lint check
lint:
	@echo "Running ruff check..."
	uv run ruff check src/ tests/

# Run ruff format check
format-check:
	@echo "Checking format..."
	uv run ruff format --check src/ tests/

# Run ruff format
format:
	@echo "Formatting code..."
	uv run ruff format src/ tests/

# Run type checking (mypy and pyright)
typecheck:
	@echo "Running mypy..."
	uv run mypy src/
	@echo ""
	@echo "Running pyright..."
	uv run pyright src/

# Run all tests with coverage
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# Run tests with coverage report
coverage: test
	@echo ""
	@echo "Coverage report:"
	uv run pytest tests/ --cov --cov-fail-under=80

# Clean cache files
clean:
	@echo "Cleaning cache..."
	rm -rf .pytest_cache .coverage coverage.xml
	rm -rf .pyright_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# CI validation (all checks)
ci: lint format-check typecheck coverage

# Help
help:
	@echo "Available targets:"
	@echo "  all        - Run lint, format, test, and coverage (default)"
	@echo "  lint       - Run ruff check"
	@echo "  format     - Format code with ruff"
	@echo "  format-check - Check code format"
	@echo "  typecheck  - Run mypy and pyright"
	@echo "  test       - Run all tests"
	@echo "  coverage   - Run tests with coverage (fails if < 80%)"
	@echo "  ci         - Run all CI checks"
	@echo "  clean      - Clean cache files"
	@echo "  help       - Show this help"
