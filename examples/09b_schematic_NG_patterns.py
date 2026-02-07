#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-07 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/09b_schematic_NG_patterns.py


"""Demonstrates all Schematic validation rules via NG (failing) figures.

Each function triggers a rule violation. The figure is still saved with a
_FAILED suffix so you can visually inspect what went wrong.

Rules:
  R1  Container must enclose all children          -> ValueError
  R2  No two boxes may overlap                     -> ValueError
  R5  Text-to-text margin >= 2mm                   -> ValueError
  R7  Arrow visible-length ratio >= 90%            -> ValueError
  R8  Curved-arrow label on same side as arc       -> ValueError
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import scitex as stx

import figrecipe as fr


def ng_r1_child_outside_container(out):
    """R1: Child extends outside container."""
    s = fr.Schematic(width_mm=170, height_mm=80)
    s.add_container(
        "c",
        title="Container",
        children=["a"],
        x_mm=85,
        y_mm=40,
        width_mm=40,
        height_mm=30,
    )
    s.add_box("a", "Box A", x_mm=130, y_mm=40, width_mm=30, height_mm=20)
    s.render_to_file(out / "ng_r1_child_outside.png")


def ng_r2_box_overlap(out):
    """R2: Two boxes overlap."""
    s = fr.Schematic(width_mm=170, height_mm=80)
    s.add_box("a", "Box A", x_mm=60, y_mm=40, width_mm=40, height_mm=25)
    s.add_box("b", "Box B", x_mm=70, y_mm=40, width_mm=40, height_mm=25)
    s.render_to_file(out / "ng_r2_box_overlap.png")


def ng_r5_text_too_close(out):
    """R5: Arrow labels too close to each other."""
    s = fr.Schematic(width_mm=170, height_mm=80)
    s.add_box("a", "A", x_mm=30, y_mm=40, width_mm=30, height_mm=20)
    s.add_box("b", "B", x_mm=140, y_mm=40, width_mm=30, height_mm=20)
    s.add_arrow("a", "b", label="forward")
    s.add_arrow("b", "a", label="backward")
    s.render_to_file(out / "ng_r5_text_too_close.png")


def ng_r7_arrow_occluded(out):
    """R7: Arrow occluded by text (< 90% visible)."""
    s = fr.Schematic(width_mm=170, height_mm=80)
    s.add_box("a", "Long Title", x_mm=50, y_mm=40, width_mm=50, height_mm=25)
    s.add_box("b", "Long Title", x_mm=120, y_mm=40, width_mm=50, height_mm=25)
    s.add_arrow("a", "b", label="occluded-label")
    s.render_to_file(out / "ng_r7_arrow_occluded.png")


def ng_r8_label_wrong_side(out):
    """R8: Curved-arrow label on wrong side of arc."""
    s = fr.Schematic(width_mm=170, height_mm=80)
    s.add_box("a", "A", x_mm=40, y_mm=40, width_mm=30, height_mm=20)
    s.add_box("b", "B", x_mm=130, y_mm=40, width_mm=30, height_mm=20)
    s.add_arrow(
        "a",
        "b",
        label="wrong-side",
        curve=0.5,
        label_offset_mm=(0, 50),
    )
    s.render_to_file(out / "ng_r8_label_wrong_side.png")


@stx.session
def main(CONFIG=stx.session.INJECTED, logger=stx.session.INJECTED):
    """Generate NG pattern figures (all saved with _FAILED suffix)."""
    out = Path(CONFIG.SDIR_OUT)

    cases = [
        ("R1", ng_r1_child_outside_container),
        ("R2", ng_r2_box_overlap),
        ("R5", ng_r5_text_too_close),
        ("R7", ng_r7_arrow_occluded),
        ("R8", ng_r8_label_wrong_side),
    ]
    for rule, fn in cases:
        try:
            fn(out)
            logger.warning(f"{rule}: UNEXPECTED PASS")
        except ValueError as e:
            logger.info(f"{rule}: {e}")
    return 0


if __name__ == "__main__":
    main()

# EOF
