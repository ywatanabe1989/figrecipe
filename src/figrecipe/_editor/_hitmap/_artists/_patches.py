#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch processing for hitmap generation."""

from typing import Any, Dict

from matplotlib.patches import Polygon, Rectangle, Wedge

from .._colors import id_to_rgb, mpl_color_to_hex, normalize_color


def process_patches(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process patches (bars, wedges, polygons) on an axes.

    Returns updated element_id.
    """
    ax_plot_types = ax_info.get("types", set())
    ax_call_ids = ax_info.get("call_ids", {})

    has_hist = "hist" in ax_plot_types
    has_bar = "bar" in ax_plot_types

    hist_ids = list(ax_call_ids.get("hist", []))
    bar_ids = list(ax_call_ids.get("bar", []))
    pie_ids = list(ax_call_ids.get("pie", []))

    if has_hist and hist_ids:
        rect_call_id = hist_ids[0]
        rect_type = "hist"
    elif has_bar and bar_ids:
        rect_call_id = bar_ids[0]
        rect_type = "bar"
    else:
        rect_call_id = f"bar_{ax_idx}"
        rect_type = "bar"

    for i, patch in enumerate(ax.patches):
        if isinstance(patch, Rectangle):
            element_id = _process_rectangle(
                patch,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                rect_call_id,
                rect_type,
            )
        elif isinstance(patch, Wedge):
            element_id = _process_wedge(
                patch, i, ax_idx, element_id, original_props, color_map, pie_ids
            )
        elif isinstance(patch, Polygon):
            element_id = _process_polygon(
                patch, i, ax_idx, element_id, original_props, color_map
            )

    return element_id


def _process_rectangle(
    patch, i, ax_idx, element_id, original_props, color_map, rect_call_id, rect_type
):
    """Process Rectangle patch (bars, histogram bins)."""
    if not patch.get_visible():
        return element_id
    if patch.get_width() == 1.0 and patch.get_height() == 1.0:
        return element_id

    key = f"ax{ax_idx}_bar{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "facecolor": patch.get_facecolor(),
        "edgecolor": patch.get_edgecolor(),
    }

    patch.set_facecolor(normalize_color(rgb))
    patch.set_edgecolor(normalize_color(rgb))

    label = rect_call_id or patch.get_label() or f"bar_{i}"

    color_map[key] = {
        "id": element_id,
        "type": rect_type,
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
        "call_id": rect_call_id,
    }
    return element_id + 1


def _process_wedge(patch, i, ax_idx, element_id, original_props, color_map, pie_ids):
    """Process Wedge patch (pie chart slices)."""
    if not patch.get_visible():
        return element_id

    key = f"ax{ax_idx}_wedge{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "facecolor": patch.get_facecolor(),
        "edgecolor": patch.get_edgecolor(),
    }

    patch.set_facecolor(normalize_color(rgb))
    patch.set_edgecolor(normalize_color(rgb))

    call_id = pie_ids[0] if pie_ids else None
    label = call_id or f"wedge_{i}"

    color_map[key] = {
        "id": element_id,
        "type": "pie",
        "label": label,
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
        "call_id": call_id,
    }
    return element_id + 1


def _process_polygon(patch, i, ax_idx, element_id, original_props, color_map):
    """Process Polygon patch (fill areas)."""
    if not patch.get_visible():
        return element_id

    key = f"ax{ax_idx}_polygon{i}"
    rgb = id_to_rgb(element_id)

    original_props[key] = {
        "facecolor": patch.get_facecolor(),
        "edgecolor": patch.get_edgecolor(),
    }

    patch.set_facecolor(normalize_color(rgb))
    patch.set_edgecolor(normalize_color(rgb))

    color_map[key] = {
        "id": element_id,
        "type": "fill",
        "label": f"fill_{i}",
        "ax_index": ax_idx,
        "rgb": list(rgb),
        "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
        "call_id": None,
    }
    return element_id + 1


__all__ = ["process_patches"]

# EOF
