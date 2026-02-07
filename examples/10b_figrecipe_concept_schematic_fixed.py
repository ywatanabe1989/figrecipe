#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-07 18:46:09 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/10b_figrecipe_concept_schematic_fixed.py


"""FigRecipe concept diagram — fixed layout passing all validations.

Demonstrates iterative layout adjustment guided by Schematic validation
errors. Compare with 10a (intentionally failing) to see the difference.
NOTE: position_mm is the CENTER of the box, not bottom-left.
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
    """Generate FigRecipe concept schematic."""
    out = Path(CONFIG.SDIR_OUT)

    W, H = 170, 175
    s = fr.Schematic(
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
        position_mm=(24, row1_cy),
        size_mm=(bw, bh),
    )
    s.add_box(
        "recipe",
        "Recipe (YAML)",
        subtitle="Structure + Plot Calls",
        emphasis="warning",
        position_mm=(W / 2, row1_cy),
        size_mm=(bw, bh),
    )
    s.add_box(
        "figure",
        "Figure",
        subtitle="PNG / PDF / SVG",
        emphasis="red",
        position_mm=(W - 24, row1_cy),
        size_mm=(bw, bh),
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
        position_mm=(W / 2, row2_cy),
        size_mm=(cw, ch),
    )
    s.add_box(
        "data",
        "DATA",
        subtitle="CSV / NPZ files",
        content=["WHAT to show"],
        emphasis="success",
        position_mm=(W / 2 - iw / 2 - 8, row2_cy - 2),
        size_mm=(iw, ih),
    )
    s.add_box(
        "style",
        "STYLE",
        subtitle="Presets / GUI editing",
        content=["HOW to show"],
        emphasis="purple",
        position_mm=(W / 2 + iw / 2 + 8, row2_cy - 2),
        size_mm=(iw, ih),
    )

    # Arrows from Recipe/Figure down to DATA/STYLE
    s.add_arrow("recipe", "data", color="orange", style="dashed")
    s.add_arrow("recipe", "style", color="purple")
    s.add_arrow("data", "figure", color="green")
    s.add_arrow("style", "figure", color="purple")

    # --- Row 3: Benefits container ---
    bbw, bbh = 40, 20
    row3_cy = 20

    bcw, bch = W - 20, bbh + 18
    s.add_container(
        "benefits",
        title="Benefits for Researchers",
        children=["repro", "flex", "verify"],
        position_mm=(W / 2, row3_cy),
        size_mm=(bcw, bch),
    )
    spacing = bcw / 3
    s.add_box(
        "repro",
        "Reproducibility",
        subtitle="Same recipe = Same figure",
        position_mm=(W / 2 - spacing, row3_cy - 4),
        size_mm=(bbw, bbh),
    )
    s.add_box(
        "flex",
        "Flexibility",
        subtitle="Change style, keep meaning",
        position_mm=(W / 2, row3_cy - 4),
        size_mm=(bbw, bbh),
    )
    s.add_box(
        "verify",
        "Verification",
        subtitle="Pixel-level validation",
        position_mm=(W / 2 + spacing, row3_cy - 4),
        size_mm=(bbw, bbh),
    )

    # Render
    fig, ax = fr.subplots()
    ax.schematic(s, id="figrecipe_concept")
    fr.save(fig, out / "figrecipe_concept.png", validate=False)

    logger.info(f"Saved to: {out}/figrecipe_concept.png")
    return 0


if __name__ == "__main__":
    main()

# EOF
