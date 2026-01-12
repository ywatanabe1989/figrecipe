#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boxplot hitmap processing."""

from typing import Any, Dict

from matplotlib.patches import Rectangle

from ._base import get_call_ids, id_to_rgb, mpl_color_to_hex, normalize_color


def process_boxplot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process boxplots.

    Boxplots consist of:
    - Rectangle patches for boxes
    - Line2D for whiskers, medians, caps
    - PathPatch for fliers

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
    boxplot_ids = get_call_ids(ax_info, "boxplot")
    if not boxplot_ids:
        return element_id

    call_id = boxplot_ids[0] if boxplot_ids else None

    # Process Rectangle patches (boxes)
    box_idx = 0
    for i, patch in enumerate(ax.patches):
        if not isinstance(patch, Rectangle):
            continue
        if not patch.get_visible():
            continue
        # Skip default background
        if patch.get_width() == 1.0 and patch.get_height() == 1.0:
            continue

        key = f"ax{ax_idx}_boxplot_box{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolor": patch.get_facecolor(),
            "edgecolor": patch.get_edgecolor(),
        }

        patch.set_facecolor(normalize_color(rgb))
        patch.set_edgecolor(normalize_color(rgb))

        label = f"{call_id}_box{box_idx}" if call_id else f"boxplot_box_{box_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "boxplot",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
            "call_id": call_id,
        }
        element_id += 1
        box_idx += 1

    # Process lines (whiskers, medians, caps)
    line_idx = 0
    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue

        orig_label = line.get_label() or ""
        # Boxplot elements have underscore labels
        if not orig_label.startswith("_"):
            continue

        xdata = line.get_xdata()
        if len(xdata) == 0:
            continue

        key = f"ax{ax_idx}_boxplot_line{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "color": line.get_color(),
            "markerfacecolor": line.get_markerfacecolor(),
            "markeredgecolor": line.get_markeredgecolor(),
        }

        line.set_color(normalize_color(rgb))
        line.set_markerfacecolor(normalize_color(rgb))
        line.set_markeredgecolor(normalize_color(rgb))

        # Identify line type
        ydata = line.get_ydata()
        if len(xdata) == 2 and len(ydata) == 2:
            if ydata[0] == ydata[1]:  # Horizontal line
                elem_label = (
                    f"{call_id}_median" if call_id else f"boxplot_median_{line_idx}"
                )
            else:  # Vertical line (whisker)
                elem_label = (
                    f"{call_id}_whisker" if call_id else f"boxplot_whisker_{line_idx}"
                )
        else:
            elem_label = (
                f"{call_id}_line{line_idx}" if call_id else f"boxplot_line_{line_idx}"
            )

        color_map[key] = {
            "id": element_id,
            "type": "boxplot",
            "label": elem_label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["color"]),
            "call_id": call_id,
        }
        element_id += 1
        line_idx += 1

    return element_id


__all__ = ["process_boxplot"]

# EOF
