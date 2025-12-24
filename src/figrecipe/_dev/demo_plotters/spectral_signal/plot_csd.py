#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""csd: cross spectral density demo."""

import numpy as np


def plot_csd(plt, rng, ax=None):
    """Cross spectral density demo.

    Demonstrates: ax.csd()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    fs = 1000
    t = np.linspace(0, 1, fs)
    x = np.sin(2 * np.pi * 50 * t) + rng.normal(0, 0.3, len(t))
    y = np.sin(2 * np.pi * 50 * t + np.pi / 4) + rng.normal(0, 0.3, len(t))
    ax.csd(x, y, Fs=fs, id="csd")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("CSD")
    ax.set_title("csd")
    return fig, ax


# EOF
