#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/04_style_change.py

"""Demonstrate style switching between SCITEX and matplotlib default.

Shows how figrecipe supports different visual styles while maintaining
reproducibility. The same data is plotted with different styles.

Outputs:
    ./05_style_change_out/plot_scitex.png
    ./05_style_change_out/plot_default.png
    ./05_style_change_out/comparison.png
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import numpy as np
import scitex as stx

import figrecipe as fr


def create_demo_plot(style_name: str, output_dir: Path, logger):
    """Create a demo plot with the specified style."""
    # Load the style (available: SCITEX, MATPLOTLIB)
    fr.load_style(style_name)

    # Generate sample data
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x) + np.random.normal(0, 0.1, len(x))
    y2 = np.cos(x) + np.random.normal(0, 0.1, len(x))

    # Create figure
    fig, ax = fr.subplots()

    # Plot data
    ax.plot(x, y1, label="Signal A", id="line_a")
    ax.scatter(x[::5], y2[::5], label="Signal B", id="scatter_b")
    ax.fill_between(x, y1 - 0.2, y1 + 0.2, alpha=0.3, id="fill_a")

    # Decorations
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Style: {style_name}")
    ax.legend()

    # Save
    output_path = output_dir / f"plot_{style_name.lower()}.yaml"
    fr.save(fig, output_path, verbose=True, validate=False)
    logger.info(f"Created {style_name} style plot: {output_path}")

    return output_path


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate style switching in figrecipe."""
    output_dir = Path(CONFIG.SDIR_OUT)
    output_dir.mkdir(exist_ok=True)

    logger.info("FigRecipe Style Switching Demo")
    logger.info("=" * 50)

    # Create plots with different styles
    scitex_path = create_demo_plot("SCITEX", output_dir, logger)
    matplotlib_path = create_demo_plot("MATPLOTLIB", output_dir, logger)

    # Create side-by-side comparison
    logger.info("Creating comparison figure...")
    fig, axes = fr.compose(
        sources={
            (0, 0): str(scitex_path),
            (0, 1): str(matplotlib_path),
        },
        panel_labels=True,
        label_style="uppercase",
    )

    comparison_path = output_dir / "comparison.png"
    fr.save(fig, comparison_path, verbose=True, validate=False)

    logger.info(f"Comparison saved: {comparison_path}")
    logger.info("Style differences:")
    logger.info("  - SCITEX: Scientific publication style (40x28mm axes)")
    logger.info("  - MATPLOTLIB: Matplotlib default style")

    return 0


if __name__ == "__main__":
    main()

# EOF
