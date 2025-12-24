#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plotter registry for demo plotters."""

import importlib
from pathlib import Path

from .._params import PLOTTING_METHODS

# Auto-import plotters from demo_plotters subdirectories
_demo_dir = Path(__file__).parent / "demo_plotters"
PLOTTERS = {}

# Category subdirectories
_category_dirs = [
    "line_curve",
    "scatter_points",
    "bar_categorical",
    "distribution",
    "image_matrix",
    "contour_surface",
    "spectral_signal",
    "vector_flow",
    "special",
]

# Build mapping from method_name to category
_method_to_category = {}
for cat_dir in _category_dirs:
    cat_path = _demo_dir / cat_dir
    if cat_path.is_dir():
        for plot_file in cat_path.glob("plot_*.py"):
            method_name = plot_file.stem.replace("plot_", "")
            _method_to_category[method_name] = cat_dir

for method_name in sorted(PLOTTING_METHODS):
    module_name = f"plot_{method_name}"
    func_name = f"plot_{method_name}"

    # Check if we have this plotter in a category subdirectory
    if method_name in _method_to_category:
        cat_dir = _method_to_category[method_name]
        try:
            module = importlib.import_module(
                f".demo_plotters.{cat_dir}.{module_name}", package="figrecipe._dev"
            )
            if hasattr(module, func_name):
                PLOTTERS[method_name] = getattr(module, func_name)
        except ImportError:
            pass


def list_plotters():
    """List all available plotter names."""
    return list(PLOTTERS.keys())


def get_plotter(name):
    """Get a plotter function by name.

    Parameters
    ----------
    name : str
        Name of the plotting method (e.g., 'plot', 'scatter').

    Returns
    -------
    callable
        The plotter function with signature (plt, rng, ax=None) -> (fig, ax).
    """
    if name in PLOTTERS:
        return PLOTTERS[name]
    raise KeyError(f"Unknown plotter: {name}. Available: {list(PLOTTERS.keys())}")


# EOF
