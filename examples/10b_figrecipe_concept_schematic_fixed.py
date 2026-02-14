#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-07 18:46:09 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/10b_figrecipe_concept_schematic_fixed.py


"""FigRecipe concept diagram — fixed layout passing all validations.

Demonstrates iterative layout adjustment guided by Diagram validation
errors. Compare with 10a (intentionally failing) to see the difference.
NOTE: x_mm/y_mm is the CENTER of the box, not bottom-left.
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

    W, H = 170, 130
    s = fr.Diagram(
        title="FigRecipe: Reproducible Scientific Figures",
        width_mm=W,
        height_mm=H,
    )

    # --- Row 1: Python Code -> Recipe (YAML) -> Figure ---
    bw, bh = 34, 26
    row1_cy = H - 35

    s.add_box(
        "python",
        "Python Code",
        content=["import figrecipe as fr", "ax.plot(x, y)"],
        x_mm=24,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )
    s.add_box(
        "recipe",
        "Recipe (YAML)",
        subtitle="Structure + Plot Calls",
        emphasis="warning",
        x_mm=W / 2,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )
    s.add_box(
        "figure",
        "Figure",
        subtitle="PNG / PDF / SVG",
        emphasis="red",
        x_mm=W - 24,
        y_mm=row1_cy,
        width_mm=bw,
        height_mm=bh,
    )

    # Arrows: Python -> Recipe -> Figure
    s.add_arrow("python", "recipe", label="Record")
    s.add_arrow("recipe", "figure", label="Reproduce")
    s.add_arrow(
        "figure",
        "recipe",
        label="Validate",
        style="dashed",
        color="red",
        source_anchor="left",
        target_anchor="right",
        curve=0.5,
    )

    # --- Row 2: DATA + STYLE inside container ---
    iw, ih = 44, 30
    row2_cy = row1_cy - 58

    cw, ch = 124, ih + 16
    s.add_container(
        "concerns",
        title="Separation of Concerns",
        children=["data", "style"],
        x_mm=W / 2,
        y_mm=row2_cy,
        width_mm=cw,
        height_mm=ch,
    )
    s.add_box(
        "data",
        "DATA",
        subtitle="CSV / NPZ files",
        content=["WHAT to show"],
        emphasis="success",
        x_mm=W / 2 - iw / 2 - 8,
        y_mm=row2_cy - 2,
        width_mm=iw,
        height_mm=ih,
    )
    s.add_box(
        "style",
        "STYLE",
        subtitle="Presets / GUI editing",
        content=["HOW to show"],
        emphasis="purple",
        x_mm=W / 2 + iw / 2 + 8,
        y_mm=row2_cy - 2,
        width_mm=iw,
        height_mm=ih,
    )

    # Arrows from Recipe/Figure down to DATA/STYLE
    s.add_arrow("recipe", "data", color="orange", style="dashed")
    s.add_arrow("recipe", "style", color="purple")
    s.add_arrow("data", "figure", color="green")
    s.add_arrow("style", "figure", color="purple")

    # Render
    fig, ax = fr.subplots()
    ax.diagram(s, id="figrecipe_concept")
    fr.save(fig, out / "figrecipe_concept.png", validate=False)

    logger.info(f"Saved to: {out}/figrecipe_concept.png")
    return 0


if __name__ == "__main__":
    main()

# EOF
