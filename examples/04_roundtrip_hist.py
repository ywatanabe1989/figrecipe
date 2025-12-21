#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roundtrip Demo 04: Histogram
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
    print("Roundtrip Demo 04: Histogram")
    print("=" * 50)

    # Data
    np.random.seed(42)
    data1 = np.random.normal(0, 1, 1000)
    data2 = np.random.normal(2, 1.5, 1000)

    # === ORIGINAL ===
    fig, ax = ps.subplots(figsize=(10, 6))

    ax.hist(data1, bins=30, alpha=0.7, label='Distribution 1', color='#3498db', id='dist1')
    ax.hist(data2, bins=30, alpha=0.7, label='Distribution 2', color='#e74c3c', id='dist2')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.set_title('Overlapping Histograms')
    ax.legend()

    fig.fig.savefig('outputs/04_original.png', dpi=150, bbox_inches='tight', facecolor='white')
    ps.save(fig, 'outputs/04_recipe.yaml')
    plt.close(fig.fig)

    # === REPRODUCED ===
    fig2, ax2 = ps.reproduce('outputs/04_recipe.yaml')
    fig2.savefig('outputs/04_reproduced.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig2)

    print("Original:   outputs/04_original.png")
    print("Reproduced: outputs/04_reproduced.png")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    main()
