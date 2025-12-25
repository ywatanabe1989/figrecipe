#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for the figure editor.
"""

from typing import Any, Dict, Optional


def get_form_values_from_style(style: Dict[str, Any]) -> Dict[str, Any]:
    """Extract form field values from a style dictionary.

    Maps style dictionary values to HTML form input IDs.

    Parameters
    ----------
    style : dict
        Style configuration dictionary

    Returns
    -------
    dict
        Mapping of form input IDs to values
    """
    values = {}

    # Axes dimensions
    if "axes" in style:
        values["axes_width_mm"] = style["axes"].get("width_mm", 80)
        values["axes_height_mm"] = style["axes"].get("height_mm", 55)
        values["axes_thickness_mm"] = style["axes"].get("thickness_mm", 0.2)

    # Margins
    if "margins" in style:
        values["margins_left_mm"] = style["margins"].get("left_mm", 12)
        values["margins_right_mm"] = style["margins"].get("right_mm", 3)
        values["margins_bottom_mm"] = style["margins"].get("bottom_mm", 10)
        values["margins_top_mm"] = style["margins"].get("top_mm", 3)

    # Spacing
    if "spacing" in style:
        values["spacing_horizontal_mm"] = style["spacing"].get("horizontal_mm", 8)
        values["spacing_vertical_mm"] = style["spacing"].get("vertical_mm", 8)

    # Fonts
    if "fonts" in style:
        values["fonts_family"] = style["fonts"].get("family", "Arial")
        values["fonts_axis_label_pt"] = style["fonts"].get("axis_label_pt", 7)
        values["fonts_tick_label_pt"] = style["fonts"].get("tick_label_pt", 6)
        values["fonts_title_pt"] = style["fonts"].get("title_pt", 8)
        values["fonts_legend_pt"] = style["fonts"].get("legend_pt", 6)

    # Ticks
    if "ticks" in style:
        values["ticks_length_mm"] = style["ticks"].get("length_mm", 1.0)
        values["ticks_thickness_mm"] = style["ticks"].get("thickness_mm", 0.2)
        values["ticks_direction"] = style["ticks"].get("direction", "out")

    # Lines
    if "lines" in style:
        values["lines_trace_mm"] = style["lines"].get("trace_mm", 0.2)

    # Markers
    if "markers" in style:
        values["markers_size_mm"] = style["markers"].get("size_mm", 0.8)

    # Output
    if "output" in style:
        values["output_dpi"] = style["output"].get("dpi", 300)

    # Behavior
    if "behavior" in style:
        values["behavior_hide_top_spine"] = style["behavior"].get(
            "hide_top_spine", True
        )
        values["behavior_hide_right_spine"] = style["behavior"].get(
            "hide_right_spine", True
        )
        values["behavior_grid"] = style["behavior"].get("grid", False)

    # Legend
    if "legend" in style:
        values["legend_frameon"] = style["legend"].get("frameon", True)

    return values


def render_with_overrides(
    fig, overrides: Optional[Dict[str, Any]], dark_mode: bool = False
):
    """
    Re-render figure with overrides applied directly.

    Applies style overrides directly to the existing figure for reliable rendering.
    """
    import base64
    import io
    import warnings

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from PIL import Image

    from ._bbox import extract_bboxes

    # Get the underlying matplotlib figure
    new_fig = fig.fig if hasattr(fig, "fig") else fig

    # Safety check: validate figure size before rendering
    fig_width, fig_height = new_fig.get_size_inches()
    dpi = 150
    pixel_width = fig_width * dpi
    pixel_height = fig_height * dpi

    # Sanity check: prevent enormous figures (max 10000x10000 pixels)
    MAX_PIXELS = 10000
    if pixel_width > MAX_PIXELS or pixel_height > MAX_PIXELS:
        # Reset to reasonable size
        new_fig.set_size_inches(
            min(fig_width, MAX_PIXELS / dpi), min(fig_height, MAX_PIXELS / dpi)
        )

    # Switch to Agg backend to avoid Tkinter thread issues
    new_fig.set_canvas(FigureCanvasAgg(new_fig))

    # Disable constrained_layout if present (can cause rendering issues)
    layout_engine = new_fig.get_layout_engine()
    if layout_engine is not None and hasattr(layout_engine, "__class__"):
        layout_name = layout_engine.__class__.__name__
        if "Constrained" in layout_name:
            new_fig.set_layout_engine("none")

    # Apply overrides directly to existing figure
    # Get record for call_id grouping (if fig is a RecordingFigure)
    record = fig.record if hasattr(fig, "record") else None
    if overrides:
        from ._render_overrides import apply_overrides

        apply_overrides(new_fig, overrides, record)

    # Apply dark mode if requested
    if dark_mode:
        from ._render_overrides import apply_dark_mode

        apply_dark_mode(new_fig)

    # Validate axes bounds before rendering (prevent infinite/invalid extents)
    for ax in new_fig.get_axes():
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        # Check for invalid limits (inf, nan, or extremely large)
        if any(not (-1e10 < v < 1e10) for v in xlim + ylim):
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)

    # Save to PNG using same params as static save
    # Re-create canvas to ensure clean state (avoids matplotlib renderer issues)
    # Also save/restore the figure's draw method which can get corrupted by _get_renderer
    original_draw = getattr(new_fig, "draw", None)
    new_fig.set_canvas(FigureCanvasAgg(new_fig))

    buf = io.BytesIO()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "constrained_layout not applied")
        warnings.filterwarnings("ignore", category=UserWarning)
        try:
            # Don't use bbox_inches="tight" - it recalculates bounding box each time
            # causing layout shifts when elements change (e.g., pie chart colors)
            new_fig.savefig(buf, format="png", dpi=150)
        except Exception:
            # Fall back to saving without bbox_inches="tight"
            # Catches matplotlib internal exceptions (e.g., Done from _get_renderer)
            buf = io.BytesIO()
            # Reset canvas and draw method to clean state
            new_fig.set_canvas(FigureCanvasAgg(new_fig))
            if original_draw is not None:
                new_fig.draw = original_draw
            try:
                new_fig.savefig(buf, format="png", dpi=150)
            except Exception:
                # Last resort: create empty placeholder
                from PIL import Image as PILImage

                placeholder = PILImage.new("RGB", (400, 300), color=(240, 240, 240))
                placeholder.save(buf, format="PNG")
                buf.seek(0)
        finally:
            # Always restore original draw method to prevent corruption
            if original_draw is not None and hasattr(new_fig, "draw"):
                try:
                    new_fig.draw = original_draw
                except AttributeError:
                    pass
    buf.seek(0)
    png_bytes = buf.read()
    base64_str = base64.b64encode(png_bytes).decode("utf-8")

    # Get image size
    buf.seek(0)
    img = Image.open(buf)
    img_size = img.size

    # Extract bboxes
    # Ensure clean canvas state before drawing
    new_fig.set_canvas(FigureCanvasAgg(new_fig))
    original_dpi = new_fig.dpi
    new_fig.set_dpi(150)
    try:
        new_fig.canvas.draw()
    except Exception:
        # Canvas draw failed, likely due to corrupted state - reset and retry
        new_fig.set_canvas(FigureCanvasAgg(new_fig))
        try:
            new_fig.canvas.draw()
        except Exception:
            pass  # If still fails, proceed with possibly stale bboxes
    bboxes = extract_bboxes(new_fig, img_size[0], img_size[1])
    new_fig.set_dpi(original_dpi)

    return base64_str, bboxes, img_size


def to_json_serializable(obj):
    """Convert numpy arrays and other non-serializable objects to JSON-safe types."""
    import numpy as np

    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    # Handle pandas Series
    elif hasattr(obj, "values") and hasattr(obj, "tolist"):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_json_serializable(item) for item in obj]
    return obj


__all__ = [
    "get_form_values_from_style",
    "render_with_overrides",
    "to_json_serializable",
]
