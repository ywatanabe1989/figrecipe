#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Free-form mm-based positioning for figure composition."""

from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from ._utils import load_images, mm_to_px, resize_to_fit


def _get_background_rgba(facecolor: str) -> tuple:
    """Convert facecolor string to RGBA tuple."""
    if facecolor.lower() == "white":
        return (255, 255, 255, 255)
    elif facecolor.lower() == "black":
        return (0, 0, 0, 255)
    else:
        try:
            from PIL import ImageColor

            rgb = ImageColor.getrgb(facecolor)
            return (*rgb, 255)
        except ValueError:
            return (255, 255, 255, 255)


def compose_freeform(
    sources: Dict[str, Dict[str, Any]],
    canvas_size_mm: Optional[Tuple[float, float]],
    dpi: int,
    facecolor: str = "white",
) -> Tuple[Image.Image, List[Tuple[int, int, int, int]], List[str]]:
    """Compose images with free-form mm-based positioning.

    Parameters
    ----------
    sources : dict
        Mapping of source paths to positioning specs.
        Each spec should have 'xy_mm' (x, y) and 'size_mm' (width, height).
    canvas_size_mm : tuple or None
        Canvas size as (width_mm, height_mm). If None, auto-calculated.
    dpi : int
        Output DPI.
    facecolor : str
        Background color for the canvas. Default is 'white'.

    Returns
    -------
    result : Image
        Composed image.
    positions : list
        List of (x, y, width, height) in pixels for each panel.
    source_paths : list
        List of source paths in order.

    Examples
    --------
    >>> sources = {
    ...     "panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)},
    ...     "panel_b.yaml": {"xy_mm": (90, 0), "size_mm": (80, 50)},
    ...     "panel_c.yaml": {"xy_mm": (0, 60), "size_mm": (170, 50)},
    ... }
    >>> result, positions, paths = compose_freeform(sources, (180, 120), 300)
    """
    if not sources:
        raise ValueError("No sources provided for composition")

    # Validate and extract positioning info
    panels = []
    for source_path, spec in sources.items():
        if not isinstance(spec, dict):
            raise ValueError(
                f"Source spec for '{source_path}' must be a dict "
                "with 'xy_mm' and 'size_mm'"
            )

        xy_mm = spec.get("xy_mm")
        size_mm = spec.get("size_mm")

        if xy_mm is None or size_mm is None:
            raise ValueError(
                f"Source '{source_path}' missing required 'xy_mm' or 'size_mm'"
            )

        x_mm, y_mm = xy_mm
        w_mm, h_mm = size_mm

        panels.append(
            {
                "path": source_path,
                "x_mm": x_mm,
                "y_mm": y_mm,
                "w_mm": w_mm,
                "h_mm": h_mm,
            }
        )

    # Determine canvas size
    if canvas_size_mm is not None:
        canvas_w_mm, canvas_h_mm = canvas_size_mm
    else:
        # Auto-calculate canvas size to fit all panels
        max_x = max(p["x_mm"] + p["w_mm"] for p in panels)
        max_y = max(p["y_mm"] + p["h_mm"] for p in panels)
        canvas_w_mm = max_x
        canvas_h_mm = max_y

    canvas_w_px = mm_to_px(canvas_w_mm, dpi)
    canvas_h_px = mm_to_px(canvas_h_mm, dpi)

    # Create canvas with specified facecolor
    bg_rgba = _get_background_rgba(facecolor)
    result = Image.new("RGBA", (canvas_w_px, canvas_h_px), bg_rgba)

    # Load and place each panel
    positions = []
    source_paths = []

    for panel in panels:
        # Load image with consistent facecolor
        images = load_images([panel["path"]], dpi, facecolor)
        if not images:
            raise ValueError(f"Could not load source: {panel['path']}")
        img = images[0]

        # Calculate pixel positions and sizes
        x_px = mm_to_px(panel["x_mm"], dpi)
        y_px = mm_to_px(panel["y_mm"], dpi)
        w_px = mm_to_px(panel["w_mm"], dpi)
        h_px = mm_to_px(panel["h_mm"], dpi)

        # Resize image to target size while maintaining aspect ratio
        img_resized = resize_to_fit(img, w_px, h_px)

        # Center the resized image within the target area
        offset_x = (w_px - img_resized.width) // 2
        offset_y = (h_px - img_resized.height) // 2

        # Paste image onto canvas
        result.paste(img_resized, (x_px + offset_x, y_px + offset_y))

        # Record position (using actual resized image dimensions for label placement)
        positions.append(
            (
                x_px + offset_x,
                y_px + offset_y,
                img_resized.width,
                img_resized.height,
            )
        )
        source_paths.append(panel["path"])

    return result, positions, source_paths
