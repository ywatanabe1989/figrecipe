#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PolyCollection processing for hitmap generation."""

from typing import Any, Dict, Tuple

from ..._colors import id_to_rgb, mpl_color_to_hex, normalize_color
from ..._detect import is_violin_element


def determine_fill_type(
    has_fill_between: bool,
    has_fill_betweenx: bool,
    has_stackplot: bool,
    has_stairs: bool,
    has_violin: bool,
    has_hexbin: bool,
    has_pcolor: bool,
    has_tripcolor: bool,
    fill_between_ids: list,
    fill_betweenx_ids: list,
    stackplot_ids: list,
    stairs_ids: list,
    hexbin_ids: list,
    pcolor_ids: list,
    tripcolor_ids: list,
    fill_between_idx: int,
    fill_betweenx_idx: int,
    stackplot_idx: int,
    stairs_idx: int,
) -> Dict[str, Any]:
    """Determine which fill type a PolyCollection belongs to.

    Returns
    -------
    dict
        Fill type info with 'type', 'call_id', and 'elem_type'.
    """
    # Priority: fill_between > fill_betweenx > stackplot > stairs > hexbin > pcolor
    # Check which type still has remaining IDs to assign
    if has_fill_between and fill_between_idx < len(fill_between_ids):
        return {
            "type": "fill_between",
            "call_id": fill_between_ids[fill_between_idx],
            "elem_type": "fill",
        }
    if has_fill_betweenx and fill_betweenx_idx < len(fill_betweenx_ids):
        return {
            "type": "fill_betweenx",
            "call_id": fill_betweenx_ids[fill_betweenx_idx],
            "elem_type": "fill",
        }
    # stackplot creates multiple PolyCollections - one call_id for all layers
    if has_stackplot and stackplot_ids:
        return {
            "type": "stackplot",
            "call_id": stackplot_ids[0],
            "elem_type": "stackplot",
        }
    if has_stairs and stairs_idx < len(stairs_ids):
        return {
            "type": "stairs",
            "call_id": stairs_ids[stairs_idx],
            "elem_type": "stairs",
        }
    if has_hexbin and hexbin_ids:
        return {
            "type": "hexbin",
            "call_id": hexbin_ids[0],
            "elem_type": "hexbin",
        }
    if has_pcolor and pcolor_ids:
        return {
            "type": "pcolor",
            "call_id": pcolor_ids[0],
            "elem_type": "pcolor",
        }
    if has_tripcolor and tripcolor_ids:
        return {
            "type": "tripcolor",
            "call_id": tripcolor_ids[0],
            "elem_type": "tripcolor",
        }
    if has_violin:
        return {"type": "violin", "call_id": None, "elem_type": "violin"}
    return {"type": "fill", "call_id": None, "elem_type": "fill"}


def process_polycoll(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    has_violin: bool,
    violin_call_id: str,
    has_record: bool,
    has_any_fill: bool,
    ax,
    fill_info: Dict[str, Any],
    fill_between_idx: int,
    fill_betweenx_idx: int,
    stackplot_idx: int,
    stairs_idx: int,
    violin_idx: int = 0,
) -> Tuple[int, int, int, int, int, int]:
    """Process PolyCollection with proper fill type detection.

    Parameters
    ----------
    coll : PolyCollection
        The collection to process.
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
    has_violin : bool
        Whether violin plot is detected.
    violin_call_id : str
        Violin plot call ID.
    has_record : bool
        Whether plot types are recorded.
    has_any_fill : bool
        Whether any fill type is detected.
    ax : Axes
        The axes containing the collection.
    fill_info : dict
        Fill type information.
    fill_between_idx : int
        Current fill_between index.
    fill_betweenx_idx : int
        Current fill_betweenx index.
    stackplot_idx : int
        Current stackplot layer index.
    stairs_idx : int
        Current stairs index.
    violin_idx : int
        Current violin body index.

    Returns
    -------
    tuple
        (element_id, fill_between_idx, fill_betweenx_idx, stackplot_idx,
         stairs_idx, violin_idx)
    """
    if not coll.get_visible():
        return (
            element_id,
            fill_between_idx,
            fill_betweenx_idx,
            stackplot_idx,
            stairs_idx,
            violin_idx,
        )

    orig_label = coll.get_label() or ""

    # Skip internal labels only if no fill type detected
    if has_record and not has_any_fill and not has_violin:
        if orig_label.startswith("_child") or orig_label.startswith("_nolegend"):
            return (
                element_id,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
                violin_idx,
            )

    key = f"ax{ax_idx}_fill{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "facecolors": coll.get_facecolors().copy(),
        "edgecolors": coll.get_edgecolors().copy(),
    }

    coll.set_facecolors([normalize_color(rgb)])
    coll.set_edgecolors([normalize_color(rgb)])

    orig_fc = original_props[key]["facecolors"]
    orig_color = orig_fc[0] if len(orig_fc) > 0 else [0.5, 0.5, 0.5, 1]

    # Use fill_info to determine type and call_id
    fill_type = fill_info.get("type", "fill")
    elem_type = fill_info.get("elem_type", "fill")
    call_id = fill_info.get("call_id")

    layer_index = None
    if has_violin and is_violin_element(coll, ax):
        elem_type = "violin"
        label = (
            f"{violin_call_id}_body{violin_idx}"
            if violin_call_id
            else f"violin_body{violin_idx}"
        )
        call_id = violin_call_id
        violin_idx += 1
    elif call_id:
        # Increment the appropriate index and set layer_index for multi-layer types
        if fill_type == "fill_between":
            fill_between_idx += 1
            label = call_id
        elif fill_type == "fill_betweenx":
            fill_betweenx_idx += 1
            label = call_id
        elif fill_type == "stackplot":
            # For stackplot, include layer index in label for uniqueness
            layer_index = stackplot_idx
            label = f"{call_id}_layer{layer_index}"
            stackplot_idx += 1
        elif fill_type == "stairs":
            stairs_idx += 1
            label = call_id
        else:
            label = call_id
    else:
        label = orig_label if not orig_label.startswith("_") else f"fill_{i}"

    color_map[key] = {
        "id": element_id,
        "type": elem_type,
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(orig_color),
        "call_id": call_id,
    }

    # Add layer_index for multi-layer elements (stackplot, etc.)
    if layer_index is not None:
        color_map[key]["layer_index"] = layer_index

    return (
        element_id + 1,
        fill_between_idx,
        fill_betweenx_idx,
        stackplot_idx,
        stairs_idx,
        violin_idx,
    )


__all__ = ["determine_fill_type", "process_polycoll"]

# EOF
