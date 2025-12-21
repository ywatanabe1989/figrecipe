#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style application utilities for plotspec.

Applies mm-based styling to matplotlib axes for publication-quality figures.
"""

__all__ = ["apply_style_mm", "apply_theme_colors"]

from typing import Any, Dict, Optional

from matplotlib.axes import Axes

from .._utils._units import mm_to_pt


# Default theme color palettes
THEME_COLORS = {
    "dark": {
        "background": "#1a1a2e",
        "axes_bg": "#1a1a2e",
        "text": "#e8e8e8",
        "spine": "#4a4a5a",
        "tick": "#e8e8e8",
        "grid": "#3a3a4a",
    },
    "light": {
        "background": "none",  # Transparent
        "axes_bg": "none",     # Transparent
        "text": "black",
        "spine": "black",
        "tick": "black",
        "grid": "#cccccc",
    },
}


def apply_theme_colors(
    ax: Axes,
    theme: str = "light",
    custom_colors: Optional[Dict[str, str]] = None,
) -> None:
    """Apply theme colors to axes for dark/light mode support.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to apply theme to
    theme : str
        Color theme: "light" or "dark" (default: "light")
    custom_colors : dict, optional
        Custom color overrides. Keys: background, axes_bg, text, spine, tick, grid

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> apply_theme_colors(ax, theme="dark")  # Eye-friendly dark mode
    """
    # Get base theme colors
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"]).copy()

    # Apply custom overrides
    if custom_colors:
        colors.update(custom_colors)

    # Apply axes background (handle "none" for transparency)
    axes_bg = colors["axes_bg"]
    if axes_bg.lower() == "none":
        ax.set_facecolor("none")
        ax.patch.set_alpha(0)
    else:
        ax.set_facecolor(axes_bg)

    # Apply figure background if accessible (handle "none" for transparency)
    fig = ax.get_figure()
    if fig is not None:
        fig_bg = colors["background"]
        if fig_bg.lower() == "none":
            fig.patch.set_facecolor("none")
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(fig_bg)

    # Apply text colors (labels, titles)
    ax.xaxis.label.set_color(colors["text"])
    ax.yaxis.label.set_color(colors["text"])
    ax.title.set_color(colors["text"])

    # Apply spine colors
    for spine in ax.spines.values():
        spine.set_color(colors["spine"])

    # Apply tick colors (both marks and labels)
    ax.tick_params(colors=colors["tick"], which="both")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(colors["tick"])

    # Apply legend colors if legend exists
    legend = ax.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_color(colors["text"])
        title = legend.get_title()
        if title:
            title.set_color(colors["text"])
        frame = legend.get_frame()
        if frame:
            frame.set_facecolor(colors["axes_bg"])
            frame.set_edgecolor(colors["spine"])


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
        import matplotlib as mpl
        marker_size_pt = mm_to_pt(marker_size_mm)
        mpl.rcParams["lines.markersize"] = marker_size_pt

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
    font_family = style.get("font_family", "Arial")

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

    # Set legend font size if legend exists
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

    # Configure number of ticks
    n_ticks = style.get("n_ticks")
    if n_ticks is not None:
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(nbins=n_ticks))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=n_ticks))

    # Apply color palette via rcParams if provided
    color_palette = style.get("color_palette")
    if color_palette is not None:
        import matplotlib as mpl
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=color_palette)

    # Store style in axes for reference
    if not hasattr(ax, "_plotspec_style"):
        ax._plotspec_style = {}
    ax._plotspec_style.update(style)

    return trace_lw_pt


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Test styling
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
