#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""psd: power spectral density demo."""

import numpy as np


def plot_psd(plt, rng, ax=None):
    """Power spectral density demo.

    Demonstrates: ax.psd()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    fs = 1000
    t = np.linspace(0, 1, fs)
    signal = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)
    signal += rng.normal(0, 0.3, len(t))
    ax.psd(signal, Fs=fs, id="psd")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Power/Frequency (dB/Hz)")
    ax.set_title("psd")
    return fig, ax


# EOF
