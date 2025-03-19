.PHONY: install install-dev test test-cov lint format clean docs docs-clean help

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=a2e --cov-report=term-missing

lint:
	flake8
	mypy
	black --check .
	isort --check-only .

format:
	black .
	isort .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf .tox/
	rm -rf .nox/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .hypothesis/
	rm -rf docs/_build/
	rm -rf docs/api/

docs:
	sphinx-build -b html docs/ docs/_build/

docs-clean:
	rm -rf docs/_build/
	rm -rf docs/api/

help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linters and type checkers"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Remove build and cache files"
	@echo "  docs         - Build documentation"
	@echo "  docs-clean   - Remove documentation build files"
	@echo "  help         - Show this help message" 