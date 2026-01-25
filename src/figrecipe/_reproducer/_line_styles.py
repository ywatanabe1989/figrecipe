#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Line styling for reproduced figures."""

from typing import Any, Dict

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points (1 inch = 72 pt = 25.4 mm)."""
    return mm * 72 / 25.4


def apply_line_styles(axes_2d: np.ndarray, style: Dict[str, Any]) -> None:
    """Apply trace linewidth styling to all Line2D objects in axes.

    This ensures pixel-perfect reproduction by applying the same line
    thickness used during original figure creation.

    Parameters
    ----------
    axes_2d : np.ndarray
        2D array of matplotlib axes.
    style : dict
        Style dictionary containing trace_thickness_mm or lines_trace_mm.
    """
    # Get trace linewidth from style (support multiple key names)
    trace_mm = style.get("trace_thickness_mm") or style.get("lines_trace_mm", 0.12)
    trace_lw = mm_to_pt(trace_mm)

    nrows, ncols = axes_2d.shape
    for row in range(nrows):
        for col in range(ncols):
            ax = axes_2d[row, col]
            _apply_linewidth_to_ax(ax, trace_lw)


def _apply_linewidth_to_ax(ax: Axes, trace_lw: float) -> None:
    """Apply linewidth to all Line2D objects in an axes.

    Skips special elements like error bars, boxplot parts, etc.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes.
    trace_lw : float
        Line width in points.
    """
    for child in ax.get_children():
        if isinstance(child, Line2D):
            # Skip if linewidth was explicitly set to a different value
            # by checking if it's close to matplotlib default (1.5)
            current_lw = child.get_linewidth()

            # Only adjust if close to matplotlib default
            # This avoids modifying error bars, boxplot parts, etc.
            if 0.5 < current_lw < 3.0:
                # Check if this is a main data line (has data, not just markers)
                xdata = child.get_xdata()
                linestyle = child.get_linestyle()

                # Main plot lines have data and visible linestyle
                if len(xdata) > 2 and linestyle not in ("None", "", " ", "none"):
                    child.set_linewidth(trace_lw)


__all__ = ["apply_line_styles"]
