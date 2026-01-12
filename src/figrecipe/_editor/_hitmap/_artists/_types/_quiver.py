#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quiver and barbs plot hitmap processing."""

from typing import Any, Dict

from matplotlib.quiver import Barbs, Quiver

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_quiver_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process quiver plots (vector fields).

    Quiver plots use Quiver collection for arrows.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes
    ax_idx : int
        Axes index
    element_id : int
        Starting element ID
    original_props : dict
        Dict to store original properties
    color_map : dict
        Dict to store element color mappings
    ax_info : dict
        Axes plot type information

    Returns
    -------
    int
        Updated element ID
    """
    quiver_ids = get_call_ids(ax_info, "quiver")
    quiver_idx = 0

    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, Quiver):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_quiver{i}"
        rgb = id_to_rgb(element_id)

        orig_color = coll.get_facecolor().copy()
        original_props[key] = {"color": orig_color}
        coll.set_color(normalize_color(rgb))

        if quiver_idx < len(quiver_ids):
            call_id = quiver_ids[quiver_idx]
            label = call_id
        else:
            call_id = f"quiver_{ax_idx}_{quiver_idx}"
            label = call_id

        # Get representative color for display
        orig_color_val = orig_color[0] if len(orig_color) > 0 else [0.5, 0.5, 0.5, 1]

        color_map[key] = {
            "id": element_id,
            "type": "quiver",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color_val),
            "call_id": call_id,
        }
        element_id += 1
        quiver_idx += 1

    return element_id


def process_barbs_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process barbs plots (wind barbs).

    Barbs plots use Barbs collection.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes
    ax_idx : int
        Axes index
    element_id : int
        Starting element ID
    original_props : dict
        Dict to store original properties
    color_map : dict
        Dict to store element color mappings
    ax_info : dict
        Axes plot type information

    Returns
    -------
    int
        Updated element ID
    """
    barbs_ids = get_call_ids(ax_info, "barbs")
    barbs_idx = 0

    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, Barbs):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_barbs{i}"
        rgb = id_to_rgb(element_id)

        orig_color = coll.get_facecolor().copy()
        original_props[key] = {"color": orig_color}
        coll.set_color(normalize_color(rgb))

        if barbs_idx < len(barbs_ids):
            call_id = barbs_ids[barbs_idx]
            label = call_id
        else:
            call_id = f"barbs_{ax_idx}_{barbs_idx}"
            label = call_id

        # Get representative color for display
        orig_color_val = orig_color[0] if len(orig_color) > 0 else [0.5, 0.5, 0.5, 1]

        color_map[key] = {
            "id": element_id,
            "type": "barbs",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color_val),
            "call_id": call_id,
        }
        element_id += 1
        barbs_idx += 1

    return element_id


__all__ = ["process_quiver_plot", "process_barbs_plot"]

# EOF
