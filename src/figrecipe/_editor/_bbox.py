#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bounding box extraction for figure elements.

This module extracts pixel coordinates for all figure elements,
enabling precise hit detection and visual selection overlays.

Coordinate Pipeline:
    Matplotlib display coords (points) → inches → image pixels
"""

import io
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox


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
        Enables proximity-based hit detection.

    Returns
    -------
    dict
        Mapping from element key to bbox info:
        {
            'element_key': {
                'x': float,      # Left edge in pixels
                'y': float,      # Top edge in pixels
                'width': float,  # Width in pixels
                'height': float, # Height in pixels
                'type': str,     # Element type
                'ax_index': int, # Axes index
                'points': [[x, y], ...],  # Optional path points
            }
        }
    """
    bboxes = {}

    # Get renderer for bbox calculations
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Get tight bbox for coordinate transformation
    tight_bbox = fig.get_tightbbox(renderer)
    if tight_bbox is None:
        tight_bbox = Bbox.from_bounds(0, 0, fig.get_figwidth(), fig.get_figheight())

    # Calculate scale factors
    fig_width_inches = tight_bbox.width
    fig_height_inches = tight_bbox.height
    scale_x = img_width / fig_width_inches if fig_width_inches > 0 else 1
    scale_y = img_height / fig_height_inches if fig_height_inches > 0 else 1

    # Process each axes
    axes_list = fig.get_axes()
    for ax_idx, ax in enumerate(axes_list):
        # Axes bounding box
        ax_bbox = _get_element_bbox(
            ax, fig, renderer, tight_bbox, img_width, img_height, scale_x, scale_y
        )
        if ax_bbox:
            bboxes[f"ax{ax_idx}_axes"] = {
                **ax_bbox,
                'type': 'axes',
                'ax_index': ax_idx,
            }

        # Lines
        for i, line in enumerate(ax.get_lines()):
            if not line.get_visible():
                continue

            key = f"ax{ax_idx}_line{i}"
            bbox = _get_line_bbox(
                line, ax, fig, renderer, tight_bbox,
                img_width, img_height, scale_x, scale_y,
                include_points=include_points,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    'type': 'line',
                    'label': line.get_label() or f'line_{i}',
                    'ax_index': ax_idx,
                }

        # Scatter plots
        scatter_idx = 0
        for i, coll in enumerate(ax.collections):
            if isinstance(coll, PathCollection):
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_scatter{scatter_idx}"
                bbox = _get_collection_bbox(
                    coll, ax, fig, renderer, tight_bbox,
                    img_width, img_height, scale_x, scale_y,
                    include_points=include_points,
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        'type': 'scatter',
                        'label': coll.get_label() or f'scatter_{scatter_idx}',
                        'ax_index': ax_idx,
                    }
                scatter_idx += 1

            elif isinstance(coll, PolyCollection):
                if not coll.get_visible():
                    continue

                key = f"ax{ax_idx}_fill{i}"
                bbox = _get_collection_bbox(
                    coll, ax, fig, renderer, tight_bbox,
                    img_width, img_height, scale_x, scale_y,
                    include_points=False,  # Fills use bbox only
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        'type': 'fill',
                        'label': coll.get_label() or f'fill_{i}',
                        'ax_index': ax_idx,
                    }

        # Bars
        bar_idx = 0
        for i, patch in enumerate(ax.patches):
            if isinstance(patch, Rectangle):
                if not patch.get_visible():
                    continue
                # Skip frame rectangles
                if patch.get_width() == 1.0 and patch.get_height() == 1.0:
                    continue

                key = f"ax{ax_idx}_bar{bar_idx}"
                bbox = _get_patch_bbox(
                    patch, ax, fig, renderer, tight_bbox,
                    img_width, img_height, scale_x, scale_y,
                )
                if bbox:
                    bboxes[key] = {
                        **bbox,
                        'type': 'bar',
                        'label': patch.get_label() or f'bar_{bar_idx}',
                        'ax_index': ax_idx,
                    }
                bar_idx += 1

        # Title
        title = ax.get_title()
        if title:
            key = f"ax{ax_idx}_title"
            bbox = _get_text_bbox(
                ax.title, fig, renderer, tight_bbox,
                img_width, img_height, scale_x, scale_y,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    'type': 'title',
                    'label': 'title',
                    'ax_index': ax_idx,
                    'text': title,
                }

        # X label
        xlabel = ax.get_xlabel()
        if xlabel:
            key = f"ax{ax_idx}_xlabel"
            bbox = _get_text_bbox(
                ax.xaxis.label, fig, renderer, tight_bbox,
                img_width, img_height, scale_x, scale_y,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    'type': 'xlabel',
                    'label': 'xlabel',
                    'ax_index': ax_idx,
                    'text': xlabel,
                }

        # Y label
        ylabel = ax.get_ylabel()
        if ylabel:
            key = f"ax{ax_idx}_ylabel"
            bbox = _get_text_bbox(
                ax.yaxis.label, fig, renderer, tight_bbox,
                img_width, img_height, scale_x, scale_y,
            )
            if bbox:
                bboxes[key] = {
                    **bbox,
                    'type': 'ylabel',
                    'label': 'ylabel',
                    'ax_index': ax_idx,
                    'text': ylabel,
                }

        # Legend
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            key = f"ax{ax_idx}_legend"
            try:
                legend_bbox = legend.get_window_extent(renderer)
                if legend_bbox is not None:
                    bbox = _transform_bbox(
                        legend_bbox, fig, tight_bbox,
                        img_width, img_height, scale_x, scale_y,
                    )
                    if bbox:
                        bboxes[key] = {
                            **bbox,
                            'type': 'legend',
                            'label': 'legend',
                            'ax_index': ax_idx,
                        }
            except Exception:
                pass

        # Spines
        for spine_name, spine in ax.spines.items():
            if spine.get_visible():
                key = f"ax{ax_idx}_spine_{spine_name}"
                try:
                    spine_bbox = spine.get_window_extent(renderer)
                    if spine_bbox is not None:
                        bbox = _transform_bbox(
                            spine_bbox, fig, tight_bbox,
                            img_width, img_height, scale_x, scale_y,
                        )
                        if bbox:
                            bboxes[key] = {
                                **bbox,
                                'type': 'spine',
                                'label': spine_name,
                                'ax_index': ax_idx,
                            }
                except Exception:
                    pass

    # Add metadata
    bboxes['_meta'] = {
        'img_width': img_width,
        'img_height': img_height,
        'fig_width_inches': fig.get_figwidth(),
        'fig_height_inches': fig.get_figheight(),
        'dpi': fig.dpi,
    }

    return bboxes


def _get_element_bbox(
    element,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a general element."""
    try:
        window_extent = element.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent, fig, tight_bbox,
            img_width, img_height, scale_x, scale_y,
        )
    except Exception:
        return None


def _get_line_bbox(
    line,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    include_points: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get bbox and points for a line."""
    try:
        # Get window extent
        window_extent = line.get_window_extent(renderer)
        if window_extent is None:
            return None

        bbox = _transform_bbox(
            window_extent, fig, tight_bbox,
            img_width, img_height, scale_x, scale_y,
        )
        if bbox is None:
            return None

        # Add path points for proximity detection
        if include_points:
            xdata = line.get_xdata()
            ydata = line.get_ydata()

            if len(xdata) > 0 and len(ydata) > 0:
                # Transform data coords to image pixels
                transform = ax.transData
                points = []

                # Downsample if too many points
                max_points = 100
                step = max(1, len(xdata) // max_points)

                for i in range(0, len(xdata), step):
                    try:
                        display_coords = transform.transform((xdata[i], ydata[i]))
                        img_coords = _display_to_image(
                            display_coords[0], display_coords[1],
                            fig, tight_bbox, img_width, img_height, scale_x, scale_y,
                        )
                        if img_coords:
                            points.append(img_coords)
                    except Exception:
                        continue

                if points:
                    bbox['points'] = points

        return bbox

    except Exception:
        return None


def _get_collection_bbox(
    coll,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    include_points: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get bbox and points for a collection (scatter, fill)."""
    try:
        # Get window extent
        window_extent = coll.get_window_extent(renderer)
        if window_extent is None:
            return None

        bbox = _transform_bbox(
            window_extent, fig, tight_bbox,
            img_width, img_height, scale_x, scale_y,
        )
        if bbox is None:
            return None

        # Add points for scatter
        if include_points and isinstance(coll, PathCollection):
            offsets = coll.get_offsets()
            if len(offsets) > 0:
                transform = ax.transData
                points = []

                # Limit to reasonable number of points
                max_points = 200
                step = max(1, len(offsets) // max_points)

                for i in range(0, len(offsets), step):
                    try:
                        offset = offsets[i]
                        display_coords = transform.transform(offset)
                        img_coords = _display_to_image(
                            display_coords[0], display_coords[1],
                            fig, tight_bbox, img_width, img_height, scale_x, scale_y,
                        )
                        if img_coords:
                            points.append(img_coords)
                    except Exception:
                        continue

                if points:
                    bbox['points'] = points

        return bbox

    except Exception:
        return None


def _get_patch_bbox(
    patch,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a patch (bar, rectangle)."""
    try:
        window_extent = patch.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent, fig, tight_bbox,
            img_width, img_height, scale_x, scale_y,
        )
    except Exception:
        return None


def _get_text_bbox(
    text,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a text element."""
    try:
        window_extent = text.get_window_extent(renderer)
        if window_extent is None:
            return None
        return _transform_bbox(
            window_extent, fig, tight_bbox,
            img_width, img_height, scale_x, scale_y,
        )
    except Exception:
        return None


def _transform_bbox(
    window_extent: Bbox,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
) -> Optional[Dict[str, float]]:
    """
    Transform matplotlib window extent to image pixel coordinates.

    Parameters
    ----------
    window_extent : Bbox
        Bbox in display coordinates (points).
    fig : Figure
        Matplotlib figure.
    tight_bbox : Bbox
        Tight bbox of figure in inches.
    img_width, img_height : int
        Output image dimensions.
    scale_x, scale_y : float
        Scale factors from inches to pixels.

    Returns
    -------
    dict or None
        {x, y, width, height} in image pixels.
    """
    try:
        dpi = fig.dpi

        # Convert display coords to inches
        x0_inches = window_extent.x0 / dpi
        y0_inches = window_extent.y0 / dpi
        x1_inches = window_extent.x1 / dpi
        y1_inches = window_extent.y1 / dpi

        # Subtract tight bbox origin
        x0_rel = x0_inches - tight_bbox.x0
        y0_rel = y0_inches - tight_bbox.y0
        x1_rel = x1_inches - tight_bbox.x0
        y1_rel = y1_inches - tight_bbox.y0

        # Scale to image pixels
        x0_px = x0_rel * scale_x
        y0_px = y0_rel * scale_y
        x1_px = x1_rel * scale_x
        y1_px = y1_rel * scale_y

        # Flip y (image origin is top-left, matplotlib is bottom-left)
        y0_px_flipped = img_height - y1_px
        y1_px_flipped = img_height - y0_px

        # Clamp to bounds
        x0_px = max(0, min(x0_px, img_width))
        x1_px = max(0, min(x1_px, img_width))
        y0_px_flipped = max(0, min(y0_px_flipped, img_height))
        y1_px_flipped = max(0, min(y1_px_flipped, img_height))

        width = x1_px - x0_px
        height = y1_px_flipped - y0_px_flipped

        if width <= 0 or height <= 0:
            return None

        return {
            'x': float(x0_px),
            'y': float(y0_px_flipped),
            'width': float(width),
            'height': float(height),
        }

    except Exception:
        return None


def _display_to_image(
    display_x: float,
    display_y: float,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
) -> Optional[List[float]]:
    """
    Transform display coordinates to image pixel coordinates.

    Returns
    -------
    list or None
        [x, y] in image pixels.
    """
    try:
        dpi = fig.dpi

        # Convert to inches
        x_inches = display_x / dpi
        y_inches = display_y / dpi

        # Subtract tight bbox origin
        x_rel = x_inches - tight_bbox.x0
        y_rel = y_inches - tight_bbox.y0

        # Scale to image pixels
        x_px = x_rel * scale_x
        y_px = y_rel * scale_y

        # Flip y
        y_px_flipped = img_height - y_px

        # Clamp
        x_px = max(0, min(x_px, img_width))
        y_px_flipped = max(0, min(y_px_flipped, img_height))

        return [float(x_px), float(y_px_flipped)]

    except Exception:
        return None


__all__ = ['extract_bboxes']
