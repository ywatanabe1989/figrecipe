#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram element matching for hitmap generation.

Maps FancyBboxPatch and FancyArrowPatch to diagram box/arrow IDs
by cross-referencing patch positions with diagram_data positions.
This enables the override system to target specific diagram elements.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from matplotlib.patches import FancyBboxPatch

from .._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def build_diagram_lookup(
    diagram_data: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build position lookup tables from diagram_data for element matching.

    Parameters
    ----------
    diagram_data : dict
        Serialized diagram data from Diagram.to_dict().

    Returns
    -------
    box_lookup : list of dict
        Each entry: {id, title, center_x, center_y, width, height, is_container}
    arrow_lookup : list of dict
        Each entry: {index, source, target, label}
    """
    positions = diagram_data.get("positions", {})
    boxes = diagram_data.get("boxes", [])
    containers = diagram_data.get("containers", [])

    box_ids = {b["id"] for b in boxes}
    container_ids = {c["id"] for c in containers}

    box_lookup = []
    for element_id_str, pos in positions.items():
        x_mm = pos.get("x_mm", 0)
        y_mm = pos.get("y_mm", 0)
        w_mm = pos.get("width_mm", 0)
        h_mm = pos.get("height_mm", 0)

        is_container = element_id_str in container_ids
        is_box = element_id_str in box_ids

        # Find title for this element
        title = element_id_str
        if is_box:
            for b in boxes:
                if b["id"] == element_id_str:
                    title = b.get("title", element_id_str)
                    break
        elif is_container:
            for c in containers:
                if c["id"] == element_id_str:
                    title = c.get("title") or element_id_str
                    break

        box_lookup.append(
            {
                "id": element_id_str,
                "title": title,
                "center_x": x_mm,
                "center_y": y_mm,
                "width": w_mm,
                "height": h_mm,
                "is_container": is_container,
            }
        )

    arrow_lookup = []
    for idx, arrow in enumerate(diagram_data.get("arrows", [])):
        arrow_lookup.append(
            {
                "index": idx,
                "source": arrow.get("source", ""),
                "target": arrow.get("target", ""),
                "label": arrow.get("label"),
            }
        )

    return box_lookup, arrow_lookup


def match_patch_to_diagram_box(
    patch: FancyBboxPatch,
    box_lookup: List[Dict[str, Any]],
    tolerance_mm: float = 2.0,
) -> Optional[Dict[str, Any]]:
    """Match a FancyBboxPatch to a diagram box by center position.

    Parameters
    ----------
    patch : FancyBboxPatch
        The matplotlib patch to match.
    box_lookup : list
        Lookup table from build_diagram_lookup.
    tolerance_mm : float
        Position matching tolerance in mm.

    Returns
    -------
    dict or None
        Matched box info, or None if no match.
    """
    # FancyBboxPatch uses get_x()/get_y(), not get_xy() like Rectangle
    px = patch.get_x()
    py = patch.get_y()
    pw = patch.get_width()
    ph = patch.get_height()
    patch_cx = px + pw / 2
    patch_cy = py + ph / 2

    best_match = None
    best_dist = float("inf")

    for box_info in box_lookup:
        dx = patch_cx - box_info["center_x"]
        dy = patch_cy - box_info["center_y"]
        dist = math.hypot(dx, dy)
        if dist < tolerance_mm and dist < best_dist:
            best_dist = dist
            best_match = box_info

    return best_match


def process_diagram_box(
    patch,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    diagram_call_id=None,
    box_lookup=None,
):
    """Process FancyBboxPatch with diagram element matching.

    When diagram_call_id and box_lookup are provided, matches the patch
    to a diagram box by center position and enriches the color_map entry
    with call_id and diagram_element fields for the override system.
    """
    if not patch.get_visible():
        return element_id

    key = f"ax{ax_idx}_dbox{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "facecolor": patch.get_facecolor(),
        "edgecolor": patch.get_edgecolor(),
    }

    patch.set_facecolor(normalize_color(rgb))
    patch.set_edgecolor(normalize_color(rgb))

    # Try to match to a diagram element for override support
    element_type = "diagram_box"
    label = f"box_{i}"
    call_id = None
    diagram_element = None

    if box_lookup is not None:
        matched = match_patch_to_diagram_box(patch, box_lookup)
        if matched:
            call_id = diagram_call_id
            box_id = matched["id"]
            label = matched["title"]
            if matched["is_container"]:
                element_type = "diagram_container"
                diagram_element = f"container:{box_id}"
            else:
                diagram_element = f"box:{box_id}"

    entry = {
        "id": element_id,
        "type": element_type,
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
    }
    if call_id is not None:
        entry["call_id"] = call_id
    if diagram_element is not None:
        entry["diagram_element"] = diagram_element

    color_map[key] = entry
    return element_id + 1


def process_diagram_arrow(
    patch,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    diagram_call_id=None,
    arrow_lookup=None,
    arrow_idx=0,
):
    """Process FancyArrowPatch with diagram element matching.

    When diagram_call_id and arrow_lookup are provided, enriches the
    color_map entry with call_id and diagram_element fields. Arrows are
    matched by index since they are rendered in order.
    """
    if not patch.get_visible():
        return element_id, arrow_idx

    key = f"ax{ax_idx}_darrow{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "edgecolor": patch.get_edgecolor(),
        "facecolor": patch.get_facecolor(),
    }

    patch.set_edgecolor(normalize_color(rgb))
    patch.set_facecolor(normalize_color(rgb))

    # Try to match to a diagram arrow by index
    label = f"arrow_{i}"
    call_id = None
    diagram_element = None

    if arrow_lookup is not None and arrow_idx < len(arrow_lookup):
        arrow_info = arrow_lookup[arrow_idx]
        call_id = diagram_call_id
        src = arrow_info["source"]
        tgt = arrow_info["target"]
        diagram_element = f"arrow:{arrow_idx}"
        arrow_label = arrow_info.get("label")
        label = arrow_label or f"{src}\u2192{tgt}"

    entry = {
        "id": element_id,
        "type": "diagram_arrow",
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_props[key]["edgecolor"]),
    }
    if call_id is not None:
        entry["call_id"] = call_id
    if diagram_element is not None:
        entry["diagram_element"] = diagram_element

    color_map[key] = entry
    return element_id + 1, arrow_idx + 1


__all__ = [
    "build_diagram_lookup",
    "match_patch_to_diagram_box",
    "process_diagram_box",
    "process_diagram_arrow",
]

# EOF
