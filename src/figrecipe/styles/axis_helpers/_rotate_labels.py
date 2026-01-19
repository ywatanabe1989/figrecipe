#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Label rotation utilities for matplotlib axes."""

__all__ = ["rotate_labels"]

from typing import Any, Optional, Tuple

import numpy as np

from ._base import get_axis_from_wrapper, validate_axis


def rotate_labels(
    ax: Any,
    x: Optional[float] = None,
    y: Optional[float] = None,
    x_ha: Optional[str] = None,
    y_ha: Optional[str] = None,
    x_va: Optional[str] = None,
    y_va: Optional[str] = None,
    auto_adjust: bool = True,
    scientific_convention: bool = True,
    tight_layout: bool = False,
) -> Any:
    """Rotate x and y axis labels with automatic positioning.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    x : float, optional
        Rotation angle for x-axis labels in degrees.
        If 0 or None, x-axis labels are not rotated.
    y : float, optional
        Rotation angle for y-axis labels in degrees.
        If 0 or None, y-axis labels are not rotated.
    x_ha : str, optional
        Horizontal alignment for x-axis labels.
        If None, automatically determined based on angle.
    y_ha : str, optional
        Horizontal alignment for y-axis labels.
    x_va : str, optional
        Vertical alignment for x-axis labels.
    y_va : str, optional
        Vertical alignment for y-axis labels.
    auto_adjust : bool
        Automatically adjust alignment based on rotation angle.
        Default: True.
    scientific_convention : bool
        Follow scientific plotting conventions for alignment.
        Default: True.
    tight_layout : bool
        Apply tight_layout to prevent overlapping. Default: False.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 2, 3])
    >>> fr.rotate_labels(ax, x=45)  # Rotate x-axis labels 45 degrees

    Notes
    -----
    Scientific conventions for label rotation:
    - X-axis: For 0-90deg, use 'right' alignment; for 90-180deg, use 'left'
    - Y-axis: For 0-90deg, use 'center' alignment; adjust as needed
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    # Determine which axes to rotate
    rotate_x = x is not None and x != 0
    rotate_y = y is not None and y != 0

    # Get current tick positions
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()

    # Set ticks explicitly
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    # Auto-adjust alignment based on rotation angle
    if auto_adjust:
        if rotate_x:
            x_ha, x_va = _get_optimal_alignment(
                "x", x, x_ha, x_va, scientific_convention
            )
        if rotate_y:
            y_ha, y_va = _get_optimal_alignment(
                "y", y, y_ha, y_va, scientific_convention
            )

    # Apply defaults if not auto-adjusting
    if rotate_x:
        x_ha = x_ha or "center"
        x_va = x_va or "center"
    if rotate_y:
        y_ha = y_ha or "center"
        y_va = y_va or "center"

    # Check if labels are visible (respects sharex/sharey)
    x_labels_visible = ax.xaxis.get_tick_params().get("labelbottom", True)
    y_labels_visible = ax.yaxis.get_tick_params().get("labelleft", True)

    # Set labels with rotation and alignment
    if x_labels_visible and rotate_x:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=x, ha=x_ha, va=x_va)
    if y_labels_visible and rotate_y:
        ax.set_yticklabels(ax.get_yticklabels(), rotation=y, ha=y_ha, va=y_va)

    # Auto-adjust subplot parameters if needed
    if auto_adjust and scientific_convention:
        x_angle = x if rotate_x else 0
        y_angle = y if rotate_y else 0
        _adjust_subplot_params(ax, x_angle, y_angle)

    # Apply tight_layout if requested
    if tight_layout:
        fig = ax.get_figure()
        try:
            fig.tight_layout()
        except Exception:
            x_angle = x if rotate_x else 0
            y_angle = y if rotate_y else 0
            _adjust_subplot_params(ax, x_angle, y_angle)

    return ax


def _get_optimal_alignment(
    axis: str,
    angle: float,
    ha: Optional[str],
    va: Optional[str],
    scientific_convention: bool,
) -> Tuple[str, str]:
    """Determine optimal alignment based on rotation angle.

    Parameters
    ----------
    axis : str
        'x' or 'y' axis.
    angle : float
        Rotation angle in degrees.
    ha : str or None
        Current horizontal alignment.
    va : str or None
        Current vertical alignment.
    scientific_convention : bool
        Whether to follow scientific conventions.

    Returns
    -------
    tuple
        (horizontal_alignment, vertical_alignment)
    """
    angle = angle % 360

    if axis == "x":
        if scientific_convention:
            if 0 <= angle <= 30:
                ha = ha or "center"
                va = va or "top"
            elif 30 < angle <= 90:
                ha = ha or "right"
                va = va or "top"
            elif 90 < angle <= 150:
                ha = ha or "right"
                va = va or "bottom"
            elif 150 < angle <= 210:
                ha = ha or "center"
                va = va or "bottom"
            elif 210 < angle <= 300:
                ha = ha or "left"
                va = va or "center"
            else:
                ha = ha or "left"
                va = va or "top"
        else:
            ha = ha or "center"
            va = va or "top"
    else:  # y-axis
        if scientific_convention:
            if 0 <= angle <= 30:
                ha = ha or "right"
                va = va or "center"
            elif 30 < angle <= 120:
                ha = ha or "center"
                va = va or "bottom"
            elif 120 < angle <= 210:
                ha = ha or "left"
                va = va or "center"
            elif 210 < angle <= 300:
                ha = ha or "center"
                va = va or "top"
            else:
                ha = ha or "right"
                va = va or "top"
        else:
            ha = ha or "center"
            va = va or "center"

    return ha, va


def _adjust_subplot_params(ax: Any, x_angle: float, y_angle: float) -> None:
    """Adjust subplot parameters to accommodate rotated labels.

    Parameters
    ----------
    ax : Axes
        The axes object.
    x_angle : float
        X-axis rotation angle.
    y_angle : float
        Y-axis rotation angle.
    """
    fig = ax.get_figure()

    # Check for layout engine incompatibility
    try:
        if hasattr(fig, "get_layout_engine"):
            layout_engine = fig.get_layout_engine()
            if layout_engine is not None:
                return
    except AttributeError:
        pass

    # Calculate required margins
    if x_angle == 90:
        x_margin_factor = 0.3
    else:
        x_margin_factor = abs(np.sin(np.radians(x_angle))) * 0.25

    y_margin_factor = abs(np.sin(np.radians(y_angle))) * 0.15

    try:
        subplotpars = fig.subplotpars
        current_bottom = subplotpars.bottom
        current_left = subplotpars.left

        new_bottom = max(current_bottom, 0.2 + x_margin_factor)
        new_left = max(current_left, 0.1 + y_margin_factor)

        if new_bottom > current_bottom + 0.02 or new_left > current_left + 0.02:
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fig.subplots_adjust(bottom=new_bottom, left=new_left)
    except Exception:
        pass


# EOF
