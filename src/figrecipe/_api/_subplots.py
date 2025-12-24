#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Subplots helper implementation for the public API."""

from typing import Any, Dict, Optional, Tuple, Union

from numpy.typing import NDArray

from .._utils._units import mm_to_inch
from .._wrappers import RecordingAxes, RecordingFigure


def _get_mm_value(explicit, global_style, style_path, default):
    """Get mm value with priority: explicit > global style > default."""
    if explicit is not None:
        return explicit
    if global_style is not None:
        try:
            val = global_style
            for key in style_path:
                val = val.get(key) if isinstance(val, dict) else getattr(val, key, None)
                if val is None:
                    break
            if val is not None:
                return val
        except (KeyError, AttributeError):
            pass
    return default


def _check_mm_layout(
    axes_width_mm,
    axes_height_mm,
    margin_left_mm,
    margin_right_mm,
    margin_bottom_mm,
    margin_top_mm,
    space_w_mm,
    space_h_mm,
    global_style,
):
    """Check if mm-based layout is requested."""
    has_explicit_mm = any(
        [
            axes_width_mm is not None,
            axes_height_mm is not None,
            margin_left_mm is not None,
            margin_right_mm is not None,
            margin_bottom_mm is not None,
            margin_top_mm is not None,
            space_w_mm is not None,
            space_h_mm is not None,
        ]
    )

    has_style_mm = False
    if global_style is not None:
        try:
            has_style_mm = (
                global_style.get("axes", {}).get("width_mm") is not None
                or getattr(getattr(global_style, "axes", None), "width_mm", None)
                is not None
            )
        except (KeyError, AttributeError):
            pass

    return has_explicit_mm or has_style_mm


def _calculate_mm_layout(
    nrows: int,
    ncols: int,
    axes_width_mm: Optional[float],
    axes_height_mm: Optional[float],
    margin_left_mm: Optional[float],
    margin_right_mm: Optional[float],
    margin_bottom_mm: Optional[float],
    margin_top_mm: Optional[float],
    space_w_mm: Optional[float],
    space_h_mm: Optional[float],
    global_style,
    kwargs: Dict[str, Any],
) -> Tuple[Optional[Dict[str, float]], Dict[str, Any]]:
    """Calculate mm-based layout and update kwargs with figsize."""
    aw = _get_mm_value(axes_width_mm, global_style, ["axes", "width_mm"], 40)
    ah = _get_mm_value(axes_height_mm, global_style, ["axes", "height_mm"], 28)
    ml = _get_mm_value(margin_left_mm, global_style, ["margins", "left_mm"], 15)
    mr = _get_mm_value(margin_right_mm, global_style, ["margins", "right_mm"], 5)
    mb = _get_mm_value(margin_bottom_mm, global_style, ["margins", "bottom_mm"], 12)
    mt = _get_mm_value(margin_top_mm, global_style, ["margins", "top_mm"], 8)
    sw = _get_mm_value(space_w_mm, global_style, ["spacing", "horizontal_mm"], 8)
    sh = _get_mm_value(space_h_mm, global_style, ["spacing", "vertical_mm"], 10)

    # Calculate total figure size
    total_width_mm = ml + (ncols * aw) + ((ncols - 1) * sw) + mr
    total_height_mm = mb + (nrows * ah) + ((nrows - 1) * sh) + mt

    # Convert to inches and set figsize
    kwargs["figsize"] = (mm_to_inch(total_width_mm), mm_to_inch(total_height_mm))

    mm_layout = {
        "axes_width_mm": aw,
        "axes_height_mm": ah,
        "margin_left_mm": ml,
        "margin_right_mm": mr,
        "margin_bottom_mm": mb,
        "margin_top_mm": mt,
        "space_w_mm": sw,
        "space_h_mm": sh,
    }

    return mm_layout, kwargs


def _apply_mm_layout_to_figure(
    fig: RecordingFigure,
    mm_layout: Dict[str, float],
    nrows: int,
    ncols: int,
):
    """Apply mm-based layout adjustments to figure."""
    ml = mm_layout["margin_left_mm"]
    mr = mm_layout["margin_right_mm"]
    mb = mm_layout["margin_bottom_mm"]
    mt = mm_layout["margin_top_mm"]
    aw = mm_layout["axes_width_mm"]
    ah = mm_layout["axes_height_mm"]
    sw = mm_layout["space_w_mm"]
    sh = mm_layout["space_h_mm"]

    total_width_mm = ml + (ncols * aw) + ((ncols - 1) * sw) + mr
    total_height_mm = mb + (nrows * ah) + ((nrows - 1) * sh) + mt

    # Calculate relative positions (0-1 range)
    left = ml / total_width_mm
    right = 1 - (mr / total_width_mm)
    bottom = mb / total_height_mm
    top = 1 - (mt / total_height_mm)

    # Calculate spacing as fraction of figure size
    wspace = sw / aw if ncols > 1 else 0
    hspace = sh / ah if nrows > 1 else 0

    fig.fig.subplots_adjust(
        left=left,
        right=right,
        bottom=bottom,
        top=top,
        wspace=wspace,
        hspace=hspace,
    )

    # Record layout in figure record for reproduction
    fig.record.layout = {
        "left": left,
        "right": right,
        "bottom": bottom,
        "top": top,
        "wspace": wspace,
        "hspace": hspace,
    }


def _apply_style_to_axes(
    fig: RecordingFigure,
    axes: Union[RecordingAxes, NDArray],
    nrows: int,
    ncols: int,
    style: Optional[Dict[str, Any]],
    apply_style_mm: bool,
    global_style,
) -> Optional[Dict[str, Any]]:
    """Apply style to axes and return style dict if applied."""
    import numpy as np

    from ..styles import apply_style_mm as _apply_style
    from ..styles import to_subplots_kwargs

    style_dict = None
    should_apply_style = False

    if style is not None:
        should_apply_style = True
        style_dict = (
            style.to_subplots_kwargs()
            if hasattr(style, "to_subplots_kwargs")
            else style
        )
    elif apply_style_mm and global_style is not None:
        style_dict = to_subplots_kwargs(global_style)
        if style_dict and style_dict.get("axes_thickness_mm") is not None:
            should_apply_style = True

    if should_apply_style and style_dict:
        if nrows == 1 and ncols == 1:
            _apply_style(axes._ax, style_dict)
        else:
            axes_array = np.array(axes)
            for ax in axes_array.flat:
                _apply_style(ax._ax if hasattr(ax, "_ax") else ax, style_dict)

        fig.record.style = style_dict

    return style_dict


def create_subplots(
    nrows: int = 1,
    ncols: int = 1,
    axes_width_mm: Optional[float] = None,
    axes_height_mm: Optional[float] = None,
    margin_left_mm: Optional[float] = None,
    margin_right_mm: Optional[float] = None,
    margin_bottom_mm: Optional[float] = None,
    margin_top_mm: Optional[float] = None,
    space_w_mm: Optional[float] = None,
    space_h_mm: Optional[float] = None,
    style: Optional[Dict[str, Any]] = None,
    apply_style_mm: bool = True,
    panel_labels: Optional[bool] = None,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Core subplots implementation."""
    from .._wrappers._figure import create_recording_subplots
    from ..styles._style_loader import _STYLE_CACHE, to_subplots_kwargs

    global_style = _STYLE_CACHE

    # Check if mm-based layout is requested
    use_mm_layout = _check_mm_layout(
        axes_width_mm,
        axes_height_mm,
        margin_left_mm,
        margin_right_mm,
        margin_bottom_mm,
        margin_top_mm,
        space_w_mm,
        space_h_mm,
        global_style,
    )

    if use_mm_layout and "figsize" not in kwargs:
        mm_layout, kwargs = _calculate_mm_layout(
            nrows,
            ncols,
            axes_width_mm,
            axes_height_mm,
            margin_left_mm,
            margin_right_mm,
            margin_bottom_mm,
            margin_top_mm,
            space_w_mm,
            space_h_mm,
            global_style,
            kwargs,
        )
    else:
        mm_layout = None

    # Apply DPI from global style if not explicitly provided
    if "dpi" not in kwargs and global_style is not None:
        style_dpi = None
        try:
            if hasattr(global_style, "figure") and hasattr(global_style.figure, "dpi"):
                style_dpi = global_style.figure.dpi
            elif hasattr(global_style, "output") and hasattr(
                global_style.output, "dpi"
            ):
                style_dpi = global_style.output.dpi
        except (KeyError, AttributeError):
            pass
        if style_dpi is not None:
            kwargs["dpi"] = style_dpi

    # Handle style parameter
    if style is not None:
        if hasattr(style, "to_subplots_kwargs"):
            style_kwargs = style.to_subplots_kwargs()
            for key, value in style_kwargs.items():
                if key not in kwargs:
                    kwargs[key] = value

    # Check if style specifies constrained_layout
    style_constrained = False
    if global_style is not None:
        style_dict_check = to_subplots_kwargs(global_style)
        style_constrained = style_dict_check.get("constrained_layout", False)

    # Use constrained_layout if: style specifies it, or non-mm layout
    if "constrained_layout" not in kwargs:
        if style_constrained:
            kwargs["constrained_layout"] = True
        elif not use_mm_layout:
            kwargs["constrained_layout"] = True

    # Create the recording subplots
    fig, axes = create_recording_subplots(nrows, ncols, **kwargs)

    # Record constrained_layout setting for reproduction
    fig.record.constrained_layout = kwargs.get("constrained_layout", False)

    # Store mm_layout metadata on figure for serialization
    use_constrained = kwargs.get("constrained_layout", False)
    if mm_layout is not None and not use_constrained:
        fig._mm_layout = mm_layout
        _apply_mm_layout_to_figure(fig, mm_layout, nrows, ncols)

    # Apply styling using helper
    _apply_style_to_axes(fig, axes, nrows, ncols, style, apply_style_mm, global_style)

    # Determine panel_labels setting
    use_panel_labels = panel_labels
    if use_panel_labels is None and global_style is not None:
        behavior = global_style.get("behavior", {})
        use_panel_labels = behavior.get("panel_labels", False)

    # Add panel labels if enabled (for multi-panel figures)
    if use_panel_labels and (nrows > 1 or ncols > 1):
        fig.add_panel_labels()

    return fig, axes


__all__ = [
    "_get_mm_value",
    "_check_mm_layout",
    "_calculate_mm_layout",
    "_apply_mm_layout_to_figure",
    "_apply_style_to_axes",
    "create_subplots",
]

# EOF
