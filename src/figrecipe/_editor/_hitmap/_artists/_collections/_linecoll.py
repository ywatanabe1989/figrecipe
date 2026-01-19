#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LineCollection processing for hitmap generation."""

from typing import Any, Dict, Tuple

from ..._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def process_linecoll(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    has_violin: bool,
    violin_call_id: str,
    has_errorbar: bool,
    errorbar_ids: list,
    has_stem: bool,
    stem_ids: list,
    has_eventplot: bool,
    eventplot_ids: list,
    linecoll_idx: int,
) -> Tuple[int, int]:
    """Process LineCollection with proper type detection.

    Parameters
    ----------
    coll : LineCollection
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
    has_errorbar : bool
        Whether errorbar is detected.
    errorbar_ids : list
        List of errorbar call IDs.
    has_stem : bool
        Whether stem plot is detected.
    stem_ids : list
        List of stem call IDs.
    has_eventplot : bool
        Whether eventplot is detected.
    eventplot_ids : list
        List of eventplot call IDs.
    linecoll_idx : int
        Current line collection index.

    Returns
    -------
    tuple
        (updated element_id, updated linecoll_idx)
    """
    if not coll.get_visible():
        return element_id, linecoll_idx

    key = f"ax{ax_idx}_linecoll{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "colors": coll.get_colors().copy() if hasattr(coll, "get_colors") else [],
        "edgecolors": coll.get_edgecolors().copy(),
    }

    coll.set_color(normalize_color(rgb))

    orig_colors = original_props[key]["colors"]
    orig_color = orig_colors[0] if len(orig_colors) > 0 else [0.5, 0.5, 0.5, 1]

    # Determine element type based on detected plot types
    if has_violin:
        elem_type = "violin"
        label = violin_call_id or "violin"
        call_id = violin_call_id
    elif has_errorbar and errorbar_ids:
        elem_type = "errorbar"
        call_id = errorbar_ids[0]
        label = call_id
    elif has_stem and stem_ids:
        elem_type = "stem"
        call_id = stem_ids[0]
        label = call_id
    elif has_eventplot and eventplot_ids:
        elem_type = "eventplot"
        call_id = eventplot_ids[0]
        label = f"{call_id}_ch{linecoll_idx}"
    else:
        elem_type = "linecollection"
        label = f"linecoll_{i}"
        call_id = None

    color_map[key] = {
        "id": element_id,
        "type": elem_type,
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(orig_color),
        "call_id": call_id,
    }
    return element_id + 1, linecoll_idx + 1


__all__ = ["process_linecoll"]

# EOF
