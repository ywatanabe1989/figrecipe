#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color utilities for hitmap generation."""

from typing import Tuple

# Hand-picked distinct colors for first 12 elements (maximum visual distinction)
DISTINCT_COLORS = [
    (255, 0, 0),  # Red
    (0, 200, 0),  # Green
    (0, 100, 255),  # Blue
    (255, 200, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 128, 0),  # Orange
    (128, 0, 255),  # Purple
    (0, 255, 128),  # Spring green
    (255, 0, 128),  # Rose
    (128, 255, 0),  # Lime
    (0, 128, 255),  # Sky blue
]

# Reserved colors
BACKGROUND_COLOR = (26, 26, 26)  # Dark gray for background
AXES_COLOR = (64, 64, 64)  # Medium gray for non-selectable axes elements


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB (0-255 range).

    Parameters
    ----------
    h : float
        Hue (0-1).
    s : float
        Saturation (0-1).
    v : float
        Value (0-1).

    Returns
    -------
    tuple
        RGB tuple (0-255 range).
    """
    if s == 0:
        r = g = b = int(v * 255)
        return (r, g, b)

    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    i %= 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def id_to_rgb(element_id: int) -> Tuple[int, int, int]:
    """Convert element ID to unique RGB color.

    Parameters
    ----------
    element_id : int
        Unique element identifier (1-based).

    Returns
    -------
    tuple of int
        RGB color tuple (0-255 range).

    Notes
    -----
    - ID 0 is reserved for background
    - IDs 1-12 use hand-picked distinct colors
    - IDs 13+ use HSV-based generation
    """
    if element_id <= 0:
        return BACKGROUND_COLOR

    if element_id <= len(DISTINCT_COLORS):
        return DISTINCT_COLORS[element_id - 1]

    # HSV-based generation for IDs > 12
    golden_ratio = 0.618033988749895
    hue = ((element_id - len(DISTINCT_COLORS)) * golden_ratio) % 1.0
    saturation = 0.7 + (element_id % 3) * 0.1
    value = 0.75 + (element_id % 4) * 0.0625

    return hsv_to_rgb(hue, saturation, value)


def rgb_to_id(rgb: Tuple[int, int, int]) -> int:
    """Convert RGB color back to element ID.

    Parameters
    ----------
    rgb : tuple of int
        RGB color tuple.

    Returns
    -------
    int
        Element ID, or 0 if background/unknown.
    """
    if rgb == BACKGROUND_COLOR:
        return 0
    if rgb == AXES_COLOR:
        return 0

    # Check hand-picked colors
    if rgb in DISTINCT_COLORS:
        return DISTINCT_COLORS.index(rgb) + 1

    # For HSV-generated colors, search
    for test_id in range(len(DISTINCT_COLORS) + 1, 1000):
        if id_to_rgb(test_id) == rgb:
            return test_id

    return 0


def normalize_color(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Normalize RGB from 0-255 to 0-1 range."""
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)


def mpl_color_to_hex(color) -> str:
    """Convert matplotlib color to hex string.

    Parameters
    ----------
    color : color
        Matplotlib color (RGBA tuple, hex string, named color).

    Returns
    -------
    str
        Hex color string (e.g., '#FF0000').
    """
    import matplotlib.colors as mcolors

    try:
        if hasattr(color, "__iter__") and not isinstance(color, str):
            color = tuple(color)
            if len(color) >= 3:
                if all(isinstance(c, (int, float)) for c in color[:3]):
                    if all(c <= 1.0 for c in color[:3]):
                        return mcolors.to_hex(color[:3])
                    else:
                        return mcolors.to_hex(tuple(c / 255 for c in color[:3]))
        return mcolors.to_hex(color)
    except Exception:
        return "#888888"


__all__ = [
    "DISTINCT_COLORS",
    "BACKGROUND_COLOR",
    "AXES_COLOR",
    "hsv_to_rgb",
    "id_to_rgb",
    "rgb_to_id",
    "normalize_color",
    "mpl_color_to_hex",
]

# EOF
