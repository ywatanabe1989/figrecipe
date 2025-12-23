#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imshow: image display demo."""


def plot_imshow(plt, rng, ax=None):
    """Image display demo.

    Demonstrates: ax.imshow()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = rng.uniform(0, 1, (20, 20))
    ax.imshow(data, id="imshow")
    ax.axis("off")
    ax.set_title("imshow")
    return fig, ax


# EOF
