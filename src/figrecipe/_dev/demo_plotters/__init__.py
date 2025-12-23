#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo plotters for all supported figrecipe plotting methods."""

import importlib
from pathlib import Path

# Get all plot_*.py files in this directory
_demo_dir = Path(__file__).parent
_demo_files = sorted(_demo_dir.glob("plot_*.py"))

# Import all demo functions
__all__ = []
for _file in _demo_files:
    _module_name = _file.stem
    _func_name = _module_name  # e.g., plot_plot, plot_scatter
    try:
        _module = importlib.import_module(f".{_module_name}", package=__name__)
        if hasattr(_module, _func_name):
            globals()[_func_name] = getattr(_module, _func_name)
            __all__.append(_func_name)
    except ImportError:
        pass


def list_demos():
    """List all available demo functions."""
    return __all__


def run_all_demos(plt, output_dir=None, show=False):
    """Run all demo plotters and optionally save outputs.

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
    import numpy as np

    rng = np.random.default_rng(42)
    results = {}

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    for func_name in __all__:
        func = globals()[func_name]
        try:
            fig, ax = func(plt, rng)
            if output_dir:
                out_path = output_dir / f"{func_name}.png"
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
            results[func_name] = {"success": True, "error": None}
        except Exception as e:
            results[func_name] = {"success": False, "error": str(e)}

    return results


# EOF
