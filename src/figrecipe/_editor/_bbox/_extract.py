#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main bounding box extraction function.

This module contains the main extract_bboxes function that coordinates
all element-specific bbox extractors.
"""

from typing import Any, Dict

from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from ._elements import get_element_bbox
from ._extract_axes import (
    extract_collections,
    extract_images,
    extract_lines,
    extract_patches,
)
from ._extract_text import (
    extract_figure_text,
    extract_legend,
    extract_spines,
    extract_text_elements,
)


def extract_bboxes(
    fig: Figure,
    img_width: int,
    img_height: int,
    include_points: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """
    Extract bounding boxes for all figure elements.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to extract bboxes from.
    img_width : int
        Width of the output image in pixels.
    img_height : int
        Height of the output image in pixels.
    include_points : bool, optional
        Whether to include point arrays for lines/scatter (default: True).

    Returns
    -------
    dict
        Mapping from element key to bbox info.
    """
    bboxes = {}

    # Get renderer for bbox calculations
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Get tight bbox for coordinate transformation
    tight_bbox = fig.get_tightbbox(renderer)
    if tight_bbox is None:
        tight_bbox = Bbox.from_bounds(0, 0, fig.get_figwidth(), fig.get_figheight())

    # bbox_inches='tight' adds pad_inches (default 0.1) around the tight bbox
    pad_inches = 0.1
    saved_width_inches = tight_bbox.width + 2 * pad_inches
    saved_height_inches = tight_bbox.height + 2 * pad_inches

    # Calculate scale factors from saved image size to pixel size
    scale_x = img_width / saved_width_inches if saved_width_inches > 0 else 1
    scale_y = img_height / saved_height_inches if saved_height_inches > 0 else 1

    # Process each axes
    for ax_idx, ax in enumerate(fig.get_axes()):
        _extract_axes_bboxes(
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
        )

    # Process figure-level text elements
    extract_figure_text(
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
    )

    # Add metadata
    bboxes["_meta"] = {
        "img_width": img_width,
        "img_height": img_height,
        "fig_width_inches": fig.get_figwidth(),
        "fig_height_inches": fig.get_figheight(),
        "dpi": fig.dpi,
    }

    return bboxes


def _extract_axes_bboxes(
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
    """Extract bboxes for all elements within an axes."""
    # Axes bounding box
    ax_bbox = get_element_bbox(
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
    if ax_bbox:
        bboxes[f"ax{ax_idx}_axes"] = {**ax_bbox, "type": "axes", "ax_index": ax_idx}

    # Extract all element types
    extract_lines(
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
    )
    extract_collections(
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
    )
    extract_patches(
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
    )
    extract_images(
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
    )
    extract_text_elements(
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
    )
    extract_legend(
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
    )
    extract_spines(
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
    )


__all__ = ["extract_bboxes"]

# EOF
