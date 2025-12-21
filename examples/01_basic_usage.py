#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo 01: Basic Usage
====================
Shows the fundamental workflow: record, save, reproduce.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as mpr


def main():
    print("Demo 01: Basic Usage")
    print("=" * 50)

    # Setup output directory
    from pathlib import Path
    output_dir = Path(__file__).parent.parent / 'outputs' / 'examples'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create sample data
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    # === RECORD ===
    print("\n1. Recording figure...")
    fig, ax = mpr.subplots(figsize=(8, 5))

    ax.plot(x, y, color='#2ecc71', linewidth=2.5, label='sin(x)')
    ax.fill_between(x, y, alpha=0.3, color='#2ecc71')
    ax.set_xlabel('x (radians)', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title('Simple Sine Wave', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 2 * np.pi)

    # Save original
    original_path = output_dir / '01_original.png'
    fig.fig.savefig(original_path, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    print(f"   Saved: {original_path}")

    # === SAVE RECIPE ===
    print("\n2. Saving recipe...")
    recipe_path = output_dir / '01_basic.yaml'
    mpr.save(fig, recipe_path)
    print(f"   Saved: {recipe_path}")
    plt.close(fig.fig)

    # === REPRODUCE ===
    print("\n3. Reproducing from recipe...")
    fig2, ax2 = mpr.reproduce(recipe_path)
    reproduced_path = output_dir / '01_reproduced.png'
    fig2.savefig(reproduced_path, dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print(f"   Saved: {reproduced_path}")
    plt.close(fig2)

    # === INFO ===
    print("\n4. Recipe info:")
    info = mpr.info(recipe_path)
    print(f"   Figure ID: {info['id']}")
    print(f"   Size: {info['figsize']}")
    print(f"   Calls: {len(info['calls'])}")

    print("\n" + "=" * 50)
    print("Demo complete!")


if __name__ == "__main__":
    main()
