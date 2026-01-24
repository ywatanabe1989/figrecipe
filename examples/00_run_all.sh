#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/00_run_all.sh

# Run all figrecipe examples in sequence.
# Usage: ./00_run_all.sh [--help]

set -e # Exit on error

show_help() {
    echo "Usage: ./00_run_all.sh [OPTIONS]"
    echo ""
    echo "Run all figrecipe examples in sequence."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "Examples run:"
    echo "  01_all_plots.py      Generate all plot types"
    echo "  02_composition.py    Compose plots into single figure"
    echo "  03_style_anatomy.py  Generate style anatomy diagram"
    echo "  05_csv_workflow.py   CSV-based workflow demo"
    echo "  06_diagram.py        Diagram generation demo"
    echo ""
    echo "Skipped (requires interaction):"
    echo "  03_editor.py         GUI editor (run manually)"
    echo "  04_mcp.org           MCP demo (interactive)"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "FigRecipe Examples Runner"
echo "========================================"
echo

# 01: Generate all plot types
echo "[1/5] Running 01_all_plots.py..."
python 01_all_plots.py
echo "Done."
echo

# 02: Compose plots into single figure
echo "[2/5] Running 02_composition.py..."
python 02_composition.py
echo "Done."
echo

# 03: Style anatomy diagram
echo "[3/5] Running 03_style_anatomy.py..."
python 03_style_anatomy.py
echo "Done."
echo

# Skip editor (requires GUI)
echo "[Note] Skipping 03_editor.py (requires GUI)"
echo "       Run manually: python 03_editor.py [PORT]"
echo

# 04: MCP demo (org file - for interactive use)
echo "[Note] 04_mcp.org is an interactive org-mode demo."
echo "       Open in Emacs with Claude Code for live demo."
echo

# 05: CSV workflow
echo "[4/5] Running 05_csv_workflow.py..."
python 05_csv_workflow.py
echo "Done."
echo

# 06: Diagram demo
echo "[5/5] Running 06_diagram.py..."
python 06_diagram.py
echo "Done."
echo

echo "========================================"
echo "Examples completed!"
echo "========================================"
echo "Output directories:"
echo "  - 01_all_plots_out/      (individual plots)"
echo "  - 02_composition_out/    (composed figure)"
echo "  - 03_style_anatomy_out/  (style anatomy)"
echo "  - 05_csv_workflow_out/   (CSV workflow)"
echo "  - 06_diagram_out/        (diagrams)"
echo
