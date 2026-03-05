#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line bbox extraction for line plots.

This module handles bbox extraction for line elements,
including data point sampling for hit detection.
"""

from typing import Any, Dict, Optional

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox

from ._transforms import display_to_image, transform_bbox


def get_line_bbox(
    line,
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
    """Get bbox and points for a line."""
    try:
        # Get window extent
        window_extent = line.get_window_extent(renderer)
        if window_extent is None:
            return None

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

                if points:
                    bbox["points"] = points

        return bbox

    except Exception:
        return None


def get_quiver_bbox(
    quiver,
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
) -> Optional[Dict[str, Any]]:
    """Get bbox for a quiver plot from its data points."""
    try:
        # Get X, Y positions from quiver
        # Quiver stores positions in X, Y arrays
        X = quiver.X
        Y = quiver.Y

        if X is None or Y is None or len(X) == 0:
            return None

        # Flatten if needed
        import numpy as np

        X_flat = np.asarray(X).flatten()
        Y_flat = np.asarray(Y).flatten()

        if len(X_flat) == 0 or len(Y_flat) == 0:
            return None

        transform = ax.transData
        points = []

        # Limit to reasonable number of points
        max_points = 100
        step = max(1, len(X_flat) // max_points)

        for i in range(0, len(X_flat), step):
            try:
                display_coords = transform.transform((X_flat[i], Y_flat[i]))
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

        if not points:
            return None

        # Calculate bbox from points
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        padding = 15  # pixels - slightly larger for quiver arrows
        return {
            "x": float(min(xs) - padding),
            "y": float(min(ys) - padding),
            "width": float(max(xs) - min(xs) + 2 * padding),
            "height": float(max(ys) - min(ys) + 2 * padding),
        }
    except Exception:
        return None


__all__ = ["get_line_bbox", "get_quiver_bbox"]
