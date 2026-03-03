#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contour plot hitmap processing."""

from typing import Any, Dict

from matplotlib.contour import QuadContourSet

from ._base import get_call_ids, id_to_rgb


def process_contour(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process contour plots (contour, contourf).

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
    contour_ids = get_call_ids(ax_info, "contour")
    contourf_ids = get_call_ids(ax_info, "contourf")
    contour_idx = 0

    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, QuadContourSet):
            continue

        key = f"ax{ax_idx}_contour{i}"
        rgb = id_to_rgb(element_id)

        # Try contourf first, then contour
        if contour_idx < len(contourf_ids):
            call_id = contourf_ids[contour_idx]
        elif contour_idx < len(contour_ids):
            call_id = contour_ids[contour_idx]
        else:
            call_id = f"contour_{ax_idx}_{contour_idx}"

        label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "contour",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "call_id": call_id,
        }
        element_id += 1
        contour_idx += 1

    return element_id


__all__ = ["process_contour"]

# EOF
