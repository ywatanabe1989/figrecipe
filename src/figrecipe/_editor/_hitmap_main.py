#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hitmap generation for interactive element selection.

This module generates color-coded images where each figure element
(line, scatter, bar, text, etc.) is rendered with a unique RGB color.
This enables precise pixel-based element detection when users click
on the figure preview.

The color encoding uses 24-bit RGB:
- First 12 elements: hand-picked visually distinct colors
- Elements 13+: HSV-based generation for deterministic uniqueness
"""

import io
from typing import Any, Dict, Tuple

from matplotlib.figure import Figure
from PIL import Image


def generate_hitmap(
    fig: Figure,
    dpi: int = 150,
    include_text: bool = True,
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Generate hitmap with unique colors per element.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to generate hitmap for.
    dpi : int, optional
        Resolution for hitmap rendering (default: 150).
    include_text : bool, optional
        Whether to include text elements like labels (default: True).

    Returns
    -------
    hitmap : PIL.Image.Image
        RGB image where each element has unique color.
    color_map : dict
        Mapping from element key to metadata:
        {
            'element_key': {
                'id': int,
                'type': str,  # 'line', 'scatter', 'bar', 'boxplot', 'violin', etc.
                'label': str,
                'ax_index': int,
                'rgb': [r, g, b],
            }
        }
    """
    # Import from helper modules (inside function to avoid circular imports)
    from ._hitmap._artists import (
        process_collections,
        process_figure_text,
        process_images,
        process_legend,
        process_lines,
        process_patches,
        process_text,
    )
    from ._hitmap._colors import (
        AXES_COLOR,
        BACKGROUND_COLOR,
        normalize_color,
    )
    from ._hitmap._detect import detect_plot_types
    from ._hitmap._restore import (
        restore_axes_properties,
        restore_backgrounds,
        restore_figure_text,
    )

    # Store original properties for restoration
    original_props = {}
    color_map = {}
    element_id = 1

    # Detect plot types from record
    plot_types = detect_plot_types(fig, debug=False)

    # Get all axes (handle RecordingFigure wrapper)
    if hasattr(fig, "fig"):
        mpl_fig = fig.fig
    else:
        mpl_fig = fig
    axes_list = mpl_fig.get_axes()

    # Process all artists and assign colors
    for ax_idx, ax in enumerate(axes_list):
        ax_info = plot_types.get(ax_idx, {"types": set(), "call_ids": {}})

        # Process lines
        element_id = process_lines(
            ax, ax_idx, element_id, original_props, color_map, ax_info
        )

        # Process collections (scatter, fills, etc.)
        element_id = process_collections(
            ax, ax_idx, element_id, original_props, color_map, ax_info
        )

        # Process patches (bars, wedges, polygons)
        element_id = process_patches(
            ax, ax_idx, element_id, original_props, color_map, ax_info
        )

        # Process images
        element_id = process_images(ax, ax_idx, element_id, color_map, ax_info)

        # Process text elements
        if include_text:
            element_id = process_text(ax, ax_idx, element_id, original_props, color_map)

        # Process legend
        element_id = process_legend(ax, ax_idx, element_id, original_props, color_map)

    # Process figure-level text elements
    if include_text:
        element_id = process_figure_text(mpl_fig, element_id, original_props, color_map)

    # Set non-selectable elements to axes color
    for ax in axes_list:
        for spine in ax.spines.values():
            spine.set_color(normalize_color(AXES_COLOR))
        ax.tick_params(colors=normalize_color(AXES_COLOR))

    # Set figure background
    fig.patch.set_facecolor(normalize_color(BACKGROUND_COLOR))
    for ax in axes_list:
        ax.set_facecolor(normalize_color(BACKGROUND_COLOR))

    # Render to buffer
    # IMPORTANT: Do NOT use bbox_inches="tight" - it causes dimension changes
    # between renders when elements change (e.g., color). Must match main render.
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=fig.get_facecolor())
    buf.seek(0)

    # Load as PIL Image
    hitmap = Image.open(buf).convert("RGB")

    # Restore original properties
    restore_axes_properties(axes_list, original_props, include_text)
    restore_figure_text(mpl_fig, original_props, include_text)
    restore_backgrounds(fig, axes_list)

    return hitmap, color_map


def hitmap_to_base64(hitmap: Image.Image) -> str:
    """
    Convert hitmap image to base64 string.

    Parameters
    ----------
    hitmap : PIL.Image.Image
        Hitmap image.

    Returns
    -------
    str
        Base64-encoded PNG string.
    """
    import base64

    buf = io.BytesIO()
    hitmap.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


__all__ = [
    "generate_hitmap",
    "hitmap_to_base64",
]

# EOF
