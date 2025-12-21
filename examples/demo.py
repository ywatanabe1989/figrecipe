#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo script for plotspec."""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

import plotspec as mpr


def main():
    """Demonstrate plotspec recording and reproduction."""
    print("=" * 60)
    print("plotspec Demo")
    print("=" * 60)

    # Setup output directory
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create sample data
    x = np.linspace(0, 2 * np.pi, 100)
    y_sin = np.sin(x)
    y_cos = np.cos(x)

    # 1. Record a figure
    print("\n1. Creating and recording a figure...")
    fig, ax = mpr.subplots(figsize=(10, 6))

    ax.plot(x, y_sin, color='blue', linewidth=2, label='sin(x)', id='sine')
    ax.plot(x, y_cos, color='red', linewidth=2, linestyle='--', label='cos(x)', id='cosine')
    ax.scatter(x[::10], y_sin[::10], s=50, color='blue', alpha=0.5, id='sine_points')
    ax.set_xlabel('x (radians)')
    ax.set_ylabel('y')
    ax.set_title('Trigonometric Functions')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Save the recipe
    recipe_path = output_dir / "demo_figure.yaml"
    mpr.save(fig, recipe_path)
    print(f"   Saved recipe to: {recipe_path}")
    plt.close(fig.fig)

    # 2. Inspect the recipe
    print("\n2. Inspecting the recipe...")
    info = mpr.info(recipe_path)
    print(f"   Figure ID: {info['id']}")
    print(f"   Created: {info['created']}")
    print(f"   Figure size: {info['figsize']}")
    print(f"   Number of calls: {len(info['calls'])}")
    print("   Calls:")
    for call in info['calls']:
        print(f"      - {call['id']}: {call['function']}()")

    # 3. Reproduce the figure
    print("\n3. Reproducing the figure...")
    fig2, ax2 = mpr.reproduce(recipe_path)
    reproduced_path = output_dir / "demo_reproduced.png"
    fig2.savefig(reproduced_path, dpi=150, bbox_inches='tight')
    print(f"   Saved reproduced figure to: {reproduced_path}")
    plt.close(fig2)

    # 4. Reproduce only specific calls
    print("\n4. Reproducing only 'sine' call...")
    fig3, ax3 = mpr.reproduce(recipe_path, calls=['sine'])
    ax3.set_title('Only Sine Wave')
    sine_only_path = output_dir / "demo_sine_only.png"
    fig3.savefig(sine_only_path, dpi=150, bbox_inches='tight')
    print(f"   Saved to: {sine_only_path}")
    plt.close(fig3)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)

    # Show the recipe file content
    print("\nRecipe file content:")
    print("-" * 40)
    with open(str(recipe_path)) as f:
        content = f.read()
        # Print first 80 lines
        lines = content.split('\n')[:80]
        print('\n'.join(lines))
        if len(content.split('\n')) > 80:
            print("... (truncated)")


if __name__ == "__main__":
    main()
