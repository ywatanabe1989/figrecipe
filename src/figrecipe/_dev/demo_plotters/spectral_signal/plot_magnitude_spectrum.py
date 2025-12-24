#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""magnitude_spectrum: magnitude spectrum demo."""

import numpy as np


def plot_magnitude_spectrum(plt, rng, ax=None):
    """Magnitude spectrum demo.

    Demonstrates: ax.magnitude_spectrum()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    fs = 1000
    t = np.linspace(0, 1, fs)
    signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)
    ax.magnitude_spectrum(signal, Fs=fs, id="magnitude_spectrum")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Magnitude")
    ax.set_title("magnitude_spectrum")
    return fig, ax


# EOF
