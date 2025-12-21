.PHONY: help install install-dev test examples clean clean-outputs lint format

PYTHON := python3
PIP := pip3

help:
	@echo "plotspec - Record and reproduce matplotlib figures"
	@echo ""
	@echo "Usage:"
	@echo "  make install       Install package"
	@echo "  make install-dev   Install package with dev dependencies"
	@echo "  make test          Run tests"
	@echo "  make examples      Run all examples"
	@echo "  make clean         Clean build artifacts and outputs"
	@echo "  make clean-outputs Clean only outputs directory"
	@echo "  make lint          Run linter"
	@echo "  make format        Format code"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v

examples: examples-basic examples-demo examples-roundtrip examples-seaborn

examples-basic:
	@echo "Running basic usage example..."
	$(PYTHON) examples/01_basic_usage.py

examples-demo:
	@echo "Running demo..."
	$(PYTHON) examples/demo.py

examples-roundtrip:
	@echo "Running roundtrip tests..."
	$(PYTHON) examples/roundtrip_all_types.py

examples-seaborn:
	@echo "Running seaborn example..."
	$(PYTHON) examples/05_seaborn.py

clean: clean-outputs
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-outputs:
	rm -rf outputs/

lint:
	$(PYTHON) -m ruff check src/ tests/ examples/

format:
	$(PYTHON) -m ruff format src/ tests/ examples/
