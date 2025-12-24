#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""violinplot: violin plot demo."""


def plot_violinplot(plt, rng, ax=None):
    """Violin plot demo.

    Demonstrates: ax.violinplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    data = [rng.normal(i, 1, 100) for i in range(4)]
    # Modern style: show box inside (default from SCITEX style)
    ax.violinplot(data, id="violinplot")
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    ax.set_title("violinplot")
    return fig, ax


# EOF
