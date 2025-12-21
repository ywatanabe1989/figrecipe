#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 05: Seaborn Integration
============================
Shows how to record and reproduce seaborn plots.
"""

import sys
sys.path.insert(0, '../src')

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    import pandas as pd
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Seaborn/pandas not installed. Skipping seaborn demo.")
    print("Install with: pip install seaborn pandas")
    sys.exit(0)

import plotspec as ps


def main():
    print("Demo 05: Seaborn Integration")
    print("=" * 50)

    # Setup output directory
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create sample data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'x': np.random.randn(n),
        'y': np.random.randn(n) * 2 + 1,
        'category': np.random.choice(['A', 'B', 'C'], n),
        'size': np.random.rand(n) * 100,
    })

    # === RECORD ===
    print("\n1. Recording seaborn figure...")
    fig, ax = ps.subplots(figsize=(10, 6))

    # Use ps.sns instead of sns directly
    ps.sns.scatterplot(
        data=df,
        x='x',
        y='y',
        hue='category',
        size='size',
        sizes=(20, 200),
        alpha=0.7,
        ax=ax,
        id='scatter_by_category',
    )

    ax.set_title('Seaborn Scatterplot with plotspec')
    ax.set_xlabel('X Value')
    ax.set_ylabel('Y Value')

    # Save original
    original_path = output_dir / '05_seaborn_original.png'
    fig.fig.savefig(original_path, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    print(f"   Saved: {original_path}")

    # === SAVE RECIPE ===
    print("\n2. Saving recipe...")
    recipe_path = output_dir / '05_seaborn.yaml'
    ps.save(fig, recipe_path)
    print(f"   Saved: {recipe_path}")
    plt.close(fig.fig)

    # === REPRODUCE ===
    print("\n3. Reproducing from recipe...")
    fig2, ax2 = ps.reproduce(recipe_path)
    reproduced_path = output_dir / '05_seaborn_reproduced.png'
    fig2.savefig(reproduced_path, dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print(f"   Saved: {reproduced_path}")
    plt.close(fig2)

    # === INFO ===
    print("\n4. Recipe info:")
    info = ps.info(recipe_path)
    print(f"   Figure ID: {info['id']}")
    print(f"   Size: {info['figsize']}")
    print(f"   Calls: {len(info['calls'])}")
    for call in info['calls']:
        print(f"      - {call['id']}: {call['function']}()")

    # === LINEPLOT ===
    print("\n5. Lineplot example...")
    fig3, ax3 = ps.subplots(figsize=(10, 6))

    # Create time series data
    time_df = pd.DataFrame({
        'time': np.tile(np.arange(20), 3),
        'value': np.concatenate([
            np.sin(np.linspace(0, 4*np.pi, 20)) + np.random.randn(20) * 0.1,
            np.cos(np.linspace(0, 4*np.pi, 20)) + np.random.randn(20) * 0.1,
            np.sin(np.linspace(0, 4*np.pi, 20) + 1) + np.random.randn(20) * 0.1,
        ]),
        'group': np.repeat(['A', 'B', 'C'], 20),
    })

    ps.sns.lineplot(
        data=time_df,
        x='time',
        y='value',
        hue='group',
        ax=ax3,
        id='lineplot',
    )
    ax3.set_title('Lineplot with Groups')

    # Save
    line_recipe = output_dir / '05_seaborn_line.yaml'
    ps.save(fig3, line_recipe)
    fig3.fig.savefig(output_dir / '05_seaborn_line_original.png',
                     dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig3.fig)
    print(f"   Saved: {line_recipe}")

    # Reproduce
    fig4, _ = ps.reproduce(line_recipe)
    fig4.savefig(output_dir / '05_seaborn_line_reproduced.png',
                 dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig4)
    print("   Reproduced lineplot successfully!")

    print("\n" + "=" * 50)
    print("Demo complete!")


if __name__ == "__main__":
    main()
