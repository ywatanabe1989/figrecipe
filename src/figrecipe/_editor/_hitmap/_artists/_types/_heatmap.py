#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heatmap and mesh plot hitmap processing (pcolormesh, imshow, hexbin)."""

from typing import Any, Dict

from matplotlib.collections import QuadMesh
from matplotlib.image import AxesImage

from ._base import get_call_ids, id_to_rgb


def process_pcolormesh(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process pcolormesh plots.

    pcolormesh creates QuadMesh objects.

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
    pcolormesh_ids = get_call_ids(ax_info, "pcolormesh")
    mesh_idx = 0

    for i, coll in enumerate(ax.collections):
        if not isinstance(coll, QuadMesh):
            continue
        if not coll.get_visible():
            continue

        key = f"ax{ax_idx}_quadmesh{i}"
        rgb = id_to_rgb(element_id)

        if mesh_idx < len(pcolormesh_ids):
            call_id = pcolormesh_ids[mesh_idx]
            label = call_id
        else:
            call_id = f"pcolormesh_{ax_idx}_{mesh_idx}"
            label = call_id

        # QuadMesh doesn't easily support solid color override
        # Just register in color_map for detection
        color_map[key] = {
            "id": element_id,
            "type": "quadmesh",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "call_id": call_id,
        }
        element_id += 1
        mesh_idx += 1

    return element_id


def process_imshow(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process imshow (image display).

    imshow creates AxesImage objects.

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
    imshow_ids = get_call_ids(ax_info, "imshow")
    img_idx = 0

    for i, img in enumerate(ax.images):
        if not isinstance(img, AxesImage):
            continue
        if not img.get_visible():
            continue

        key = f"ax{ax_idx}_image{i}"
        rgb = id_to_rgb(element_id)

        if img_idx < len(imshow_ids):
            call_id = imshow_ids[img_idx]
            label = call_id
        else:
            call_id = f"imshow_{ax_idx}_{img_idx}"
            label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "image",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "call_id": call_id,
        }
        element_id += 1
        img_idx += 1

    return element_id


__all__ = ["process_pcolormesh", "process_imshow"]

# EOF
