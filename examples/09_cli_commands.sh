#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/08_cli_commands.sh

# FigRecipe CLI Commands Demo
# ===========================
#
# This script demonstrates all figrecipe CLI commands.
# Run: ./08_cli_commands.sh

set -e

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$THIS_DIR")"
PYTHON="$PROJECT_DIR/.venv/bin/python"
FIGRECIPE="$PROJECT_DIR/.venv/bin/figrecipe"
OUTPUT_DIR="$THIS_DIR/08_cli_commands_out"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "FigRecipe CLI Commands Demo"
echo "========================================"
echo

# Create a sample figure first
echo "1. Creating sample figure..."
"$PYTHON" -c "
import figrecipe as fr
fig, ax = fr.subplots()
ax.plot([1,2,3,4,5], [1,4,2,5,3], label='Demo', id='line')
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_title('CLI Demo Figure')
ax.legend()
fr.save(fig, '$OUTPUT_DIR/demo.yaml')
print('Created: $OUTPUT_DIR/demo.yaml')
"
echo

# 2. figrecipe info - Show recipe information
echo "2. figrecipe info - Recipe information"
echo "   Command: figrecipe info $OUTPUT_DIR/demo.yaml"
"$FIGRECIPE" info "$OUTPUT_DIR/demo.yaml"
echo

# 3. figrecipe reproduce - Reproduce from recipe
echo "3. figrecipe reproduce - Reproduce figure from recipe"
echo "   Command: figrecipe reproduce $OUTPUT_DIR/demo.yaml -o $OUTPUT_DIR/reproduced.png"
"$FIGRECIPE" reproduce "$OUTPUT_DIR/demo.yaml" -o "$OUTPUT_DIR/reproduced.png"
echo "   Created: $OUTPUT_DIR/reproduced.png"
echo

# 4. figrecipe validate - Validate reproduction fidelity
echo "4. figrecipe validate - Validate pixel-perfect reproduction"
echo "   Command: figrecipe validate $OUTPUT_DIR/demo.yaml"
"$FIGRECIPE" validate "$OUTPUT_DIR/demo.yaml" || true
echo

# 5. figrecipe crop - Crop whitespace
echo "5. figrecipe crop - Crop whitespace from figure"
echo "   Command: figrecipe crop $OUTPUT_DIR/demo.png -o $OUTPUT_DIR/cropped.png"
"$FIGRECIPE" crop "$OUTPUT_DIR/demo.png" -o "$OUTPUT_DIR/cropped.png"
echo

# 6. figrecipe extract - Extract data from recipe
echo "6. figrecipe extract - Extract plotted data"
echo "   Command: figrecipe extract $OUTPUT_DIR/demo.yaml"
"$FIGRECIPE" extract "$OUTPUT_DIR/demo.yaml"
echo

# 7. figrecipe mcp - MCP server commands
echo "7. figrecipe mcp - MCP server (for AI integration)"
echo "   Available subcommands:"
echo "   - figrecipe mcp stdio    : Run MCP server via stdio"
echo "   - figrecipe mcp sse      : Run MCP server via SSE"
echo "   - figrecipe mcp install  : Install MCP server to Claude Code"
echo

# 8. figrecipe editor - GUI editor
echo "8. figrecipe editor - Launch GUI editor (interactive)"
echo "   Command: figrecipe editor $OUTPUT_DIR/demo.yaml"
echo "   (Not running - requires display)"
echo

# Summary
echo "========================================"
echo "CLI Demo Complete"
echo "========================================"
echo "Output files:"
ls -la "$OUTPUT_DIR"/*.{png,yaml} 2>/dev/null || true
echo
echo "For help on any command:"
echo "  figrecipe --help"
echo "  figrecipe <command> --help"

# EOF
