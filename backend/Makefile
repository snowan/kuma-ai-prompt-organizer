.PHONY: install test lint format check-format mypy test-cov clean help

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
ISORT = isort -rc
FLAKE8 = flake8
MYPY = mypy
COVERAGE = coverage

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install development dependencies"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Run linters (black, isort, flake8)"
	@echo "  make format       Format code with black and isort"
	@echo "  make check-format Check code formatting"
	@echo "  make mypy         Run type checking"
	@echo "  make clean        Clean up temporary files"

# Install development dependencies
install:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

# Run tests
test:
	$(PYTEST) -v tests/

# Run tests with coverage
test-cov:
	$(PYTEST) -v --cov=app --cov-report=term-missing tests/

# Run linters
lint: check-format
	$(FLAKE8) app/
	$(MYPY) app/

# Format code
format:
	$(BLACK) app/ tests/
	$(ISORT) app/ tests/

# Check code formatting
check-format:
	$(BLACK) --check app/ tests/
	$(ISORT) --check-only app/ tests/

# Run type checking
mypy:
	$(MYPY) app/

# Clean up
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '*.mypy_cache' -exec rm -rf {} +
	find . -type d -name '*.pytest_cache' -exec rm -rf {} +
	rm -rf .coverage htmlcov/ build/ dist/ *.egg-info/
