#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection bbox extraction for scatter, fill, and patch elements.

This module handles bbox extraction for matplotlib collections
(scatter plots, fills, bars, etc.).
"""

import math
from typing import Any, Dict, Optional

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from ._elements import get_element_bbox
from ._transforms import display_to_image, transform_bbox


def get_collection_bbox(
    coll,
    ax: Axes,
    fig: Figure,
    renderer,
    tight_bbox: Bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
    include_points: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get bbox and points for a collection (scatter, fill)."""
    try:
        bbox = None

        # For scatter plots, get_window_extent() can fail or return empty
        # So we calculate bbox from data points as fallback
        if isinstance(coll, PathCollection):
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
                        img_coords = display_to_image(
                            display_coords[0],
                            display_coords[1],
                            fig,
                            tight_bbox,
                            img_width,
                            img_height,
                            scale_x,
                            scale_y,
                            pad_inches,
                            saved_height_inches,
                        )
                        if img_coords:
                            points.append(img_coords)
                    except Exception:
                        continue

                # Calculate bbox from points
                if points:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    # Add padding around scatter points for easier clicking
                    padding = 10  # pixels
                    bbox = {
                        "x": float(min(xs) - padding),
                        "y": float(min(ys) - padding),
                        "width": float(max(xs) - min(xs) + 2 * padding),
                        "height": float(max(ys) - min(ys) + 2 * padding),
                        "points": points,
                    }
                    return bbox

        # Fallback: try standard window extent
        window_extent = coll.get_window_extent(renderer)
        if window_extent is None:
            # Use axes extent as fallback
            return get_element_bbox(
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

        # Check if window_extent is valid (not inf)
        if (
            math.isinf(window_extent.x0)
            or math.isinf(window_extent.y0)
            or math.isinf(window_extent.x1)
            or math.isinf(window_extent.y1)
        ):
            # Invalid extent - use axes extent as fallback
            return get_element_bbox(
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

        bbox = transform_bbox(
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

        return bbox

    except Exception:
        return None


def get_patch_bbox(
    patch,
    ax: Axes,
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
    """Get bbox for a patch (bar, rectangle)."""
    try:
        window_extent = patch.get_window_extent(renderer)
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


__all__ = ["get_collection_bbox", "get_patch_bbox"]
