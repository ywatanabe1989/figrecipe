#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Axes element bbox extraction (lines, collections, patches, images)."""

from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.patches import Rectangle

from ._collections import get_collection_bbox, get_patch_bbox
from ._elements import get_element_bbox
from ._lines import get_line_bbox, get_quiver_bbox


def extract_lines(
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
    include_points,
    bboxes,
):
    """Extract bboxes for line elements."""
    for i, line in enumerate(ax.get_lines()):
        if not line.get_visible():
            continue
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        if len(xdata) == 0 or len(ydata) == 0:
            continue
        if line.axes != ax:
            continue

        bbox = get_line_bbox(
            line,
            ax,
            fig,
            renderer,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
            include_points,
        )
        if bbox:
            bboxes[f"ax{ax_idx}_line{i}"] = {
                **bbox,
                "type": "line",
                "label": line.get_label() or f"line_{i}",
                "ax_index": ax_idx,
            }


def extract_collections(
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
    include_points,
    bboxes,
):
    """Extract bboxes for collection elements (scatter, fill, quiver, etc.)."""
    from matplotlib.collections import LineCollection, QuadMesh
    from matplotlib.contour import QuadContourSet
    from matplotlib.quiver import Quiver

    scatter_idx = 0
    for i, coll in enumerate(ax.collections):
        if isinstance(coll, Quiver):
            if not coll.get_visible():
                continue
            bbox = get_quiver_bbox(
                coll,
                ax,
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
                bboxes[f"ax{ax_idx}_quiver{i}"] = {
                    **bbox,
                    "type": "quiver",
                    "label": coll.get_label() or f"quiver_{i}",
                    "ax_index": ax_idx,
                }

        elif isinstance(coll, PathCollection):
            if not coll.get_visible():
                continue
            bbox = get_collection_bbox(
                coll,
                ax,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
                include_points,
            )
            if bbox:
                bboxes[f"ax{ax_idx}_scatter{scatter_idx}"] = {
                    **bbox,
                    "type": "scatter",
                    "label": coll.get_label() or f"scatter_{scatter_idx}",
                    "ax_index": ax_idx,
                }
            scatter_idx += 1

        elif isinstance(coll, PolyCollection):
            if not coll.get_visible():
                continue
            bbox = get_collection_bbox(
                coll,
                ax,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
                False,
            )
            if bbox:
                bboxes[f"ax{ax_idx}_fill{i}"] = {
                    **bbox,
                    "type": "fill",
                    "label": coll.get_label() or f"fill_{i}",
                    "ax_index": ax_idx,
                }

        elif isinstance(coll, LineCollection):
            if not coll.get_visible():
                continue
            bbox = get_collection_bbox(
                coll,
                ax,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
                False,
            )
            if bbox:
                bboxes[f"ax{ax_idx}_linecoll{i}"] = {
                    **bbox,
                    "type": "linecollection",
                    "label": coll.get_label() or f"linecoll_{i}",
                    "ax_index": ax_idx,
                }

        elif isinstance(coll, QuadMesh):
            if not coll.get_visible():
                continue
            bbox = get_collection_bbox(
                coll,
                ax,
                fig,
                renderer,
                tight_bbox,
                img_width,
                img_height,
                scale_x,
                scale_y,
                pad_inches,
                saved_height_inches,
                False,
            )
            if bbox:
                bboxes[f"ax{ax_idx}_quadmesh{i}"] = {
                    **bbox,
                    "type": "quadmesh",
                    "label": f"quadmesh_{i}",
                    "ax_index": ax_idx,
                }

        elif isinstance(coll, QuadContourSet):
            bbox = get_element_bbox(
                ax,
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
                bboxes[f"ax{ax_idx}_contour{i}"] = {
                    **bbox,
                    "type": "contour",
                    "label": f"contour_{i}",
                    "ax_index": ax_idx,
                }


def extract_patches(
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
    """Extract bboxes for patch elements (bars, wedges, polygons)."""
    from matplotlib.patches import Polygon, Wedge

    bar_idx = 0
    for i, patch in enumerate(ax.patches):
        if isinstance(patch, Rectangle):
            if not patch.get_visible():
                continue
            if patch.get_width() == 1.0 and patch.get_height() == 1.0:
                continue
            bbox = get_patch_bbox(
                patch,
                ax,
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
                bboxes[f"ax{ax_idx}_bar{bar_idx}"] = {
                    **bbox,
                    "type": "bar",
                    "label": patch.get_label() or f"bar_{bar_idx}",
                    "ax_index": ax_idx,
                }
            bar_idx += 1

        elif isinstance(patch, Wedge):
            if not patch.get_visible():
                continue
            bbox = get_patch_bbox(
                patch,
                ax,
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
                bboxes[f"ax{ax_idx}_wedge{i}"] = {
                    **bbox,
                    "type": "pie",
                    "label": patch.get_label() or f"wedge_{i}",
                    "ax_index": ax_idx,
                }

        elif isinstance(patch, Polygon):
            if not patch.get_visible():
                continue
            bbox = get_patch_bbox(
                patch,
                ax,
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
                bboxes[f"ax{ax_idx}_polygon{i}"] = {
                    **bbox,
                    "type": "fill",
                    "label": patch.get_label() or f"fill_{i}",
                    "ax_index": ax_idx,
                }


def extract_images(
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
    """Extract bboxes for image elements."""
    from matplotlib.image import AxesImage

    for i, img in enumerate(ax.images):
        if isinstance(img, AxesImage):
            if not img.get_visible():
                continue
            bbox = get_element_bbox(
                img,
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
                bboxes[f"ax{ax_idx}_image{i}"] = {
                    **bbox,
                    "type": "image",
                    "label": img.get_label() or f"image_{i}",
                    "ax_index": ax_idx,
                }


__all__ = ["extract_lines", "extract_collections", "extract_patches", "extract_images"]

# EOF
