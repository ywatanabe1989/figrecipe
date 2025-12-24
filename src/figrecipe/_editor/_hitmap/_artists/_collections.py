#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collection processing for hitmap generation."""

from typing import Any, Dict

from matplotlib.collections import (
    LineCollection,
    PathCollection,
    PolyCollection,
)

from .._colors import id_to_rgb, mpl_color_to_hex, normalize_color
from .._detect import is_violin_element


def process_collections(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process collections (scatter, fills, etc.) on an axes.

    Returns updated element_id.
    """
    from matplotlib.collections import QuadMesh
    from matplotlib.contour import QuadContourSet
    from matplotlib.quiver import Quiver

    ax_plot_types = ax_info.get("types", set())
    ax_call_ids = ax_info.get("call_ids", {})
    has_violin = "violinplot" in ax_plot_types
    has_record = len(ax_plot_types) > 0

    violin_ids = list(ax_call_ids.get("violinplot", []))
    scatter_ids = list(ax_call_ids.get("scatter", []))
    quiver_ids = list(ax_call_ids.get("quiver", []))
    fill_between_ids = list(ax_call_ids.get("fill_between", []))
    pcolormesh_ids = list(ax_call_ids.get("pcolormesh", []))
    contour_ids = list(ax_call_ids.get("contour", []))
    contourf_ids = list(ax_call_ids.get("contourf", []))

    violin_call_id = violin_ids[0] if violin_ids else None
    pcolormesh_call_id = pcolormesh_ids[0] if pcolormesh_ids else None
    contour_call_id = contour_ids[0] if contour_ids else None
    contourf_call_id = contourf_ids[0] if contourf_ids else None
    scatter_coll_idx = 0
    fill_coll_idx = 0

    for i, coll in enumerate(ax.collections):
        if isinstance(coll, Quiver):
            element_id = _process_quiver(
                coll, i, ax_idx, element_id, original_props, color_map, quiver_ids
            )
        elif isinstance(coll, PathCollection):
            element_id, scatter_coll_idx = _process_scatter(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                scatter_ids,
                scatter_coll_idx,
            )
        elif isinstance(coll, PolyCollection):
            element_id, fill_coll_idx = _process_polycoll(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
                has_record,
                ax,
                fill_between_ids,
                fill_coll_idx,
            )
        elif isinstance(coll, LineCollection):
            element_id = _process_linecoll(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
            )
        elif isinstance(coll, QuadMesh):
            element_id = _process_quadmesh(
                coll, i, ax_idx, element_id, color_map, pcolormesh_call_id
            )
        elif isinstance(coll, QuadContourSet):
            element_id = _process_contour(
                coll,
                i,
                ax_idx,
                element_id,
                color_map,
                contour_call_id,
                contourf_call_id,
            )

    return element_id


def _process_quiver(coll, i, ax_idx, element_id, original_props, color_map, quiver_ids):
    """Process Quiver collection."""
    if not coll.get_visible():
        return element_id

    key = f"ax{ax_idx}_quiver{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {"color": coll.get_facecolor().copy()}
    coll.set_color(normalize_color(rgb))

    call_id = quiver_ids[0] if quiver_ids else None
    label = call_id or f"quiver_{i}"

    color_map[key] = {
        "id": element_id,
        "type": "quiver",
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "call_id": call_id,
    }
    return element_id + 1


def _process_scatter(
    coll,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    scatter_ids,
    scatter_coll_idx,
):
    """Process PathCollection (scatter)."""
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


def _process_polycoll(
    coll,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    has_violin,
    violin_call_id,
    has_record,
    ax,
    fill_between_ids=None,
    fill_coll_idx=0,
):
    """Process PolyCollection (fills, violin bodies)."""
    if fill_between_ids is None:
        fill_between_ids = []

    if not coll.get_visible():
        return element_id, fill_coll_idx

    orig_label = coll.get_label() or ""

    # Check if this is a fill_between element (should NOT be skipped)
    has_fill_between = len(fill_between_ids) > 0

    if has_record and not has_fill_between:
        # Only skip _child/_nolegend if NOT from fill_between
        if orig_label.startswith("_child") or orig_label.startswith("_nolegend"):
            return element_id, fill_coll_idx

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

    if has_violin and is_violin_element(coll, ax):
        elem_type = "violin"
        label = violin_call_id or "violin"
        call_id = violin_call_id
    else:
        elem_type = "fill"
        # Try to get fill_between call_id
        if fill_coll_idx < len(fill_between_ids):
            call_id = fill_between_ids[fill_coll_idx]
            label = call_id
            fill_coll_idx += 1
        else:
            label = orig_label if not orig_label.startswith("_") else f"fill_{i}"
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
    return element_id + 1, fill_coll_idx


def _process_linecoll(
    coll, i, ax_idx, element_id, original_props, color_map, has_violin, violin_call_id
):
    """Process LineCollection (violin inner lines)."""
    if not coll.get_visible():
        return element_id

    key = f"ax{ax_idx}_linecoll{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "colors": coll.get_colors().copy() if hasattr(coll, "get_colors") else [],
        "edgecolors": coll.get_edgecolors().copy(),
    }

    coll.set_color(normalize_color(rgb))

    orig_colors = original_props[key]["colors"]
    orig_color = orig_colors[0] if len(orig_colors) > 0 else [0.5, 0.5, 0.5, 1]

    if has_violin:
        elem_type = "violin"
        label = violin_call_id or "violin"
        call_id = violin_call_id
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
    return element_id + 1


def _process_quadmesh(coll, i, ax_idx, element_id, color_map, pcolormesh_call_id=None):
    """Process QuadMesh (pcolormesh, hexbin, hist2d)."""
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


def _process_contour(
    coll, i, ax_idx, element_id, color_map, contour_call_id=None, contourf_call_id=None
):
    """Process QuadContourSet (contour, contourf)."""
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


__all__ = ["process_collections"]

# EOF
