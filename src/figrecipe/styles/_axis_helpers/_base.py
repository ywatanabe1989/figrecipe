#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base utilities for axis helpers."""

__all__ = ["validate_axis", "get_axis_from_wrapper"]

from typing import Any


def validate_axis(axis: Any, error_msg: str = None) -> bool:
    """Validate that the input is a matplotlib axes or compatible wrapper.

    Parameters
    ----------
    axis : Any
        Object to validate.
    error_msg : str, optional
        Custom error message if validation fails.

    Returns
    -------
    bool
        True if valid.

    Raises
    ------
    TypeError
        If the axis is not a valid matplotlib axes.
    """
    import matplotlib.axes

    # Check for figrecipe wrapper
    if hasattr(axis, "_ax"):
        return True

    # Check for direct matplotlib axes
    if isinstance(axis, matplotlib.axes.Axes):
        return True

    msg = error_msg or "Argument must be a matplotlib Axes or figrecipe wrapper"
    raise TypeError(msg)


def get_axis_from_wrapper(axis: Any) -> Any:
    """Extract matplotlib axes from wrapper if needed.

    Parameters
    ----------
    axis : Any
        Either a matplotlib axes or a wrapper containing one.

    Returns
    -------
    matplotlib.axes.Axes
        The underlying matplotlib axes.
    """
    # Check for figrecipe wrapper
    if hasattr(axis, "_ax"):
        return axis._ax

    return axis


# EOF
