#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Theme color utilities for figrecipe styles."""

from typing import Dict, Optional

from matplotlib.axes import Axes

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

        # Apply text colors to figure-level text elements
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

    # Update rcParams for dark mode support (pie charts, panel labels)
    import matplotlib as mpl

    mpl.rcParams["text.color"] = colors["text"]
    mpl.rcParams["axes.labelcolor"] = colors["text"]
    mpl.rcParams["xtick.color"] = colors["tick"]
    mpl.rcParams["ytick.color"] = colors["tick"]

    # Apply spine colors
    for spine in ax.spines.values():
        spine.set_color(colors["spine"])

    # Apply tick colors (both marks and labels)
    ax.tick_params(colors=colors["tick"], which="both")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(colors["tick"])

    # Apply text colors to all text objects (panel labels, pie labels, annotations)
    for text in ax.texts:
        text.set_color(colors["text"])

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


__all__ = ["THEME_COLORS", "apply_theme_colors"]

# EOF
