#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roundtrip Demo 03: Bar Chart
============================
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plotspec as ps


def main():
    print("Roundtrip Demo 03: Bar Chart")
    print("=" * 50)

    # Data
    categories = ['A', 'B', 'C', 'D', 'E']
    values1 = [23, 45, 56, 78, 32]
    values2 = [17, 35, 42, 65, 28]
    x = np.arange(len(categories))
    width = 0.35

    # === ORIGINAL ===
    fig, ax = ps.subplots(figsize=(10, 6))

    ax.bar(x - width/2, values1, width, label='Group 1', color='#3498db', id='group1')
    ax.bar(x + width/2, values2, width, label='Group 2', color='#e74c3c', id='group2')
    ax.set_xlabel('Category')
    ax.set_ylabel('Values')
    ax.set_title('Grouped Bar Chart')
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)

    fig.fig.savefig('outputs/03_original.png', dpi=150, bbox_inches='tight', facecolor='white')
    ps.save(fig, 'outputs/03_recipe.yaml')
    plt.close(fig.fig)

    # === REPRODUCED ===
    fig2, ax2 = ps.reproduce('outputs/03_recipe.yaml')
    fig2.savefig('outputs/03_reproduced.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig2)

    print("Original:   outputs/03_original.png")
    print("Reproduced: outputs/03_reproduced.png")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    main()
