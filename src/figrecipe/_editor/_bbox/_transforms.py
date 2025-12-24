#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coordinate transformation utilities for bbox extraction.

This module handles the transformation from matplotlib display coordinates
to image pixel coordinates for hit detection.
"""

from typing import Dict, List, Optional

from matplotlib.figure import Figure
from matplotlib.transforms import Bbox


def transform_bbox(
    window_extent: Bbox,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
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
    pad_inches : float
        Padding added by bbox_inches='tight' (default 0.1).
    saved_height_inches : float
        Total saved image height including padding.

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

        # Transform to saved image coordinates
        # Account for tight bbox origin and padding
        x0_rel = x0_inches - tight_bbox.x0 + pad_inches
        x1_rel = x1_inches - tight_bbox.x0 + pad_inches

        # Y coordinate flip: matplotlib Y=0 at bottom, image Y=0 at top
        y0_rel = saved_height_inches - (y1_inches - tight_bbox.y0 + pad_inches)
        y1_rel = saved_height_inches - (y0_inches - tight_bbox.y0 + pad_inches)

        # Scale to image pixels
        x0_px = x0_rel * scale_x
        y0_px = y0_rel * scale_y
        x1_px = x1_rel * scale_x
        y1_px = y1_rel * scale_y

        # Clamp to bounds
        x0_px = max(0, min(x0_px, img_width))
        x1_px = max(0, min(x1_px, img_width))
        y0_px = max(0, min(y0_px, img_height))
        y1_px = max(0, min(y1_px, img_height))

        width = x1_px - x0_px
        height = y1_px - y0_px

        if width <= 0 or height <= 0:
            return None

        return {
            "x": float(x0_px),
            "y": float(y0_px),
            "width": float(width),
            "height": float(height),
        }

    except Exception:
        return None


def display_to_image(
    display_x: float,
    display_y: float,
    fig: Figure,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
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

        # Transform to saved image coordinates with padding
        x_rel = x_inches - tight_bbox.x0 + pad_inches

        # Y coordinate flip: matplotlib Y=0 at bottom, image Y=0 at top
        y_rel = saved_height_inches - (y_inches - tight_bbox.y0 + pad_inches)

        # Scale to image pixels
        x_px = x_rel * scale_x
        y_px = y_rel * scale_y

        # Clamp
        x_px = max(0, min(x_px, img_width))
        y_px = max(0, min(y_px, img_height))

        return [float(x_px), float(y_px)]

    except Exception:
        return None


__all__ = ["transform_bbox", "display_to_image"]
