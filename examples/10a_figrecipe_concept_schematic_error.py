#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-07 17:18:19 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/10_figrecipe_concept_schematic.py


"""FigRecipe concept diagram using fr.Schematic.

Recreates the FigRecipe architecture concept diagram using the
Schematic API with manual mm-based positioning.
NOTE: position_mm is the CENTER of the box, not bottom-left.

Outputs:
    ./10_figrecipe_concept_schematic_out/figrecipe_concept.{png,yaml}
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

    W, H = 170, 145
    s = fr.Schematic(
        title="FigRecipe: Reproducible Scientific Figures",
        width_mm=W,
        height_mm=H,
    )

    # --- Row 1: Python Code -> Recipe (YAML) -> Figure ---
    bw, bh = 38, 22
    row1_cy = H - 30

    s.add_box(
        "python",
        "Python Code",
        content=["import figrecipe as fr", "ax.plot(x, y)"],
        position_mm=(28, row1_cy),
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
        position_mm=(W - 28, row1_cy),
        size_mm=(bw, bh),
    )

    # Arrows: Python -> Recipe -> Figure
    s.add_arrow("python", "recipe", label="auto-record")
    s.add_arrow("recipe", "figure", label="reproduce")
    s.add_arrow(
        "figure",
        "recipe",
        label="validate",
        style="dashed",
        color="red",
        curve=0.4,
    )

    # --- Row 2: DATA + STYLE inside container ---
    iw, ih = 42, 28
    row2_cy = row1_cy - 45

    cw, ch = 120, ih + 14
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
    bbw, bbh = 38, 18
    row3_cy = 18

    bcw, bch = W - 20, bbh + 16
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
        position_mm=(W / 2 - spacing, row3_cy - 3),
        size_mm=(bbw, bbh),
    )
    s.add_box(
        "flex",
        "Flexibility",
        subtitle="Change style, keep meaning",
        position_mm=(W / 2, row3_cy - 3),
        size_mm=(bbw, bbh),
    )
    s.add_box(
        "verify",
        "Verification",
        subtitle="Pixel-level validation",
        position_mm=(W / 2 + spacing, row3_cy - 3),
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
