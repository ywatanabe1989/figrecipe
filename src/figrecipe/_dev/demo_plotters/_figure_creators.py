#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure creation functions for demo plotters."""

import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from ._registry import REGISTRY


def create_all_plots_figure(plt, seed: int = 42) -> Tuple:
    """Create a single figure with all supported plot types.

    Parameters
    ----------
    plt : module
        figrecipe module (import figrecipe as fr).
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    tuple
        (fig, axes, results) where results maps name to success/error.
    """
    rng = np.random.default_rng(seed)

    n_plots = len(REGISTRY)
    ncols = 7
    nrows = math.ceil(n_plots / ncols)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
    axes_flat = axes.flatten()

    results = {}
    for i, (name, plotter) in enumerate(REGISTRY.items()):
        ax = axes_flat[i]
        try:
            plotter(plt, rng, ax=ax)
            results[name] = {"success": True, "error": None}
        except Exception as e:
            ax.set_title(f"{name}\n(ERROR)")
            ax.text(
                0.5,
                0.5,
                str(e)[:50],
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=6,
                wrap=True,
            )
            results[name] = {"success": False, "error": str(e)}

    # Hide unused axes
    for i in range(n_plots, len(axes_flat)):
        axes_flat[i].set_visible(False)

    # Add panel labels
    panel_labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 2
    for i, ax in enumerate(axes_flat[:n_plots]):
        if i < len(panel_labels):
            plt.panel_label(ax, panel_labels[i])

    fig.suptitle(f"All {n_plots} Supported Plot Types")

    return fig, axes, results


def run_individual_demos(plt, output_dir=None, show=False) -> Dict:
    """Run all demo plotters individually and optionally save outputs.

    Parameters
    ----------
    plt : module
        figrecipe or matplotlib.pyplot module.
    output_dir : Path, optional
        Directory to save output images.
    show : bool
        Whether to show figures.

    Returns
    -------
    dict
        Results for each demo: {name: {'success': bool, 'error': str or None}}
    """
    rng = np.random.default_rng(42)
    results = {}

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    for name, plotter in REGISTRY.items():
        try:
            fig, ax = plotter(plt, rng)
            if output_dir:
                out_path = output_dir / f"plot_{name}.png"
                mpl_fig = fig.fig if hasattr(fig, "fig") else fig
                mpl_fig.savefig(out_path, dpi=100, bbox_inches="tight")
            if show:
                plt.show()
            else:
                mpl_fig = fig.fig if hasattr(fig, "fig") else fig
                plt.close(mpl_fig)
            results[name] = {"success": True, "error": None}
        except Exception as e:
            results[name] = {"success": False, "error": str(e)}

    return results


# Legacy alias
run_all_demos = run_individual_demos

# EOF
