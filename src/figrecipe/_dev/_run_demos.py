#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo runner for all plotters."""

from pathlib import Path

from ._plotters import PLOTTERS


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


# EOF
