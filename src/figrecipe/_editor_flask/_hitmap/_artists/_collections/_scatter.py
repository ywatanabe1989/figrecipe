#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scatter collection processing for hitmap generation."""

from typing import Any, Dict, Tuple

from ..._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def process_scatter(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    scatter_ids: list,
    scatter_coll_idx: int,
) -> Tuple[int, int]:
    """Process PathCollection (scatter).

    Parameters
    ----------
    coll : PathCollection
        The scatter collection to process.
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
    scatter_ids : list
        List of scatter call IDs.
    scatter_coll_idx : int
        Current scatter collection index.

    Returns
    -------
    tuple
        (updated element_id, updated scatter_coll_idx)
    """
    if not coll.get_visible():
        return element_id, scatter_coll_idx

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
    if scatter_coll_idx < len(scatter_ids):
        call_id = scatter_ids[scatter_coll_idx]
        label = call_id
    else:
        call_id = f"scatter_{ax_idx}_{scatter_coll_idx}"
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
    return element_id + 1, scatter_coll_idx + 1


__all__ = ["process_scatter"]

# EOF
