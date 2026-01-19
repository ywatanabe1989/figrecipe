#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation specialized plots: vertical fills, rectangles, and regions."""

__all__ = ["fillv", "rectangle"]

from typing import Any, List, Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle as MplRectangle


def fillv(
    ax: Union[Axes, np.ndarray],
    starts: np.ndarray,
    ends: np.ndarray,
    color: str = "red",
    alpha: float = 0.2,
    **kwargs: Any,
) -> Union[Axes, List[Axes]]:
    """Fill vertical regions between specified start and end x-positions.

    Useful for highlighting time periods, stimulus intervals, or other
    regions of interest on a plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray of axes
        The axis object(s) to fill intervals on.
    starts : array-like, shape (n_regions,)
        1D array of start x-positions for vertical fill regions.
    ends : array-like, shape (n_regions,)
        1D array of end x-positions for vertical fill regions.
    color : str, optional
        The color for the filled regions (default: "red").
    alpha : float, optional
        Transparency value, 0 (transparent) to 1 (opaque) (default: 0.2).
    **kwargs : dict
        Additional arguments passed to axvspan.

    Returns
    -------
    ax : matplotlib.axes.Axes or list of Axes
        The axis/axes with filled intervals.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> t = np.linspace(0, 10, 100)
    >>> ax.plot(t, np.sin(t))
    >>> fr.fillv(ax, [2, 6], [4, 8], color='blue', alpha=0.3)
    """
    # Handle array of axes
    is_array = isinstance(ax, np.ndarray)
    axes_list = ax.flatten() if is_array else [ax]

    starts = np.asarray(starts)
    ends = np.asarray(ends)

    for axis in axes_list:
        # Unwrap recording axes if needed
        mpl_ax = axis._ax if hasattr(axis, "_ax") else axis

        for start, end in zip(starts, ends):
            mpl_ax.axvspan(
                start,
                end,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
                **kwargs,
            )

    if is_array:
        return list(axes_list)
    return axes_list[0]


def fillh(
    ax: Union[Axes, np.ndarray],
    starts: np.ndarray,
    ends: np.ndarray,
    color: str = "red",
    alpha: float = 0.2,
    **kwargs: Any,
) -> Union[Axes, List[Axes]]:
    """Fill horizontal regions between specified start and end y-positions.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray of axes
        The axis object(s) to fill intervals on.
    starts : array-like, shape (n_regions,)
        1D array of start y-positions for horizontal fill regions.
    ends : array-like, shape (n_regions,)
        1D array of end y-positions for horizontal fill regions.
    color : str, optional
        The color for the filled regions (default: "red").
    alpha : float, optional
        Transparency value (default: 0.2).
    **kwargs : dict
        Additional arguments passed to axhspan.

    Returns
    -------
    ax : matplotlib.axes.Axes or list of Axes
        The axis/axes with filled intervals.
    """
    is_array = isinstance(ax, np.ndarray)
    axes_list = ax.flatten() if is_array else [ax]

    starts = np.asarray(starts)
    ends = np.asarray(ends)

    for axis in axes_list:
        mpl_ax = axis._ax if hasattr(axis, "_ax") else axis

        for start, end in zip(starts, ends):
            mpl_ax.axhspan(
                start,
                end,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
                **kwargs,
            )

    if is_array:
        return list(axes_list)
    return axes_list[0]


def rectangle(
    ax: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str = "red",
    alpha: float = 0.3,
    edgecolor: Optional[str] = None,
    linewidth: float = 1.0,
    fill: bool = True,
    **kwargs: Any,
) -> Tuple[Axes, MplRectangle]:
    """Add a rectangle annotation to the plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to add the rectangle to.
    x : float
        X-coordinate of the lower-left corner.
    y : float
        Y-coordinate of the lower-left corner.
    width : float
        Width of the rectangle.
    height : float
        Height of the rectangle.
    color : str, optional
        Fill color (default: "red").
    alpha : float, optional
        Transparency (default: 0.3).
    edgecolor : str, optional
        Edge color. If None, uses the fill color.
    linewidth : float, optional
        Edge line width (default: 1.0).
    fill : bool, optional
        Whether to fill the rectangle (default: True).
    **kwargs : dict
        Additional arguments passed to Rectangle.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the rectangle.
    rect : matplotlib.patches.Rectangle
        The rectangle patch object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> t = np.linspace(0, 10, 100)
    >>> ax.plot(t, np.sin(t))
    >>> ax, rect = fr.rectangle(ax, 2, -0.5, 2, 1.0, color='blue', alpha=0.2)
    """
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    if edgecolor is None:
        edgecolor = color

    rect = MplRectangle(
        (x, y),
        width,
        height,
        facecolor=color if fill else "none",
        edgecolor=edgecolor,
        alpha=alpha,
        linewidth=linewidth,
        **kwargs,
    )
    mpl_ax.add_patch(rect)

    return ax, rect


def vline(
    ax: Union[Axes, np.ndarray],
    x: Union[float, List[float]],
    color: str = "red",
    linestyle: str = "--",
    linewidth: float = 1.0,
    alpha: float = 0.8,
    **kwargs: Any,
) -> Union[Axes, List[Axes]]:
    """Add vertical line(s) to the plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray of axes
        The axis object(s).
    x : float or list of float
        X-position(s) for vertical line(s).
    color : str, optional
        Line color (default: "red").
    linestyle : str, optional
        Line style (default: "--").
    linewidth : float, optional
        Line width (default: 1.0).
    alpha : float, optional
        Transparency (default: 0.8).
    **kwargs : dict
        Additional arguments passed to axvline.

    Returns
    -------
    ax : matplotlib.axes.Axes or list of Axes
        The axis/axes with vertical lines.
    """
    is_array = isinstance(ax, np.ndarray)
    axes_list = ax.flatten() if is_array else [ax]

    x_values = [x] if isinstance(x, (int, float)) else x

    for axis in axes_list:
        mpl_ax = axis._ax if hasattr(axis, "_ax") else axis

        for x_val in x_values:
            mpl_ax.axvline(
                x_val,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                **kwargs,
            )

    if is_array:
        return list(axes_list)
    return axes_list[0]


def hline(
    ax: Union[Axes, np.ndarray],
    y: Union[float, List[float]],
    color: str = "red",
    linestyle: str = "--",
    linewidth: float = 1.0,
    alpha: float = 0.8,
    **kwargs: Any,
) -> Union[Axes, List[Axes]]:
    """Add horizontal line(s) to the plot.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or np.ndarray of axes
        The axis object(s).
    y : float or list of float
        Y-position(s) for horizontal line(s).
    color : str, optional
        Line color (default: "red").
    linestyle : str, optional
        Line style (default: "--").
    linewidth : float, optional
        Line width (default: 1.0).
    alpha : float, optional
        Transparency (default: 0.8).
    **kwargs : dict
        Additional arguments passed to axhline.

    Returns
    -------
    ax : matplotlib.axes.Axes or list of Axes
        The axis/axes with horizontal lines.
    """
    is_array = isinstance(ax, np.ndarray)
    axes_list = ax.flatten() if is_array else [ax]

    y_values = [y] if isinstance(y, (int, float)) else y

    for axis in axes_list:
        mpl_ax = axis._ax if hasattr(axis, "_ax") else axis

        for y_val in y_values:
            mpl_ax.axhline(
                y_val,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                alpha=alpha,
                **kwargs,
            )

    if is_array:
        return list(axes_list)
    return axes_list[0]


# EOF
