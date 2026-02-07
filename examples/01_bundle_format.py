#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example 01: Bundle Format - The recommended way to save and share figures.

This example demonstrates the ZIP bundle format which packages:
- spec.json: What to plot (semantic specification)
- style.json: How it looks (appearance settings)
- data.csv: Immutable source data
- exports/: PNG and hitmap images

Usage:
    python 01_bundle_format.py
"""

from pathlib import Path

import numpy as np
import scitex as stx

import figrecipe as fr


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate bundle format for reproducible figures."""
    OUT = Path(CONFIG.SDIR_OUT)

    logger.info("=" * 60)
    logger.info("FigRecipe Bundle Format Example")
    logger.info("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Create a figure with tracked data
    # -------------------------------------------------------------------------
    logger.info("1. Creating figure with scatter and line data...")

    fig, ax = fr.subplots()

    # Create sample data
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([1, 4, 9, 16, 25])

    # Plot with explicit IDs (used in data.csv column names)
    ax.scatter(x, y, s=100, c="steelblue", label="Data points", id="measurements")
    ax.plot(x, y, "--", alpha=0.5, color="gray", label="Trend", id="trend")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Value")
    ax.set_title("Quadratic Growth")
    ax.legend()

    # -------------------------------------------------------------------------
    # 2. Save as ZIP bundle (recommended for sharing)
    # -------------------------------------------------------------------------
    logger.info("2. Saving as ZIP bundle...")

    bundle_path = fr.save(fig, OUT / "figure.zip")
    logger.info(f"   Created: {bundle_path[0]}")

    # -------------------------------------------------------------------------
    # 3. Examine bundle contents
    # -------------------------------------------------------------------------
    logger.info("3. Bundle contents:")
    logger.info("   figure.zip")
    logger.info("   ├── spec.json      (WHAT: traces, axes, data mappings)")
    logger.info("   ├── style.json     (HOW: colors, fonts, sizes)")
    logger.info("   ├── data.csv       (DATA: immutable source)")
    logger.info("   └── exports/")
    logger.info("       ├── figure.png")
    logger.info("       └── figure_hitmap.png")

    # -------------------------------------------------------------------------
    # 4. Load bundle components
    # -------------------------------------------------------------------------
    logger.info("4. Loading bundle components...")

    spec, style, data = fr.load_bundle(OUT / "figure.zip")

    logger.info(f"   Spec keys: {list(spec.keys())}")
    logger.info(f"   Style keys: {list(style.keys())}")
    logger.info(f"   Data columns: {list(data.columns)}")
    logger.info(f"   Data shape: {data.shape}")

    # -------------------------------------------------------------------------
    # 5. Reproduce from bundle
    # -------------------------------------------------------------------------
    logger.info("5. Reproducing figure from bundle...")

    fig2, axes2 = fr.reproduce_bundle(OUT / "figure.zip")
    fr.save(fig2, OUT / "reproduced.png", verbose=False)
    logger.info(f"   Saved: {OUT / 'reproduced.png'}")

    # -------------------------------------------------------------------------
    # 6. Also save as YAML for comparison
    # -------------------------------------------------------------------------
    logger.info("6. For comparison, also saving as YAML format...")

    fig3, ax3 = fr.subplots()
    ax3.scatter(x, y, s=100, c="steelblue", id="measurements")
    ax3.set_title("Same data, YAML format")
    fr.save(fig3, OUT / "figure_yaml.png", verbose=False)
    logger.info(f"   Created: {OUT / 'figure_yaml.png'}")
    logger.info(f"   Created: {OUT / 'figure_yaml.yaml'}")
    logger.info(f"   Created: {OUT / 'figure_yaml_data/'}")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    logger.info("=" * 60)
    logger.info("Summary: ZIP vs YAML formats")
    logger.info("=" * 60)
    logger.info("""
    ZIP Bundle (recommended for sharing):
    + Self-contained single file
    + Layered architecture (spec + style + data)
    + Portable across systems
    + Includes hitmap for GUI editor

    YAML Format (for development):
    + Human-readable recipe
    + Easy to edit manually
    + Git-friendly diffs
    + Separate data files
    """)

    logger.info(f"Output directory: {OUT}")

    return 0


if __name__ == "__main__":
    main()
