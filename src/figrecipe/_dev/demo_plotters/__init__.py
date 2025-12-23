#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo plotters registry for all supported figrecipe plotting methods.

Usage
-----
>>> from figrecipe._dev.demo_plotters import REGISTRY, create_all_plots_figure
>>>
>>> # List all available plot types
>>> print(list(REGISTRY.keys()))
>>>
>>> # Create a single figure with all plot types
>>> fig, axes = create_all_plots_figure(fr)
>>>
>>> # Run individual plotter
>>> fig, ax = REGISTRY['plot'](fr, rng, ax)
"""

import importlib
import math
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import numpy as np

# Registry: plot_name -> plotter function
REGISTRY: Dict[str, Callable] = {}

# Get all plot_*.py files in this directory
_demo_dir = Path(__file__).parent
_demo_files = sorted(_demo_dir.glob("plot_*.py"))

# Import all demo functions into registry
for _file in _demo_files:
    _module_name = _file.stem  # e.g., plot_scatter
    _plot_name = _module_name.replace("plot_", "")  # e.g., scatter
    _func_name = _module_name  # e.g., plot_scatter
    try:
        _module = importlib.import_module(f".{_module_name}", package=__name__)
        if hasattr(_module, _func_name):
            REGISTRY[_plot_name] = getattr(_module, _func_name)
    except ImportError as e:
        print(f"Warning: Could not import {_module_name}: {e}")


def list_plots():
    """List all available plot types.

    Returns
    -------
    list of str
        Names of available plot types.
    """
    return list(REGISTRY.keys())


def get_plotter(name: str) -> Optional[Callable]:
    """Get plotter function by name.

    Parameters
    ----------
    name : str
        Plot type name (e.g., 'scatter', 'bar', 'hist').

    Returns
    -------
    callable or None
        Plotter function or None if not found.
    """
    return REGISTRY.get(name)


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
        (fig, axes) where fig is RecordingFigure and axes is array of RecordingAxes.
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
    panel_labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 2  # 52 labels
    for i, ax in enumerate(axes_flat[:n_plots]):
        if i < len(panel_labels):
            plt.panel_label(ax, panel_labels[i])

    fig.suptitle(f"All {n_plots} Supported Plot Types")

    return fig, axes, results


def run_individual_demos(plt, output_dir=None, show=False):
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
                if hasattr(fig, "fig"):
                    fig.fig.savefig(out_path, dpi=100, bbox_inches="tight")
                else:
                    fig.savefig(out_path, dpi=100, bbox_inches="tight")
            if show:
                plt.show()
            else:
                if hasattr(fig, "fig"):
                    plt.close(fig.fig)
                else:
                    plt.close(fig)
            results[name] = {"success": True, "error": None}
        except Exception as e:
            results[name] = {"success": False, "error": str(e)}

    return results


# Legacy exports for backwards compatibility
__all__ = [f"plot_{name}" for name in REGISTRY.keys()]
for _name, _func in REGISTRY.items():
    globals()[f"plot_{_name}"] = _func


def list_demos():
    """Legacy: List all available demo functions."""
    return __all__


def run_all_demos(plt, output_dir=None, show=False):
    """Legacy: Alias for run_individual_demos."""
    return run_individual_demos(plt, output_dir, show)


# EOF
