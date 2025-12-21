#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roundtrip Demo 02: Scatter Plot
===============================
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as mpr


def main():
    print("Roundtrip Demo 02: Scatter Plot")
    print("=" * 50)

    # Data
    np.random.seed(42)
    n = 50
    x = np.random.randn(n)
    y = x + np.random.randn(n) * 0.5
    colors = np.random.rand(n)
    sizes = np.abs(np.random.randn(n)) * 100 + 20

    # === ORIGINAL ===
    fig, ax = mpr.subplots(figsize=(8, 8))

    ax.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis', id='points')
    ax.set_xlabel('X values')
    ax.set_ylabel('Y values')
    ax.set_title('Scatter Plot with Color and Size')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)

    fig.fig.savefig('outputs/02_original.png', dpi=150, bbox_inches='tight', facecolor='white')
    mpr.save(fig, 'outputs/02_recipe.yaml')
    plt.close(fig.fig)

    # === REPRODUCED ===
    fig2, ax2 = mpr.reproduce('outputs/02_recipe.yaml')
    fig2.savefig('outputs/02_reproduced.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig2)

    print("Original:   outputs/02_original.png")
    print("Reproduced: outputs/02_reproduced.png")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    main()
