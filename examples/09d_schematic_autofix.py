#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstrates auto_fix=True for Diagram validation violations.

Each case intentionally creates a layout violation that would fail
with render(). Using render(auto_fix=True) resolves them automatically:

1. Overlapping boxes      (R2) -> pushed apart
2. Child outside container (R1) -> container expanded
3. Arrow label occlusion   (R7) -> label offset perpendicular
4. Box beyond canvas       (R9) -> canvas expanded
5. Combined violations          -> all resolved in one call

Outputs:
    ./09d_schematic_autofix_out/fix_overlap.png
    ./09d_schematic_autofix_out/fix_container.png
    ./09d_schematic_autofix_out/fix_arrow_label.png
    ./09d_schematic_autofix_out/fix_canvas.png
    ./09d_schematic_autofix_out/fix_combined.png
"""

import matplotlib

matplotlib.use("Agg")

import warnings
from pathlib import Path

import scitex as stx

import figrecipe as fr


def fix_overlap(out):
    """R2: Two overlapping boxes are pushed apart."""
    s = fr.Diagram(width_mm=170, height_mm=80)
    s.add_box("a", "Box A", x_mm=60, y_mm=40, width_mm=40, height_mm=25)
    s.add_box("b", "Box B", x_mm=70, y_mm=40, width_mm=40, height_mm=25)
    s.add_arrow("a", "b")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = s.render(auto_fix=True)
    fig.savefig(out / "fix_overlap.png", dpi=200, bbox_inches="tight")


def fix_container(out):
    """R1: Container expanded to enclose child."""
    s = fr.Diagram(width_mm=300, height_mm=150)
    s.add_container(
        "c",
        title="Container",
        children=["a"],
        x_mm=85,
        y_mm=60,
        width_mm=40,
        height_mm=30,
    )
    s.add_box("a", "Box A", x_mm=160, y_mm=60, width_mm=30, height_mm=20)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = s.render(auto_fix=True)
    fig.savefig(out / "fix_container.png", dpi=200, bbox_inches="tight")


def fix_arrow_label(out):
    """R7: Arrow label offset so it doesn't occlude the arrow."""
    s = fr.Diagram(width_mm=180, height_mm=100)
    s.add_box("a", "Yusuke", x_mm=40, y_mm=50, width_mm=40, height_mm=25)
    s.add_box("b", "Nandeyanen", x_mm=130, y_mm=50, width_mm=50, height_mm=25)
    s.add_arrow("a", "b", label="Why?!")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = s.render(auto_fix=True)
    fig.savefig(out / "fix_arrow_label.png", dpi=200, bbox_inches="tight")


def fix_canvas(out):
    """R9: Canvas expanded to contain out-of-bounds box."""
    s = fr.Diagram(width_mm=170, height_mm=80)
    s.add_box("near", "Near", x_mm=50, y_mm=40, width_mm=40, height_mm=25)
    s.add_box("far", "Far Away", x_mm=200, y_mm=40, width_mm=40, height_mm=25)
    s.add_arrow("near", "far")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = s.render(auto_fix=True)
    fig.savefig(out / "fix_canvas.png", dpi=200, bbox_inches="tight")


def fix_combined(out):
    """Multiple violations resolved in one render call."""
    s = fr.Diagram(width_mm=170, height_mm=80)
    # Overlapping boxes
    s.add_box("a", "Step A", x_mm=50, y_mm=40, width_mm=40, height_mm=25)
    s.add_box("b", "Step B", x_mm=55, y_mm=40, width_mm=40, height_mm=25)
    # Box beyond canvas
    s.add_box("c", "Step C", x_mm=200, y_mm=40, width_mm=40, height_mm=25)
    s.add_arrow("a", "b", label="process")
    s.add_arrow("b", "c")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig, ax = s.render(auto_fix=True)
    fig.savefig(out / "fix_combined.png", dpi=200, bbox_inches="tight")


@stx.session
def main(CONFIG=stx.session.INJECTED, logger=stx.session.INJECTED):
    """Run auto_fix demos - all violations resolved automatically."""
    out = Path(CONFIG.SDIR_OUT)

    cases = [
        ("R2 overlap", fix_overlap),
        ("R1 container", fix_container),
        ("R7 arrow label", fix_arrow_label),
        ("R9 canvas", fix_canvas),
        ("Combined", fix_combined),
    ]
    for name, fn in cases:
        fn(out)
        logger.info(f"{name}: auto_fix resolved -> saved")

    logger.info(f"All outputs saved to: {out}/")
    return 0


if __name__ == "__main__":
    main()

# EOF
