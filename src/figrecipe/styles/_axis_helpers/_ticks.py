#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tick utilities for matplotlib axes."""

__all__ = [
    "set_n_ticks",
    "set_ticks",
    "set_x_ticks",
    "set_y_ticks",
    "map_ticks",
]

from typing import Any, Optional, Sequence

import matplotlib.ticker
import numpy as np

from ._base import get_axis_from_wrapper, validate_axis


def set_n_ticks(
    ax: Any,
    n_xticks: Optional[int] = 4,
    n_yticks: Optional[int] = 4,
) -> Any:
    """Set the number of ticks on x and y axes using MaxNLocator.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    n_xticks : int, optional
        Number of ticks on x-axis. If None, x-axis is not modified.
        Default: 4.
    n_yticks : int, optional
        Number of ticks on y-axis. If None, y-axis is not modified.
        Default: 4.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3, 4, 5], [1, 4, 9, 16, 25])
    >>> fr.set_n_ticks(ax, n_xticks=3, n_yticks=5)
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    if n_xticks is not None:
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(n_xticks))

    if n_yticks is not None:
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(n_yticks))

    return ax


def set_ticks(
    ax: Any,
    xvals: Optional[Sequence] = None,
    xticks: Optional[Sequence] = None,
    yvals: Optional[Sequence] = None,
    yticks: Optional[Sequence] = None,
) -> Any:
    """Set custom tick labels on both x and y axes.

    Convenience function to set tick positions and labels for both axes
    at once.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    xvals : array-like, optional
        Values corresponding to x-axis data points.
    xticks : list, optional
        Desired tick labels for the x-axis.
    yvals : array-like, optional
        Values corresponding to y-axis data points.
    yticks : list, optional
        Desired tick labels for the y-axis.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> x = np.linspace(0, 10, 100)
    >>> ax.plot(x, np.sin(x))
    >>> ax = fr.set_ticks(ax, xvals=x, xticks=[0, 5, 10])
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    ax = set_x_ticks(ax, x_vals=xvals, x_ticks=xticks)
    ax = set_y_ticks(ax, y_vals=yvals, y_ticks=yticks)

    return ax


def set_x_ticks(
    ax: Any,
    x_vals: Optional[Sequence] = None,
    x_ticks: Optional[Sequence] = None,
) -> Any:
    """Set custom tick labels on the x-axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    x_vals : array-like, optional
        Values corresponding to x-axis data points. If provided alone,
        generates 4 evenly spaced ticks across the range.
    x_ticks : list, optional
        Desired tick labels for the x-axis.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> fr.set_x_ticks(ax, x_ticks=[1, 2, 3])
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    x_vals_passed = x_vals is not None
    x_ticks_passed = x_ticks is not None

    if not x_vals_passed and not x_ticks_passed:
        # Do nothing
        pass

    elif x_vals_passed and not x_ticks_passed:
        # Replaces the x axis to x_vals with auto-generated ticks
        x_vals = np.array(x_vals)
        x_ticks = np.linspace(x_vals[0], x_vals[-1], 4)
        new_x_axis = np.linspace(*ax.get_xlim(), len(x_ticks))
        ax.set_xticks(new_x_axis)
        ax.set_xticklabels([f"{xv}" for xv in x_ticks])

    elif not x_vals_passed and x_ticks_passed:
        # Locates 'x_ticks' on the original x axis
        x_ticks = np.array(x_ticks)
        if x_ticks.dtype.kind in ["U", "S", "O"]:  # String ticks
            ax.set_xticks(range(len(x_ticks)))
            ax.set_xticklabels(x_ticks)
        else:
            ax.set_xticks(x_ticks)

    elif x_vals_passed and x_ticks_passed:
        # Replaces the original x axis to 'x_vals' and locates 'x_ticks'
        if isinstance(x_vals, str) and x_vals == "auto":
            x_vals = np.arange(len(x_ticks))

        x_vals = np.array(x_vals)
        new_x_axis = np.linspace(*ax.get_xlim(), len(x_vals))
        ax.set_xticks(new_x_axis)
        ax.set_xticklabels([f"{xv}" for xv in x_vals])

        # Now locate x_ticks on the new axis
        x_ticks = np.array(x_ticks)
        if x_ticks.dtype.kind not in ["U", "S", "O"]:
            labels = [
                label.get_text().replace("−", "-") for label in ax.get_xticklabels()
            ]
            label_vals = np.array([float(lbl) if lbl else 0 for lbl in labels])
            indices = np.argmin(
                np.abs(label_vals[:, np.newaxis] - x_ticks[np.newaxis, :]), axis=0
            )
            ax.set_xticks(ax.get_xticks()[indices])
            ax.set_xticklabels([f"{xt}" for xt in x_ticks])

    return ax


def set_y_ticks(
    ax: Any,
    y_vals: Optional[Sequence] = None,
    y_ticks: Optional[Sequence] = None,
) -> Any:
    """Set custom tick labels on the y-axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    y_vals : array-like, optional
        Values corresponding to y-axis data points.
    y_ticks : list, optional
        Desired tick labels for the y-axis.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> fr.set_y_ticks(ax, y_ticks=[1, 4, 9])
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    y_vals_passed = y_vals is not None
    y_ticks_passed = y_ticks is not None

    if not y_vals_passed and not y_ticks_passed:
        # Do nothing
        pass

    elif y_vals_passed and not y_ticks_passed:
        # Replaces the y axis to y_vals
        y_vals = np.array(y_vals)
        new_y_axis = np.linspace(*ax.get_ylim(), len(y_vals))
        ax.set_yticks(new_y_axis)
        ax.set_yticklabels([f"{yv:.2f}" for yv in y_vals])

    elif not y_vals_passed and y_ticks_passed:
        # Locates 'y_ticks' on the original y axis
        y_ticks = np.array(y_ticks)
        if y_ticks.dtype.kind in ["U", "S", "O"]:  # String ticks
            ax.set_yticks(range(len(y_ticks)))
            ax.set_yticklabels(y_ticks)
        else:
            ax.set_yticks(y_ticks)

    elif y_vals_passed and y_ticks_passed:
        # Replaces the original y axis to 'y_vals' and locates 'y_ticks'
        if y_vals == "auto":
            y_vals = np.arange(len(y_ticks))

        y_vals = np.array(y_vals)
        new_y_axis = np.linspace(*ax.get_ylim(), len(y_vals))
        ax.set_yticks(new_y_axis)
        ax.set_yticklabels([f"{yv:.2f}" for yv in y_vals])

        # Now locate y_ticks on the new axis
        y_ticks = np.array(y_ticks)
        if y_ticks.dtype.kind not in ["U", "S", "O"]:
            labels = [
                label.get_text().replace("−", "-") for label in ax.get_yticklabels()
            ]
            label_vals = np.array([float(lbl) if lbl else 0 for lbl in labels])
            indices = np.argmin(
                np.abs(label_vals[:, np.newaxis] - y_ticks[np.newaxis, :]), axis=0
            )
            ax.set_yticks(ax.get_yticks()[indices])
            ax.set_yticklabels([f"{yt}" for yt in y_ticks])

    return ax


def map_ticks(
    ax: Any,
    src: Sequence,
    tgt: Sequence[str],
    axis: str = "x",
) -> Any:
    """Map source tick positions or labels to new target labels.

    Supports both numeric positions and string labels for source ticks,
    enabling the mapping to new target labels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    src : list of str or numeric
        Source positions (if numeric) or labels (if str) to map from.
    tgt : list of str
        New target labels to apply. Must have the same length as 'src'.
    axis : str
        Which axis to apply the mapping to ('x' or 'y'). Default: 'x'.

    Returns
    -------
    Axes
        The modified Axes object.

    Raises
    ------
    ValueError
        If src and tgt have different lengths or invalid axis specified.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> x = np.linspace(0, 2 * np.pi, 100)
    >>> ax.plot(x, np.sin(x))
    >>> src = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]
    >>> tgt = ['0', 'pi/2', 'pi', '3pi/2', '2pi']
    >>> fr.map_ticks(ax, src, tgt, axis='x')
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    if len(src) != len(tgt):
        raise ValueError(
            "Source ('src') and target ('tgt') must have the same number of elements."
        )

    # Determine tick positions if src is string data
    if all(isinstance(item, str) for item in src):
        if axis == "x":
            all_labels = [label.get_text() for label in ax.get_xticklabels()]
        else:
            all_labels = [label.get_text() for label in ax.get_yticklabels()]

        # Find positions of src labels
        src_positions = [all_labels.index(s) for s in src if s in all_labels]
    else:
        # Use src as positions directly if numeric
        src_positions = src

    # Set the ticks and labels based on the specified axis
    if axis == "x":
        ax.set_xticks(src_positions)
        ax.set_xticklabels(tgt)
    elif axis == "y":
        ax.set_yticks(src_positions)
        ax.set_yticklabels(tgt)
    else:
        raise ValueError("Invalid axis argument. Use 'x' or 'y'.")

    return ax


# EOF
