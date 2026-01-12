#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bar-based plot hitmap processing (bar, barh, hist)."""

from typing import Any, Dict

from matplotlib.patches import Rectangle

from ._base import (
    get_call_ids,
    id_to_rgb,
    mpl_color_to_hex,
    normalize_color,
)


def process_bar_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process bar plots (bar, barh).

    Bar plots use Rectangle patches.

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
    bar_ids = get_call_ids(ax_info, "bar")
    barh_ids = get_call_ids(ax_info, "barh")
    all_bar_ids = bar_ids + barh_ids

    if not all_bar_ids:
        return element_id

    bar_idx = 0
    for i, patch in enumerate(ax.patches):
        if not isinstance(patch, Rectangle):
            continue
        if not patch.get_visible():
            continue
        # Skip default background rectangle
        if patch.get_width() == 1.0 and patch.get_height() == 1.0:
            continue

        key = f"ax{ax_idx}_bar{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolor": patch.get_facecolor(),
            "edgecolor": patch.get_edgecolor(),
        }

        patch.set_facecolor(normalize_color(rgb))
        patch.set_edgecolor(normalize_color(rgb))

        if bar_idx < len(all_bar_ids):
            call_id = all_bar_ids[0]  # Use first call_id for all bars in same call
            label = call_id
        else:
            call_id = f"bar_{ax_idx}_{bar_idx}"
            label = patch.get_label() or call_id

        color_map[key] = {
            "id": element_id,
            "type": "bar",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
            "call_id": call_id,
        }
        element_id += 1
        bar_idx += 1

    return element_id


def process_histogram(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process histogram plots.

    Histograms use Rectangle patches similar to bar plots.

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
    hist_ids = get_call_ids(ax_info, "hist")
    if not hist_ids:
        return element_id

    hist_idx = 0
    for i, patch in enumerate(ax.patches):
        if not isinstance(patch, Rectangle):
            continue
        if not patch.get_visible():
            continue
        # Skip default background rectangle
        if patch.get_width() == 1.0 and patch.get_height() == 1.0:
            continue

        key = f"ax{ax_idx}_hist{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "facecolor": patch.get_facecolor(),
            "edgecolor": patch.get_edgecolor(),
        }

        patch.set_facecolor(normalize_color(rgb))
        patch.set_edgecolor(normalize_color(rgb))

        call_id = hist_ids[0] if hist_ids else None
        label = call_id or f"hist_bin_{hist_idx}"

        color_map[key] = {
            "id": element_id,
            "type": "hist",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["facecolor"]),
            "call_id": call_id,
        }
        element_id += 1
        hist_idx += 1

    return element_id


__all__ = ["process_bar_plot", "process_histogram"]

# EOF
