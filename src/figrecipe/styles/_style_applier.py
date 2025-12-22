#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style application utilities for figrecipe.

Applies mm-based styling to matplotlib axes for publication-quality figures.
"""

__all__ = ["apply_style_mm", "apply_theme_colors", "check_font", "list_available_fonts"]

import warnings
from typing import Any, Dict, List, Optional

from matplotlib.axes import Axes

from .._utils._units import mm_to_pt


def list_available_fonts() -> List[str]:
    """List all available font families.

    Returns
    -------
    list of str
        Sorted list of available font family names.

    Examples
    --------
    >>> fonts = ps.list_available_fonts()
    >>> print(fonts[:5])
    ['Arial', 'Courier New', 'DejaVu Sans', ...]
    """
    import matplotlib.font_manager as fm
    fonts = set()
    for font in fm.fontManager.ttflist:
        fonts.add(font.name)
    return sorted(fonts)


def check_font(font_family: str, fallback: str = "DejaVu Sans") -> str:
    """Check if font is available, with fallback and helpful error message.

    Parameters
    ----------
    font_family : str
        Requested font family name.
    fallback : str
        Fallback font if requested font is not available.

    Returns
    -------
    str
        The font to use (original if available, fallback otherwise).

    Examples
    --------
    >>> font = check_font("Arial")  # Returns "Arial" if available
    >>> font = check_font("NonExistentFont")  # Returns fallback with warning
    """
    import matplotlib.font_manager as fm

    available = list_available_fonts()

    if font_family in available:
        return font_family

    # Font not found - show helpful message
    similar = [f for f in available if font_family.lower() in f.lower()]

    msg = f"Font '{font_family}' not found.\n"
    if similar:
        msg += f"  Similar fonts available: {similar[:5]}\n"
    msg += f"  Using fallback: '{fallback}'\n"
    msg += f"  To see all available fonts: ps.list_available_fonts()\n"
    msg += f"  To install Arial on Linux: sudo apt install ttf-mscorefonts-installer"

    warnings.warn(msg, UserWarning)

    return fallback if fallback in available else "DejaVu Sans"


# Default theme color palettes (Monaco/VS Code style for dark)
THEME_COLORS = {
    "dark": {
        "figure_bg": "#1e1e1e",     # VS Code main background
        "axes_bg": "#252526",       # VS Code panel background
        "legend_bg": "#252526",     # Same as axes
        "text": "#d4d4d4",          # VS Code default text
        "spine": "#3c3c3c",         # Subtle border color
        "tick": "#d4d4d4",          # Match text
        "grid": "#3a3a3a",          # Subtle grid
    },
    "light": {
        "figure_bg": "none",        # Transparent
        "axes_bg": "none",          # Transparent
        "legend_bg": "none",        # Transparent
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
        Custom color overrides. Keys: figure_bg, axes_bg, legend_bg, text, spine, tick, grid

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> apply_theme_colors(ax, theme="dark")  # Eye-friendly dark mode
    """
    # Get base theme colors
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"]).copy()

    # Apply custom overrides
    if custom_colors:
        # Handle legacy key name (background -> figure_bg)
        if "background" in custom_colors and "figure_bg" not in custom_colors:
            custom_colors["figure_bg"] = custom_colors.pop("background")
        colors.update(custom_colors)

    # Helper to check for transparent/none
    def is_transparent(color):
        if color is None:
            return False
        return str(color).lower() in ("none", "transparent")

    # Apply axes background (handle "none"/"transparent" for transparency)
    axes_bg = colors.get("axes_bg", "none")
    if is_transparent(axes_bg):
        ax.set_facecolor("none")
        ax.patch.set_alpha(0)
    else:
        ax.set_facecolor(axes_bg)

    # Apply figure background if accessible
    fig = ax.get_figure()
    if fig is not None:
        fig_bg = colors.get("figure_bg", "none")
        if is_transparent(fig_bg):
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
            legend_bg = colors.get("legend_bg", colors.get("axes_bg", "none"))
            if is_transparent(legend_bg):
                frame.set_facecolor("none")
                frame.set_alpha(0)
            else:
                frame.set_facecolor(legend_bg)
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

    # Apply font sizes and family (with font availability check)
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

    # Set legend font size and background via rcParams (for future legends)
    import matplotlib as mpl
    mpl.rcParams['legend.fontsize'] = legend_fs
    mpl.rcParams['legend.title_fontsize'] = legend_fs

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
        mpl.rcParams['legend.facecolor'] = 'none'
        mpl.rcParams['legend.framealpha'] = 0
    else:
        mpl.rcParams['legend.facecolor'] = legend_bg
        mpl.rcParams['legend.framealpha'] = 1.0

    # Set legend text and edge colors
    mpl.rcParams['legend.edgecolor'] = spine_color
    mpl.rcParams['legend.labelcolor'] = text_color

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

    # Apply color palette to both rcParams and this specific axes
    color_palette = style.get("color_palette")
    if color_palette is not None:
        import matplotlib as mpl
        # Normalize colors (RGB 0-255 to 0-1)
        normalized_palette = []
        for c in color_palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                # Check if already normalized
                if all(v <= 1.0 for v in c):
                    normalized_palette.append(tuple(c))
                else:
                    normalized_palette.append(tuple(v / 255.0 for v in c))
            else:
                normalized_palette.append(c)
        # Set rcParams for future axes
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=normalized_palette)
        # Also set the color cycle on this specific axes (axes cache cycler at creation)
        ax.set_prop_cycle(color=normalized_palette)

    # Store style in axes for reference
    if not hasattr(ax, "_figrecipe_style"):
        ax._figrecipe_style = {}
    ax._figrecipe_style.update(style)

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
