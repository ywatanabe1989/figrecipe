#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QuadMesh and Contour collection processing for hitmap generation."""

from typing import Any, Dict

from ..._colors import id_to_rgb


def process_quadmesh(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    color_map: Dict[str, Any],
    pcolormesh_call_id: str = None,
) -> int:
    """Process QuadMesh (pcolormesh, hexbin, hist2d).

    Parameters
    ----------
    coll : QuadMesh
        The QuadMesh to process.
    i : int
        Collection index.
    ax_idx : int
        Axes index.
    element_id : int
        Current element ID.
    color_map : dict
        Dict to store element color mappings.
    pcolormesh_call_id : str, optional
        Call ID for pcolormesh.

    Returns
    -------
    int
        Updated element ID.
    """
    if not coll.get_visible():
        return element_id

    key = f"ax{ax_idx}_quadmesh{i}"
    rgb = id_to_rgb(element_id)

    call_id = pcolormesh_call_id
    label = call_id or f"quadmesh_{i}"

    color_map[key] = {
        "id": element_id,
        "type": "quadmesh",
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "call_id": call_id,
    }
    return element_id + 1


def process_contour(
    coll,
    i: int,
    ax_idx: int,
    element_id: int,
    color_map: Dict[str, Any],
    contour_call_id: str = None,
    contourf_call_id: str = None,
) -> int:
    """Process QuadContourSet (contour, contourf).

    Parameters
    ----------
    coll : QuadContourSet
        The contour set to process.
    i : int
        Collection index.
    ax_idx : int
        Axes index.
    element_id : int
        Current element ID.
    color_map : dict
        Dict to store element color mappings.
    contour_call_id : str, optional
        Call ID for contour.
    contourf_call_id : str, optional
        Call ID for contourf.

    Returns
    -------
    int
        Updated element ID.
    """
    key = f"ax{ax_idx}_contour{i}"
    rgb = id_to_rgb(element_id)

    # Try contourf first, then contour
    call_id = contourf_call_id or contour_call_id
    label = call_id or f"contour_{i}"

    color_map[key] = {
        "id": element_id,
        "type": "contour",
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "call_id": call_id,
    }
    return element_id + 1


__all__ = ["process_quadmesh", "process_contour"]

# EOF
