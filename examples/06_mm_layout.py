#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 06: MM-Based Layout
========================
Demonstrates millimeter-based figure sizing and positioning for
precise control over publication figure dimensions.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as ps


def main():
    print("Demo 06: MM-Based Layout")
    print("=" * 50)

    # Setup output directory
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # === Single panel with precise mm dimensions ===
    print("\n1. Single panel with mm dimensions...")

    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    # Create figure with specific mm dimensions
    fig, ax = ps.subplots(
        axes_width_mm=60,       # 60mm wide axes
        axes_height_mm=40,      # 40mm tall axes
        margin_left_mm=15,      # Space for y-axis labels
        margin_right_mm=5,
        margin_bottom_mm=12,    # Space for x-axis labels
        margin_top_mm=8,        # Space for title
    )

    # Report actual size
    figsize_in = fig.fig.get_size_inches()
    figsize_mm = (figsize_in[0] * 25.4, figsize_in[1] * 25.4)
    print(f"   Figure size: {figsize_mm[0]:.1f} x {figsize_mm[1]:.1f} mm")
    print(f"   Axes size: 60 x 40 mm")

    ax.plot(x, y, color='#0072B2', linewidth=1.5, label='sin(x)', id='sine')
    ax.set_xlabel('x (radians)')
    ax.set_ylabel('y')
    ax.set_title('Single Panel (60x40 mm axes)')
    ax.legend()

    original_path = output_dir / '06_mm_layout_original.png'
    fig.fig.savefig(original_path, dpi=300)  # No bbox_inches='tight' for exact size
    print(f"   Saved: {original_path}")

    # Save recipe
    recipe_path = output_dir / '06_mm_layout.yaml'
    ps.save(fig, recipe_path)
    print(f"   Recipe: {recipe_path}")
    plt.close(fig.fig)

    # === Reproduce from recipe ===
    print("\n2. Reproducing from recipe...")
    fig2, ax2 = ps.reproduce(recipe_path)

    reproduced_path = output_dir / '06_mm_layout_reproduced.png'
    fig2.savefig(reproduced_path, dpi=300)  # No bbox_inches='tight' for exact size
    print(f"   Saved: {reproduced_path}")

    # Verify figure size matches
    reproduced_size = fig2.get_size_inches()
    print(f"   Original size: {figsize_mm[0]:.1f} x {figsize_mm[1]:.1f} mm")
    print(f"   Reproduced size: {reproduced_size[0]*25.4:.1f} x {reproduced_size[1]*25.4:.1f} mm")
    plt.close(fig2)

    # Image diff validation
    from plotspec._utils import compare_images
    diff = compare_images(original_path, reproduced_path)
    print(f"\n   Image comparison:")
    print(f"   - Dimensions: {diff['size1']} vs {diff['size2']} ({'match' if diff['same_size'] else 'DIFFER'})")
    print(f"   - File sizes: {diff['file_size1']//1024}K vs {diff['file_size2']//1024}K")
    print(f"   - Pixel MSE: {diff['mse']:.2f}")
    print(f"   - Identical: {diff['identical']}")

    # === Multi-panel with mm spacing ===
    print("\n3. Multi-panel with mm spacing...")

    fig3, axes = ps.subplots(
        nrows=2,
        ncols=2,
        axes_width_mm=35,       # Compact 35mm wide panels
        axes_height_mm=25,      # 25mm tall panels
        margin_left_mm=12,
        margin_right_mm=3,
        margin_bottom_mm=10,
        margin_top_mm=6,
        space_w_mm=15,          # 15mm horizontal gap
        space_h_mm=15,          # 15mm vertical gap
    )

    figsize_in = fig3.fig.get_size_inches()
    figsize_mm = (figsize_in[0] * 25.4, figsize_in[1] * 25.4)
    print(f"   Figure size: {figsize_mm[0]:.1f} x {figsize_mm[1]:.1f} mm")
    print(f"   Each panel: 35 x 25 mm")
    print(f"   Spacing: 15 mm (h & v)")

    np.random.seed(42)
    colors = ['#0072B2', '#D55E00', '#009E73', '#CC79A7']

    # Panel A
    axes[0][0].plot(x, np.sin(x), color=colors[0], id='panel_a')
    axes[0][0].set_title('A) Sine')

    # Panel B
    axes[0][1].plot(x, np.cos(x), color=colors[1], id='panel_b')
    axes[0][1].set_title('B) Cosine')

    # Panel C
    axes[1][0].bar(['A', 'B', 'C'], [3, 7, 5], color=colors[2], id='panel_c')
    axes[1][0].set_title('C) Bar')

    # Panel D
    axes[1][1].scatter(np.random.randn(30), np.random.randn(30),
                       s=20, color=colors[3], id='panel_d')
    axes[1][1].set_title('D) Scatter')

    multi_path = output_dir / '06_mm_layout_multi.png'
    fig3.fig.savefig(multi_path, dpi=300)
    print(f"   Saved: {multi_path}")

    multi_recipe = output_dir / '06_mm_layout_multi.yaml'
    ps.save(fig3, multi_recipe)
    print(f"   Recipe: {multi_recipe}")
    plt.close(fig3.fig)

    # === Unit conversion utilities ===
    print("\n4. Unit conversion utilities...")
    print(f"   10 mm = {ps.mm_to_inch(10):.3f} inches")
    print(f"   10 mm = {ps.mm_to_pt(10):.1f} points")
    print(f"   1 inch = {ps.inch_to_mm(1):.1f} mm")
    print(f"   72 pt = {ps.pt_to_mm(72):.1f} mm")

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nKey mm-layout features:")
    print("  - axes_width_mm, axes_height_mm: Precise axes dimensions")
    print("  - margin_*_mm: Precise margins for labels")
    print("  - space_w_mm, space_h_mm: Inter-panel spacing")
    print("  - Unit conversion: mm_to_inch(), mm_to_pt(), etc.")


if __name__ == "__main__":
    main()
