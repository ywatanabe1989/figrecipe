#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Development utilities for figrecipe.

Provides demo plotters for all supported matplotlib plotting methods.
All plotters follow signature: (plt, rng, ax=None) -> (fig, ax)

Usage:
    import figrecipe as fr
    from figrecipe._dev import PLOTTERS, run_all_demos

    # Run a single demo
    fig, ax = PLOTTERS["plot"](fr, np.random.default_rng(42))

    # Run all demos
    results = run_all_demos(fr, output_dir="./outputs")
"""

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


def run_all_demos(plt, output_dir=None, show=False):
    """Run all demo plotters and optionally save outputs.

    Parameters
    ----------
    plt : module
        figrecipe module (e.g., `import figrecipe as fr`).
    output_dir : Path or str, optional
        Directory to save output images.
    show : bool
        Whether to show figures interactively.

    Returns
    -------
    dict
        Results for each demo: {name: {'success': bool, 'error': str or None}}
    """
    import matplotlib.pyplot as _plt
    import numpy as np

    rng = np.random.default_rng(42)
    results = {}

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    for name, func in PLOTTERS.items():
        try:
            fig, ax = func(plt, rng)
            if output_dir:
                out_path = output_dir / f"plot_{name}.png"
                mpl_fig = fig.fig if hasattr(fig, "fig") else fig
                mpl_fig.savefig(out_path, dpi=100, bbox_inches="tight")
            if show:
                _plt.show()
            else:
                mpl_fig = fig.fig if hasattr(fig, "fig") else fig
                _plt.close(mpl_fig)
            results[name] = {"success": True, "error": None}
        except Exception as e:
            results[name] = {"success": False, "error": str(e)}

    return results


__all__ = [
    "PLOTTERS",
    "list_plotters",
    "get_plotter",
    "run_all_demos",
]

# EOF
