#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plotter registry for demo plotters."""

import importlib
from pathlib import Path

from .._params import PLOTTING_METHODS

# Auto-import plotters from demo_plotters directory
_demo_dir = Path(__file__).parent / "demo_plotters"
PLOTTERS = {}

for method_name in sorted(PLOTTING_METHODS):
    module_name = f"plot_{method_name}"
    func_name = f"plot_{method_name}"
    module_path = _demo_dir / f"{module_name}.py"

    if module_path.exists():
        try:
            module = importlib.import_module(
                f".demo_plotters.{module_name}", package="figrecipe._dev"
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
