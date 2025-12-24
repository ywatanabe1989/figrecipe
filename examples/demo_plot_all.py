#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-24 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_plot_all.py

"""Demo script that generates all supported plot types.

Outputs saved to ./outputs/examples/*.{png,yaml}
"""

import matplotlib

matplotlib.use("Agg")

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

import matplotlib.pyplot as plt

import figrecipe as fr
from figrecipe._dev.demo_plotters import (
    CATEGORIES,
    REGISTRY,
    create_all_plots_figure,
    get_plotter,
)


def close_fig(fig):
    """Close figure properly."""
    if hasattr(fig, "fig"):
        plt.close(fig.fig)
    else:
        plt.close(fig)


OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "examples"


def create_category_figure(category_name, plot_names, plt, rng):
    """Create a figure with all plots from a single category."""
    n_plots = len(plot_names)
    if n_plots == 0:
        return None, None, {}

    # Calculate grid size
    n_cols = min(4, n_plots)
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3.5 * n_rows))

    # Handle single plot case
    if n_plots == 1:
        axes = np.array([[axes]])
    elif n_rows == 1:
        axes = axes.reshape(1, -1)

    axes_flat = axes.flatten()

    results = {}
    for idx, name in enumerate(plot_names):
        ax = axes_flat[idx]
        try:
            plotter = get_plotter(name)
            plotter(plt, rng, ax=ax)
            results[name] = {"success": True, "error": None}
        except Exception as e:
            ax.set_title(f"{name} (failed)")
            ax.text(0.5, 0.5, str(e)[:50], ha="center", va="center", fontsize=8)
            results[name] = {"success": False, "error": str(e)}

    # Hide unused axes
    for idx in range(n_plots, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fig.suptitle(category_name, fontsize=14, fontweight="bold")
    fig.tight_layout()

    return fig, axes, results


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fr.load_style("SCITEX")
    rng = np.random.default_rng(42)

    all_results = {}

    # Generate figure for each category
    print("Generating category figures...")
    for category_name, plot_names in CATEGORIES.items():
        print(f"  {category_name}: {len(plot_names)} plots")

        fig, axes, results = create_category_figure(category_name, plot_names, fr, rng)
        all_results.update(results)

        if fig is not None:
            # Clean filename
            clean_name = category_name.lower().replace(" & ", "_").replace(" ", "_")
            out_path = OUTPUT_DIR / f"category_{clean_name}.png"
            fr.save(fig, out_path, validate_error_level="warning")
            print(f"    Saved: {out_path}")
            close_fig(fig)

    # Generate single figure with ALL plots
    print("\nGenerating combined figure with all plots...")
    fig, axes, results = create_all_plots_figure(fr, seed=42)
    all_results.update(results)

    out_path = OUTPUT_DIR / "all_plot_types.png"
    fr.save(fig, out_path, validate_error_level="warning")
    print(f"  Saved: {out_path}")
    close_fig(fig)

    # Generate individual plots
    print("\nGenerating individual plot files...")
    for name, plotter in REGISTRY.items():
        try:
            fig, ax = plotter(fr, rng)
            out_path = OUTPUT_DIR / f"plot_{name}.png"
            fr.save(fig, out_path, validate_error_level="warning")
            close_fig(fig)
        except Exception as e:
            print(f"  Failed: {name} - {e}")

    # Summary
    successes = sum(1 for r in all_results.values() if r["success"])
    total = len(all_results)
    print(f"\nSummary: {successes}/{total} plots successful")

    if successes < total:
        print("\nFailed plots:")
        for name, r in all_results.items():
            if not r["success"]:
                print(f"  - {name}: {r['error']}")


if __name__ == "__main__":
    main()

# EOF
