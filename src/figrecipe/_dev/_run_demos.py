#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo runner for all plotters."""

from pathlib import Path

from ._plotters import PLOTTERS


def run_all_demos(fr, output_dir=None, show=False, verbose=True):
    """Run all demo plotters and save outputs using fr.save().

    Parameters
    ----------
    fr : module
        figrecipe module (e.g., `import figrecipe as fr`).
    output_dir : Path or str, optional
        Directory to save output images. If None, uses /tmp/figrecipe_demos.
    show : bool
        Whether to show figures interactively.
    verbose : bool
        Whether to print progress.

    Returns
    -------
    dict
        Results for each demo: {name: {'success': bool, 'error': str or None, 'path': str}}
    """
    import matplotlib.pyplot as _plt
    import numpy as np

    rng = np.random.default_rng(42)
    results = {}

    if output_dir is None:
        output_dir = Path("/tmp/figrecipe_demos")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(PLOTTERS)
    for i, (name, func) in enumerate(sorted(PLOTTERS.items()), 1):
        try:
            fig, ax = func(fr, rng)
            out_path = output_dir / f"plot_{name}.png"
            # Use fr.save() for proper mm layout and auto-cropping
            fr.save(fig, out_path, validate=False, verbose=False)
            if show:
                _plt.show()
            else:
                _plt.close("all")
            results[name] = {"success": True, "error": None, "path": str(out_path)}
            if verbose:
                print(f"[{i}/{total}] {name}: OK")
        except Exception as e:
            results[name] = {"success": False, "error": str(e), "path": None}
            if verbose:
                print(f"[{i}/{total}] {name}: FAILED - {e}")
            _plt.close("all")

    # Summary
    success = sum(1 for r in results.values() if r["success"])
    if verbose:
        print(f"\nSummary: {success}/{total} demos succeeded")
        print(f"Output directory: {output_dir}")

    return results


# EOF
