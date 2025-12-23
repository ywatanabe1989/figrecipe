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
    "list_available_fonts",
]

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

    available = list_available_fonts()

    if font_family in available:
        return font_family

    # Font not found - show helpful message
    similar = [f for f in available if font_family.lower() in f.lower()]

    msg = f"Font '{font_family}' not found.\n"
    if similar:
        msg += f"  Similar fonts available: {similar[:5]}\n"
    msg += f"  Using fallback: '{fallback}'\n"
    msg += "  To see all available fonts: ps.list_available_fonts()\n"
    msg += "  To install Arial on Linux: sudo apt install ttf-mscorefonts-installer"

    warnings.warn(msg, UserWarning)

    return fallback if fallback in available else "DejaVu Sans"


# Default theme color palettes (Monaco/VS Code style for dark)
THEME_COLORS = {
    "dark": {
        "figure_bg": "#1e1e1e",  # VS Code main background
        "axes_bg": "#252526",  # VS Code panel background
        "legend_bg": "#252526",  # Same as axes
        "text": "#d4d4d4",  # VS Code default text
        "spine": "#3c3c3c",  # Subtle border color
        "tick": "#d4d4d4",  # Match text
        "grid": "#3a3a3a",  # Subtle grid
    },
    "light": {
        "figure_bg": "none",  # Transparent
        "axes_bg": "none",  # Transparent
        "legend_bg": "none",  # Transparent
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
    theme : str or dict
        Color theme: "light" or "dark" (default: "light")
        If dict, extracts 'mode' key (for YAML-style theme dicts)
    custom_colors : dict, optional
        Custom color overrides. Keys: figure_bg, axes_bg, legend_bg, text, spine, tick, grid

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> apply_theme_colors(ax, theme="dark")  # Eye-friendly dark mode
    """
    # Handle dict-style theme (from YAML: {mode: "light", dark: {...}})
    if isinstance(theme, dict):
        theme = theme.get("mode", "light")

    # Ensure theme is a string
    if not isinstance(theme, str):
        theme = "light"

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

        # Apply text colors to figure-level text elements (suptitle, supxlabel, supylabel)
        if hasattr(fig, "_suptitle") and fig._suptitle is not None:
            fig._suptitle.set_color(colors["text"])
        if hasattr(fig, "_supxlabel") and fig._supxlabel is not None:
            fig._supxlabel.set_color(colors["text"])
        if hasattr(fig, "_supylabel") and fig._supylabel is not None:
            fig._supylabel.set_color(colors["text"])

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

    # Set boxplot flier (outlier) marker size
    flier_mm = style.get("markers_flier_mm", style.get("flier_mm"))
    if flier_mm is not None:
        import matplotlib as mpl

        flier_size_pt = mm_to_pt(flier_mm)
        mpl.rcParams["boxplot.flierprops.markersize"] = flier_size_pt

    # Set boxplot median color
    median_color = style.get("boxplot_median_color")
    if median_color is not None:
        import matplotlib as mpl

        mpl.rcParams["boxplot.medianprops.color"] = median_color

    # Apply boxplot line widths to existing boxplot elements
    _apply_boxplot_style(ax, style)

    # Apply violinplot line widths to existing violinplot elements
    _apply_violinplot_style(ax, style)

    # Apply barplot edge widths to existing bar elements
    _apply_barplot_style(ax, style)

    # Apply histogram edge widths to existing histogram elements
    _apply_histogram_style(ax, style)

    # Apply pie chart styling
    _apply_pie_style(ax, style)

    # Apply imshow/matshow/spy styling (hide axes if configured)
    _apply_matrix_style(ax, style)

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

    # Configure number of ticks (only for numeric axes, not categorical)
    # We defer tick configuration to avoid interfering with categorical axes
    # that get set up later by bar(), boxplot(), etc.
    n_ticks = style.get("n_ticks")
    if n_ticks is not None:
        # Store n_ticks preference on the axes for later application
        # This will be applied in _finalize_ticks() before saving
        ax._figrecipe_n_ticks = n_ticks

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
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=normalized_palette)
        # Also set the color cycle on this specific axes (axes cache cycler at creation)
        ax.set_prop_cycle(color=normalized_palette)

    # Store style in axes for reference
    if not hasattr(ax, "_figrecipe_style"):
        ax._figrecipe_style = {}
    ax._figrecipe_style.update(style)

    return trace_lw_pt


def _apply_boxplot_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply boxplot line width styling to existing boxplot elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing boxplot elements.
    style : dict
        Style dictionary with boxplot_* keys.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import PathPatch

    # Get line widths from style
    box_lw = mm_to_pt(style.get("boxplot_line_mm", 0.2))
    whisker_lw = mm_to_pt(style.get("boxplot_whisker_mm", 0.2))
    cap_lw = mm_to_pt(style.get("boxplot_cap_mm", 0.2))
    median_lw = mm_to_pt(style.get("boxplot_median_mm", 0.2))
    median_color = style.get("boxplot_median_color", "black")
    flier_edge_lw = mm_to_pt(style.get("boxplot_flier_edge_mm", 0.2))

    # Boxplot creates Line2D objects for whiskers, caps, medians, fliers
    # and PathPatch objects for boxes
    for child in ax.get_children():
        # Check if it's a boxplot box (PathPatch with specific properties)
        if isinstance(child, PathPatch):
            # Boxes are typically PathPatch with edgecolor
            if child.get_edgecolor() is not None:
                child.set_linewidth(box_lw)

        # Check for Line2D objects (whiskers, caps, medians, fliers)
        elif isinstance(child, Line2D):
            xdata = child.get_xdata()
            ydata = child.get_ydata()

            # Fliers are markers with no line (linestyle='None' or '')
            # and typically have varying number of points (outliers)
            marker = child.get_marker()
            linestyle = child.get_linestyle()
            if marker and marker != "None" and linestyle in ("None", "", " "):
                # This is likely a flier (outlier marker)
                child.set_markeredgewidth(flier_edge_lw)
            elif len(xdata) == 2 and len(ydata) == 2:
                # Horizontal line (could be median or cap)
                if ydata[0] == ydata[1]:
                    # Check if it's likely a median (middle of box) or cap
                    # Medians are usually solid, caps are at extremes
                    if linestyle == "-":
                        # Could be median - apply median style
                        child.set_linewidth(median_lw)
                        if median_color:
                            child.set_color(median_color)
                    else:
                        child.set_linewidth(cap_lw)
                # Vertical line (whisker)
                elif xdata[0] == xdata[1]:
                    child.set_linewidth(whisker_lw)


def _apply_violinplot_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply violinplot line width styling to existing violinplot elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing violinplot elements.
    style : dict
        Style dictionary with violinplot_* keys.
    """
    from matplotlib.collections import LineCollection, PolyCollection

    # Get line widths from style
    body_lw = mm_to_pt(style.get("violinplot_line_mm", 0.2))
    whisker_lw = mm_to_pt(style.get("violinplot_whisker_mm", 0.2))

    for child in ax.get_children():
        # Violin bodies are PolyCollection
        if isinstance(child, PolyCollection):
            child.set_linewidth(body_lw)

        # Violin inner elements (cbars, cmins, cmaxes) are LineCollection
        elif isinstance(child, LineCollection):
            child.set_linewidth(whisker_lw)


def _apply_barplot_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply barplot edge styling to existing bar elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing bar elements.
    style : dict
        Style dictionary with barplot_* keys.
    """
    from matplotlib.patches import Rectangle

    # Get edge width from style
    edge_lw = mm_to_pt(style.get("barplot_edge_mm", 0.2))

    # Bar plots create Rectangle patches
    for patch in ax.patches:
        if isinstance(patch, Rectangle):
            patch.set_linewidth(edge_lw)
            # Set edge color to black for clean scientific look
            patch.set_edgecolor("black")


def _apply_histogram_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply histogram edge styling to existing histogram elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing histogram elements.
    style : dict
        Style dictionary with histogram_* keys.
    """
    from matplotlib.patches import Rectangle

    # Get edge width from style
    edge_lw = mm_to_pt(style.get("histogram_edge_mm", 0.2))

    # Histograms also create Rectangle patches
    for patch in ax.patches:
        if isinstance(patch, Rectangle):
            patch.set_linewidth(edge_lw)
            # Set edge color to black for clean scientific look
            patch.set_edgecolor("black")


def _apply_pie_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply pie chart styling to existing pie elements.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing pie chart elements.
    style : dict
        Style dictionary with pie_* keys.
    """
    from matplotlib.patches import Wedge

    # Check if axes contains pie chart (wedge patches)
    has_pie = any(isinstance(p, Wedge) for p in ax.patches)
    if not has_pie:
        return

    # Get pie text size from style (default 6pt for scientific publications)
    text_pt = style.get("pie_text_pt", 6)
    show_axes = style.get("pie_show_axes", False)
    font_family = check_font(style.get("font_family", "Arial"))

    # Apply text size to all pie text elements (labels and percentages)
    for text in ax.texts:
        text.set_fontsize(text_pt)
        text.set_fontfamily(font_family)

    # Hide axes if configured (default: hide for pie charts)
    if not show_axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        # Hide spines
        for spine in ax.spines.values():
            spine.set_visible(False)


def _apply_matrix_style(ax: Axes, style: Dict[str, Any]) -> None:
    """Apply imshow/matshow/spy styling (hide axes if configured).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes containing matrix plot elements.
    style : dict
        Style dictionary with imshow_*, matshow_*, spy_* keys.
    """
    from matplotlib.image import AxesImage

    # Check if axes contains an image (imshow/matshow)
    has_image = any(isinstance(c, AxesImage) for c in ax.get_children())
    if not has_image:
        return

    # Check if imshow_show_axes is False
    show_axes = style.get("imshow_show_axes", True)
    show_labels = style.get("imshow_show_labels", True)

    if not show_axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        # Hide spines
        for spine in ax.spines.values():
            spine.set_visible(False)

    if not show_labels:
        ax.set_xlabel("")
        ax.set_ylabel("")


def finalize_ticks(ax: Axes) -> None:
    """
    Apply deferred tick configuration after all plotting is done.

    This function applies the n_ticks setting stored by apply_style_mm(),
    but only to numeric axes (not categorical).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to finalize.
    """
    from matplotlib.ticker import MaxNLocator

    n_ticks = getattr(ax, "_figrecipe_n_ticks", None)
    if n_ticks is None:
        return

    # Check if x-axis is categorical (has string tick labels)
    x_labels = [t.get_text() for t in ax.get_xticklabels()]
    x_is_categorical = any(
        lbl and not lbl.replace(".", "").replace("-", "").replace("+", "").isdigit()
        for lbl in x_labels
        if lbl
    )
    if not x_is_categorical:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=n_ticks))

    # Check if y-axis is categorical
    y_labels = [t.get_text() for t in ax.get_yticklabels()]
    y_is_categorical = any(
        lbl and not lbl.replace(".", "").replace("-", "").replace("+", "").isdigit()
        for lbl in y_labels
        if lbl
    )
    if not y_is_categorical:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=n_ticks))


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
