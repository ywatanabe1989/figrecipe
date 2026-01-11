.PHONY: help install install-dev install-arial test notebook pdf clean clean-outputs lint lint-fix format pre-commit demo-gui demo-gui-browser demo-gui-periodic

help:
	@echo "figrecipe - Record and reproduce matplotlib figures"
	@echo ""
	@echo "Usage:"
	@echo "  make install            Install package"
	@echo "  make install-dev        Install package with dev dependencies"
	@echo "  make install-arial      Install Arial font for matplotlib"
	@echo "  make test               Run tests"
	@echo "  make notebook           Execute demo notebook"
	@echo "  make pdf                Generate PDF from notebook"
	@echo "  make clean              Clean build artifacts and outputs"
	@echo "  make clean-outputs      Clean only outputs directory"
	@echo "  make lint               Run linter"
	@echo "  make lint-fix           Run linter with auto-fix"
	@echo "  make format             Format code"
	@echo "  make pre-commit         Install pre-commit hooks"
	@echo "  make demo-gui           Launch GUI editor demo (PORT=5050 by default)"
	@echo "  make demo-gui PORT=5051 Launch GUI editor on custom port"
	@echo "  make demo-gui-browser   Launch GUI editor and open in browser"
	@echo "  make demo-gui-periodic  Launch GUI editor with 60s auto-restart (supports PORT=)"

PORT ?= 5050

install:
	@./scripts/maintenance/install.sh

install-dev:
	@./scripts/maintenance/install-dev.sh

install-arial:
	@./scripts/maintenance/install_arial.sh

test:
	@./scripts/maintenance/test.sh

notebook:
	@./scripts/maintenance/notebook.sh

pdf:
	@./scripts/maintenance/pdf.sh

clean:
	@./scripts/maintenance/clean.sh

clean-outputs:
	@./scripts/maintenance/clean-outputs.sh

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

demo-gui-browser:
	@./scripts/maintenance/demo-gui-browser.sh $(PORT)

demo-gui-periodic:
	@./scripts/maintenance/demo-gui-periodic.sh 60 $(PORT)
