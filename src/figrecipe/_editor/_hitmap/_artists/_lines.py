#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Line processing for hitmap generation."""

from typing import Any, Dict

from .._colors import id_to_rgb, mpl_color_to_hex, normalize_color
from .._detect import is_boxplot_element


def process_lines(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process lines (traces) on an axes.

    Returns updated element_id.
    """
    ax_plot_types = ax_info.get("types", set())
    ax_call_ids = ax_info.get("call_ids", {})
    has_boxplot = "boxplot" in ax_plot_types
    has_violin = "violinplot" in ax_plot_types
    has_regular_plot = "plot" in ax_plot_types

    boxplot_ids = list(ax_call_ids.get("boxplot", []))
    violin_ids = list(ax_call_ids.get("violinplot", []))
    plot_ids = list(ax_call_ids.get("plot", []))

    boxplot_call_id = boxplot_ids[0] if boxplot_ids else None
    violin_call_id = violin_ids[0] if violin_ids else None
    regular_line_idx = 0
    has_record = len(ax_plot_types) > 0

    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue

        orig_label = line.get_label() or ""

        if has_record:
            if (
                orig_label.startswith("_child")
                and not has_boxplot
                and not has_violin
                and not has_regular_plot
            ):
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

        call_id = None
        if has_boxplot and (is_boxplot_element(line, ax) or orig_label.startswith("_")):
            elem_type = "boxplot"
            label = boxplot_call_id or "boxplot"
            call_id = boxplot_call_id
        elif has_violin and orig_label.startswith("_"):
            elem_type = "violin"
            label = violin_call_id or "violin"
            call_id = violin_call_id
        else:
            elem_type = "line"
            label = orig_label if orig_label else f"line_{i}"
            if regular_line_idx < len(plot_ids):
                call_id = plot_ids[regular_line_idx]
                label = call_id
            else:
                call_id = f"line_{ax_idx}_{regular_line_idx}"
                if orig_label.startswith("_"):
                    label = call_id
            regular_line_idx += 1

        color_map[key] = {
            "id": element_id,
            "type": elem_type,
            "label": label,
            "ax_index": ax_idx,
            "rgb": list(rgb),
            "original_color": mpl_color_to_hex(original_props[key]["color"]),
            "call_id": call_id,
        }
        element_id += 1

    return element_id


__all__ = ["process_lines"]

# EOF
