#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event plot hitmap processing."""

from typing import Any, Dict

from matplotlib.collections import EventCollection, LineCollection

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_eventplot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process event plots.

    Event plots use EventCollection or LineCollection.

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
    eventplot_ids = get_call_ids(ax_info, "eventplot")
    if not eventplot_ids:
        return element_id

    call_id = eventplot_ids[0] if eventplot_ids else None
    event_idx = 0

    for i, coll in enumerate(ax.collections):
        # EventCollection inherits from LineCollection
        if not isinstance(coll, (EventCollection, LineCollection)):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_event{i}"
        rgb = id_to_rgb(element_id)

        orig_colors = coll.get_colors().copy() if hasattr(coll, "get_colors") else []
        original_props[key] = {
            "colors": orig_colors,
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_color(normalize_color(rgb))

        orig_color = orig_colors[0] if len(orig_colors) > 0 else [0.5, 0.5, 0.5, 1]
        label = f"{call_id}_channel{event_idx}" if call_id else f"event_{event_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "eventplot",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        event_idx += 1

    return element_id


__all__ = ["process_eventplot"]

# EOF
