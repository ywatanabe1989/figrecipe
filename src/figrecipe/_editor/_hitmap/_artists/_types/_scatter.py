#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scatter plot hitmap processing."""

from typing import Any, Dict

from matplotlib.collections import PathCollection

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_scatter_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process scatter plots.

    Scatter plots use PathCollection for rendering points.

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
    scatter_ids = get_call_ids(ax_info, "scatter")
    scatter_idx = 0

    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PathCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_scatter{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        orig_label = coll.get_label() or f"scatter_{i}"
        if scatter_idx < len(scatter_ids):
            call_id = scatter_ids[scatter_idx]
            label = call_id
        else:
            call_id = f"scatter_{ax_idx}_{scatter_idx}"
            label = call_id if orig_label.startswith("_") else orig_label

        color_map[key] = {
            "id": element_id,
            "type": "scatter",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        scatter_idx += 1

    return element_id


__all__ = ["process_scatter_plot"]

# EOF
