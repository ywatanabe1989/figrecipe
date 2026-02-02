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
    result = ax.specgram(signal, Fs=fs, id="specgram")
    # specgram returns (spectrum, freqs, t, im) - need im for colorbar
    im = result[-1] if isinstance(result, tuple) else result
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency")
    ax.set_title("specgram")
    from figrecipe._utils._colorbar import add_colorbar

    add_colorbar(fig, im, ax=ax)
    return fig, ax


# EOF
