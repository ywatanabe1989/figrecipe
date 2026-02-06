#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-panel figure composition with fr.compose().

Demonstrates two layout modes:
1. Grid-based: sources={(row, col): recipe_path}
2. Free-form mm-based: sources={path: {"xy_mm": ..., "size_mm": ...}}

Outputs:
    ./03_composition_out/composed_grid.png
    ./03_composition_out/composed_freeform.png
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import scitex as stx

import figrecipe as fr


def create_sample_panels(output_dir: Path, logger):
    """Create sample panel figures for composition demo."""
    output_dir.mkdir(parents=True, exist_ok=True)

    fig_a, ax_a = fr.subplots()
    ax_a.plot([1, 2, 3, 4, 5], [1, 4, 2, 5, 3], id="line_a")
    ax_a.set_xlabel("X")
    ax_a.set_ylabel("Y")
    ax_a.set_title("Panel A: Line")
    panel_a = output_dir / "panel_a.yaml"
    fr.save(fig_a, panel_a, validate=False, verbose=False)

    fig_b, ax_b = fr.subplots()
    ax_b.scatter([1, 2, 3, 4, 5], [2, 3, 1, 4, 2], id="scatter_b")
    ax_b.set_xlabel("X")
    ax_b.set_ylabel("Y")
    ax_b.set_title("Panel B: Scatter")
    panel_b = output_dir / "panel_b.yaml"
    fr.save(fig_b, panel_b, validate=False, verbose=False)

    fig_c, ax_c = fr.subplots()
    ax_c.bar([1, 2, 3, 4], [3, 1, 4, 2], id="bar_c")
    ax_c.set_xlabel("Category")
    ax_c.set_ylabel("Value")
    ax_c.set_title("Panel C: Bar")
    panel_c = output_dir / "panel_c.yaml"
    fr.save(fig_c, panel_c, validate=False, verbose=False)

    logger.info(f"Created sample panels in {output_dir}")
    return panel_a, panel_b, panel_c


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Run composition demos."""
    OUT = Path(CONFIG.SDIR_OUT)

    panel_a, panel_b, panel_c = create_sample_panels(OUT, logger)

    # --- Grid-based layout ---
    logger.info("Demo 1: Grid-based layout")
    fig, axes = fr.compose(
        sources={
            (0, 0): str(panel_a),
            (0, 1): str(panel_b),
            (0, 2): str(panel_c),
        },
        panel_labels=True,
        label_style="uppercase",
    )
    fr.save(fig, OUT / "composed_grid.png", verbose=True, validate=False)

    # --- Free-form mm-based positioning ---
    logger.info("Demo 2: Free-form mm-based positioning")
    fig2, axes2 = fr.compose(
        canvas_size_mm=(180, 120),
        sources={
            str(panel_a): {"xy_mm": (0, 0), "size_mm": (85, 55)},
            str(panel_b): {"xy_mm": (90, 0), "size_mm": (85, 55)},
            str(panel_c): {"xy_mm": (0, 60), "size_mm": (175, 55)},
        },
        panel_labels=True,
        label_style="uppercase",
    )
    fr.save(fig2, OUT / "composed_freeform.png", verbose=True, validate=False)

    logger.info(f"All outputs saved to: {OUT}/")
    return 0


if __name__ == "__main__":
    main()

# EOF
