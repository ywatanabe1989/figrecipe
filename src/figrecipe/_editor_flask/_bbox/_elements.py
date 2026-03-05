#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Element bbox extraction for general elements, text, and ticks.

This module handles bbox extraction for axes, text labels, and tick marks.
"""

from typing import Dict, Optional

from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from ._transforms import transform_bbox


def get_element_bbox(
    element,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a general element."""
    try:
        window_extent = element.get_window_extent(renderer)
        if window_extent is None:
            return None
        return transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
    except Exception:
        return None


def get_text_bbox(
    text,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """Get bbox for a text element."""
    try:
        window_extent = text.get_window_extent(renderer)
        if window_extent is None:
            return None
        return transform_bbox(
            window_extent,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )
    except Exception:
        return None


def get_tick_labels_bbox(
    axis,
    axis_type: str,  # 'x' or 'y'
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
) -> Optional[Dict[str, float]]:
    """
    Get bbox for tick labels, extended to span the full axis dimension.

    For x-axis: tick labels bbox spans the full width of the plot area.
    For y-axis: tick labels bbox spans the full height of the plot area.
    """
    try:
        all_bboxes = []

        # Get all tick label bboxes
        for tick in axis.get_major_ticks():
            tick_label = tick.label1 if hasattr(tick, "label1") else tick.label
            if tick_label and tick_label.get_visible():
                try:
                    tick_extent = tick_label.get_window_extent(renderer)
                    if tick_extent is not None and tick_extent.width > 0:
                        all_bboxes.append(tick_extent)
                except Exception:
                    pass

        if not all_bboxes:
            return None

        # Merge all tick label bboxes
        merged = all_bboxes[0]
        for bbox in all_bboxes[1:]:
            merged = Bbox.union([merged, bbox])

        # Get the axes extent to extend the tick labels region
        ax = axis.axes
        ax_bbox = ax.get_window_extent(renderer)

        if axis_type == "x":
            # For x-axis: extend width to match axes width, keep tick labels height
            merged = Bbox.from_extents(
                ax_bbox.x0,  # Align left with axes
                merged.y0,  # Keep tick labels y position
                ax_bbox.x1,  # Align right with axes
                merged.y1,  # Keep tick labels height
            )
        else:  # y-axis
            # For y-axis: extend height to match axes height, keep tick labels width
            merged = Bbox.from_extents(
                merged.x0,  # Keep tick labels x position
                ax_bbox.y0,  # Align bottom with axes
                merged.x1,  # Keep tick labels width
                ax_bbox.y1,  # Align top with axes
            )

        return transform_bbox(
            merged,
            fig,
            tight_bbox,
            img_width,
            img_height,
            scale_x,
            scale_y,
            pad_inches,
            saved_height_inches,
        )

    except Exception:
        return None


__all__ = ["get_element_bbox", "get_text_bbox", "get_tick_labels_bbox"]
