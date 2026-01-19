#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-19 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/00_run_all.sh

# Run all figrecipe examples in sequence.
# Usage: ./00_run_all.sh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "FigRecipe Examples Runner"
echo "========================================"
echo

# 01: Generate all plot types
echo "[1/3] Running 01_all_plots.py..."
python 01_all_plots.py
echo "Done."
echo

# 02: Compose plots into single figure
echo "[2/3] Running 02_composition.py..."
python 02_composition.py
echo "Done."
echo

# 03: Editor demo (skipped in batch mode - requires GUI)
echo "[3/3] Skipping 03_editor.py (requires GUI)"
echo "      Run manually: python 03_editor.py [PORT]"
echo

# 04: MCP demo (org file - for interactive use)
echo "[Note] 04_mcp.org is an interactive org-mode demo."
echo "       Open in Emacs with Claude Code for live demo."
echo

echo "========================================"
echo "Examples completed!"
echo "========================================"
echo "Output directories:"
echo "  - 01_all_plots_out/    (individual plots)"
echo "  - 02_composition_out/  (composed figure)"
echo
