#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-element bbox extraction for collections.

Extracts individual bboxes from LineCollection (eventplot segments)
and PolyCollection (violin bodies) instead of one big rectangle.
"""

from typing import Any, Dict, List, Optional

from ._collections import get_collection_bbox
from ._transforms import display_to_image


def extract_linecoll_with_points(
    coll,
    ax,
    fig,
    tight_bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
    renderer=None,
) -> Optional[Dict[str, Any]]:
    """Extract LineCollection bbox with segment midpoints as points.

    For eventplot/violin LineCollections, this provides per-segment
    point data so the overlay can render polylines instead of one big rect.

    Parameters
    ----------
    coll : LineCollection
        The line collection.
    ax : Axes
        Parent axes.
    fig : Figure
        Parent figure.
    tight_bbox : Bbox
        Tight bounding box of the figure.
    img_width, img_height : int
        Rendered image dimensions.
    scale_x, scale_y : float
        Scale factors.
    pad_inches : float
        Padding in inches.
    saved_height_inches : float
        Saved figure height.
    renderer : optional
        Matplotlib renderer (for fallback).

    Returns
    -------
    dict or None
        Bbox dict with ``points`` key, or None.
    """
    transform = ax.transData
    segments = coll.get_segments()
    points: List = []

    for seg in segments:
        if len(seg) < 2:
            continue
        mid_x = (seg[0][0] + seg[-1][0]) / 2.0
        mid_y = (seg[0][1] + seg[-1][1]) / 2.0
        try:
            display_coords = transform.transform((mid_x, mid_y))
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
        return get_collection_bbox(
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

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    padding = 6
    return {
        "x": float(min(xs) - padding),
        "y": float(min(ys) - padding),
        "width": float(max(xs) - min(xs) + 2 * padding),
        "height": float(max(ys) - min(ys) + 2 * padding),
        "points": points,
    }


def extract_polycoll_per_path(
    coll,
    paths,
    coll_idx: int,
    ax,
    ax_idx: int,
    fig,
    tight_bbox,
    img_width: int,
    img_height: int,
    scale_x: float,
    scale_y: float,
    pad_inches: float,
    saved_height_inches: float,
    bboxes: Dict[str, Any],
) -> None:
    """Extract per-path bboxes from PolyCollection (e.g., violin bodies).

    Each path becomes a separate bbox entry so individual violin bodies
    can be selected independently.

    Parameters
    ----------
    coll : PolyCollection
        The collection.
    paths : list
        Paths from ``coll.get_paths()``.
    coll_idx : int
        Index of the collection in ``ax.collections``.
    ax : Axes
        Parent axes.
    ax_idx : int
        Axes index.
    fig : Figure
        Parent figure.
    tight_bbox : Bbox
        Tight bounding box.
    img_width, img_height : int
        Rendered image dimensions.
    scale_x, scale_y : float
        Scale factors.
    pad_inches : float
        Padding in inches.
    saved_height_inches : float
        Saved figure height.
    bboxes : dict
        Output dict; new entries are added in-place.
    """
    transform = ax.transData
    label_base = coll.get_label() or "fill"

    for p_idx, path in enumerate(paths):
        verts = path.vertices
        if len(verts) == 0:
            continue

        points: List = []
        for v in verts:
            try:
                display_coords = transform.transform(v)
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
            continue

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        padding = 4
        bbox = {
            "x": float(min(xs) - padding),
            "y": float(min(ys) - padding),
            "width": float(max(xs) - min(xs) + 2 * padding),
            "height": float(max(ys) - min(ys) + 2 * padding),
        }
        bboxes[f"ax{ax_idx}_violin{coll_idx}_{p_idx}"] = {
            **bbox,
            "type": "fill",
            "label": f"{label_base}_{p_idx}",
            "ax_index": ax_idx,
        }


__all__ = ["extract_linecoll_with_points", "extract_polycoll_per_path"]

# EOF
