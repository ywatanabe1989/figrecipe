#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 07: SCITEX Style
=====================
Demonstrates publication-quality styling with SCITEX color palette,
font settings, and theme support.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as ps


def main():
    print("Demo 07: SCITEX Style")
    print("=" * 50)

    # Setup output directory
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # === Load style configuration ===
    print("\n1. Loading style configuration...")
    style = ps.load_style()
    print(f"   Font family: {style.fonts.family}")
    print(f"   Axis font size: {style.fonts.axis_label_pt} pt")
    print(f"   Tick font size: {style.fonts.tick_label_pt} pt")
    print(f"   Axes thickness: {style.axes.thickness_mm} mm")
    print(f"   Trace line width: {style.lines.trace_mm} mm")

    # === SCITEX color palette ===
    print("\n2. SCITEX color palette...")
    palette = style.colors.palette
    for i, color in enumerate(palette[:6]):
        names = ['Blue', 'Orange', 'Green', 'Purple', 'Yellow', 'Cyan']
        print(f"   {names[i]}: {color}")

    # === Styled figure with auto color cycling ===
    print("\n3. Creating styled figure with auto color cycling...")

    x = np.linspace(0, 2 * np.pi, 100)

    # Create figure with style applied
    fig, ax = ps.subplots(
        axes_width_mm=70,
        axes_height_mm=50,
        margin_left_mm=15,
        margin_bottom_mm=12,
        apply_style_mm=True,  # Apply SCITEX style
    )

    # Colors auto-cycle from SCITEX palette
    trace_lw = ps.mm_to_pt(style.lines.trace_mm)
    ax.plot(x, np.sin(x), linewidth=trace_lw, label='sin(x)', id='sin')
    ax.plot(x, np.cos(x), linewidth=trace_lw, label='cos(x)', id='cos')
    ax.plot(x, np.sin(2*x), linewidth=trace_lw, label='sin(2x)', id='sin2x')
    ax.plot(x, np.cos(2*x), linewidth=trace_lw, label='cos(2x)', id='cos2x')

    ax.set_xlabel('x (radians)')
    ax.set_ylabel('y')
    ax.set_title('Auto Color Cycling')
    ax.legend(loc='upper right')

    styled_path = output_dir / '07_style_colors.png'
    fig.fig.savefig(styled_path, dpi=300, bbox_inches='tight', transparent=True)
    print(f"   Saved: {styled_path}")

    # Save with validation
    recipe_path = output_dir / '07_style_colors.yaml'
    path, validation = ps.save(fig, recipe_path, validate=True)
    print(f"   Recipe: {recipe_path}")
    print(f"   Validation: {'PASSED' if validation.valid else 'FAILED'} (MSE: {validation.mse:.2f})")
    plt.close(fig.fig)

    # === Dark theme ===
    print("\n4. Dark theme example...")

    fig2, ax2 = ps.subplots(
        axes_width_mm=70,
        axes_height_mm=50,
        margin_left_mm=15,
        margin_bottom_mm=12,
    )

    # Apply dark theme
    from plotspec.styles import apply_theme_colors
    apply_theme_colors(ax2.ax, theme='dark')

    ax2.plot(x, np.sin(x), color='#56B4E9', linewidth=1.5, label='Signal', id='signal')
    ax2.fill_between(x, np.sin(x) - 0.2, np.sin(x) + 0.2, alpha=0.3,
                     color='#56B4E9', id='confidence')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('Dark Theme')
    ax2.legend()

    dark_path = output_dir / '07_style_dark.png'
    fig2.fig.savefig(dark_path, dpi=300, bbox_inches='tight')
    print(f"   Saved: {dark_path}")
    plt.close(fig2.fig)

    # === Manual style application ===
    print("\n5. Manual style application...")

    fig3, ax3 = plt.subplots(figsize=(4, 3))

    # Plot first
    ax3.plot(x, np.sin(x), label='Data')
    ax3.scatter(x[::10], np.sin(x[::10]), s=30, zorder=5, label='Points')
    ax3.set_xlabel('X axis')
    ax3.set_ylabel('Y axis')
    ax3.set_title('Manual Style')
    ax3.legend()

    # Apply style after plotting
    ps.apply_style(ax3)

    manual_path = output_dir / '07_style_manual.png'
    fig3.savefig(manual_path, dpi=300, bbox_inches='tight', transparent=True)
    print(f"   Saved: {manual_path}")
    plt.close(fig3)

    # === Style configuration details ===
    print("\n6. Style configuration keys...")
    kwargs = style.to_subplots_kwargs()
    print(f"   Available: {list(kwargs.keys())[:6]}...")

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nKey style features:")
    print("  - SCITEX colorblind-friendly palette")
    print("  - Auto color cycling with apply_style_mm=True")
    print("  - Dark/light theme support")
    print("  - Publication-quality fonts and line widths")
    print("  - Transparent background (none)")
    print("  - ps.apply_style() for manual application")


if __name__ == "__main__":
    main()
