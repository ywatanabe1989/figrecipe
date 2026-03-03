#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quiver and Barbs collection processing for hitmap generation."""

from typing import Any, Dict

from ..._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def process_quiver(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    quiver_ids: list,
) -> int:
    """Process Quiver collection.

    Parameters
    ----------
    coll : Quiver
        The quiver collection to process.
    i : int
        Collection index.
    ax_idx : int
        Axes index.
    element_id : int
        Current element ID.
    original_props : dict
        Dict to store original properties.
    color_map : dict
        Dict to store element color mappings.
    quiver_ids : list
        List of quiver call IDs.

    Returns
    -------
    int
        Updated element ID.
    """
    if not coll.get_visible():
        return element_id

    key = f"ax{ax_idx}_quiver{i}"
    rgb = id_to_rgb(element_id)

    orig_color = coll.get_facecolor().copy()
    original_props[key] = {"color": orig_color}
    coll.set_color(normalize_color(rgb))

    call_id = quiver_ids[0] if quiver_ids else None
    label = call_id or f"quiver_{i}"

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
    return element_id + 1


def process_barbs(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    barbs_ids: list,
) -> int:
    """Process Barbs collection.

    Parameters
    ----------
    coll : Barbs
        The barbs collection to process.
    i : int
        Collection index.
    ax_idx : int
        Axes index.
    element_id : int
        Current element ID.
    original_props : dict
        Dict to store original properties.
    color_map : dict
        Dict to store element color mappings.
    barbs_ids : list
        List of barbs call IDs.

    Returns
    -------
    int
        Updated element ID.
    """
    if not coll.get_visible():
        return element_id

    key = f"ax{ax_idx}_barbs{i}"
    rgb = id_to_rgb(element_id)

    orig_color = coll.get_facecolor().copy()
    original_props[key] = {"color": orig_color}
    coll.set_color(normalize_color(rgb))

    call_id = barbs_ids[0] if barbs_ids else None
    label = call_id or f"barbs_{i}"

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
    return element_id + 1


__all__ = ["process_quiver", "process_barbs"]

# EOF
