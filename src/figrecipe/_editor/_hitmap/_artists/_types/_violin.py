#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Violin plot hitmap processing."""

from typing import Any, Dict

from matplotlib.collections import LineCollection, PolyCollection

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_violin_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process violin plots.

    Violin plots consist of:
    - PolyCollection for violin bodies
    - LineCollection for inner lines (quartiles, medians)

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
    violin_ids = get_call_ids(ax_info, "violinplot")
    if not violin_ids:
        return element_id

    call_id = violin_ids[0] if violin_ids else None

    # Process PolyCollection (violin bodies)
    body_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PolyCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_violin_body{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        label = f"{call_id}_body{body_idx}" if call_id else f"violin_body_{body_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "violin",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        body_idx += 1

    # Process LineCollection (inner lines)
    line_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, LineCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_violin_lines{i}"
        rgb = id_to_rgb(element_id)

        orig_colors = coll.get_colors().copy() if hasattr(coll, "get_colors") else []
        original_props[key] = {
            "colors": orig_colors,
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_color(normalize_color(rgb))

        orig_color = orig_colors[0] if len(orig_colors) > 0 else [0.5, 0.5, 0.5, 1]
        label = f"{call_id}_lines{line_idx}" if call_id else f"violin_lines_{line_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "violin",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        line_idx += 1

    return element_id


__all__ = ["process_violin_plot"]

# EOF
