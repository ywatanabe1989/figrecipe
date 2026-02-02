#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boxplot replay handler for color kwarg and styling."""

from typing import Any

from matplotlib.axes import Axes

from .._recorder import CallRecord
from ._reconstruct import reconstruct_kwargs, reconstruct_value


def replay_boxplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a boxplot call, handling the color kwarg specially.

    The boxplot wrapper records 'color' kwarg for compatibility,
    but matplotlib's ax.boxplot() doesn't accept 'color' directly.
    Instead, we need to apply colors to the boxes after creation.

    Also applies boxplot-specific styling (linewidths) from the loaded style
    to ensure pixel-perfect reproduction.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to plot on.
    call : CallRecord
        The recorded call.

    Returns
    -------
    dict
        Result from ax.boxplot() containing boxes, whiskers, etc.
    """
    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = reconstruct_value(arg_data, {})
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = reconstruct_kwargs(call.kwargs)

    # Extract color kwarg (not valid for matplotlib's boxplot)
    box_colors = kwargs.pop("color", None)

    # Call matplotlib's boxplot without the color kwarg
    result = ax.boxplot(*args, **kwargs)

    # Apply colors to boxplot boxes if specified
    if box_colors is not None:
        import numpy as np

        boxes = result.get("boxes", [])
        if isinstance(box_colors, str):
            for box in boxes:
                box.set_facecolor(box_colors)
        elif isinstance(box_colors, (list, tuple, np.ndarray)):
            for box, color in zip(boxes, box_colors):
                box.set_facecolor(color)

    # Apply boxplot styling from loaded style (linewidths, etc.)
    from ..styles._internal import get_style
    from ..styles._kwargs_converter import to_subplots_kwargs
    from ..styles._plot_styles import apply_boxplot_style

    style = get_style()
    if style:
        style_dict = to_subplots_kwargs(style)
        apply_boxplot_style(ax, style_dict)

    return result


__all__ = ["replay_boxplot_call"]
