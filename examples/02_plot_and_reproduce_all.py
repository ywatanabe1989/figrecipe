#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-25 04:26:38 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/01_all_plots.py


"""Generate all supported plot types.

Uses fr.run_all_demos() to generate individual plot files with proper
mm-based layout and auto-cropping.

Outputs saved to ./01_all_plots_out/plot_*.png

See 02a_composition.py for combining all plots into a single figure.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import scitex as stx

import figrecipe as fr
from figrecipe._dev import run_all_demos


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
    pixel_perfect: bool = True,
    tolerance: int = 0,
    full: bool = False,
):
    """Generate demo plots and their reproduced versions.

    Parameters
    ----------
    pixel_perfect : bool
        If True, verify each plot is pixel-perfect reproduced before proceeding.
        Stops immediately on first mismatch. Default: True.
    tolerance : int
        Maximum allowed pixel difference (0 = exact match). Default: 0.
    full : bool
        If True, run all 47 plots. If False (default), run only 18 representative
        plots for faster testing. Use --full for comprehensive testing.
    """
    output_dir = Path(CONFIG.SDIR_OUT)
    output_dir.mkdir(exist_ok=True)

    # Load SCITEX style (40x28mm axes, 1mm margins after crop)
    fr.load_style("SCITEX")

    mode = "all 47 plots" if full else "18 representative plots"
    logger.info(f"Generating {mode}...")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Pixel-perfect mode: {pixel_perfect}, Tolerance: {tolerance}")
    if not full:
        logger.info("(Use --full flag to run all 47 plot types)")

    # Run demos with pixel-perfect verification
    results = run_all_demos(
        fr,
        output_dir=output_dir,
        show=False,
        verbose=True,
        reproduce=True,
        pixel_perfect=pixel_perfect,
        tolerance=tolerance,
        representative_only=not full,
    )

    # Summary
    successes = sum(1 for r in results.values() if r["success"])
    failures = [name for name, r in results.items() if not r["success"]]
    logger.info(f"Generated {successes}/{len(results)} plots successfully")

    if failures:
        logger.warning(f"Failed plots ({len(failures)}):")
        for name in failures:
            logger.warning(f"  - {name}: {results[name]['error']}")

    return 0


if __name__ == "__main__":
    main()

# EOF
