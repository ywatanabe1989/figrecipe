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
    mpl_fig = fig.fig if hasattr(fig, "fig") else fig

    # Apply style overrides
    if overrides:
        _apply_overrides(mpl_fig, overrides)

    # Apply dark mode if requested
    if dark_mode:
        _apply_dark_mode(mpl_fig)

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
        # YAML-compatible keys are canonical, legacy keys supported for backwards compatibility

        # Font sizes (YAML: fonts_axis_label_pt, legacy: axis_font_size_pt)
        axis_fs = overrides.get(
            "fonts_axis_label_pt", overrides.get("axis_font_size_pt")
        )
        if axis_fs is not None:
            ax.xaxis.label.set_fontsize(axis_fs)
            ax.yaxis.label.set_fontsize(axis_fs)

        tick_fs = overrides.get(
            "fonts_tick_label_pt", overrides.get("tick_font_size_pt")
        )
        if tick_fs is not None:
            ax.tick_params(labelsize=tick_fs)

        title_fs = overrides.get("fonts_title_pt", overrides.get("title_font_size_pt"))
        if title_fs is not None:
            ax.title.set_fontsize(title_fs)

        family = overrides.get("fonts_family", overrides.get("font_family"))
        if family is not None:
            ax.xaxis.label.set_fontfamily(family)
            ax.yaxis.label.set_fontfamily(family)
            ax.title.set_fontfamily(family)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontfamily(family)

        # Ticks (YAML: ticks_direction, legacy: tick_direction)
        tick_dir = overrides.get("ticks_direction", overrides.get("tick_direction"))
        if tick_dir is not None and tick_dir in ("in", "out", "inout"):
            ax.tick_params(direction=tick_dir)

        tick_len = overrides.get("ticks_length_mm", overrides.get("tick_length_mm"))
        if tick_len is not None:
            from .._utils._units import mm_to_pt

            length = mm_to_pt(tick_len)
            ax.tick_params(length=length)

        # Grid (YAML: behavior_grid, legacy: grid)
        grid_value = overrides.get("behavior_grid", overrides.get("grid"))
        if grid_value is not None:
            if grid_value:
                ax.grid(True, alpha=0.3)
            else:
                ax.grid(False)

        # Spines (YAML: behavior_hide_top_spine, legacy: hide_top_spine)
        hide_top = overrides.get(
            "behavior_hide_top_spine", overrides.get("hide_top_spine")
        )
        if hide_top is not None:
            ax.spines["top"].set_visible(not hide_top)

        hide_right = overrides.get(
            "behavior_hide_right_spine", overrides.get("hide_right_spine")
        )
        if hide_right is not None:
            ax.spines["right"].set_visible(not hide_right)

        # Legend
        legend = ax.get_legend()
        if legend is not None:
            if "legend_frameon" in overrides:
                legend.set_frame_on(overrides["legend_frameon"])

            if "legend_alpha" in overrides:
                frame = legend.get_frame()
                fc = frame.get_facecolor()
                frame.set_facecolor((*fc[:3], overrides["legend_alpha"]))

        # Line widths (YAML: lines_trace_mm, legacy: trace_thickness_mm)
        trace_mm = overrides.get("lines_trace_mm", overrides.get("trace_thickness_mm"))
        if trace_mm is not None:
            from .._utils._units import mm_to_pt

            lw = mm_to_pt(trace_mm)
            for line in ax.get_lines():
                line.set_linewidth(lw)

        # Marker sizes (YAML: markers_scatter_mm, legacy: marker_size_mm)
        # Only apply to PathCollection (scatter), not PolyCollection (violin/fill)
        scatter_mm = overrides.get(
            "markers_scatter_mm",
            overrides.get("markers_size_mm", overrides.get("marker_size_mm")),
        )
        if scatter_mm is not None:
            from matplotlib.collections import PathCollection

            from .._utils._units import mm_to_scatter_size

            size = mm_to_scatter_size(scatter_mm)
            for coll in ax.collections:
                # Only apply to scatter plots (PathCollection), not violin/fill (PolyCollection)
                if isinstance(coll, PathCollection):
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
    bg_color = "#1a1a1a"
    text_color = "#e8e8e8"

    # Figure background
    fig.patch.set_facecolor(bg_color)

    # Figure-level text elements (suptitle, supxlabel, supylabel)
    if hasattr(fig, "_suptitle") and fig._suptitle is not None:
        fig._suptitle.set_color(text_color)
    if hasattr(fig, "_supxlabel") and fig._supxlabel is not None:
        fig._supxlabel.set_color(text_color)
    if hasattr(fig, "_supylabel") and fig._supylabel is not None:
        fig._supylabel.set_color(text_color)

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

    if overrides:
        _apply_overrides(mpl_fig, overrides)

    if dark_mode:
        _apply_dark_mode(mpl_fig)

    buf = io.BytesIO()
    mpl_fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
    buf.seek(0)

    return buf.read()


__all__ = [
    "render_preview",
    "render_to_base64",
    "render_download",
]
