#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2026-01-11 22:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/02_composition.py

"""Demo script for figure composition using fr.compose().

Combines all plot types from 01_all_plots into a single composed figure.
Demonstrates the composition feature with proper recipe output.

Requires: Run 01_all_plots.py first to generate the individual plot recipes.

Outputs:
    ./02_composition_out/composed.png
    ./02_composition_out/composed.yaml
    ./02_composition_out/composed_data/
"""

import matplotlib

matplotlib.use("Agg")

import math
from pathlib import Path

import figrecipe as fr

# Input: recipes from 01_all_plots
INPUT_DIR = Path(__file__).parent / "01_all_plots_out"
OUTPUT_DIR = Path(__file__.replace(".py", "_out"))


def main():
    """Compose all plot recipes into a single figure."""
    # Check input exists
    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}")
        print("Run 'make demo-plot-all' first to generate individual plots.")
        return

    # Find all recipe YAML files
    recipe_files = sorted(INPUT_DIR.glob("plot_*.yaml"))
    if not recipe_files:
        print("No recipe files found. Run 'make demo-plot-all' first.")
        return

    print(f"Found {len(recipe_files)} recipes to compose")

    # Calculate grid layout
    ncols = 8
    n_recipes = len(recipe_files)
    nrows = math.ceil(n_recipes / ncols)
    print(f"Layout: {nrows} rows x {ncols} cols")

    # Build sources mapping: (row, col) -> recipe_path
    sources = {}
    names = []
    for idx, recipe_path in enumerate(recipe_files):
        row = idx // ncols
        col = idx % ncols
        sources[(row, col)] = recipe_path
        names.append(recipe_path.stem.replace("plot_", ""))

    # Load style
    fr.load_style("SCITEX")

    # Compose figure from all recipes
    print("Composing figure...")
    fig, axes = fr.compose(layout=(nrows, ncols), sources=sources)

    # Add titles to each panel
    for idx, name in enumerate(names):
        row = idx // ncols
        col = idx % ncols
        if nrows == 1 and ncols == 1:
            ax = axes
        elif nrows == 1:
            ax = axes[col]
        elif ncols == 1:
            ax = axes[row]
        else:
            ax = axes[row, col]
        ax.set_title(name, fontsize=6)

    # Save composed figure with recipe (PNG format explicitly)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "composed.png"
    fr.save(fig, output_path, verbose=True, validate=False)

    print(f"\nComposed figure saved to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

# EOF
