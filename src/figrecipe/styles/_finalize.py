#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finalization utilities for figrecipe styles."""

from typing import Any, Dict

from matplotlib.axes import Axes

from ._fonts import check_font


def finalize_ticks(ax: Axes) -> None:
    """
    Apply deferred tick configuration after all plotting is done.

    This function applies the n_ticks setting stored by apply_style_mm(),
    but only to numeric axes (not categorical). Skips pie charts and other
    plot types that should have hidden axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to finalize.
    """
    from matplotlib.patches import Wedge
    from matplotlib.ticker import MaxNLocator

    # Skip pie charts - they should have no ticks
    has_pie = any(isinstance(p, Wedge) for p in ax.patches)
    if has_pie:
        return

    # Get tick count preferences (new format: min/max)
    n_ticks_min = getattr(ax, "_figrecipe_n_ticks_min", None)
    n_ticks_max = getattr(ax, "_figrecipe_n_ticks_max", None)

    if n_ticks_min is None and n_ticks_max is None:
        return

    # Default values - minimum 3 ticks required
    n_ticks_min = max(3, n_ticks_min or 3)
    n_ticks_max = max(n_ticks_min, n_ticks_max or 4)

    nbins = n_ticks_max

    def _is_numeric_label(lbl: str) -> bool:
        """Check if a tick label represents a numeric value."""
        if not lbl:
            return True
        stripped = lbl.replace(".", "").replace("-", "").replace("+", "")
        stripped = stripped.replace("−", "")  # Unicode minus sign
        stripped = stripped.replace("e", "").replace("E", "")
        return stripped.isdigit() or stripped == ""

    # Check if x-axis is categorical
    x_labels = [t.get_text() for t in ax.get_xticklabels()]
    x_is_categorical = any(not _is_numeric_label(lbl) for lbl in x_labels)
    if not x_is_categorical:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=nbins, min_n_ticks=n_ticks_min))

    # Check if y-axis is categorical
    y_labels = [t.get_text() for t in ax.get_yticklabels()]
    y_is_categorical = any(not _is_numeric_label(lbl) for lbl in y_labels)
    if not y_is_categorical:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=nbins, min_n_ticks=n_ticks_min))


def finalize_special_plots(ax: Axes, style: Dict[str, Any] = None) -> None:
    """
    Finalize axes visibility for special plot types (pie, imshow, etc.).

    This should be called after all plotting is done, before saving.
    It handles plot types that need axes/ticks hidden.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to finalize.
    style : dict, optional
        Style dictionary. If None, uses defaults.
    """
    from matplotlib.image import AxesImage
    from matplotlib.patches import Wedge

    if style is None:
        style = {}

    # Check for pie chart
    has_pie = any(isinstance(p, Wedge) for p in ax.patches)
    if has_pie:
        show_axes = style.get("pie_show_axes", False)
        text_pt = style.get("pie_text_pt", 6)
        font_family = check_font(style.get("font_family", "Arial"))

        for text in ax.texts:
            transform = text.get_transform()
            if transform == ax.transAxes:
                x, y = text.get_position()
                if y > 1.0 or y < 0.0:
                    continue
            text.set_fontsize(text_pt)
            text.set_fontfamily(font_family)

        if not show_axes:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_xlabel("")
            ax.set_ylabel("")
            for spine in ax.spines.values():
                spine.set_visible(False)

    # Check for imshow/matshow (has AxesImage)
    has_image = any(isinstance(c, AxesImage) for c in ax.get_children())
    if has_image:
        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()
        is_specgram = xlabel or ylabel

        if not is_specgram:
            show_axes = style.get("imshow_show_axes", False)
            if not show_axes:
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                for spine in ax.spines.values():
                    spine.set_visible(False)


__all__ = ["finalize_ticks", "finalize_special_plots"]

# EOF
