#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-09
# File: src/figrecipe/_utils/_mk_colorbar.py

"""Create custom gradient colorbars."""


def mk_colorbar(start="white", end="blue"):
    """Create a colorbar gradient between two colors.

    Parameters
    ----------
    start : str
        Starting color name (must be in figrecipe.colors.PARAMS['RGB'])
    end : str
        Ending color name

    Returns
    -------
    matplotlib.figure.Figure
        Figure with the gradient colorbar
    """
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import numpy as np

    from ..colors._PARAMS import RGB

    start_rgb = np.array(RGB[start]) / 255.0
    end_rgb = np.array(RGB[end]) / 255.0

    colors = [start_rgb, end_rgb]
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", colors, N=256)

    fig, ax = plt.subplots(figsize=(6, 1))
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(gradient, aspect="auto", cmap=cmap)
    ax.set_xticks([])
    ax.set_yticks([])

    return fig


# EOF
