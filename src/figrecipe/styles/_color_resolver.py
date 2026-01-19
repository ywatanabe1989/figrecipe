#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color resolver for figrecipe.

Maps named color strings to style-defined RGB values when a style is loaded.
This enables consistent theming where "blue" means SCITEX blue [0, 128, 192],
not matplotlib's CSS4 blue [0, 0, 255].

Usage:
    from figrecipe.styles import resolve_color, resolve_colors_in_kwargs

    # Resolve a single color
    color = resolve_color("blue")  # Returns (0, 0.502, 0.753) with SCITEX style

    # Resolve colors in kwargs dict
    kwargs = resolve_colors_in_kwargs({"color": "blue", "edgecolor": "red"})
"""

__all__ = [
    "resolve_color",
    "resolve_colors_in_kwargs",
    "get_color_map",
]

from typing import Any, Dict, List, Optional, Tuple

# Color-related kwargs keys to resolve
COLOR_KWARGS = {
    "color",
    "c",
    "facecolor",
    "fc",
    "edgecolor",
    "ec",
    "markerfacecolor",
    "mfc",
    "markeredgecolor",
    "mec",
    "ecolor",  # errorbar color
}

# Cached color map from current style
_COLOR_MAP_CACHE: Optional[Dict[str, Tuple[float, float, float]]] = None
_CACHE_STYLE_NAME: Optional[str] = None


def _normalize_rgb(rgb: List) -> Tuple[float, float, float]:
    """Normalize RGB values to 0.0-1.0 range.

    Parameters
    ----------
    rgb : list
        RGB values as [r, g, b], either 0-255 or 0.0-1.0 range.

    Returns
    -------
    tuple
        Normalized (r, g, b) tuple with values in 0.0-1.0 range.
    """
    if len(rgb) < 3:
        return tuple(rgb)

    # Check if values are in 0-255 range
    if any(v > 1.0 for v in rgb[:3]):
        return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    return (rgb[0], rgb[1], rgb[2])


def get_color_map() -> Dict[str, Tuple[float, float, float]]:
    """Get the color name to RGB mapping from current style.

    Returns
    -------
    dict
        Mapping of color names to normalized RGB tuples.
        Returns empty dict if no style is loaded or style has no color map.
    """
    global _COLOR_MAP_CACHE, _CACHE_STYLE_NAME

    from ._style_loader import _CURRENT_STYLE_NAME, _STYLE_CACHE

    # Check if cache is valid
    if _COLOR_MAP_CACHE is not None and _CACHE_STYLE_NAME == _CURRENT_STYLE_NAME:
        return _COLOR_MAP_CACHE

    # Build new color map from style
    _COLOR_MAP_CACHE = {}
    _CACHE_STYLE_NAME = _CURRENT_STYLE_NAME

    if _STYLE_CACHE is None:
        return _COLOR_MAP_CACHE

    # Get colors.rgb from style
    colors = _STYLE_CACHE.get("colors", {})
    rgb_list = colors.get("rgb", [])

    # Parse the rgb list (list of single-key dicts)
    for item in rgb_list:
        if isinstance(item, dict):
            for name, rgb in item.items():
                if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
                    _COLOR_MAP_CACHE[name.lower()] = _normalize_rgb(rgb)

    return _COLOR_MAP_CACHE


def resolve_color(
    color: Any,
    fallback: bool = True,
) -> Any:
    """Resolve a color value using the current style's color map.

    Parameters
    ----------
    color : any
        Color specification. Can be:
        - String color name (e.g., "blue", "red")
        - RGB/RGBA tuple or list
        - Hex color string (e.g., "#0080c0")
        - Any other matplotlib color spec
    fallback : bool
        If True, return original color if not found in style map.
        If False, return None if not found.

    Returns
    -------
    any
        Resolved color value. If color is a named color in the style's
        color map, returns the normalized RGB tuple. Otherwise returns
        the original color (if fallback=True) or None.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.load_style("SCITEX")
    >>> resolve_color("blue")
    (0.0, 0.5019607843137255, 0.7529411764705882)

    >>> resolve_color("unknown_color")  # Falls back to original
    'unknown_color'
    """
    # Only resolve string color names
    if not isinstance(color, str):
        return color

    # Skip hex colors and other special formats
    if color.startswith("#") or color.startswith("C"):
        return color

    # Look up in style color map
    color_map = get_color_map()
    if not color_map:
        return color if fallback else None

    # Case-insensitive lookup
    resolved = color_map.get(color.lower())
    if resolved is not None:
        return resolved

    return color if fallback else None


def resolve_colors_in_kwargs(
    kwargs: Dict[str, Any],
    keys: Optional[set] = None,
) -> Dict[str, Any]:
    """Resolve all color-related values in a kwargs dict.

    Parameters
    ----------
    kwargs : dict
        Keyword arguments that may contain color specifications.
    keys : set, optional
        Set of keys to check for colors. Defaults to COLOR_KWARGS.

    Returns
    -------
    dict
        New dict with color values resolved to style colors.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.load_style("SCITEX")
    >>> kwargs = {"color": "blue", "linewidth": 2}
    >>> resolve_colors_in_kwargs(kwargs)
    {'color': (0.0, 0.502, 0.753), 'linewidth': 2}
    """
    if keys is None:
        keys = COLOR_KWARGS

    result = kwargs.copy()

    for key in keys:
        if key in result:
            value = result[key]
            if isinstance(value, str):
                result[key] = resolve_color(value)
            elif isinstance(value, (list, tuple)):
                # Handle list of colors
                result[key] = [
                    resolve_color(c) if isinstance(c, str) else c for c in value
                ]

    return result


def invalidate_cache() -> None:
    """Invalidate the color map cache.

    Call this when the style is changed or unloaded.
    """
    global _COLOR_MAP_CACHE, _CACHE_STYLE_NAME
    _COLOR_MAP_CACHE = None
    _CACHE_STYLE_NAME = None


# EOF
