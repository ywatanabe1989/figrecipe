.PHONY: help install install-dev test notebook pdf clean clean-outputs lint lint-fix format pre-commit gui gui-periodic

PYTHON := python3
PIP := pip3
PORT ?= 5050

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
	@echo "  make lint-fix      Run linter with auto-fix"
	@echo "  make format        Format code"
	@echo "  make pre-commit    Install pre-commit hooks"
	@echo "  make gui           Launch GUI editor demo (PORT=5050 by default)"
	@echo "  make gui PORT=5051 Launch GUI editor on custom port"
	@echo "  make gui-periodic  Launch GUI editor with 60s auto-restart (supports PORT=)"

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

lint-fix:
	$(PYTHON) -m ruff check --fix src/ tests/

format:
	$(PYTHON) -m ruff format src/ tests/

pre-commit:
	pip install pre-commit
	pre-commit install

gui:
	$(PYTHON) examples/demo_editor.py $(PORT)

gui-browser:
	@echo "Starting editor and opening in Windows Chrome on port $(PORT)..."
	@$(PYTHON) examples/demo_editor.py $(PORT) & \
	sleep 3 && \
	(cmd.exe /c start chrome http://127.0.0.1:$(PORT) 2>/dev/null || \
	 "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" http://127.0.0.1:$(PORT) 2>/dev/null || \
	 wslview http://127.0.0.1:$(PORT) 2>/dev/null || \
	 echo "Could not open browser. Please open http://127.0.0.1:$(PORT) manually") && \
	wait

gui-periodic:
	./scripts/gui_periodic.sh 60 $(PORT)
