#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""angle_spectrum: phase angle spectrum demo."""

import numpy as np


def plot_angle_spectrum(plt, rng, ax=None):
    """Phase angle spectrum demo.

    Demonstrates: ax.angle_spectrum()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    fs = 1000
    t = np.linspace(0, 1, fs)
    signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t + np.pi / 3)
    ax.angle_spectrum(signal, Fs=fs, id="angle_spectrum")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Phase (radians)")
    ax.set_title("angle_spectrum")
    return fig, ax


# EOF
