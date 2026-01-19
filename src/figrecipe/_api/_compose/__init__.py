#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure composition utilities for combining multiple figures.

This module provides two composition modes:
1. Grid-based layout: Automatic arrangement using 'horizontal', 'vertical', or 'grid'
2. Free-form positioning: Precise mm-based placement with canvas_size_mm and per-source xy_mm/size_mm
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ._freeform import compose_freeform
from ._grid import compose_grid_layout
from ._utils import (
    add_caption,
    add_panel_labels,
    create_source_symlinks,
    load_images,
    mm_to_px,
)


def compose_figures(
    sources: Union[List[str], Dict[str, Dict[str, Any]]],
    output_path: str,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    label_fontsize: int = 10,
    label_fontweight: str = "bold",
    caption: Optional[str] = None,
    caption_fontsize: int = 8,
    create_symlinks: bool = True,
    canvas_size_mm: Optional[Tuple[float, float]] = None,
    facecolor: str = "white",
) -> Dict[str, Any]:
    """Compose multiple figures into a single figure.

    Supports two modes:
    1. Grid-based layout (list sources): automatic arrangement with layout parameter
    2. Free-form positioning (dict sources): precise mm-based positioning

    Parameters
    ----------
    sources : list of str or dict
        Either:
        - List of paths to source images or recipe files (grid-based layout)
        - Dict mapping source paths to positioning specs with 'xy_mm' and 'size_mm':
          {"panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)}, ...}
    output_path : str
        Path to save the composed figure.
    layout : str
        Layout mode for list sources: 'horizontal', 'vertical', or 'grid'.
        Ignored when using dict sources with mm positioning.
    gap_mm : float
        Gap between panels in millimeters (for grid-based layout only).
    dpi : int
        DPI for output.
    panel_labels : bool
        If True, add panel labels (A, B, C, D) to each panel.
    label_style : str
        Label style: 'uppercase' (A, B, C), 'lowercase' (a, b, c), 'numeric' (1, 2, 3).
    label_fontsize : int
        Font size for panel labels.
    label_fontweight : str
        Font weight for panel labels ('bold', 'normal').
    caption : str, optional
        Figure caption to add below the composed figure.
    caption_fontsize : int
        Font size for caption.
    create_symlinks : bool
        If True (default), create symlinks to source files in a subdirectory
        for traceability and single source of truth.
    canvas_size_mm : tuple of (float, float), optional
        Canvas size as (width_mm, height_mm) for free-form positioning.
        Required when sources is a dict with mm positioning.
    facecolor : str
        Background color for the composed figure and all panels.
        Default is 'white'. Use this to ensure consistent backgrounds
        when source panels have different/transparent backgrounds.

    Returns
    -------
    dict
        Result with 'output_path', 'success', and 'sources_dir' (if symlinks created).

    Examples
    --------
    Grid-based layout (existing API):

    >>> compose_figures(
    ...     sources=["panel_a.png", "panel_b.png"],
    ...     output_path="figure.png",
    ...     layout="horizontal",
    ...     gap_mm=5.0,
    ... )

    Free-form mm-based positioning:

    >>> compose_figures(
    ...     canvas_size_mm=(180, 120),
    ...     sources={
    ...         "panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)},
    ...         "panel_b.yaml": {"xy_mm": (90, 0), "size_mm": (80, 50)},
    ...         "panel_c.yaml": {"xy_mm": (0, 60), "size_mm": (170, 50)},
    ...     },
    ...     output_path="figure.png",
    ... )
    """
    output_path = Path(output_path)

    # Determine if using free-form mm positioning or grid-based layout
    if isinstance(sources, dict):
        # Free-form mm-based positioning
        result, positions, source_paths = compose_freeform(
            sources, canvas_size_mm, dpi, facecolor
        )
    else:
        # Grid-based layout (original behavior)
        gap_px = mm_to_px(gap_mm, dpi)
        images = load_images(sources, dpi, facecolor)
        if not images:
            raise ValueError("No valid source images provided")
        result, positions = compose_grid_layout(images, layout, gap_px, facecolor)
        source_paths = sources

    # Add panel labels if requested
    if panel_labels:
        result = add_panel_labels(
            result, positions, label_style, label_fontsize, label_fontweight, dpi
        )

    # Add caption if provided
    if caption:
        result = add_caption(result, caption, caption_fontsize, dpi)

    # Save result
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        result = result.convert("RGB")
    result.save(output_path, dpi=(dpi, dpi))

    result_dict = {
        "output_path": str(output_path),
        "success": True,
    }

    # Create symlinks to source files for traceability
    if create_symlinks:
        sources_dir = create_source_symlinks(source_paths, output_path)
        if sources_dir:
            result_dict["sources_dir"] = str(sources_dir)

    return result_dict


__all__ = ["compose_figures"]
