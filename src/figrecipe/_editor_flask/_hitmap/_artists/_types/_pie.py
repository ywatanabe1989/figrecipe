#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pie chart hitmap processing."""

from typing import Any, Dict

from matplotlib.patches import Wedge

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_pie_chart(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process pie charts.

    Pie charts use Wedge patches for slices.

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
    pie_ids = get_call_ids(ax_info, "pie")
    call_id = pie_ids[0] if pie_ids else None

    wedge_idx = 0
    for i, patch in enumerate(ax.patches):
        if not isinstance(patch, Wedge):
            continue
        if not patch.get_visible():
            continue

        key = f"ax{ax_idx}_wedge{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolor": patch.get_facecolor(),
            "edgecolor": patch.get_edgecolor(),
        }

        patch.set_facecolor(normalize_color(rgb))
        patch.set_edgecolor(normalize_color(rgb))

        label = f"{call_id}_slice{wedge_idx}" if call_id else f"pie_slice_{wedge_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "pie",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
            "call_id": call_id,
        }
        element_id += 1
        wedge_idx += 1

    return element_id


__all__ = ["process_pie_chart"]

# EOF
