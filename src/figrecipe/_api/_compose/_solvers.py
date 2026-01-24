#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layout solvers for figure composition.

These solvers convert list-based sources into mm-based positioning specs.
All layout algorithms output a unified format that flows through the
mm-based composition pipeline.
"""

import math
from typing import Any, Dict, List, Tuple

from ._utils import load_images, px_to_mm


def solve_horizontal(
    sources: List[str],
    gap_mm: float,
    dpi: int,
    facecolor: str = "white",
) -> Tuple[Dict[str, Dict[str, Any]], Tuple[float, float]]:
    """Solve horizontal layout: panels arranged left to right.

    Parameters
    ----------
    sources : list of str
        Paths to source images or recipe files.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for size calculations.
    facecolor : str
        Background color for loading images.

    Returns
    -------
    sources_mm : dict
        Dict mapping source paths to {"xy_mm": (x, y), "size_mm": (w, h)}.
    canvas_size_mm : tuple
        Canvas size as (width_mm, height_mm).
    """
    images = load_images(sources, dpi, facecolor)
    if not images:
        raise ValueError("No valid source images provided")

    sources_mm = {}
    x_mm = 0.0
    max_h_mm = 0.0

    for source, img in zip(sources, images):
        w_mm = px_to_mm(img.width, dpi)
        h_mm = px_to_mm(img.height, dpi)

        sources_mm[source] = {
            "xy_mm": (x_mm, 0.0),
            "size_mm": (w_mm, h_mm),
        }

        x_mm += w_mm + gap_mm
        max_h_mm = max(max_h_mm, h_mm)

    # Canvas size: total width minus last gap, max height
    canvas_w_mm = x_mm - gap_mm if sources else 0.0
    canvas_size_mm = (canvas_w_mm, max_h_mm)

    return sources_mm, canvas_size_mm


def solve_vertical(
    sources: List[str],
    gap_mm: float,
    dpi: int,
    facecolor: str = "white",
) -> Tuple[Dict[str, Dict[str, Any]], Tuple[float, float]]:
    """Solve vertical layout: panels arranged top to bottom.

    Parameters
    ----------
    sources : list of str
        Paths to source images or recipe files.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for size calculations.
    facecolor : str
        Background color for loading images.

    Returns
    -------
    sources_mm : dict
        Dict mapping source paths to {"xy_mm": (x, y), "size_mm": (w, h)}.
    canvas_size_mm : tuple
        Canvas size as (width_mm, height_mm).
    """
    images = load_images(sources, dpi, facecolor)
    if not images:
        raise ValueError("No valid source images provided")

    sources_mm = {}
    y_mm = 0.0
    max_w_mm = 0.0

    for source, img in zip(sources, images):
        w_mm = px_to_mm(img.width, dpi)
        h_mm = px_to_mm(img.height, dpi)

        sources_mm[source] = {
            "xy_mm": (0.0, y_mm),
            "size_mm": (w_mm, h_mm),
        }

        y_mm += h_mm + gap_mm
        max_w_mm = max(max_w_mm, w_mm)

    # Canvas size: max width, total height minus last gap
    canvas_h_mm = y_mm - gap_mm if sources else 0.0
    canvas_size_mm = (max_w_mm, canvas_h_mm)

    return sources_mm, canvas_size_mm


def solve_grid(
    sources: List[str],
    gap_mm: float,
    dpi: int,
    facecolor: str = "white",
    ncols: int = None,
) -> Tuple[Dict[str, Dict[str, Any]], Tuple[float, float]]:
    """Solve grid layout: panels arranged in rows and columns.

    Parameters
    ----------
    sources : list of str
        Paths to source images or recipe files.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for size calculations.
    facecolor : str
        Background color for loading images.
    ncols : int, optional
        Number of columns. If None, auto-calculated as ceil(sqrt(n)).

    Returns
    -------
    sources_mm : dict
        Dict mapping source paths to {"xy_mm": (x, y), "size_mm": (w, h)}.
    canvas_size_mm : tuple
        Canvas size as (width_mm, height_mm).
    """
    images = load_images(sources, dpi, facecolor)
    if not images:
        raise ValueError("No valid source images provided")

    n = len(images)
    if ncols is None:
        ncols = math.ceil(math.sqrt(n))
    nrows = math.ceil(n / ncols)

    # Find max cell dimensions
    max_w_mm = max(px_to_mm(img.width, dpi) for img in images)
    max_h_mm = max(px_to_mm(img.height, dpi) for img in images)

    sources_mm = {}
    for idx, (source, img) in enumerate(zip(sources, images)):
        row = idx // ncols
        col = idx % ncols

        x_mm = col * (max_w_mm + gap_mm)
        y_mm = row * (max_h_mm + gap_mm)
        w_mm = px_to_mm(img.width, dpi)
        h_mm = px_to_mm(img.height, dpi)

        sources_mm[source] = {
            "xy_mm": (x_mm, y_mm),
            "size_mm": (w_mm, h_mm),
        }

    # Canvas size
    canvas_w_mm = ncols * max_w_mm + (ncols - 1) * gap_mm
    canvas_h_mm = nrows * max_h_mm + (nrows - 1) * gap_mm
    canvas_size_mm = (canvas_w_mm, canvas_h_mm)

    return sources_mm, canvas_size_mm


# Registry of layout solvers
LAYOUT_SOLVERS = {
    "horizontal": solve_horizontal,
    "vertical": solve_vertical,
    "grid": solve_grid,
}


def solve_layout(
    sources: List[str],
    layout: str,
    gap_mm: float,
    dpi: int,
    facecolor: str = "white",
    **kwargs,
) -> Tuple[Dict[str, Dict[str, Any]], Tuple[float, float]]:
    """Dispatch to appropriate layout solver.

    Parameters
    ----------
    sources : list of str
        Paths to source images or recipe files.
    layout : str
        Layout mode: 'horizontal', 'vertical', or 'grid'.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for size calculations.
    facecolor : str
        Background color for loading images.
    **kwargs
        Additional arguments passed to specific solvers.

    Returns
    -------
    sources_mm : dict
        Dict mapping source paths to {"xy_mm": (x, y), "size_mm": (w, h)}.
    canvas_size_mm : tuple
        Canvas size as (width_mm, height_mm).

    Raises
    ------
    ValueError
        If layout is not recognized.
    """
    if layout not in LAYOUT_SOLVERS:
        available = ", ".join(f"'{k}'" for k in LAYOUT_SOLVERS.keys())
        raise ValueError(f"Unknown layout: '{layout}'. Available: {available}")

    solver = LAYOUT_SOLVERS[layout]
    return solver(sources, gap_mm, dpi, facecolor, **kwargs)
