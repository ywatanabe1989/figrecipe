#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication-quality heatmap with smart annotation colors.

Ported from scitex.plt.ax._plot._stx_heatmap for figrecipe integration.
"""

import numpy as np
from matplotlib.axes import Axes


def _brightness(color_rgba):
    """Compute perceived brightness (0-1) of an RGBA color."""
    r, g, b = color_rgba[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b


def stx_heatmap(
    ax: Axes,
    values_2d,
    x_labels=None,
    y_labels=None,
    cmap="viridis",
    cbar_label="ColorBar Label",
    annot_format="{x:.1f}",
    show_annot=True,
    annot_color_lighter="black",
    annot_color_darker="white",
    vmin=None,
    vmax=None,
    **kwargs,
):
    """Plot a heatmap with automatic annotation color switching.

    Text color switches between light/dark based on cell brightness
    for optimal readability.

    Parameters
    ----------
    ax : Axes
    values_2d : array-like, shape (rows, cols)
        Data to display.
    x_labels, y_labels : list, optional
        Axis tick labels.
    cmap : str
        Colormap name.
    cbar_label : str
        Colorbar label.
    annot_format : str
        Format string for cell annotations.
    show_annot : bool
        Whether to show cell annotations.
    annot_color_lighter, annot_color_darker : str
        Text colors for light/dark backgrounds.
    vmin, vmax : float, optional
        Colormap range.

    Returns
    -------
    ax : Axes
    """
    import matplotlib
    import matplotlib.pyplot as plt

    values_2d = np.asarray(values_2d, dtype=float)
    n_rows, n_cols = values_2d.shape

    # Display image
    _vmin = vmin if vmin is not None else np.nanmin(values_2d)
    _vmax = vmax if vmax is not None else np.nanmax(values_2d)

    im = ax.imshow(
        values_2d,
        cmap=cmap,
        aspect="auto",
        vmin=_vmin,
        vmax=_vmax,
        **kwargs,
    )

    # Colorbar with limited ticks
    from matplotlib.ticker import MaxNLocator

    fig = ax.get_figure()
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
    if cbar_label:
        cbar.set_label(cbar_label)

    # Tick labels
    ax.set_xticks(np.arange(n_cols))
    ax.set_yticks(np.arange(n_rows))
    if x_labels is not None:
        ax.set_xticklabels(x_labels)
    if y_labels is not None:
        ax.set_yticklabels(y_labels)

    # Annotations with brightness-aware colors
    if show_annot:
        colormap = plt.get_cmap(cmap)
        norm = matplotlib.colors.Normalize(vmin=_vmin, vmax=_vmax)

        # Dynamic fontsize: smaller for large matrices
        total_cells = n_rows * n_cols
        if total_cells <= 25:
            fontsize = 8
        elif total_cells <= 100:
            fontsize = 6
        else:
            fontsize = 4

        for i in range(n_rows):
            for j in range(n_cols):
                val = values_2d[i, j]
                if np.isnan(val):
                    continue
                rgba = colormap(norm(val))
                text_color = (
                    annot_color_lighter
                    if _brightness(rgba) > 0.5
                    else annot_color_darker
                )
                text = annot_format.format(x=val)
                ax.text(
                    j,
                    i,
                    text,
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=fontsize,
                )

    return ax


__all__ = ["stx_heatmap"]

# EOF
