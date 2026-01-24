#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boxplot wrapper with patch_artist=True by default."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


def boxplot_plot(
    ax: "Axes",
    x,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    **kwargs,
) -> dict:
    """Boxplot with patch_artist=True by default for editor color selection.

    Setting patch_artist=True ensures boxes are rendered as patches (PathPatch)
    rather than lines, which allows the editor to detect and modify box colors.
    """
    from ..styles import get_style, resolve_colors_in_kwargs
    from ..styles._plot_styles import apply_boxplot_style

    # Resolve named colors to style colors
    kwargs = resolve_colors_in_kwargs(kwargs)

    # Enable patch_artist for filled boxes (editor needs patches for color picking)
    kwargs.setdefault("patch_artist", True)

    # Extract color/colors for box facecolors
    box_colors = kwargs.pop("color", None) or kwargs.pop("colors", None)

    # Call matplotlib's boxplot
    result = ax.boxplot(x, **kwargs)

    # Apply colors to boxplot boxes if specified
    if box_colors is not None:
        boxes = result.get("boxes", [])
        if isinstance(box_colors, str):
            for box in boxes:
                box.set_facecolor(box_colors)
        elif isinstance(box_colors, (list, tuple)):
            for box, color in zip(boxes, box_colors):
                box.set_facecolor(color)

    # Apply publication styling from loaded style
    style = get_style()
    if style:
        apply_boxplot_style(ax, style)

    # Record the call if tracking is enabled
    if track:
        recorded_kwargs = kwargs.copy()
        if box_colors is not None:
            recorded_kwargs["color"] = box_colors
        recorder.record_call(
            ax_position=position,
            method_name="boxplot",
            args=(x,),
            kwargs=recorded_kwargs,
            call_id=call_id,
        )

    return result


__all__ = ["boxplot_plot"]

# EOF
