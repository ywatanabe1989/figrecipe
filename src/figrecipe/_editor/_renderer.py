#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preview rendering with style overrides.

This module renders figure previews with user-specified style overrides
applied, enabling real-time preview updates in the GUI editor.
"""

import io
from typing import Any, Dict, Optional, Tuple

from .._wrappers import RecordingFigure
from ._bbox import extract_bboxes
from ._render_overrides import apply_dark_mode, apply_overrides


def render_preview(
    fig: RecordingFigure,
    overrides: Optional[Dict[str, Any]] = None,
    dpi: int = 150,
    dark_mode: bool = False,
) -> Tuple[bytes, Dict[str, Any], Tuple[int, int]]:
    """
    Render figure preview with style overrides applied.

    Parameters
    ----------
    fig : RecordingFigure
        Figure to render.
    overrides : dict, optional
        Style overrides to apply.
    dpi : int, optional
        Render resolution (default: 150).
    dark_mode : bool, optional
        Whether to render in dark mode (default: False).

    Returns
    -------
    png_bytes : bytes
        PNG image data.
    bboxes : dict
        Element bounding boxes.
    img_size : tuple
        (width, height) in pixels.
    """
    # Get underlying matplotlib figure
    mpl_fig = fig.fig if hasattr(fig, "fig") else fig

    # Get record for call_id grouping (if fig is a RecordingFigure)
    record = fig.record if hasattr(fig, "record") else None

    # Apply style overrides
    if overrides:
        apply_overrides(mpl_fig, overrides, record)

    # Apply dark mode if requested
    if dark_mode:
        apply_dark_mode(mpl_fig)

    # Finalize ticks and special plots (must be done after all plotting)
    _finalize_figure(fig, mpl_fig)

    # Render to buffer first
    buf = io.BytesIO()
    mpl_fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    png_bytes = buf.read()

    # Get image dimensions
    from PIL import Image

    buf.seek(0)
    img = Image.open(buf)
    img_width, img_height = img.size

    # Set figure DPI to match render DPI and force canvas redraw for accurate bbox extraction
    original_dpi = mpl_fig.dpi
    mpl_fig.set_dpi(dpi)
    mpl_fig.canvas.draw()

    # Extract bounding boxes (with figure DPI matching render DPI)
    bboxes = extract_bboxes(mpl_fig, img_width, img_height)

    # Restore original DPI
    mpl_fig.set_dpi(original_dpi)

    return png_bytes, bboxes, (img_width, img_height)


def render_to_base64(
    fig: RecordingFigure,
    overrides: Optional[Dict[str, Any]] = None,
    dpi: int = 150,
    dark_mode: bool = False,
) -> Tuple[str, Dict[str, Any], Tuple[int, int]]:
    """
    Render figure preview as base64 string.

    Parameters
    ----------
    fig : RecordingFigure
        Figure to render.
    overrides : dict, optional
        Style overrides to apply.
    dpi : int, optional
        Render resolution (default: 150).
    dark_mode : bool, optional
        Whether to render in dark mode (default: False).

    Returns
    -------
    base64_str : str
        Base64-encoded PNG image.
    bboxes : dict
        Element bounding boxes.
    img_size : tuple
        (width, height) in pixels.
    """
    import base64

    png_bytes, bboxes, img_size = render_preview(fig, overrides, dpi, dark_mode)
    base64_str = base64.b64encode(png_bytes).decode("utf-8")

    return base64_str, bboxes, img_size


def render_download(
    fig: RecordingFigure,
    fmt: str = "png",
    dpi: int = 300,
    overrides: Optional[Dict[str, Any]] = None,
    dark_mode: bool = False,
) -> bytes:
    """
    Render figure for download in specified format.

    Parameters
    ----------
    fig : RecordingFigure
        Figure to render.
    fmt : str
        Output format: 'png', 'svg', 'pdf' (default: 'png').
    dpi : int
        Resolution for raster formats (default: 300).
    overrides : dict, optional
        Style overrides to apply.
    dark_mode : bool, optional
        Whether to render in dark mode.

    Returns
    -------
    bytes
        File content.
    """
    mpl_fig = fig.fig if hasattr(fig, "fig") else fig

    # Get record for call_id grouping (if fig is a RecordingFigure)
    record = fig.record if hasattr(fig, "record") else None

    if overrides:
        apply_overrides(mpl_fig, overrides, record)

    if dark_mode:
        apply_dark_mode(mpl_fig)

    # Finalize ticks and special plots (must be done after all plotting)
    _finalize_figure(fig, mpl_fig)

    buf = io.BytesIO()
    mpl_fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
    buf.seek(0)

    return buf.read()


def _finalize_figure(fig: RecordingFigure, mpl_fig: Any) -> None:
    """Finalize ticks and special plots for all axes in the figure."""
    from ..styles._style_applier import finalize_special_plots, finalize_ticks

    # Get style dict for finalization
    style_dict = {}
    if hasattr(fig, "style") and fig.style:
        from ..styles import get_style

        style_dict = get_style(fig.style)

    for ax in mpl_fig.get_axes():
        finalize_ticks(ax)
        finalize_special_plots(ax, style_dict)


__all__ = [
    "render_preview",
    "render_to_base64",
    "render_download",
]

# EOF
