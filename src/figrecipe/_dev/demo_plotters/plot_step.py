#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""step: step plot demo."""

import numpy as np


def plot_step(plt, rng, ax=None):
    """Step plot demo.

    Demonstrates: ax.step()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    x = np.arange(10)
    y = rng.uniform(0, 1, 10)
    ax.step(x, y, where="mid", id="step")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("step")
    return fig, ax


# EOF
