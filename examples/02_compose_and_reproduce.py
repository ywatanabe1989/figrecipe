#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-25 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/02_composition_mm.py

"""Figure composition with grid and mm-based positioning.

Demonstrates the unified fr.compose() API supporting:
1. Grid-based layout: sources={(row, col): path}
2. Free-form mm-based positioning: sources={path: {"xy_mm": ..., "size_mm": ...}}

All composition is matplotlib-native for reproducibility.

Outputs:
    ./02_composition_mm_out/composed_grid.png
    ./02_composition_mm_out/composed_freeform.png
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import scitex as stx

import figrecipe as fr


def create_sample_panels(output_dir: Path, logger):
    """Create sample panel figures for composition demo."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Panel A: Line plot
    fig_a, ax_a = fr.subplots()
    ax_a.plot([1, 2, 3, 4, 5], [1, 4, 2, 5, 3], id="line_a")
    ax_a.set_xlabel("X")
    ax_a.set_ylabel("Y")
    ax_a.set_title("Panel A: Line")
    panel_a = output_dir / "panel_a.yaml"
    fr.save(fig_a, panel_a, validate=False, verbose=False)

    # Panel B: Scatter plot
    fig_b, ax_b = fr.subplots()
    ax_b.scatter([1, 2, 3, 4, 5], [2, 3, 1, 4, 2], id="scatter_b")
    ax_b.set_xlabel("X")
    ax_b.set_ylabel("Y")
    ax_b.set_title("Panel B: Scatter")
    panel_b = output_dir / "panel_b.yaml"
    fr.save(fig_b, panel_b, validate=False, verbose=False)

    # Panel C: Bar plot
    fig_c, ax_c = fr.subplots()
    ax_c.bar([1, 2, 3, 4], [3, 1, 4, 2], id="bar_c")
    ax_c.set_xlabel("Category")
    ax_c.set_ylabel("Value")
    ax_c.set_title("Panel C: Bar")
    panel_c = output_dir / "panel_c.yaml"
    fr.save(fig_c, panel_c, validate=False, verbose=False)

    logger.info(f"Created sample panels in {output_dir}")
    return panel_a, panel_b, panel_c


def demo_grid_layout(panel_a, panel_b, panel_c, output_dir, logger):
    """Demo: Grid-based layout with (row, col) positioning."""
    logger.info("Demo 1: Grid-based Layout")

    # Compose using grid positions
    fig, axes = fr.compose(
        sources={
            (0, 0): str(panel_a),
            (0, 1): str(panel_b),
            (0, 2): str(panel_c),
        },
        panel_labels=True,
        label_style="uppercase",
    )

    output_path = output_dir / "composed_grid.png"
    fr.save(fig, output_path, verbose=True, validate=False)
    logger.info(f"Output: {output_path}")

    return fig


def demo_freeform_layout(panel_a, panel_b, panel_c, output_dir, logger):
    """Demo: Free-form mm-based positioning for precise control."""
    logger.info("Demo 2: Free-form mm-based Positioning")

    # Custom layout: A and B side by side, C below spanning full width
    fig, axes = fr.compose(
        canvas_size_mm=(180, 120),
        sources={
            str(panel_a): {"xy_mm": (0, 0), "size_mm": (85, 55)},
            str(panel_b): {"xy_mm": (90, 0), "size_mm": (85, 55)},
            str(panel_c): {"xy_mm": (0, 60), "size_mm": (175, 55)},
        },
        panel_labels=True,
        label_style="uppercase",
    )

    output_path = output_dir / "composed_freeform.png"
    fr.save(fig, output_path, verbose=True, validate=False)

    logger.info(f"Output: {output_path}")
    for i, ax in enumerate(axes):
        logger.info(f"  Panel {chr(ord('A') + i)}: axes at index {i}")

    return fig


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Run composition demos with unified fr.compose() API."""
    output_path = Path(CONFIG.SDIR_OUT)

    logger.info("FigRecipe Composition Demo (matplotlib-native)")
    logger.info("=" * 50)

    # Create sample panels
    panel_a, panel_b, panel_c = create_sample_panels(output_path, logger)

    # Demo 1: Grid-based layout
    demo_grid_layout(panel_a, panel_b, panel_c, output_path, logger)

    # Demo 2: Free-form mm-based positioning
    demo_freeform_layout(panel_a, panel_b, panel_c, output_path, logger)

    logger.info(f"All outputs saved to: {output_path}/")
    return 0


if __name__ == "__main__":
    main()

# EOF
