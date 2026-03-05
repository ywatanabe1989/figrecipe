#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stem plot hitmap processing."""

from typing import Any, Dict

from matplotlib.collections import LineCollection

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_stem_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process stem plots.

    Stem plots consist of:
    - Markers at data points (via Line2D)
    - Vertical/horizontal stems (via LineCollection)
    - A baseline (via Line2D)

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
    stem_ids = get_call_ids(ax_info, "stem")
    if not stem_ids:
        return element_id

    call_id = stem_ids[0] if stem_ids else None

    # Process LineCollection (stems)
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, LineCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_stem_lines{i}"
        rgb = id_to_rgb(element_id)

        orig_colors = coll.get_colors().copy() if hasattr(coll, "get_colors") else []
        original_props[key] = {
            "colors": orig_colors,
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_color(normalize_color(rgb))

        orig_color = orig_colors[0] if len(orig_colors) > 0 else [0.5, 0.5, 0.5, 1]

        color_map[key] = {
            "id": element_id,
            "type": "stem",
            "label": call_id or f"stem_lines_{i}",
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1

    # Process markers and baseline (Line2D)
    stem_line_idx = 0
    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue

        orig_label = line.get_label() or ""
        # Stem markers typically have _child or similar label
        if not orig_label.startswith("_"):
            continue

        xdata = line.get_xdata()
        if len(xdata) == 0:
            continue

        key = f"ax{ax_idx}_stem_marker{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "color": line.get_color(),
            "markerfacecolor": line.get_markerfacecolor(),
            "markeredgecolor": line.get_markeredgecolor(),
        }

        line.set_color(normalize_color(rgb))
        line.set_markerfacecolor(normalize_color(rgb))
        line.set_markeredgecolor(normalize_color(rgb))

        # Distinguish baseline from markers based on data pattern
        if len(xdata) == 2:  # Likely baseline
            elem_label = (
                f"{call_id}_baseline" if call_id else f"stem_baseline_{stem_line_idx}"
            )
        else:
            elem_label = (
                f"{call_id}_markers" if call_id else f"stem_markers_{stem_line_idx}"
            )

        color_map[key] = {
            "id": element_id,
            "type": "stem",
            "label": elem_label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["color"]),
            "call_id": call_id,
        }
        element_id += 1
        stem_line_idx += 1

    return element_id


__all__ = ["process_stem_plot"]

# EOF
