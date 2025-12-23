#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""specgram: spectrogram demo."""

import numpy as np


def plot_specgram(plt, rng, ax=None):
    """Spectrogram demo.

    Demonstrates: ax.specgram()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Create signal with varying frequency
    fs = 1000
    t = np.linspace(0, 2, 2000)
    freq = 50 + 50 * t  # Chirp signal
    signal = np.sin(2 * np.pi * freq * t)
    ax.specgram(signal, Fs=fs, id="specgram")
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency")
    ax.set_title("specgram")
    return fig, ax


# EOF
