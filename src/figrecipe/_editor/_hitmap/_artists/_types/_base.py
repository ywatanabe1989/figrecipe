#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base utilities for plot-type-specific hitmap processing.

This module provides shared utilities used by all plot-type processors.
"""

from typing import Any, Dict, Tuple

from ..._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def register_element(
    key: str,
    element_id: int,
    elem_type: str,
    label: str,
    ax_idx: int,
    original_color: Any,
    call_id: str = None,
    color_map: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Register an element in the color map.

    Parameters
    ----------
    key : str
        Unique key for this element (e.g., "ax0_line1")
    element_id : int
        Unique numeric ID for this element
    elem_type : str
        Element type (e.g., "line", "scatter", "bar")
    label : str
        Display label for this element
    ax_idx : int
        Axes index containing this element
    original_color : Any
        Original color of the element
    call_id : str, optional
        Call ID from recorder if available
    color_map : dict, optional
        Color map to update (if provided)

    Returns
    -------
    dict
        Element entry for color map
    """
    rgb = id_to_rgb(element_id)
    entry = {
        "id": element_id,
        "type": elem_type,
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_color),
        "call_id": call_id,
    }
    if color_map is not None:
        color_map[key] = entry
    return entry


def apply_hitmap_color(artist: Any, element_id: int) -> Tuple[int, int, int]:
    """Apply hitmap color to an artist.

    This is a convenience function that gets the RGB color for an element ID.

    Parameters
    ----------
    artist : Any
        Matplotlib artist (unused, for interface consistency)
    element_id : int
        Element ID to generate color for

    Returns
    -------
    tuple
        RGB color tuple
    """
    return id_to_rgb(element_id)


def get_call_ids(ax_info: Dict[str, Any], plot_type: str) -> list:
    """Get call IDs for a specific plot type.

    Parameters
    ----------
    ax_info : dict
        Axes info containing plot types and call IDs
    plot_type : str
        Plot type name (e.g., "bar", "scatter")

    Returns
    -------
    list
        List of call IDs for this plot type
    """
    call_ids = ax_info.get("call_ids", {})
    return list(call_ids.get(plot_type, []))


def has_plot_type(ax_info: Dict[str, Any], plot_type: str) -> bool:
    """Check if axes has a specific plot type.

    Parameters
    ----------
    ax_info : dict
        Axes info containing plot types
    plot_type : str
        Plot type to check for

    Returns
    -------
    bool
        True if plot type is present
    """
    types = ax_info.get("types", set())
    return plot_type in types


__all__ = [
    "register_element",
    "apply_hitmap_color",
    "get_call_ids",
    "has_plot_type",
    "id_to_rgb",
    "normalize_color",
    "mpl_color_to_hex",
]

# EOF
