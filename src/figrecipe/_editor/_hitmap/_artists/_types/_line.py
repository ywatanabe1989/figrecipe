#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Line plot hitmap processing (plot, step, semilogx, semilogy, loglog)."""

from typing import Any, Dict

from ._base import (
    get_call_ids,
    id_to_rgb,
    mpl_color_to_hex,
    normalize_color,
)


def process_line_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process regular line plots (plot, semilogx, semilogy, loglog).

    Parameters
    ----------
    ax : Axes
        Matplotlib axes
    ax_idx : int
        Axes index
    element_id : int
        Starting element ID
    original_props : dict
        Dict to store original properties for restoration
    color_map : dict
        Dict to store element color mappings
    ax_info : dict
        Axes plot type information

    Returns
    -------
    int
        Updated element ID
    """
    plot_ids = get_call_ids(ax_info, "plot")
    has_record = len(ax_info.get("types", set())) > 0

    line_idx = 0
    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue

        orig_label = line.get_label() or ""

        # Skip internal labels unless this is a known plot
        if has_record and orig_label.startswith("_child"):
            continue

        xdata = line.get_xdata()
        if len(xdata) == 0:
            continue

        key = f"ax{ax_idx}_line{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "color": line.get_color(),
            "markerfacecolor": line.get_markerfacecolor(),
            "markeredgecolor": line.get_markeredgecolor(),
        }

        line.set_color(normalize_color(rgb))
        line.set_markerfacecolor(normalize_color(rgb))
        line.set_markeredgecolor(normalize_color(rgb))

        if line_idx < len(plot_ids):
            call_id = plot_ids[line_idx]
            label = call_id
        else:
            call_id = f"line_{ax_idx}_{line_idx}"
            label = orig_label if not orig_label.startswith("_") else call_id

        color_map[key] = {
            "id": element_id,
            "type": "line",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["color"]),
            "call_id": call_id,
        }
        element_id += 1
        line_idx += 1

    return element_id


def process_step_plot(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process step plots.

    Step plots create lines with step-like appearance.

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
    step_ids = get_call_ids(ax_info, "step")
    if not step_ids:
        return element_id

    step_idx = 0
    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue

        orig_label = line.get_label() or ""
        if not orig_label.startswith("_"):
            continue

        xdata = line.get_xdata()
        if len(xdata) == 0:
            continue

        key = f"ax{ax_idx}_step{i}"
        rgb = id_to_rgb(element_id)

        original_props[key] = {
            "color": line.get_color(),
            "markerfacecolor": line.get_markerfacecolor(),
            "markeredgecolor": line.get_markeredgecolor(),
        }

        line.set_color(normalize_color(rgb))
        line.set_markerfacecolor(normalize_color(rgb))
        line.set_markeredgecolor(normalize_color(rgb))

        if step_idx < len(step_ids):
            call_id = step_ids[step_idx]
            label = call_id
        else:
            call_id = f"step_{ax_idx}_{step_idx}"
            label = call_id

        color_map[key] = {
            "id": element_id,
            "type": "step",
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["color"]),
            "call_id": call_id,
        }
        element_id += 1
        step_idx += 1

    return element_id


__all__ = ["process_line_plot", "process_step_plot"]

# EOF
