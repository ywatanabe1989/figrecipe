#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Colorbar styling utilities for figrecipe.

Provides consistent colorbar styling based on SCITEX style preset.
"""

__all__ = ["style_colorbar", "add_colorbar"]

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from matplotlib.colorbar import Colorbar
    from matplotlib.figure import Figure
    from matplotlib.image import AxesImage


def style_colorbar(cbar: "Colorbar", style: Optional[dict] = None) -> "Colorbar":
    """Apply SCITEX styling to a colorbar.

    Parameters
    ----------
    cbar : matplotlib.colorbar.Colorbar
        The colorbar to style.
    style : dict, optional
        Style settings. If None, loads from current SCITEX style.

    Returns
    -------
    Colorbar
        The styled colorbar (same object, modified in place).

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> im = ax.imshow(data)
    >>> cbar = fig.colorbar(im, ax=ax)
    >>> fr.style_colorbar(cbar)
    """
    from matplotlib.ticker import MaxNLocator

    from ._units import mm_to_pt

    # Get style settings
    if style is None:
        try:
            from ..styles._internal import get_style

            style = get_style() or {}
        except Exception:
            style = {}

    # Get colorbar-specific settings
    cbar_style = style.get("colorbar", {}) if style else {}

    # Get tick settings (fallback to ticks section, then defaults)
    ticks_style = style.get("ticks", {}) if style else {}

    outline_mm = cbar_style.get("outline_mm", 0.2)
    n_ticks_min = cbar_style.get("n_ticks_min", 3)
    n_ticks_max = cbar_style.get("n_ticks_max", 4)
    tick_width_mm = cbar_style.get(
        "tick_width_mm", ticks_style.get("thickness_mm", 0.2)
    )
    tick_length_mm = cbar_style.get("tick_length_mm", ticks_style.get("length_mm", 0.8))

    # Convert to points
    outline_pt = mm_to_pt(outline_mm)
    tick_width_pt = mm_to_pt(tick_width_mm)
    tick_length_pt = mm_to_pt(tick_length_mm)

    # Apply styling
    cbar.outline.set_linewidth(outline_pt)
    cbar.ax.yaxis.set_major_locator(
        MaxNLocator(nbins=n_ticks_max, min_n_ticks=n_ticks_min)
    )
    cbar.ax.tick_params(width=tick_width_pt, length=tick_length_pt)

    # Apply font size from style
    fonts_style = style.get("fonts", {}) if style else {}
    label_pt = cbar_style.get("label_pt", fonts_style.get("tick_label_pt", 7))
    for label in cbar.ax.get_yticklabels():
        label.set_fontsize(label_pt)

    return cbar


def add_colorbar(
    fig: "Figure",
    mappable: "AxesImage",
    ax=None,
    style: Optional[dict] = None,
    **kwargs,
) -> "Colorbar":
    """Add a styled colorbar to a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to add the colorbar to.
    mappable : ScalarMappable
        The image or contour set to create colorbar for.
    ax : Axes, optional
        The axes to steal space from. If None, uses mappable's axes.
    style : dict, optional
        Style settings. If None, loads from current SCITEX style.
    **kwargs
        Additional arguments passed to fig.colorbar().

    Returns
    -------
    Colorbar
        The styled colorbar.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> im = ax.imshow(data)
    >>> cbar = fr.add_colorbar(fig, im, ax=ax)
    """
    # Get style settings
    if style is None:
        try:
            from ..styles._internal import get_style

            style = get_style() or {}
        except Exception:
            style = {}

    cbar_style = style.get("colorbar", {}) if style else {}

    # Set default colorbar sizing from style
    if "fraction" not in kwargs:
        kwargs["fraction"] = cbar_style.get("width_fraction", 0.04)
    if "pad" not in kwargs:
        kwargs["pad"] = cbar_style.get("pad_fraction", 0.02)
    # Ensure colorbar height matches axes (no shrinking)
    if "shrink" not in kwargs:
        kwargs["shrink"] = cbar_style.get("shrink", 1.0)
    # Note: anchor is NOT set by default - matplotlib's default alignment works best
    # with constrained_layout. Only apply if explicitly provided in kwargs.
    # Set aspect ratio for proper sizing
    if "aspect" not in kwargs:
        kwargs["aspect"] = cbar_style.get("aspect", 20)

    # Get axes if not specified
    if ax is None:
        ax = mappable.axes

    # Create colorbar
    cbar = fig.colorbar(mappable, ax=ax, **kwargs)

    # Apply styling
    style_colorbar(cbar, style)

    return cbar


# EOF
