#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 06: MM-Layout and Style
=============================
Demonstrates publication-quality figure creation with millimeter-based
layout control and style application.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as ps


def main():
    print("Demo 06: MM-Layout and Style")
    print("=" * 50)

    # Setup output directory
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # === Load and inspect style ===
    print("\n1. Loading style configuration...")
    style = ps.load_style()
    print(f"   Axes width: {style.axes.width_mm} mm")
    print(f"   Axes height: {style.axes.height_mm} mm")
    print(f"   Font family: {style.fonts.family}")
    print(f"   Axis label size: {style.fonts.axis_label_pt} pt")

    # === Create figure with MM-based layout ===
    print("\n2. Creating figure with mm-based layout...")

    # Create sample data
    x = np.linspace(0, 2 * np.pi, 100)
    y_sin = np.sin(x)
    y_cos = np.cos(x)

    # Create figure with specific mm dimensions
    fig, ax = ps.subplots(
        axes_width_mm=60,       # 60mm wide axes
        axes_height_mm=40,      # 40mm tall axes
        margin_left_mm=15,      # Space for y-axis labels
        margin_right_mm=5,
        margin_bottom_mm=12,    # Space for x-axis labels
        margin_top_mm=8,        # Space for title
        apply_style_mm=True,    # Apply publication style
    )

    figsize_in = fig.fig.get_size_inches()
    figsize_mm = (figsize_in[0] * 25.4, figsize_in[1] * 25.4)
    print(f"   Figure size: {figsize_mm[0]:.1f} x {figsize_mm[1]:.1f} mm")

    # Plot with style-aware line width (colors auto-cycle from SCITEX palette)
    trace_lw = ps.mm_to_pt(style.lines.trace_mm)
    ax.plot(x, y_sin, linewidth=trace_lw, label='sin(x)', id='sine')  # Auto: blue
    ax.plot(x, y_cos, linewidth=trace_lw, label='cos(x)', id='cosine')  # Auto: orange

    ax.set_xlabel('x (radians)')
    ax.set_ylabel('y')
    ax.set_title('Trigonometric Functions')
    ax.legend(loc='upper right')

    # Save original (transparent background)
    original_path = output_dir / '06_mm_layout_original.png'
    fig.fig.savefig(original_path, dpi=300, bbox_inches='tight',
                    transparent=True, edgecolor='none')
    print(f"   Saved: {original_path}")

    # === Save recipe ===
    print("\n3. Saving recipe...")
    recipe_path = output_dir / '06_mm_layout.yaml'
    ps.save(fig, recipe_path)
    print(f"   Saved: {recipe_path}")
    plt.close(fig.fig)

    # === Reproduce with style ===
    print("\n4. Reproducing from recipe...")
    fig2, ax2 = ps.reproduce(recipe_path)

    # Apply style to reproduced figure
    ps.apply_style(ax2)

    reproduced_path = output_dir / '06_mm_layout_reproduced.png'
    fig2.savefig(reproduced_path, dpi=300, bbox_inches='tight',
                 transparent=True, edgecolor='none')
    print(f"   Saved: {reproduced_path}")
    plt.close(fig2)

    # === Multi-panel figure with mm layout ===
    print("\n5. Creating multi-panel figure...")

    # Colors will auto-cycle from SCITEX palette (set via apply_style_mm=True)
    fig3, axes = ps.subplots(
        nrows=2,
        ncols=2,
        axes_width_mm=35,       # Compact panels
        axes_height_mm=25,
        margin_left_mm=12,
        margin_right_mm=3,
        margin_bottom_mm=12,    # More space for x labels
        margin_top_mm=8,        # More space for titles
        space_w_mm=15,          # Horizontal spacing (for y labels)
        space_h_mm=18,          # Vertical spacing (for titles + x labels)
        apply_style_mm=True,
    )

    figsize_in = fig3.fig.get_size_inches()
    figsize_mm = (figsize_in[0] * 25.4, figsize_in[1] * 25.4)
    print(f"   Figure size: {figsize_mm[0]:.1f} x {figsize_mm[1]:.1f} mm")

    # Fill panels
    np.random.seed(42)

    # Get first 4 colors from the auto-set palette for consistency across panels
    import matplotlib as mpl
    palette = mpl.rcParams['axes.prop_cycle'].by_key()['color']

    # Panel A: Line plot (auto blue)
    axes[0][0].plot(x, y_sin, lw=trace_lw, id='panel_a')  # Uses first color
    axes[0][0].set_xlabel('Time (s)')
    axes[0][0].set_ylabel('Amplitude')
    axes[0][0].set_title('A) Sine Wave')

    # Panel B: Scatter plot (use palette[1] for orange)
    scatter_x = np.random.randn(50)
    scatter_y = np.random.randn(50)
    axes[0][1].scatter(scatter_x, scatter_y, s=10, alpha=0.7, color=palette[1], id='panel_b')
    axes[0][1].set_xlabel('X')
    axes[0][1].set_ylabel('Y')
    axes[0][1].set_title('B) Scatter')

    # Panel C: Bar plot (use palette[2] for green)
    categories = ['A', 'B', 'C', 'D']
    values = [23, 45, 56, 78]
    axes[1][0].bar(categories, values, color=palette[2], edgecolor='black', linewidth=0.5, id='panel_c')
    axes[1][0].set_xlabel('Category')
    axes[1][0].set_ylabel('Count')
    axes[1][0].set_title('C) Bar Chart')

    # Panel D: Histogram (use palette[3] for purple)
    data = np.random.randn(200)
    axes[1][1].hist(data, bins=20, color=palette[3], edgecolor='black', linewidth=0.5, id='panel_d')
    axes[1][1].set_xlabel('Value')
    axes[1][1].set_ylabel('Frequency')
    axes[1][1].set_title('D) Histogram')

    # Save (transparent background)
    multi_path = output_dir / '06_mm_layout_multi.png'
    fig3.fig.savefig(multi_path, dpi=300, bbox_inches='tight',
                     transparent=True, edgecolor='none')
    print(f"   Saved: {multi_path}")

    # Save recipe
    multi_recipe_path = output_dir / '06_mm_layout_multi.yaml'
    ps.save(fig3, multi_recipe_path)
    print(f"   Recipe: {multi_recipe_path}")
    plt.close(fig3.fig)

    # === Using style.to_subplots_kwargs() ===
    print("\n6. Using style.to_subplots_kwargs()...")

    # This shows the alternative API using style directly
    style_kwargs = style.to_subplots_kwargs()
    print(f"   Available kwargs: {list(style_kwargs.keys())[:5]}...")

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nKey features demonstrated:")
    print("  - mm-based figure sizing (axes_width_mm, axes_height_mm)")
    print("  - mm-based margins (margin_*_mm)")
    print("  - mm-based spacing (space_w_mm, space_h_mm)")
    print("  - Style loading (ps.load_style())")
    print("  - Style application (ps.apply_style() or apply_style_mm=True)")
    print("  - Unit conversion (ps.mm_to_pt())")


if __name__ == "__main__":
    main()
