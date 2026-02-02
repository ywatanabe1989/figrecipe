#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo script for figure composition using fr.compose().

Combines all plot types from 01_all_plots into a single composed figure.
Demonstrates the composition feature with proper recipe output.

Requires: Run 01_plot_and_reproduce_all.py first to generate individual plot recipes.

Outputs:
    ./02a_composition_out/composed.png
    ./02a_composition_out/composed.yaml
    ./02a_composition_out/composed_data/
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import scitex as stx

import figrecipe as fr

# Input: recipes from 01_plot_and_reproduce_all
INPUT_DIR = Path(__file__).parent / "01_plot_and_reproduce_all_out"


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Compose all plot recipes into a single figure."""
    OUT = Path(CONFIG.SDIR_OUT)

    # Check input exists
    if not INPUT_DIR.exists():
        logger.warning(f"Input directory not found: {INPUT_DIR}")
        logger.warning("Run 01_plot_and_reproduce_all.py first.")
        return 1

    # Find all recipe YAML files
    recipe_files = sorted(INPUT_DIR.glob("plot_*.yaml"))
    if not recipe_files:
        logger.warning("No recipe files found. Run 01_plot_and_reproduce_all.py first.")
        return 1

    logger.info(f"Found {len(recipe_files)} recipes to compose")

    # Calculate grid layout
    ncols = 8
    n_recipes = len(recipe_files)
    nrows = math.ceil(n_recipes / ncols)
    logger.info(f"Layout: {nrows} rows x {ncols} cols")

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
    logger.info("Composing figure...")
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

    # Save composed figure with recipe
    output_path = OUT / "composed.png"
    fr.save(fig, output_path, verbose=True, validate=False)

    logger.info(f"Composed figure saved to: {OUT}/")

    return 0


if __name__ == "__main__":
    main()

# EOF
