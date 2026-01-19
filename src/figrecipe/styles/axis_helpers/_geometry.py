#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry utilities for matplotlib axes (aspect ratio, size, position)."""

__all__ = ["force_aspect", "extend"]

from typing import Any

from ._base import get_axis_from_wrapper, validate_axis


def force_aspect(ax: Any, aspect: float = 1.0) -> Any:
    """Force aspect ratio of an axis based on the extent of the image.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    aspect : float, optional
        The aspect ratio to apply. Default: 1.0.

    Returns
    -------
    Axes
        The Axes object with adjusted aspect ratio.

    Raises
    ------
    IndexError
        If no images are present on the axis.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> data = np.random.rand(10, 20)
    >>> ax.imshow(data)
    >>> fr.force_aspect(ax, aspect=1)  # Square pixels
    >>> fr.force_aspect(ax, aspect=2)  # Wider than tall

    Notes
    -----
    This function requires an image to be present on the axis (created via
    imshow, pcolormesh, or similar). It calculates the aspect ratio based
    on the image extent.
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    images = ax.get_images()
    if not images:
        raise IndexError("No images found on axis. force_aspect requires an image.")

    extent = images[0].get_extent()
    ax.set_aspect(abs((extent[1] - extent[0]) / (extent[3] - extent[2])) / aspect)

    return ax


def extend(ax: Any, x_ratio: float = 1.0, y_ratio: float = 1.0) -> Any:
    """Extend or shrink an axis while maintaining its center position.

    Scales the axis dimensions by the specified ratios while keeping the
    center of the axis in the same position.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    x_ratio : float, optional
        Ratio to scale the width. Values > 1 expand, < 1 shrink.
        Default: 1.0.
    y_ratio : float, optional
        Ratio to scale the height. Values > 1 expand, < 1 shrink.
        Default: 1.0.

    Returns
    -------
    Axes
        The modified Axes object.

    Raises
    ------
    ValueError
        If x_ratio or y_ratio is 0.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> fr.extend(ax, x_ratio=1.2, y_ratio=0.8)  # Wider, shorter

    Notes
    -----
    This modifies the axis position within the figure, not the data limits.
    Useful for fine-tuning subplot spacing or creating custom layouts.
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    if x_ratio == 0:
        raise ValueError("x_ratio must not be 0.")
    if y_ratio == 0:
        raise ValueError("y_ratio must not be 0.")

    # Get original coordinates
    bbox = ax.get_position()
    left_orig = bbox.x0
    bottom_orig = bbox.y0
    width_orig = bbox.x1 - bbox.x0
    height_orig = bbox.y1 - bbox.y0

    # Calculate center
    center_x = left_orig + width_orig / 2.0
    center_y = bottom_orig + height_orig / 2.0

    # Calculate target dimensions
    width_tgt = width_orig * x_ratio
    height_tgt = height_orig * y_ratio
    left_tgt = center_x - width_tgt / 2
    bottom_tgt = center_y - height_tgt / 2

    # Set new position
    ax.set_position([left_tgt, bottom_tgt, width_tgt, height_tgt])

    return ax


# EOF
