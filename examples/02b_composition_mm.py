#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo script for mm-based figure composition.

Demonstrates the new mm-based composition pipeline with:
1. Grid-based layout (auto-arranged with layout solvers)
2. Free-form mm-based positioning (precise control)
3. Recipe save/load for future editing

Outputs:
    ./02b_composition_mm_out/mm_horizontal.png
    ./02b_composition_mm_out/mm_horizontal.compose.yaml
    ./02b_composition_mm_out/mm_freeform.png
    ./02b_composition_mm_out/mm_freeform.compose.yaml
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import scitex as stx

import figrecipe as fr
from figrecipe import compose_figures, recompose


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

    return panel_a, panel_b, panel_c


def demo_grid_layout(panel_a, panel_b, panel_c, OUT, logger):
    """Demo: Grid-based layout with automatic arrangement."""
    logger.info("=== Demo 1: Grid-based Layout ===")

    # Horizontal layout
    result = compose_figures(
        sources=[str(panel_a), str(panel_b), str(panel_c)],
        output_path=str(OUT / "mm_horizontal.png"),
        layout="horizontal",
        gap_mm=5.0,
        panel_labels=True,
        label_style="uppercase",
    )

    logger.info(f"Output: {result['output_path']}")
    logger.info(f"Recipe: {result.get('recipe_path', 'N/A')}")
    logger.info(f"Canvas size: {result['layout_spec']['canvas_size_mm']} mm")

    # Vertical layout
    result_v = compose_figures(
        sources=[str(panel_a), str(panel_b)],
        output_path=str(OUT / "mm_vertical.png"),
        layout="vertical",
        gap_mm=10.0,
    )
    logger.info(f"Vertical output: {result_v['output_path']}")

    # Grid layout
    result_g = compose_figures(
        sources=[str(panel_a), str(panel_b), str(panel_c), str(panel_a)],
        output_path=str(OUT / "mm_grid.png"),
        layout="grid",
        gap_mm=5.0,
    )
    logger.info(f"Grid output: {result_g['output_path']}")

    return result


def demo_freeform_layout(panel_a, panel_b, panel_c, OUT, logger):
    """Demo: Free-form mm-based positioning for precise control."""
    logger.info("=== Demo 2: Free-form mm-based Positioning ===")

    # Custom layout: A and B side by side, C below spanning full width
    result = compose_figures(
        canvas_size_mm=(180, 120),
        sources={
            str(panel_a): {"xy_mm": (0, 0), "size_mm": (85, 55)},
            str(panel_b): {"xy_mm": (90, 0), "size_mm": (85, 55)},
            str(panel_c): {"xy_mm": (0, 60), "size_mm": (175, 55)},
        },
        output_path=str(OUT / "mm_freeform.png"),
        panel_labels=True,
    )

    logger.info(f"Output: {result['output_path']}")
    logger.info(f"Recipe: {result.get('recipe_path', 'N/A')}")
    logger.info("Panel positions:")
    for path, spec in result["layout_spec"]["panels"].items():
        name = Path(path).stem
        logger.info(f"  {name}: xy={spec['xy_mm']}, size={spec['size_mm']}")

    return result


def demo_recompose(recipe_path, OUT, logger):
    """Demo: Re-compose from saved recipe with modifications."""
    logger.info("=== Demo 3: Re-compose from Recipe ===")

    # Re-compose with different settings
    result = recompose(
        recipe_path,
        output_path=str(OUT / "mm_recomposed.png"),
        panel_labels=False,  # Override: remove labels
        caption="Recomposed figure without panel labels",
    )

    logger.info(f"Recomposed from: {recipe_path}")
    logger.info(f"Output: {result['output_path']}")


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Run all composition demos."""
    OUT = Path(CONFIG.SDIR_OUT)

    logger.info("FigRecipe mm-based Composition Demo")
    logger.info("=" * 40)

    # Create sample panels
    panel_a, panel_b, panel_c = create_sample_panels(OUT, logger)
    logger.info(f"Created sample panels in {OUT}")

    # Demo 1: Grid-based layouts
    demo_grid_layout(panel_a, panel_b, panel_c, OUT, logger)

    # Demo 2: Free-form positioning
    result_freeform = demo_freeform_layout(panel_a, panel_b, panel_c, OUT, logger)

    # Demo 3: Re-compose from recipe
    if "recipe_path" in result_freeform:
        demo_recompose(result_freeform["recipe_path"], OUT, logger)

    logger.info("=" * 40)
    logger.info(f"All outputs saved to: {OUT}/")

    return 0


if __name__ == "__main__":
    main()

# EOF
