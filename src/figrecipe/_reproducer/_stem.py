#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stem plot reproduction with color support."""

from typing import Any

from matplotlib.axes import Axes

from .._recorder import CallRecord
from ._reconstruct import reconstruct_kwargs, reconstruct_value


def replay_stem_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a stem call with proper color handling.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The call record containing stem arguments.

    Returns
    -------
    StemContainer
        The stem container.
    """
    # Reconstruct args
    args = []
    for arg_data in call.args:
        value = reconstruct_value(arg_data, {})
        args.append(value)

    # Get kwargs and reconstruct arrays
    kwargs = reconstruct_kwargs(call.kwargs)

    # Extract color before calling stem (stem doesn't accept 'color' kwarg)
    color = kwargs.pop("color", None)

    # Call stem
    container = ax.stem(*args, **kwargs)

    # Apply color to stem components if specified
    if color is not None:
        container.markerline.set_color(color)
        container.stemlines.set_color(color)
        # Optionally set baseline color too (usually kept default)
        # container.baseline.set_color(color)

    return container


__all__ = ["replay_stem_call"]

# EOF
