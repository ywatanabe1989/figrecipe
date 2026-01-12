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
    from matplotlib.quiver import Barbs, Quiver

    ax_plot_types = ax_info.get("types", set())
    ax_call_ids = ax_info.get("call_ids", {})
    has_violin = "violinplot" in ax_plot_types
    has_record = len(ax_plot_types) > 0

    # Check for specific fill types
    has_fill_between = "fill_between" in ax_plot_types
    has_fill_betweenx = "fill_betweenx" in ax_plot_types
    has_stackplot = "stackplot" in ax_plot_types
    has_stairs = "stairs" in ax_plot_types
    has_errorbar = "errorbar" in ax_plot_types
    has_stem = "stem" in ax_plot_types
    has_eventplot = "eventplot" in ax_plot_types

    # Any fill-type present means we should process PolyCollections
    has_any_fill = has_fill_between or has_fill_betweenx or has_stackplot or has_stairs

    violin_ids = list(ax_call_ids.get("violinplot", []))
    scatter_ids = list(ax_call_ids.get("scatter", []))
    quiver_ids = list(ax_call_ids.get("quiver", []))
    barbs_ids = list(ax_call_ids.get("barbs", []))
    fill_between_ids = list(ax_call_ids.get("fill_between", []))
    fill_betweenx_ids = list(ax_call_ids.get("fill_betweenx", []))
    stackplot_ids = list(ax_call_ids.get("stackplot", []))
    stairs_ids = list(ax_call_ids.get("stairs", []))
    errorbar_ids = list(ax_call_ids.get("errorbar", []))
    stem_ids = list(ax_call_ids.get("stem", []))
    eventplot_ids = list(ax_call_ids.get("eventplot", []))
    pcolormesh_ids = list(ax_call_ids.get("pcolormesh", []))
    contour_ids = list(ax_call_ids.get("contour", []))
    contourf_ids = list(ax_call_ids.get("contourf", []))

    violin_call_id = violin_ids[0] if violin_ids else None
    pcolormesh_call_id = pcolormesh_ids[0] if pcolormesh_ids else None
    contour_call_id = contour_ids[0] if contour_ids else None
    contourf_call_id = contourf_ids[0] if contourf_ids else None
    scatter_coll_idx = 0

    # Separate indices for each fill type
    fill_between_idx = 0
    fill_betweenx_idx = 0
    stackplot_idx = 0
    stairs_idx = 0
    linecoll_idx = 0

    for i, coll in enumerate(ax.collections):
        if isinstance(coll, Quiver):
            element_id = _process_quiver(
                coll, i, ax_idx, element_id, original_props, color_map, quiver_ids
            )
        elif isinstance(coll, Barbs):
            element_id = _process_barbs(
                coll, i, ax_idx, element_id, original_props, color_map, barbs_ids
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
            # Determine which fill type this belongs to based on detected types
            fill_info = _determine_fill_type(
                has_fill_between,
                has_fill_betweenx,
                has_stackplot,
                has_stairs,
                has_violin,
                fill_between_ids,
                fill_betweenx_ids,
                stackplot_ids,
                stairs_ids,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
            )
            (
                element_id,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
            ) = _process_polycoll_v2(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
                has_record,
                has_any_fill,
                ax,
                fill_info,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
            )
        elif isinstance(coll, LineCollection):
            element_id, linecoll_idx = _process_linecoll_v2(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
                has_errorbar,
                errorbar_ids,
                has_stem,
                stem_ids,
                has_eventplot,
                eventplot_ids,
                linecoll_idx,
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


def _determine_fill_type(
    has_fill_between,
    has_fill_betweenx,
    has_stackplot,
    has_stairs,
    has_violin,
    fill_between_ids,
    fill_betweenx_ids,
    stackplot_ids,
    stairs_ids,
    fill_between_idx,
    fill_betweenx_idx,
    stackplot_idx,
    stairs_idx,
):
    """Determine which fill type a PolyCollection belongs to."""
    # Priority: fill_between > fill_betweenx > stackplot > stairs
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
    if has_violin:
        return {"type": "violin", "call_id": None, "elem_type": "violin"}
    return {"type": "fill", "call_id": None, "elem_type": "fill"}


def _process_quiver(coll, i, ax_idx, element_id, original_props, color_map, quiver_ids):
    """Process Quiver collection."""
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


def _process_barbs(coll, i, ax_idx, element_id, original_props, color_map, barbs_ids):
    """Process Barbs collection."""
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


def _process_polycoll_v2(
    coll,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    has_violin,
    violin_call_id,
    has_record,
    has_any_fill,
    ax,
    fill_info,
    fill_between_idx,
    fill_betweenx_idx,
    stackplot_idx,
    stairs_idx,
):
    """Process PolyCollection with proper fill type detection."""
    if not coll.get_visible():
        return (
            element_id,
            fill_between_idx,
            fill_betweenx_idx,
            stackplot_idx,
            stairs_idx,
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

    if has_violin and is_violin_element(coll, ax):
        elem_type = "violin"
        label = violin_call_id or "violin"
        call_id = violin_call_id
    elif call_id:
        label = call_id
        # Increment the appropriate index
        if fill_type == "fill_between":
            fill_between_idx += 1
        elif fill_type == "fill_betweenx":
            fill_betweenx_idx += 1
        elif fill_type == "stackplot":
            stackplot_idx += 1
        elif fill_type == "stairs":
            stairs_idx += 1
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
    if fill_type == "stackplot":
        color_map[key]["layer_index"] = (
            stackplot_idx - 1
        )  # -1 because we already incremented

    return (
        element_id + 1,
        fill_between_idx,
        fill_betweenx_idx,
        stackplot_idx,
        stairs_idx,
    )


def _process_linecoll_v2(
    coll,
    i,
    ax_idx,
    element_id,
    original_props,
    color_map,
    has_violin,
    violin_call_id,
    has_errorbar,
    errorbar_ids,
    has_stem,
    stem_ids,
    has_eventplot,
    eventplot_ids,
    linecoll_idx,
):
    """Process LineCollection with proper type detection."""
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


__all__ = ["process_collections"]

# EOF
