#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel label helper for the public API."""

from typing import Optional, Tuple


def get_panel_label_fontsize(explicit_fontsize: Optional[float] = None) -> float:
    """Get fontsize for panel labels from style or default."""
    if explicit_fontsize is not None:
        return explicit_fontsize

    try:
        from ..styles._style_loader import _STYLE_CACHE

        if _STYLE_CACHE is not None:
            return getattr(getattr(_STYLE_CACHE, "fonts", None), "panel_label_pt", 10)
    except Exception:
        pass
    return 10


def calculate_panel_position(
    loc: str,
    offset: Tuple[float, float],
) -> Tuple[float, float]:
    """Calculate x, y position based on location and offset."""
    if loc == "upper left":
        x, y = offset
    elif loc == "upper right":
        x, y = 1.0 + abs(offset[0]), offset[1]
    elif loc == "lower left":
        x, y = offset[0], -abs(offset[1]) + 1.0
    elif loc == "lower right":
        x, y = 1.0 + abs(offset[0]), -abs(offset[1]) + 1.0
    else:
        x, y = offset
    return x, y


def panel_label(
    ax,
    label: str,
    loc: str = "upper left",
    fontsize: Optional[float] = None,
    fontweight: str = "bold",
    offset: Tuple[float, float] = (-0.1, 1.05),
    **kwargs,
):
    """Add a panel label (A, B, C, ...) to an axes.

    Parameters
    ----------
    ax : Axes or RecordingAxes
        The axes to label.
    label : str
        The label text (e.g., 'A', 'B', 'a)', '(1)').
    loc : str, optional
        Label location: 'upper left', 'upper right', etc.
    fontsize : float, optional
        Font size in points.
    fontweight : str, optional
        Font weight (default: 'bold').
    offset : tuple of float, optional
        (x, y) offset in axes coordinates.
    **kwargs
        Additional arguments passed to ax.text().

    Returns
    -------
    Text
        The matplotlib Text object.
    """
    import matplotlib.pyplot as mpl_plt

    fontsize = get_panel_label_fontsize(fontsize)
    x, y = calculate_panel_position(loc, offset)

    default_color = mpl_plt.rcParams.get("text.color", "black")

    text_kwargs = {
        "fontsize": fontsize,
        "fontweight": fontweight,
        "color": default_color,
        "transform": "axes",
        "va": "bottom",
        "ha": "right" if "right" in loc else "left",
    }
    text_kwargs.update(kwargs)

    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    render_kwargs = text_kwargs.copy()
    render_kwargs["transform"] = mpl_ax.transAxes

    if hasattr(ax, "_recorder") and hasattr(ax, "_position"):
        ax._recorder.record_call(
            ax_position=ax._position,
            method_name="text",
            args=(x, y, label),
            kwargs=text_kwargs,
        )

    return mpl_ax.text(x, y, label, **render_kwargs)


__all__ = [
    "get_panel_label_fontsize",
    "calculate_panel_position",
    "panel_label",
]

# EOF
