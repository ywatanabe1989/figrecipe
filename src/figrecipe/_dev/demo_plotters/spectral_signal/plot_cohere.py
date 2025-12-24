#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cohere: coherence demo."""

import numpy as np


def plot_cohere(plt, rng, ax=None):
    """Coherence demo.

    Demonstrates: ax.cohere()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    fs = 1000
    t = np.linspace(0, 1, fs)
    x = np.sin(2 * np.pi * 50 * t) + rng.normal(0, 0.3, len(t))
    y = np.sin(2 * np.pi * 50 * t + np.pi / 4) + rng.normal(0, 0.3, len(t))
    ax.cohere(x, y, Fs=fs, id="cohere")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Coherence")
    ax.set_title("cohere")
    return fig, ax


# EOF
