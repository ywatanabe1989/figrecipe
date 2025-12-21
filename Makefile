.PHONY: help install install-dev test notebook pdf clean clean-outputs lint format

PYTHON := python3
PIP := pip3

help:
	@echo "figrecipe - Record and reproduce matplotlib figures"
	@echo ""
	@echo "Usage:"
	@echo "  make install       Install package"
	@echo "  make install-dev   Install package with dev dependencies"
	@echo "  make test          Run tests"
	@echo "  make notebook      Execute demo notebook"
	@echo "  make pdf           Generate PDF from notebook"
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

notebook:
	@echo "Executing demo notebook..."
	$(PYTHON) -m jupyter nbconvert --to notebook --execute --inplace examples/figrecipe_demo.ipynb --ExecutePreprocessor.timeout=120

pdf: notebook
	@echo "Generating PDF from notebook..."
	jupyter nbconvert --to pdf examples/figrecipe_demo.ipynb --output-dir=examples
	@rm -rf plotspec_demo_files notebook.* 2>/dev/null || true
	@echo "PDF generated: examples/figrecipe_demo.pdf"

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
	$(PYTHON) -m ruff check src/ tests/

format:
	$(PYTHON) -m ruff format src/ tests/
