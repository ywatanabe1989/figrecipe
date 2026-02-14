#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-14 14:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/10b_figrecipe_concept_schematic_fixed.py


"""FigRecipe concept diagram — flex layout with auto-height.

Demonstrates the CSS flexbox-like layout: no manual x_mm/y_mm/height_mm.
Gap triggers auto-positioning; codeblock renders syntax-highlighted code.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import scitex as stx

import figrecipe as fr


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Generate FigRecipe concept diagram."""
    out = Path(CONFIG.SDIR_OUT)

    s = fr.Diagram(
        title="FigRecipe: Reproducible Figures",
        width_mm=120,
        padding_mm=10,
        gap_mm=18,
    )

    s.add_box(
        "script",
        "script.py",
        shape="codeblock",
        language="python",
        content=[
            "import figrecipe",
            "fig, ax = figrecipe.subplots()",
            "ax.plot_line(x, y)",
            "figrecipe.save(fig, 'fig.png')",
        ],
        width_mm=80,
    )

    s.add_container(
        "recipe",
        title="Recipe (YAML)",
        children=["data", "style"],
        direction="row",
        container_gap_mm=8,
        container_padding_mm=8,
    )

    s.add_box(
        "data",
        "DATA",
        subtitle="CSV / NPZ",
        content=["WHAT to show"],
        emphasis="success",
        width_mm=40,
    )
    s.add_box(
        "style",
        "STYLE",
        subtitle="Presets / Themes",
        content=["HOW to show"],
        emphasis="purple",
        width_mm=40,
    )

    s.add_box(
        "figure",
        "Figure",
        subtitle="PNG / PDF + CSV",
        emphasis="info",
        width_mm=60,
    )

    s.add_arrow("script", "recipe")
    s.add_arrow("recipe", "figure", label="Render", label_offset_mm=(-12, 0))
    s.add_arrow(
        "figure",
        "recipe",
        label="Validate",
        label_offset_mm=(12, 0),
        curve=1.5,
        color="red",
        style="--",
    )

    # Render
    fig, ax = fr.subplots()
    ax.diagram(s, id="figrecipe_concept")
    fr.save(fig, out / "figrecipe_concept.png", validate=False)

    logger.info(f"Saved to: {out}/figrecipe_concept.png")
    return 0


if __name__ == "__main__":
    main()

# EOF
