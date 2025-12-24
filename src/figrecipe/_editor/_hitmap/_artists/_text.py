#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text and legend processing for hitmap generation."""

from typing import Any, Dict

from .._colors import id_to_rgb, normalize_color


def process_text(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
) -> int:
    """Process text elements (title, labels) on an axes.

    Returns updated element_id.
    """
    # Title
    title = ax.get_title()
    if title:
        key = f"ax{ax_idx}_title"
        rgb = id_to_rgb(element_id)
        title_obj = ax.title

        original_props[key] = {"color": title_obj.get_color()}
        title_obj.set_color(normalize_color(rgb))

        color_map[key] = {
            "id": element_id,
            "type": "title",
            "label": "title",
            "ax_index": ax_idx,
            "rgb": list(rgb),
        }
        element_id += 1

    # X label
    xlabel = ax.get_xlabel()
    if xlabel:
        key = f"ax{ax_idx}_xlabel"
        rgb = id_to_rgb(element_id)
        xlabel_obj = ax.xaxis.label

        original_props[key] = {"color": xlabel_obj.get_color()}
        xlabel_obj.set_color(normalize_color(rgb))

        color_map[key] = {
            "id": element_id,
            "type": "xlabel",
            "label": "xlabel",
            "ax_index": ax_idx,
            "rgb": list(rgb),
        }
        element_id += 1

    # Y label
    ylabel = ax.get_ylabel()
    if ylabel:
        key = f"ax{ax_idx}_ylabel"
        rgb = id_to_rgb(element_id)
        ylabel_obj = ax.yaxis.label

        original_props[key] = {"color": ylabel_obj.get_color()}
        ylabel_obj.set_color(normalize_color(rgb))

        color_map[key] = {
            "id": element_id,
            "type": "ylabel",
            "label": "ylabel",
            "ax_index": ax_idx,
            "rgb": list(rgb),
        }
        element_id += 1

    return element_id


def process_legend(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
) -> int:
    """Process legend on an axes.

    Returns updated element_id.
    """
    legend = ax.get_legend()
    if legend is not None and legend.get_visible():
        key = f"ax{ax_idx}_legend"
        rgb = id_to_rgb(element_id)

        frame = legend.get_frame()
        original_props[key] = {
            "facecolor": frame.get_facecolor(),
            "edgecolor": frame.get_edgecolor(),
        }

        frame.set_facecolor(normalize_color(rgb))
        frame.set_edgecolor(normalize_color(rgb))

        color_map[key] = {
            "id": element_id,
            "type": "legend",
            "label": "legend",
            "ax_index": ax_idx,
            "rgb": list(rgb),
        }
        element_id += 1

    return element_id


def process_figure_text(
    mpl_fig,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
) -> int:
    """Process figure-level text elements (suptitle, supxlabel, supylabel).

    Returns updated element_id.
    """
    # Suptitle
    if hasattr(mpl_fig, "_suptitle") and mpl_fig._suptitle is not None:
        suptitle_obj = mpl_fig._suptitle
        if suptitle_obj.get_text():
            key = "fig_suptitle"
            rgb = id_to_rgb(element_id)

            original_props[key] = {"color": suptitle_obj.get_color()}
            suptitle_obj.set_color(normalize_color(rgb))

            color_map[key] = {
                "id": element_id,
                "type": "suptitle",
                "label": "suptitle",
                "ax_index": -1,
                "rgb": list(rgb),
            }
            element_id += 1

    # Supxlabel
    if hasattr(mpl_fig, "_supxlabel") and mpl_fig._supxlabel is not None:
        supxlabel_obj = mpl_fig._supxlabel
        if supxlabel_obj.get_text():
            key = "fig_supxlabel"
            rgb = id_to_rgb(element_id)

            original_props[key] = {"color": supxlabel_obj.get_color()}
            supxlabel_obj.set_color(normalize_color(rgb))

            color_map[key] = {
                "id": element_id,
                "type": "supxlabel",
                "label": "supxlabel",
                "ax_index": -1,
                "rgb": list(rgb),
            }
            element_id += 1

    # Supylabel
    if hasattr(mpl_fig, "_supylabel") and mpl_fig._supylabel is not None:
        supylabel_obj = mpl_fig._supylabel
        if supylabel_obj.get_text():
            key = "fig_supylabel"
            rgb = id_to_rgb(element_id)

            original_props[key] = {"color": supylabel_obj.get_color()}
            supylabel_obj.set_color(normalize_color(rgb))

            color_map[key] = {
                "id": element_id,
                "type": "supylabel",
                "label": "supylabel",
                "ax_index": -1,
                "rgb": list(rgb),
            }
            element_id += 1

    return element_id


__all__ = ["process_text", "process_legend", "process_figure_text"]

# EOF
