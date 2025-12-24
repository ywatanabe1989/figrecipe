#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style application utilities for figrecipe.

Applies mm-based styling to matplotlib axes for publication-quality figures.
"""

__all__ = [
    "apply_style_mm",
    "apply_theme_colors",
    "check_font",
    "finalize_ticks",
    "finalize_special_plots",
    "list_available_fonts",
]

from typing import Any, Dict

from matplotlib.axes import Axes

from .._utils._units import mm_to_pt
from ._finalize import finalize_special_plots, finalize_ticks
from ._fonts import check_font, list_available_fonts
from ._plot_styles import (
    apply_barplot_style,
    apply_boxplot_style,
    apply_histogram_style,
    apply_matrix_style,
    apply_pie_style,
    apply_violinplot_style,
)
from ._themes import THEME_COLORS, apply_theme_colors


def apply_style_mm(ax: Axes, style: Dict[str, Any]) -> float:
    """Apply publication-quality style using millimeter-based settings.

    This function applies styling to matplotlib axes using millimeter and point
    measurements for precise control over visual elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to apply styling to
    style : dict
        Dictionary containing styling parameters. Supported keys:
        - 'axes_thickness_mm' (float): Spine line width in mm (default: 0.2)
        - 'trace_thickness_mm' (float): Plot line width in mm (default: 0.3)
        - 'tick_length_mm' (float): Tick mark length in mm (default: 1.0)
        - 'tick_thickness_mm' (float): Tick mark width in mm (default: 0.2)
        - 'marker_size_mm' (float): Default marker size in mm (default: 1.0)
        - 'axis_font_size_pt' (float): Axis label font size in points (default: 8)
        - 'tick_font_size_pt' (float): Tick label font size in points (default: 7)
        - 'title_font_size_pt' (float): Title font size in points (default: 9)
        - 'legend_font_size_pt' (float): Legend font size in points (default: 7)
        - 'label_pad_pt' (float): Axis label padding in points (default: 2.0)
        - 'tick_pad_pt' (float): Tick label padding in points (default: 2.0)
        - 'title_pad_pt' (float): Title padding in points (default: 4.0)
        - 'font_family' (str): Font family (default: "Arial")
        - 'n_ticks' (int): Number of ticks on each axis (default: 5)
        - 'theme' (str): Color theme "light" or "dark" (default: "light")
        - 'theme_colors' (dict): Custom theme color overrides
        - 'hide_top_spine' (bool): Hide top spine (default: True)
        - 'hide_right_spine' (bool): Hide right spine (default: True)
        - 'grid' (bool): Show grid (default: False)

    Returns
    -------
    float
        Trace line width in points, to be used with ax.plot(..., lw=trace_lw)

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> style = {
    ...     'axes_thickness_mm': 0.2,
    ...     'trace_thickness_mm': 0.3,
    ...     'tick_length_mm': 1.0,
    ...     'axis_font_size_pt': 8,
    ...     'theme': 'light',
    ... }
    >>> trace_lw = apply_style_mm(ax, style)
    >>> ax.plot(x, y, lw=trace_lw)
    """
    import matplotlib as mpl

    # Apply theme colors (dark/light mode)
    theme = style.get("theme", "light")
    theme_colors = style.get("theme_colors", None)
    apply_theme_colors(ax, theme, theme_colors)

    # Convert spine thickness from mm to points
    axes_lw_pt = mm_to_pt(style.get("axes_thickness_mm", 0.2))
    for spine in ax.spines.values():
        spine.set_linewidth(axes_lw_pt)

    # Hide spines if requested
    if style.get("hide_top_spine", True):
        ax.spines["top"].set_visible(False)
    if style.get("hide_right_spine", True):
        ax.spines["right"].set_visible(False)

    # Convert trace thickness from mm to points
    trace_lw_pt = mm_to_pt(style.get("trace_thickness_mm", 0.3))

    # Convert marker size from mm to points
    marker_size_mm = style.get("marker_size_mm")
    if marker_size_mm is not None:
        marker_size_pt = mm_to_pt(marker_size_mm)
        mpl.rcParams["lines.markersize"] = marker_size_pt

    # Set boxplot flier (outlier) marker size
    flier_mm = style.get("markers_flier_mm", style.get("flier_mm"))
    if flier_mm is not None:
        flier_size_pt = mm_to_pt(flier_mm)
        mpl.rcParams["boxplot.flierprops.markersize"] = flier_size_pt

    # Set boxplot median color
    median_color = style.get("boxplot_median_color")
    if median_color is not None:
        mpl.rcParams["boxplot.medianprops.color"] = median_color

    # Apply plot-specific styles
    apply_boxplot_style(ax, style)
    apply_violinplot_style(ax, style)
    apply_barplot_style(ax, style)
    apply_histogram_style(ax, style)
    apply_pie_style(ax, style)
    apply_matrix_style(ax, style)

    # Configure tick parameters
    tick_pad_pt = style.get("tick_pad_pt", 2.0)
    tick_direction = style.get("tick_direction", "out")
    ax.tick_params(
        direction=tick_direction,
        length=mm_to_pt(style.get("tick_length_mm", 1.0)),
        width=mm_to_pt(style.get("tick_thickness_mm", 0.2)),
        pad=tick_pad_pt,
        top=False,
        right=False,
    )

    # Apply font sizes and family
    axis_fs = style.get("axis_font_size_pt", 8)
    tick_fs = style.get("tick_font_size_pt", 7)
    title_fs = style.get("title_font_size_pt", 9)
    legend_fs = style.get("legend_font_size_pt", 7)
    label_pad_pt = style.get("label_pad_pt", 2.0)
    requested_font = style.get("font_family", "Arial")
    font_family = check_font(requested_font)

    ax.xaxis.label.set_fontsize(axis_fs)
    ax.xaxis.label.set_fontfamily(font_family)
    ax.xaxis.labelpad = label_pad_pt
    ax.yaxis.label.set_fontsize(axis_fs)
    ax.yaxis.label.set_fontfamily(font_family)
    ax.yaxis.labelpad = label_pad_pt

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(tick_fs)
        label.set_fontfamily(font_family)

    # Set title font, size, and padding
    ax.title.set_fontfamily(font_family)
    ax.title.set_fontsize(title_fs)
    title_pad_pt = style.get("title_pad_pt", 4.0)
    ax.set_title(ax.get_title(), pad=title_pad_pt)

    # Set legend font size and background via rcParams
    mpl.rcParams["legend.fontsize"] = legend_fs
    mpl.rcParams["legend.title_fontsize"] = legend_fs

    # Set legend colors from theme
    theme = style.get("theme", "light")
    theme_colors = style.get("theme_colors", None)
    if theme_colors:
        legend_bg = theme_colors.get("legend_bg", theme_colors.get("axes_bg", "white"))
        text_color = theme_colors.get("text", "black")
        spine_color = theme_colors.get("spine", "black")
    else:
        theme_dict = THEME_COLORS.get(theme, THEME_COLORS["light"])
        legend_bg = theme_dict.get("legend_bg", "white")
        text_color = theme_dict.get("text", "black")
        spine_color = theme_dict.get("spine", "black")

    # Handle transparent backgrounds
    if str(legend_bg).lower() in ("none", "transparent"):
        mpl.rcParams["legend.facecolor"] = "none"
        mpl.rcParams["legend.framealpha"] = 0
    else:
        mpl.rcParams["legend.facecolor"] = legend_bg
        mpl.rcParams["legend.framealpha"] = 1.0

    # Set legend text and edge colors
    mpl.rcParams["legend.edgecolor"] = spine_color
    mpl.rcParams["legend.labelcolor"] = text_color

    legend = ax.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_fontsize(legend_fs)
            text.set_fontfamily(font_family)

    # Configure grid
    if style.get("grid", False):
        ax.grid(True, alpha=0.3)
    else:
        ax.grid(False)

    # Configure number of ticks (deferred to finalize_ticks)
    n_ticks_min = style.get("n_ticks_min")
    n_ticks_max = style.get("n_ticks_max")
    if n_ticks_min is not None or n_ticks_max is not None:
        ax._figrecipe_n_ticks_min = n_ticks_min or 3
        ax._figrecipe_n_ticks_max = n_ticks_max or 4

    # Apply color palette to both rcParams and this specific axes
    color_palette = style.get("color_palette")
    if color_palette is not None:
        normalized_palette = []
        for c in color_palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    normalized_palette.append(tuple(c))
                else:
                    normalized_palette.append(tuple(v / 255.0 for v in c))
            else:
                normalized_palette.append(c)
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=normalized_palette)
        ax.set_prop_cycle(color=normalized_palette)

    # Store style in axes for reference
    if not hasattr(ax, "_figrecipe_style"):
        ax._figrecipe_style = {}
    ax._figrecipe_style.update(style)

    return trace_lw_pt


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    print("Testing style application...")

    fig, ax = plt.subplots(figsize=(4, 3))

    style = {
        "axes_thickness_mm": 0.2,
        "trace_thickness_mm": 0.3,
        "tick_length_mm": 1.0,
        "tick_thickness_mm": 0.2,
        "axis_font_size_pt": 8,
        "tick_font_size_pt": 7,
        "theme": "light",
    }

    trace_lw = apply_style_mm(ax, style)

    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), lw=trace_lw)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_title("Test Plot")

    plt.savefig("/tmp/test_style.png", dpi=300, bbox_inches="tight")
    print("Saved to /tmp/test_style.png")
    plt.close()

# EOF
