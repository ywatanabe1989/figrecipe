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
    extract_annotations,
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
    # Handle matplotlib's Done exception from _get_renderer (can occur with corrupted canvas state)
    try:
        fig.canvas.draw()
    except Exception as e:
        # Matplotlib's Done exception or other draw issues - reset canvas and retry
        if "Done" in str(type(e).__name__) or "Done" in str(e):
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            fig.set_canvas(FigureCanvasAgg(fig))
            try:
                fig.canvas.draw()
            except Exception:
                pass  # Continue with potentially stale renderer
        else:
            raise
    renderer = fig.canvas.get_renderer()

    # Get figure bounds for coordinate transformation
    # NOTE: We do NOT use bbox_inches='tight' in savefig, so use fixed figsize
    fig_width_inches = fig.get_figwidth()
    fig_height_inches = fig.get_figheight()

    # Create a bbox representing the full figure (for compatibility with element extraction)
    tight_bbox = Bbox.from_bounds(0, 0, fig_width_inches, fig_height_inches)

    # No padding since we don't use bbox_inches='tight'
    pad_inches = 0.0
    saved_width_inches = fig_width_inches
    saved_height_inches = fig_height_inches

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

    # Compute panel bboxes using tight bbox from matplotlib
    panel_bboxes = _compute_panel_bboxes(
        bboxes,
        len(fig.get_axes()),
        fig=fig,
        renderer=renderer,
        img_width=img_width,
        img_height=img_height,
    )

    # Add metadata
    bboxes["_meta"] = {
        "img_width": img_width,
        "img_height": img_height,
        "fig_width_inches": fig.get_figwidth(),
        "fig_height_inches": fig.get_figheight(),
        "dpi": fig.dpi,
        "panel_bboxes": panel_bboxes,
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
    extract_annotations(
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


def _compute_panel_bboxes(
    bboxes: Dict[str, Any],
    num_axes: int,
    fig: Figure = None,
    renderer=None,
    img_width: int = None,
    img_height: int = None,
) -> Dict[int, Dict[str, float]]:
    """
    Compute tight bounding box for each panel (axis).

    Uses matplotlib's ax.get_tightbbox() for reliable panel bounds that include
    all decorators (title, labels, tick labels) without outliers.

    Falls back to union of elements if tight bbox is unavailable.

    Parameters
    ----------
    bboxes : dict
        All extracted element bboxes.
    num_axes : int
        Number of axes in the figure.
    fig : Figure, optional
        Matplotlib figure (needed for tight bbox computation).
    renderer : optional
        Matplotlib renderer (needed for tight bbox computation).
    img_width : int, optional
        Image width in pixels.
    img_height : int, optional
        Image height in pixels.

    Returns
    -------
    dict
        Mapping from ax_index to panel bbox: {ax_index: {x, y, width, height}}
    """
    panel_bboxes = {}

    # Try to use tight bbox if figure is available
    if fig is not None and renderer is not None and img_width and img_height:
        fig_width_inches = fig.get_figwidth()
        fig_height_inches = fig.get_figheight()
        dpi = fig.dpi

        for ax_idx, ax in enumerate(fig.get_axes()):
            try:
                tight = ax.get_tightbbox(renderer)
                if tight is not None:
                    # Convert from display coords to image coords
                    # Display y=0 is at bottom, image y=0 is at top
                    x = tight.x0 * img_width / (fig_width_inches * dpi)
                    y = img_height - tight.y1 * img_height / (fig_height_inches * dpi)
                    width = tight.width * img_width / (fig_width_inches * dpi)
                    height = tight.height * img_height / (fig_height_inches * dpi)
                    panel_bboxes[ax_idx] = {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                    }
            except Exception:
                pass  # Fall back to union method below

    # Fall back to union method for any missing panels
    for ax_idx in range(num_axes):
        if ax_idx in panel_bboxes:
            continue

        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")

        for key, bbox in bboxes.items():
            if key == "_meta" or not isinstance(bbox, dict):
                continue
            elem_ax_index = bbox.get("ax_index")
            if elem_ax_index is None:
                if key.startswith("ax") and "_" in key:
                    try:
                        elem_ax_index = int(key.split("_")[0][2:])
                    except (ValueError, IndexError):
                        continue
                else:
                    continue
            if elem_ax_index != ax_idx:
                continue
            x, y = bbox.get("x"), bbox.get("y")
            w, h = bbox.get("width"), bbox.get("height")
            if x is None or y is None or w is None or h is None:
                continue
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x + w), max(max_y, y + h)

        if min_x != float("inf"):
            panel_bboxes[ax_idx] = {
                "x": min_x,
                "y": min_y,
                "width": max_x - min_x,
                "height": max_y - min_y,
            }

    return panel_bboxes


__all__ = ["extract_bboxes"]

# EOF
