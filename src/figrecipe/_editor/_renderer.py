#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preview rendering with style overrides.

This module renders figure previews with user-specified style overrides
applied, enabling real-time preview updates in the GUI editor.
"""

import io
from typing import Any, Dict, Optional, Tuple

from matplotlib.figure import Figure

from .._wrappers import RecordingFigure
from ._bbox import extract_bboxes


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
    mpl_fig = fig.fig if hasattr(fig, 'fig') else fig

    # Apply style overrides
    if overrides:
        _apply_overrides(mpl_fig, overrides)

    # Apply dark mode if requested
    if dark_mode:
        _apply_dark_mode(mpl_fig)

    # Render to buffer
    buf = io.BytesIO()
    mpl_fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    png_bytes = buf.read()

    # Get image dimensions
    from PIL import Image
    buf.seek(0)
    img = Image.open(buf)
    img_width, img_height = img.size

    # Extract bounding boxes
    bboxes = extract_bboxes(mpl_fig, img_width, img_height)

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
    base64_str = base64.b64encode(png_bytes).decode('utf-8')

    return base64_str, bboxes, img_size


def _apply_overrides(fig: Figure, overrides: Dict[str, Any]) -> None:
    """
    Apply style overrides to figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure.
    overrides : dict
        Style overrides with keys like:
        - axes_width_mm, axes_height_mm
        - fonts_axis_label_pt, fonts_tick_label_pt
        - lines_trace_mm
        - etc.
    """
    from ..styles._style_applier import apply_style_mm

    axes_list = fig.get_axes()

    for ax in axes_list:
        # Apply mm-based styling
        apply_style_mm(ax, overrides)

        # Apply specific overrides that aren't handled by apply_style_mm

        # Font sizes
        if 'fonts_axis_label_pt' in overrides:
            fontsize = overrides['fonts_axis_label_pt']
            ax.xaxis.label.set_fontsize(fontsize)
            ax.yaxis.label.set_fontsize(fontsize)

        if 'fonts_tick_label_pt' in overrides:
            fontsize = overrides['fonts_tick_label_pt']
            ax.tick_params(labelsize=fontsize)

        if 'fonts_title_pt' in overrides:
            ax.title.set_fontsize(overrides['fonts_title_pt'])

        if 'fonts_family' in overrides:
            family = overrides['fonts_family']
            ax.xaxis.label.set_fontfamily(family)
            ax.yaxis.label.set_fontfamily(family)
            ax.title.set_fontfamily(family)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontfamily(family)

        # Ticks
        if 'ticks_direction' in overrides:
            ax.tick_params(direction=overrides['ticks_direction'])

        if 'ticks_length_mm' in overrides:
            from .._utils._units import mm_to_pt
            length = mm_to_pt(overrides['ticks_length_mm'])
            ax.tick_params(length=length)

        # Grid
        if 'behavior_grid' in overrides:
            if overrides['behavior_grid']:
                ax.grid(True, alpha=0.3)
            else:
                ax.grid(False)

        # Spines
        if 'behavior_hide_top_spine' in overrides:
            ax.spines['top'].set_visible(not overrides['behavior_hide_top_spine'])

        if 'behavior_hide_right_spine' in overrides:
            ax.spines['right'].set_visible(not overrides['behavior_hide_right_spine'])

        # Legend
        legend = ax.get_legend()
        if legend is not None:
            if 'legend_frameon' in overrides:
                legend.set_frame_on(overrides['legend_frameon'])

            if 'legend_alpha' in overrides:
                frame = legend.get_frame()
                fc = frame.get_facecolor()
                frame.set_facecolor((*fc[:3], overrides['legend_alpha']))

        # Line widths (for existing lines)
        if 'lines_trace_mm' in overrides:
            from .._utils._units import mm_to_pt
            lw = mm_to_pt(overrides['lines_trace_mm'])
            for line in ax.get_lines():
                line.set_linewidth(lw)

        # Marker sizes
        if 'markers_scatter_mm' in overrides:
            from .._utils._units import mm_to_scatter_size
            size = mm_to_scatter_size(overrides['markers_scatter_mm'])
            for coll in ax.collections:
                try:
                    coll.set_sizes([size])
                except Exception:
                    pass


def _apply_dark_mode(fig: Figure) -> None:
    """
    Apply dark mode colors to figure.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure.
    """
    # Dark theme colors
    bg_color = '#1a1a1a'
    text_color = '#e8e8e8'
    grid_color = '#404040'

    # Figure background
    fig.patch.set_facecolor(bg_color)

    for ax in fig.get_axes():
        # Axes background
        ax.set_facecolor(bg_color)

        # Text colors
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)

        # Tick labels
        ax.tick_params(colors=text_color)

        # Spines
        for spine in ax.spines.values():
            spine.set_color(text_color)

        # Grid
        ax.tick_params(color=text_color)

        # Legend
        legend = ax.get_legend()
        if legend is not None:
            frame = legend.get_frame()
            frame.set_facecolor(bg_color)
            frame.set_edgecolor(text_color)
            for text in legend.get_texts():
                text.set_color(text_color)


def render_download(
    fig: RecordingFigure,
    fmt: str = 'png',
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
    mpl_fig = fig.fig if hasattr(fig, 'fig') else fig

    if overrides:
        _apply_overrides(mpl_fig, overrides)

    if dark_mode:
        _apply_dark_mode(mpl_fig)

    buf = io.BytesIO()
    mpl_fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches='tight')
    buf.seek(0)

    return buf.read()


__all__ = [
    'render_preview',
    'render_to_base64',
    'render_download',
]
