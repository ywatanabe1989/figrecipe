#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10_mcp.py

Demonstrates FigRecipe's MCP (Model Context Protocol) integration.
This shows how AI agents can create figures using declarative specifications.

See also: 10_mcp.sh for CLI-based MCP commands.
"""

from pathlib import Path

import numpy as np

import figrecipe as fr


def main():
    """Demonstrate MCP-style declarative plot creation."""
    output_dir = Path("./10_mcp_out")
    output_dir.mkdir(exist_ok=True)

    print("FigRecipe MCP Integration Demo (Python)")
    print("=" * 50)

    # === Demo 1: Basic MCP-style declarative spec ===
    print("\n1. Basic MCP Declarative Specification")

    spec = {
        "figure": {"width_mm": 80, "height_mm": 60},
        "plots": [
            {
                "type": "plot",
                "x": [1, 2, 3, 4, 5],
                "y": [1, 4, 2, 5, 3],
                "kwargs": {"label": "Series A", "id": "line_a"},
            },
            {
                "type": "scatter",
                "x": [1, 2, 3, 4, 5],
                "y": [2, 3, 1, 4, 2],
                "kwargs": {"label": "Series B", "id": "scatter_b"},
            },
        ],
        "xlabel": "X Axis",
        "ylabel": "Y Axis",
        "title": "MCP Demo: Declarative Plot",
        "legend": True,
    }

    fig, ax = execute_mcp_spec(spec)
    fr.save(fig, output_dir / "mcp_basic.png")
    print(f"   Created: {output_dir / 'mcp_basic.png'}")

    # === Demo 2: CSV-based data (recommended workflow) ===
    print("\n2. CSV-based Data Workflow (Recommended)")

    # Create sample CSV
    np.random.seed(42)
    import csv

    csv_path = output_dir / "experiment_data.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "control", "treatment"])
        for t in range(20):
            writer.writerow([t, np.random.normal(10, 2), np.random.normal(15, 3)])

    # MCP spec using CSV columns
    spec_csv = {
        "figure": {"width_mm": 100, "height_mm": 70},
        "plots": [
            {
                "type": "plot",
                "data_file": str(csv_path),
                "x_column": "time",
                "y_column": "control",
                "kwargs": {"label": "Control", "id": "ctrl"},
            },
            {
                "type": "plot",
                "data_file": str(csv_path),
                "x_column": "time",
                "y_column": "treatment",
                "kwargs": {"label": "Treatment", "id": "treat"},
            },
        ],
        "xlabel": "Time (min)",
        "ylabel": "Response",
        "title": "CSV-based MCP Plot",
        "legend": True,
    }

    fig, ax = execute_mcp_spec(spec_csv)
    fr.save(fig, output_dir / "mcp_csv.png")
    print(f"   Created: {output_dir / 'mcp_csv.png'}")

    # === Demo 3: Statistical plot with annotations ===
    print("\n3. Statistical Plot with Annotations")

    spec_stats = {
        "figure": {"width_mm": 90, "height_mm": 65},
        "plots": [
            {
                "type": "bar",
                "x": [0, 1, 2],
                "height": [2.1, 3.5, 4.2],
                "kwargs": {"yerr": [0.3, 0.4, 0.35], "capsize": 3, "id": "bars"},
            }
        ],
        "stat_annotations": [
            {"x1": 0, "x2": 1, "y": 4.5, "p_value": 0.032},
            {"x1": 1, "x2": 2, "y": 5.2, "p_value": 0.008},
        ],
        "xlabel": "Group",
        "ylabel": "Value",
        "title": "MCP Stats Demo",
        "xticks": {"ticks": [0, 1, 2], "labels": ["A", "B", "C"]},
    }

    fig, ax = execute_mcp_spec(spec_stats)
    fr.save(fig, output_dir / "mcp_stats.png")
    print(f"   Created: {output_dir / 'mcp_stats.png'}")

    # Summary
    print("\n" + "=" * 50)
    print("MCP Demo Complete")
    print("=" * 50)
    print("\nTo enable MCP in Claude Code:")
    print("  figrecipe mcp install")
    print("\nMCP Resources for AI agents:")
    print("  figrecipe://cheatsheet   - Quick reference")
    print("  figrecipe://mcp-spec     - Declarative spec format")
    print("  figrecipe://api/core     - Python API documentation")


def execute_mcp_spec(spec: dict):
    """Execute an MCP-style declarative specification.

    This simulates what the MCP server does when receiving a plot request.
    """
    import pandas as pd

    # Create figure
    fig_spec = spec.get("figure", {})
    fig, ax = fr.subplots(
        width_mm=fig_spec.get("width_mm", 80),
        height_mm=fig_spec.get("height_mm", 60),
    )

    # Execute plots
    for plot in spec.get("plots", []):
        plot_type = plot["type"]
        method = getattr(ax, plot_type)

        # Handle CSV-based data
        if "data_file" in plot:
            df = pd.read_csv(plot["data_file"])
            x = df[plot["x_column"]].values
            y = df[plot["y_column"]].values
        else:
            x = plot.get("x")
            y = plot.get("y") or plot.get("height")

        kwargs = plot.get("kwargs", {})
        if plot_type == "bar":
            method(x, y, **kwargs)
        else:
            method(x, y, **kwargs)

    # Apply decorations
    if "xlabel" in spec:
        ax.set_xlabel(spec["xlabel"])
    if "ylabel" in spec:
        ax.set_ylabel(spec["ylabel"])
    if "title" in spec:
        ax.set_title(spec["title"])
    if spec.get("legend"):
        ax.legend()

    # Handle xticks
    if "xticks" in spec:
        xticks = spec["xticks"]
        ax.set_xticks(xticks["ticks"])
        ax.set_xticklabels(xticks["labels"])

    # Handle stat annotations
    for ann in spec.get("stat_annotations", []):
        ax.stat_annotation(
            ann["x1"],
            ann["x2"],
            y=ann.get("y"),
            p_value=ann.get("p_value"),
            style=ann.get("style", "stars"),
        )

    return fig, ax


if __name__ == "__main__":
    main()
