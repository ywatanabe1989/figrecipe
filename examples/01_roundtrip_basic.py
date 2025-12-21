#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roundtrip Demo 01: Basic Line Plot
==================================
Record -> Save -> Reproduce -> Compare
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as mpr


def main():
    print("Roundtrip Demo 01: Basic Line Plot")
    print("=" * 50)

    # Data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    # === ORIGINAL ===
    fig, ax = mpr.subplots(figsize=(10, 6))

    ax.plot(x, y1, 'b-', linewidth=2, label='sin(x)', id='sine')
    ax.plot(x, y2, 'r--', linewidth=2, label='cos(x)', id='cosine')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Trigonometric Functions')
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.fig.savefig('outputs/01_original.png', dpi=150, bbox_inches='tight', facecolor='white')
    mpr.save(fig, 'outputs/01_recipe.yaml')
    plt.close(fig.fig)

    # === REPRODUCED ===
    fig2, ax2 = mpr.reproduce('outputs/01_recipe.yaml')
    fig2.savefig('outputs/01_reproduced.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig2)

    print("Original:   outputs/01_original.png")
    print("Reproduced: outputs/01_reproduced.png")
    print("Recipe:     outputs/01_recipe.yaml")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    main()
