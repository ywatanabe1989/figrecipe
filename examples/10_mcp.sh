#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/09_mcp.sh

# FigRecipe MCP (Model Context Protocol) Demo
# ==========================================
#
# This script demonstrates figrecipe's MCP integration for AI agents.
# FigRecipe provides an MCP server for Claude Code and other AI tools.
#
# Run: ./09_mcp.sh

set -e

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$THIS_DIR")"
PYTHON="$PROJECT_DIR/.venv/bin/python"
OUTPUT_DIR="$THIS_DIR/09_mcp_out"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "FigRecipe MCP Integration Demo"
echo "========================================"
echo

# 1. MCP Server Installation
echo "1. Install MCP Server to Claude Code"
echo "   Command: figrecipe mcp install"
echo
echo "   This adds figrecipe MCP server to your Claude Code config."
echo "   After installation, Claude Code can create figures using:"
echo "   - mcp__figrecipe__plot      : Create declarative figures"
echo "   - mcp__figrecipe__reproduce : Reproduce from recipes"
echo "   - mcp__figrecipe__compose   : Compose multi-panel figures"
echo "   - mcp__figrecipe__info      : Get recipe information"
echo

# 2. MCP Server Protocols
echo "2. MCP Server Protocols"
echo "   stdio  : figrecipe mcp stdio"
echo "   sse    : figrecipe mcp sse --host 127.0.0.1 --port 8765"
echo

# 3. Example MCP Plot Specification
echo "3. Example Declarative Specification"
echo "   AI agents can create figures using YAML-like specs:"
echo
cat <<'EOF'
{
  "figure": {"width_mm": 80, "height_mm": 60},
  "plots": [
    {
      "type": "scatter",
      "data_file": "./data.csv",
      "x_column": "time",
      "y_column": "value",
      "kwargs": {"alpha": 0.7}
    }
  ],
  "xlabel": "Time (s)",
  "ylabel": "Value",
  "title": "MCP Generated Plot"
}
EOF
echo

# 4. Create sample MCP-style plot
echo "4. Creating sample MCP-style plot..."
"$PYTHON" <<'EOF'
import figrecipe as fr
from pathlib import Path

output_dir = Path("09_mcp_out")

# MCP-style declarative spec (what Claude Code would send)
spec = {
    "figure": {"width_mm": 80, "height_mm": 60},
    "plots": [
        {
            "type": "plot",
            "x": [1, 2, 3, 4, 5],
            "y": [1, 4, 2, 5, 3],
            "kwargs": {"label": "Line", "id": "mcp_line"}
        },
        {
            "type": "scatter",
            "x": [1, 2, 3, 4, 5],
            "y": [2, 3, 1, 4, 2],
            "kwargs": {"label": "Points", "id": "mcp_scatter"}
        }
    ],
    "xlabel": "X Axis",
    "ylabel": "Y Axis",
    "title": "MCP Demo",
    "legend": True
}

# Execute spec (simulating MCP tool call)
fig, ax = fr.subplots(width_mm=spec["figure"]["width_mm"],
                       height_mm=spec["figure"]["height_mm"])

for plot in spec["plots"]:
    method = getattr(ax, plot["type"])
    method(plot["x"], plot["y"], **plot.get("kwargs", {}))

ax.set_xlabel(spec["xlabel"])
ax.set_ylabel(spec["ylabel"])
ax.set_title(spec["title"])
if spec.get("legend"):
    ax.legend()

fr.save(fig, output_dir / "mcp_demo.yaml", verbose=True)
print(f"Created: {output_dir / 'mcp_demo.yaml'}")
EOF
echo

# 5. MCP Resources
echo "5. MCP Resources (for AI agents to read)"
echo "   figrecipe://cheatsheet   - Quick reference"
echo "   figrecipe://mcp-spec     - Declarative spec format"
echo "   figrecipe://api/core     - Python API documentation"
echo

# Summary
echo "========================================"
echo "MCP Demo Complete"
echo "========================================"
echo "To enable MCP in Claude Code:"
echo "  figrecipe mcp install"
echo
echo "Then Claude can create figures using natural language:"
echo "  'Create a scatter plot from data.csv with x=time, y=value'"
echo

# EOF
