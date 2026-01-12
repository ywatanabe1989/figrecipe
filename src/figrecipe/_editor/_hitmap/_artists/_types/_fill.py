#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill-based plot hitmap processing (fill_between, fill_betweenx, stackplot, stairs)."""

from typing import Any, Dict

from matplotlib.collections import PolyCollection

from ._base import (
    get_call_ids,
    id_to_rgb,
    mpl_color_to_hex,
    normalize_color,
)


def process_fill_between(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process fill_between plots.

    fill_between creates PolyCollection objects.

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
    fill_ids = get_call_ids(ax_info, "fill_between")
    if not fill_ids:
        return element_id

    fill_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PolyCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_fill_between{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        if fill_idx < len(fill_ids):
            call_id = fill_ids[fill_idx]
            label = call_id
        else:
            call_id = f"fill_between_{ax_idx}_{fill_idx}"
            label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "fill",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        fill_idx += 1

    return element_id


def process_fill_betweenx(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process fill_betweenx plots (horizontal fill).

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
    fill_ids = get_call_ids(ax_info, "fill_betweenx")
    if not fill_ids:
        return element_id

    fill_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PolyCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_fill_betweenx{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        if fill_idx < len(fill_ids):
            call_id = fill_ids[fill_idx]
            label = call_id
        else:
            call_id = f"fill_betweenx_{ax_idx}_{fill_idx}"
            label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "fill",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        fill_idx += 1

    return element_id


def process_stackplot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process stackplot (stacked area plots).

    stackplot creates multiple PolyCollection objects.

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
    stackplot_ids = get_call_ids(ax_info, "stackplot")
    if not stackplot_ids:
        return element_id

    stack_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PolyCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_stackplot{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        call_id = stackplot_ids[0] if stackplot_ids else None
        label = f"stackplot_layer_{stack_idx}"
        if call_id:
            label = f"{call_id}_layer{stack_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "stackplot",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
            "layer_index": stack_idx,  # For individual layer color editing
        }
        element_id += 1
        stack_idx += 1

    return element_id


def process_stairs(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process stairs plots.

    stairs creates step-like filled areas using PolyCollection.

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
    stairs_ids = get_call_ids(ax_info, "stairs")
    if not stairs_ids:
        return element_id

    stairs_idx = 0
    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, PolyCollection):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_stairs{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolors": coll.get_facecolors().copy(),
            "edgecolors": coll.get_edgecolors().copy(),
        }

        coll.set_facecolors([normalize_color(rgb)])
        coll.set_edgecolors([normalize_color(rgb)])

        orig_fc = original_props[key]["facecolors"]
        orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

        if stairs_idx < len(stairs_ids):
            call_id = stairs_ids[stairs_idx]
            label = call_id
        else:
            call_id = f"stairs_{ax_idx}_{stairs_idx}"
            label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "stairs",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(orig_color),
            "call_id": call_id,
        }
        element_id += 1
        stairs_idx += 1

    return element_id


__all__ = [
    "process_fill_between",
    "process_fill_betweenx",
    "process_stackplot",
    "process_stairs",
]

# EOF
