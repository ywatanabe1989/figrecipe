#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Native matplotlib diagram styling using figrecipe SCITEX colors.

Derives all colors from the SCITEX preset palette defined in
``styles/presets/SCITEX.yaml`` rather than hardcoding hex values.
"""

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# SCITEX palette (source of truth: styles/presets/SCITEX.yaml colors.rgb)
# Kept as constants so diagram/schematic code works without load_style().
# ---------------------------------------------------------------------------
_SCITEX_RGB = {
    "blue": (0, 128, 192),
    "red": (255, 70, 50),
    "green": (20, 180, 20),
    "yellow": (230, 160, 20),
    "purple": (200, 50, 255),
    "lightblue": (20, 200, 200),
    "orange": (228, 94, 50),
    "pink": (255, 150, 200),
    "gray": (128, 128, 128),
    "brown": (128, 0, 0),
    "navy": (0, 0, 100),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert (r, g, b) 0-255 to hex string."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _lighten(rgb: Tuple[int, int, int], factor: float = 0.75) -> str:
    """Blend color toward white. factor=1.0 → white, 0.0 → original."""
    r = int(rgb[0] + (255 - rgb[0]) * factor)
    g = int(rgb[1] + (255 - rgb[1]) * factor)
    b = int(rgb[2] + (255 - rgb[2]) * factor)
    return _rgb_to_hex((r, g, b))


def _darken(rgb: Tuple[int, int, int], factor: float = 0.4) -> str:
    """Blend color toward black. factor=1.0 → black, 0.0 → original."""
    r = int(rgb[0] * (1 - factor))
    g = int(rgb[1] * (1 - factor))
    b = int(rgb[2] * (1 - factor))
    return _rgb_to_hex((r, g, b))


# ---------------------------------------------------------------------------
# Color derivation: base color → fill / stroke / text
# ---------------------------------------------------------------------------
_FILL_FACTOR = 0.75  # lighten base → fill background
_TEXT_FACTOR = 0.4  # darken base → text foreground


def _build_emphasis(
    base_name: str,
    fill_factor: float = _FILL_FACTOR,
    text_factor: float = _TEXT_FACTOR,
) -> Dict[str, str]:
    """Derive fill/stroke/text from a SCITEX base color."""
    rgb = _SCITEX_RGB[base_name]
    return {
        "fill": _lighten(rgb, fill_factor),
        "stroke": _rgb_to_hex(rgb),
        "text": _darken(rgb, text_factor),
    }


# Semantic emphasis styles — all derived from SCITEX base colors
EMPHASIS_COLORS: Dict[str, Dict[str, str]] = {
    "normal": _build_emphasis("gray", fill_factor=0.85),
    "primary": _build_emphasis("blue"),
    "success": _build_emphasis("green"),
    "warning": _build_emphasis("yellow"),
    "muted": _build_emphasis("gray", fill_factor=0.88, text_factor=0.3),
}

# Edge styles (neutral gray tones from SCITEX gray)
EDGE_STYLES = {
    "solid": {"linestyle": "-", "color": _darken(_SCITEX_RGB["gray"], 0.25)},
    "dashed": {"linestyle": "--", "color": _rgb_to_hex(_SCITEX_RGB["gray"])},
    "dotted": {"linestyle": ":", "color": _lighten(_SCITEX_RGB["gray"], 0.25)},
}

# Font configuration
FONT_CONFIG = {
    "family": "sans-serif",
    "node_size": 9,
    "edge_label_size": 7,
    "title_size": 11,
    "weight": "normal",
}

# Named colors (hex) for direct access
COLORS = {name: _rgb_to_hex(rgb) for name, rgb in _SCITEX_RGB.items()}
COLORS_LIGHT = {name: _lighten(rgb, _FILL_FACTOR) for name, rgb in _SCITEX_RGB.items()}


def get_emphasis_style(emphasis: str) -> Dict[str, str]:
    """Get fill, stroke, text colors for an emphasis level or color name.

    Parameters
    ----------
    emphasis : str
        Semantic: "normal", "primary", "success", "warning", "muted"
        Color name: "blue", "red", "green", "yellow", "purple", etc.

    Returns
    -------
    dict
        Dictionary with 'fill', 'stroke', 'text' color values.
    """
    if emphasis in EMPHASIS_COLORS:
        return EMPHASIS_COLORS[emphasis]
    # Allow direct SCITEX color names (e.g., emphasis="blue", "red")
    if emphasis in _SCITEX_RGB:
        return _build_emphasis(emphasis)
    return EMPHASIS_COLORS["normal"]


def get_edge_style(style: str) -> Dict[str, str]:
    """Get linestyle and color for an edge style.

    Parameters
    ----------
    style : str
        Named: "solid", "dashed", "dotted"
        Matplotlib: "-", "--", ":", "-."

    Returns
    -------
    dict
        Dictionary with 'linestyle' and 'color' values.
    """
    if style in EDGE_STYLES:
        return EDGE_STYLES[style]
    # Accept matplotlib linestyle strings directly
    _MPL_ALIASES = {"--": "dashed", ":": "dotted", "-.": "dashed", "-": "solid"}
    if style in _MPL_ALIASES:
        return EDGE_STYLES[_MPL_ALIASES[style]]
    return EDGE_STYLES["solid"]


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to RGB tuple (0-1 range)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def get_auto_colors(n: int) -> List[str]:
    """Generate n distinct colors from SCITEX palette.

    Parameters
    ----------
    n : int
        Number of colors needed.

    Returns
    -------
    list
        List of hex color strings.
    """
    order = [
        "blue",
        "red",
        "green",
        "yellow",
        "purple",
        "lightblue",
        "orange",
        "pink",
        "navy",
        "brown",
    ]
    return [COLORS[order[i % len(order)]] for i in range(n)]


__all__ = [
    "COLORS",
    "COLORS_LIGHT",
    "EMPHASIS_COLORS",
    "EDGE_STYLES",
    "FONT_CONFIG",
    "get_emphasis_style",
    "get_edge_style",
    "hex_to_rgb",
    "get_auto_colors",
]

# EOF
