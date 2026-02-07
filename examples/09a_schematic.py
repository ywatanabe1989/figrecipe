#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schematic diagrams with fr.Schematic().

Demonstrates box-and-arrow schematics with mm-based coordinates:
1. Left-to-right pipeline layout
2. Top-to-bottom architecture layout
3. Serialization roundtrip (to_dict / from_dict)
4. Reproduction validation (fr.save + fr.reproduce pixel match)

Outputs:
    ./09_schematic_out/schematic_lr.{png,yaml}
    ./09_schematic_out/schematic_tb.{png,yaml}
    ./09_schematic_out/roundtrip.{png,yaml}
    ./09_schematic_out/reproduced.{png,yaml}
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
    """Run schematic demos."""
    OUT = Path(CONFIG.SDIR_OUT)

    # --- 1. Left-to-Right pipeline ---
    logger.info("Demo 1: Left-to-Right pipeline")
    s = fr.Schematic(title="EEG Analysis Pipeline", width_mm=350, height_mm=100)
    s.add_box("raw", "Raw EEG", subtitle="64 channels", emphasis="muted")
    s.add_box("filter", "Bandpass Filter", subtitle="0.5-45 Hz", emphasis="primary")
    s.add_box("ica", "ICA", subtitle="Artifact removal", emphasis="primary")
    s.add_box("epoch", "Epoching", subtitle="-0.2 to 0.8s", emphasis="success")
    s.add_box("classify", "Classification", subtitle="SVM / CNN", emphasis="warning")
    s.add_arrow("raw", "filter")
    s.add_arrow("filter", "ica")
    s.add_arrow("ica", "epoch")
    s.add_arrow("epoch", "classify")
    s.auto_layout(layout="lr", gap_mm=15)
    fig1, ax1 = fr.subplots()
    ax1.schematic(s, id="eeg_pipeline")
    fr.save(fig1, OUT / "schematic_lr.png", validate=False)

    # --- 2. Top-to-Bottom architecture ---
    logger.info("Demo 2: Top-to-Bottom architecture")
    s2 = fr.Schematic(title="Neural Network", width_mm=150, height_mm=250)
    s2.add_box("input", "Input Layer", subtitle="784 neurons", emphasis="muted")
    s2.add_box("conv1", "Conv2D", subtitle="32 filters", emphasis="primary")
    s2.add_box("pool1", "MaxPool", subtitle="2x2", emphasis="normal")
    s2.add_box("fc", "Dense", subtitle="128 neurons", emphasis="success")
    s2.add_box("out", "Output", subtitle="10 classes", emphasis="warning")
    s2.add_arrow("input", "conv1")
    s2.add_arrow("conv1", "pool1")
    s2.add_arrow("pool1", "fc")
    s2.add_arrow("fc", "out")
    s2.auto_layout(layout="tb", gap_mm=10)
    fig2, ax2 = fr.subplots()
    ax2.schematic(s2, id="neural_net")
    fr.save(fig2, OUT / "schematic_tb.png", validate=False)

    # --- 3. Serialization roundtrip ---
    logger.info("Demo 3: Serialization roundtrip")
    data = s.to_dict()
    s_loaded = fr.Schematic.from_dict(data)
    fig3, ax3 = fr.subplots()
    ax3.schematic(s_loaded, id="roundtrip")
    fr.save(fig3, OUT / "roundtrip.png", validate=False)
    logger.info(f"  Boxes: {len(data['boxes'])}, Arrows: {len(data['arrows'])}")

    # --- 4. Reproduction validation ---
    logger.info("Demo 4: Reproduction validation")
    fig4, ax4 = fr.subplots()
    s4 = fr.Schematic(title="Simple Flow")
    s4.add_box("a", "Step A", emphasis="primary")
    s4.add_box("b", "Step B", emphasis="success")
    s4.add_arrow("a", "b")
    s4.auto_layout(layout="lr")
    ax4.schematic(s4, id="my_schematic")
    fr.save(fig4, OUT / "recipe.yaml", validate=False)

    fig5, axes5 = fr.reproduce(OUT / "recipe.yaml")
    fr.save(fig5, OUT / "reproduced.png", validate=False)
    logger.info("  Saved recipe.yaml and reproduced.png")

    logger.info(f"All outputs saved to: {OUT}/")
    return 0


if __name__ == "__main__":
    main()

# EOF
