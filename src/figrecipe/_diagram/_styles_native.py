#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Native matplotlib diagram styling with Material Design colors."""

from typing import Dict, Tuple

# Material Design 500-level colors
MATERIAL_COLORS = {
    "blue": "#2196F3",
    "red": "#F44336",
    "green": "#4CAF50",
    "amber": "#FFC107",
    "purple": "#9C27B0",
    "teal": "#009688",
    "orange": "#FF9800",
    "pink": "#E91E63",
    "indigo": "#3F51B5",
    "cyan": "#00BCD4",
    "lime": "#CDDC39",
    "brown": "#795548",
    "grey": "#9E9E9E",
    "blue_grey": "#607D8B",
}

# Lighter variants (100-level) for fills
MATERIAL_COLORS_LIGHT = {
    "blue": "#BBDEFB",
    "red": "#FFCDD2",
    "green": "#C8E6C9",
    "amber": "#FFECB3",
    "purple": "#E1BEE7",
    "teal": "#B2DFDB",
    "orange": "#FFE0B2",
    "pink": "#F8BBD0",
    "indigo": "#C5CAE9",
    "cyan": "#B2EBF2",
    "lime": "#F0F4C3",
    "brown": "#D7CCC8",
    "grey": "#F5F5F5",
    "blue_grey": "#CFD8DC",
}

# Emphasis level to color mapping
EMPHASIS_COLORS: Dict[str, Dict[str, str]] = {
    "normal": {
        "fill": MATERIAL_COLORS_LIGHT["grey"],
        "stroke": MATERIAL_COLORS["grey"],
        "text": "#212121",
    },
    "primary": {
        "fill": MATERIAL_COLORS_LIGHT["blue"],
        "stroke": MATERIAL_COLORS["blue"],
        "text": "#0D47A1",  # Blue 900
    },
    "success": {
        "fill": MATERIAL_COLORS_LIGHT["green"],
        "stroke": MATERIAL_COLORS["green"],
        "text": "#1B5E20",  # Green 900
    },
    "warning": {
        "fill": MATERIAL_COLORS_LIGHT["amber"],
        "stroke": MATERIAL_COLORS["amber"],
        "text": "#F57F17",  # Amber 900
    },
    "muted": {
        "fill": "#FAFAFA",
        "stroke": "#BDBDBD",
        "text": "#757575",
    },
}

# Default edge colors
EDGE_STYLES = {
    "solid": {"linestyle": "-", "color": "#616161"},
    "dashed": {"linestyle": "--", "color": "#757575"},
    "dotted": {"linestyle": ":", "color": "#9E9E9E"},
}

# Font configuration
FONT_CONFIG = {
    "family": "sans-serif",
    "node_size": 9,
    "edge_label_size": 7,
    "title_size": 11,
    "weight": "normal",
}


def get_emphasis_style(emphasis: str) -> Dict[str, str]:
    """Get fill, stroke, text colors for an emphasis level.

    Parameters
    ----------
    emphasis : str
        One of: normal, primary, success, warning, muted

    Returns
    -------
    dict
        Dictionary with 'fill', 'stroke', 'text' color values.
    """
    return EMPHASIS_COLORS.get(emphasis, EMPHASIS_COLORS["normal"])


def get_edge_style(style: str) -> Dict[str, str]:
    """Get linestyle and color for an edge style.

    Parameters
    ----------
    style : str
        One of: solid, dashed, dotted

    Returns
    -------
    dict
        Dictionary with 'linestyle' and 'color' values.
    """
    return EDGE_STYLES.get(style, EDGE_STYLES["solid"])


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to RGB tuple (0-1 range)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def get_auto_colors(n: int) -> list:
    """Generate n distinct colors from Material palette.

    Parameters
    ----------
    n : int
        Number of colors needed.

    Returns
    -------
    list
        List of hex color strings.
    """
    color_order = [
        "blue",
        "green",
        "amber",
        "red",
        "purple",
        "teal",
        "orange",
        "pink",
        "indigo",
        "cyan",
    ]
    colors = []
    for i in range(n):
        color_name = color_order[i % len(color_order)]
        colors.append(MATERIAL_COLORS[color_name])
    return colors


__all__ = [
    "MATERIAL_COLORS",
    "MATERIAL_COLORS_LIGHT",
    "EMPHASIS_COLORS",
    "EDGE_STYLES",
    "FONT_CONFIG",
    "get_emphasis_style",
    "get_edge_style",
    "hex_to_rgb",
    "get_auto_colors",
]
