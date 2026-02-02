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

import figrecipe as fr

OUT = Path(__file__).parent / "01_bundle_format_out"
OUT.mkdir(exist_ok=True)


def main():
    """Demonstrate bundle format for reproducible figures."""
    print("=" * 60)
    print("FigRecipe Bundle Format Example")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # 1. Create a figure with tracked data
    # -------------------------------------------------------------------------
    print("\n1. Creating figure with scatter and line data...")

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
    print("\n2. Saving as ZIP bundle...")

    bundle_path = fr.save(fig, OUT / "figure.zip")
    print(f"   Created: {bundle_path[0]}")

    # -------------------------------------------------------------------------
    # 3. Examine bundle contents
    # -------------------------------------------------------------------------
    print("\n3. Bundle contents:")
    print("   figure.zip")
    print("   ├── spec.json      (WHAT: traces, axes, data mappings)")
    print("   ├── style.json     (HOW: colors, fonts, sizes)")
    print("   ├── data.csv       (DATA: immutable source)")
    print("   └── exports/")
    print("       ├── figure.png")
    print("       └── figure_hitmap.png")

    # -------------------------------------------------------------------------
    # 4. Load bundle components
    # -------------------------------------------------------------------------
    print("\n4. Loading bundle components...")

    spec, style, data = fr.load_bundle(OUT / "figure.zip")

    print(f"   Spec keys: {list(spec.keys())}")
    print(f"   Style keys: {list(style.keys())}")
    print(f"   Data columns: {list(data.columns)}")
    print(f"   Data shape: {data.shape}")

    # -------------------------------------------------------------------------
    # 5. Reproduce from bundle
    # -------------------------------------------------------------------------
    print("\n5. Reproducing figure from bundle...")

    fig2, axes2 = fr.reproduce_bundle(OUT / "figure.zip")
    fr.save(fig2, OUT / "reproduced.png", verbose=False)
    print(f"   Saved: {OUT / 'reproduced.png'}")

    # -------------------------------------------------------------------------
    # 6. Also save as YAML for comparison
    # -------------------------------------------------------------------------
    print("\n6. For comparison, also saving as YAML format...")

    fig3, ax3 = fr.subplots()
    ax3.scatter(x, y, s=100, c="steelblue", id="measurements")
    ax3.set_title("Same data, YAML format")
    fr.save(fig3, OUT / "figure_yaml.png", verbose=False)
    print(f"   Created: {OUT / 'figure_yaml.png'}")
    print(f"   Created: {OUT / 'figure_yaml.yaml'}")
    print(f"   Created: {OUT / 'figure_yaml_data/'}")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary: ZIP vs YAML formats")
    print("=" * 60)
    print("""
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

    print(f"Output directory: {OUT}")
    print("\nDone!")


if __name__ == "__main__":
    main()
