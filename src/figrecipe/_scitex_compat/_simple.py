#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple plot helpers: fillv, rectangle, image, violin.

Ported from scitex.plt.ax._plot for figrecipe integration.
"""

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle


def stx_fillv(ax, starts_1d, ends_1d, color="red", alpha=0.2):
    """Fill vertical spans between start and end positions.

    Parameters
    ----------
    ax : Axes or array of Axes
        Axes to fill on.
    starts_1d : array-like
        Start x-positions.
    ends_1d : array-like
        End x-positions.
    color : str
    alpha : float

    Returns
    -------
    ax : Axes or list
    """
    is_array = isinstance(ax, np.ndarray)
    axes = ax if is_array else [ax]

    for a in axes:
        for start, end in zip(starts_1d, ends_1d):
            a.axvspan(start, end, facecolor=color, edgecolor="none", alpha=alpha)

    return ax if is_array else axes[0]


def stx_rectangle(ax: Axes, xx, yy, ww, hh, **kwargs):
    """Add a rectangle patch to axes.

    Parameters
    ----------
    ax : Axes
    xx, yy : float
        Bottom-left corner.
    ww, hh : float
        Width and height.
    **kwargs
        Passed to Rectangle.

    Returns
    -------
    ax : Axes
    """
    if "edgecolor" not in kwargs and "ec" not in kwargs:
        kwargs["edgecolor"] = "none"
    ax.add_patch(Rectangle((xx, yy), ww, hh, **kwargs))
    return ax


def stx_image(
    ax: Axes,
    arr_2d,
    cbar=True,
    cbar_label=None,
    cbar_shrink=1.0,
    cbar_fraction=0.046,
    cbar_pad=0.04,
    cmap="viridis",
    aspect="auto",
    vmin=None,
    vmax=None,
    **kwargs,
):
    """Display a 2D array as an image with correct orientation.

    The first dimension is x (left-right), second is y (bottom-top).

    Parameters
    ----------
    ax : Axes
    arr_2d : array-like, shape (nx, ny)
    cbar : bool
    cbar_label : str, optional
    cmap : str
    aspect : str
    vmin, vmax : float, optional

    Returns
    -------
    ax : Axes
    """
    arr_2d = np.asarray(arr_2d)

    # Transpose for correct orientation
    arr_2d = arr_2d.T

    im = ax.imshow(arr_2d, cmap=cmap, vmin=vmin, vmax=vmax, aspect=aspect, **kwargs)

    if cbar:
        fig = ax.get_figure()
        cb = fig.colorbar(
            im, ax=ax, shrink=cbar_shrink, fraction=cbar_fraction, pad=cbar_pad
        )
        if cbar_label:
            cb.set_label(cbar_label)

    ax.invert_yaxis()
    return ax


def stx_violin(
    ax: Axes,
    values_list,
    labels=None,
    colors=None,
    half=False,
    **kwargs,
):
    """Plot violins from a list of arrays.

    Parameters
    ----------
    ax : Axes
    values_list : list of array-like
        One array per violin group.
    labels : list, optional
        Group labels.
    colors : list, optional
        Violin colors.
    half : bool
        If True, show only left half.
    **kwargs
        Passed to seaborn.violinplot.

    Returns
    -------
    ax : Axes
    """
    try:
        import seaborn as sns
    except ImportError:
        raise ImportError("stx_violin requires seaborn: pip install seaborn") from None

    # Build DataFrame
    all_values, all_groups = [], []
    for idx, values in enumerate(values_list):
        all_values.extend(values)
        lbl = labels[idx] if labels and idx < len(labels) else f"x {idx}"
        all_groups.extend([lbl] * len(values))

    df = pd.DataFrame({"x": all_groups, "y": all_values})

    if colors:
        if isinstance(colors, list):
            unique_groups = list(dict.fromkeys(all_groups))
            kwargs["palette"] = {
                g: c for g, c in zip(unique_groups, colors[: len(unique_groups)])
            }
        else:
            kwargs["palette"] = colors

    if not half:
        sns.violinplot(data=df, x="x", y="y", hue="x", ax=ax, **kwargs)
    else:
        _half_violin(ax, df, "x", "y", **kwargs)

    return ax


def _half_violin(ax, df, x_col, y_col, **kwargs):
    """Plot half-violins (left side only)."""

    try:
        import seaborn as sns
    except ImportError:
        raise ImportError("half violin requires seaborn") from None

    hue = x_col
    df = df.copy()
    df["_fake"] = df[hue] + "_right"

    groups = df[x_col].unique().tolist()
    hue_order = []
    for g in groups:
        hue_order.extend([g, g + "_right"])
    kwargs["hue_order"] = hue_order

    if "palette" in kwargs:
        pal = kwargs["palette"]
        if isinstance(pal, dict):
            kwargs["palette"] = {**pal, **{k + "_right": v for k, v in pal.items()}}

    # Left: real data, Right: NaN
    df_left = df[[x_col, y_col]]
    df_right = df[["_fake", y_col]].rename(columns={"_fake": x_col})
    df_right[y_col] = np.nan
    df_conc = pd.concat([df_left, df_right], ignore_index=True).sort_values(x_col)

    sns.violinplot(
        data=df_conc, x=x_col, y=y_col, hue=x_col, split=True, ax=ax, **kwargs
    )

    # Clean legend
    if ax.legend_ is not None:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[: len(handles) // 2], labels[: len(labels) // 2])

    return ax


__all__ = [
    "stx_fillv",
    "stx_image",
    "stx_rectangle",
    "stx_violin",
]

# EOF
