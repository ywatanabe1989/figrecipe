#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text, legend, spine, and figure text bbox extraction."""

from ._elements import get_text_bbox, get_tick_labels_bbox
from ._transforms import transform_bbox


def extract_text_elements(
    ax,
    ax_idx,
    fig,
    renderer,
    tight_bbox,
    img_width,
    img_height,
    scale_x,
    scale_y,
    pad_inches,
    saved_height_inches,
    bboxes,
):
    """Extract bboxes for text elements (title, labels, ticks)."""
    # Title
    title = ax.get_title()
    if title:
        bbox = get_text_bbox(
            ax.title,
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if bbox:
            bboxes[f"ax{ax_idx}_title"] = {
                **bbox,
                "type": "title",
                "label": "title",
                "ax_index": ax_idx,
                "text": title,
            }

    # X label
    xlabel = ax.get_xlabel()
    if xlabel:
        bbox = get_text_bbox(
            ax.xaxis.label,
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if bbox:
            bboxes[f"ax{ax_idx}_xlabel"] = {
                **bbox,
                "type": "xlabel",
                "label": "xlabel",
                "ax_index": ax_idx,
                "text": xlabel,
            }

    # X tick labels
    xtick_bbox = get_tick_labels_bbox(
        ax.xaxis,
        "x",
        fig,
        renderer,
        tight_bbox,
        img_width,
        img_height,
        scale_x,
        scale_y,
        pad_inches,
        saved_height_inches,
    )
    if xtick_bbox:
        bboxes[f"ax{ax_idx}_xticks"] = {
            **xtick_bbox,
            "type": "xticks",
            "label": "x tick labels",
            "ax_index": ax_idx,
        }

    # Y label
    ylabel = ax.get_ylabel()
    if ylabel:
        bbox = get_text_bbox(
            ax.yaxis.label,
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
        if bbox:
            bboxes[f"ax{ax_idx}_ylabel"] = {
                **bbox,
                "type": "ylabel",
                "label": "ylabel",
                "ax_index": ax_idx,
                "text": ylabel,
            }

    # Y tick labels
    ytick_bbox = get_tick_labels_bbox(
        ax.yaxis,
        "y",
        fig,
        renderer,
        tight_bbox,
        img_width,
        img_height,
        scale_x,
        scale_y,
        pad_inches,
        saved_height_inches,
    )
    if ytick_bbox:
        bboxes[f"ax{ax_idx}_yticks"] = {
            **ytick_bbox,
            "type": "yticks",
            "label": "y tick labels",
            "ax_index": ax_idx,
        }


def extract_legend(
    ax,
    ax_idx,
    fig,
    renderer,
    tight_bbox,
    img_width,
    img_height,
    scale_x,
    scale_y,
    pad_inches,
    saved_height_inches,
    bboxes,
):
    """Extract bbox for legend."""
    legend = ax.get_legend()
    if legend is not None and legend.get_visible():
        try:
            legend_bbox = legend.get_window_extent(renderer)
            if legend_bbox is not None:
                bbox = transform_bbox(
                    legend_bbox,
                    fig,
                    tight_bbox,
                    img_width,
                    img_height,
                    scale_x,
                    scale_y,
                    pad_inches,
                    saved_height_inches,
                )
                if bbox:
                    bboxes[f"ax{ax_idx}_legend"] = {
                        **bbox,
                        "type": "legend",
                        "label": "legend",
                        "ax_index": ax_idx,
                    }
        except Exception:
            pass


def extract_spines(
    ax,
    ax_idx,
    fig,
    renderer,
    tight_bbox,
    img_width,
    img_height,
    scale_x,
    scale_y,
    pad_inches,
    saved_height_inches,
    bboxes,
):
    """Extract bboxes for spines with padding for easier clicking."""
    spine_min_size = 8
    for spine_name, spine in ax.spines.items():
        if spine.get_visible():
            try:
                spine_bbox = spine.get_window_extent(renderer)
                if spine_bbox is not None:
                    bbox = transform_bbox(
                        spine_bbox,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        if bbox["width"] < spine_min_size:
                            expand = (spine_min_size - bbox["width"]) / 2
                            bbox["x"] -= expand
                            bbox["width"] = spine_min_size
                        if bbox["height"] < spine_min_size:
                            expand = (spine_min_size - bbox["height"]) / 2
                            bbox["y"] -= expand
                            bbox["height"] = spine_min_size
                        bboxes[f"ax{ax_idx}_spine_{spine_name}"] = {
                            **bbox,
                            "type": "spine",
                            "label": spine_name,
                            "ax_index": ax_idx,
                        }
            except Exception:
                pass


def extract_figure_text(
    fig,
    renderer,
    tight_bbox,
    img_width,
    img_height,
    scale_x,
    scale_y,
    pad_inches,
    saved_height_inches,
    bboxes,
):
    """Extract bboxes for figure-level text (suptitle, supxlabel, supylabel)."""
    # Suptitle
    if hasattr(fig, "_suptitle") and fig._suptitle is not None:
        suptitle_obj = fig._suptitle
        if suptitle_obj.get_text():
            try:
                suptitle_extent = suptitle_obj.get_window_extent(renderer)
                if suptitle_extent is not None:
                    bbox = transform_bbox(
                        suptitle_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_suptitle"] = {
                            **bbox,
                            "type": "suptitle",
                            "label": "suptitle",
                            "ax_index": -1,
                            "text": suptitle_obj.get_text(),
                        }
            except Exception:
                pass

    # Supxlabel
    if hasattr(fig, "_supxlabel") and fig._supxlabel is not None:
        supxlabel_obj = fig._supxlabel
        if supxlabel_obj.get_text():
            try:
                supxlabel_extent = supxlabel_obj.get_window_extent(renderer)
                if supxlabel_extent is not None:
                    bbox = transform_bbox(
                        supxlabel_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_supxlabel"] = {
                            **bbox,
                            "type": "supxlabel",
                            "label": "supxlabel",
                            "ax_index": -1,
                            "text": supxlabel_obj.get_text(),
                        }
            except Exception:
                pass

    # Supylabel
    if hasattr(fig, "_supylabel") and fig._supylabel is not None:
        supylabel_obj = fig._supylabel
        if supylabel_obj.get_text():
            try:
                supylabel_extent = supylabel_obj.get_window_extent(renderer)
                if supylabel_extent is not None:
                    bbox = transform_bbox(
                        supylabel_extent,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes["fig_supylabel"] = {
                            **bbox,
                            "type": "supylabel",
                            "label": "supylabel",
                            "ax_index": -1,
                            "text": supylabel_obj.get_text(),
                        }
            except Exception:
                pass


def extract_annotations(
    ax,
    ax_idx,
    fig,
    renderer,
    tight_bbox,
    img_width,
    img_height,
    scale_x,
    scale_y,
    pad_inches,
    saved_height_inches,
    bboxes,
):
    """Extract bboxes for decorative elements (ax.text, ax.annotate, panel labels).

    These are cosmetic elements that can be repositioned without affecting data.
    """
    import string

    panel_label_chars = set(string.ascii_uppercase)

    # Extract ax.texts (includes panel labels and other text annotations)
    for i, text_obj in enumerate(ax.texts):
        text_content = text_obj.get_text().strip()
        if not text_content:
            continue

        try:
            bbox = get_text_bbox(
                text_obj,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
            )
            if bbox:
                # Determine if this is a panel label
                is_panel_label = (
                    text_content in panel_label_chars
                    and text_obj.get_transform() == ax.transAxes
                )

                # Get position
                pos = text_obj.get_position()

                # Calculate axes-relative position (0-1)
                if text_obj.get_transform() == ax.transAxes:
                    # Already in axes coordinates
                    rel_x, rel_y = pos[0], pos[1]
                else:
                    # Convert from data coordinates to axes
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    rel_x = (
                        (pos[0] - xlim[0]) / (xlim[1] - xlim[0])
                        if xlim[1] != xlim[0]
                        else 0.5
                    )
                    rel_y = (
                        (pos[1] - ylim[0]) / (ylim[1] - ylim[0])
                        if ylim[1] != ylim[0]
                        else 0.5
                    )

                if is_panel_label:
                    key = f"ax{ax_idx}_panel_label"
                    elem_type = "panel_label"
                else:
                    key = f"ax{ax_idx}_text_{i}"
                    elem_type = "text"

                bboxes[key] = {
                    **bbox,
                    "type": elem_type,
                    "label": elem_type,
                    "ax_index": ax_idx,
                    "text": text_content,
                    "text_index": i,
                    "pos_x": pos[0],
                    "pos_y": pos[1],
                    "rel_x": rel_x,
                    "rel_y": rel_y,
                }
        except Exception:
            pass

    # Extract ax.patches that are arrows (FancyArrowPatch)
    from matplotlib.patches import FancyArrowPatch

    for i, patch in enumerate(ax.patches):
        if isinstance(patch, FancyArrowPatch):
            try:
                patch_bbox = patch.get_window_extent(renderer)
                if patch_bbox is not None:
                    bbox = transform_bbox(
                        patch_bbox,
                        fig,
                        tight_bbox,
                        img_width,
                        img_height,
                        scale_x,
                        scale_y,
                        pad_inches,
                        saved_height_inches,
                    )
                    if bbox:
                        bboxes[f"ax{ax_idx}_arrow_{i}"] = {
                            **bbox,
                            "type": "arrow",
                            "label": "arrow",
                            "ax_index": ax_idx,
                            "arrow_index": i,
                        }
            except Exception:
                pass


__all__ = [
    "extract_text_elements",
    "extract_legend",
    "extract_spines",
    "extract_figure_text",
    "extract_annotations",
]

# EOF
