.PHONY: help install install-dev install-arial test demo-notebook pdf clean clean-outputs clean-old-legacy lint lint-fix format pre-commit demo-gui demo-gui-all demo-plot-all demo-composition

help:
	@echo "figrecipe - Record and reproduce matplotlib figures"
	@echo ""
	@echo "Usage:"
	@echo "  make install            Install package"
	@echo "  make install-dev        Install package with dev dependencies"
	@echo "  make install-arial      Install Arial font for matplotlib"
	@echo "  make test               Run tests"
	@echo "  make demo-notebook      Execute demo notebook"
	@echo "  make pdf                Generate PDF from notebook"
	@echo "  make clean              Clean build artifacts and outputs"
	@echo "  make clean-outputs      Clean only outputs directory"
	@echo "  make clean-old-legacy   Remove all .old and .legacy directories"
	@echo "  make lint               Run linter"
	@echo "  make lint-fix           Run linter with auto-fix"
	@echo "  make format             Format code"
	@echo "  make pre-commit         Install pre-commit hooks"
	@echo "  make demo-gui PORT=5050 Launch GUI editor demo (9 representative plots)"
	@echo "  make demo-gui-all       Launch GUI editor with ALL plot types (47 plots)"
	@echo "  make demo-plot-all      Generate all demo plots to examples/demo_all_plots_out/"
	@echo "  make demo-composition   Compose all plots into single figure"

PORT ?= 5050

install:
	@./scripts/maintenance/install.sh

install-dev:
	@./scripts/maintenance/install-dev.sh

install-arial:
	@./scripts/maintenance/install_arial.sh

test:
	@./scripts/maintenance/test.sh

demo-notebook:
	@./scripts/maintenance/notebook.sh

pdf:
	@./scripts/maintenance/pdf.sh

clean:
	@./scripts/maintenance/clean.sh

clean-outputs:
	@./scripts/maintenance/clean-outputs.sh

clean-old-legacy:
	@echo "Removing .old and .legacy directories..."
	@find . -type d \( -name ".old" -o -name ".legacy" \) -print -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete"

lint:
	@./scripts/maintenance/lint.sh

lint-fix:
	@./scripts/maintenance/lint-fix.sh

format:
	@./scripts/maintenance/format.sh

pre-commit:
	@./scripts/maintenance/pre-commit.sh

demo-gui:
	@./scripts/maintenance/demo-gui.sh $(PORT)

demo-gui-all:
	@echo "Launching GUI editor with ALL plot types..."
	@python3 ./examples/demo_editor.py $(PORT) --all

demo-plot-all:
	@echo "Generating all demo plots..."
	@python3 ./examples/demo_all_plots.py

demo-composition:
	@echo "Composing all plots into single figure..."
	@python3 ./examples/demo_composition.py
