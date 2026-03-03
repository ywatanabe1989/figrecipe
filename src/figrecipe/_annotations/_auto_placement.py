#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-placement utilities for statistical annotations.

Provides logic to position brackets and text above existing data
without overlapping other annotations or data elements.
"""

__all__ = ["auto_y_position"]

from typing import Any, Optional

import numpy as np

# Style constants (also used by _stat_bracket.py)
BRACKET_TICK_HEIGHT_FRAC = 0.02  # fraction of y-range for bracket tick height
BRACKET_TEXT_OFFSET_FRAC = 0.01  # fraction of y-range between bracket and text


def _get_data_max_in_range(ax: Any, x1: float, x2: float) -> Optional[float]:
    """Find the maximum y-value of plotted data between x1 and x2.

    Inspects line plots, bar containers, and errorbar collections.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to inspect.
    x1 : float
        Left x boundary of the region of interest.
    x2 : float
        Right x boundary of the region of interest.

    Returns
    -------
    float or None
        Maximum y value found in range, or None if no data found.
    """
    x_lo, x_hi = min(x1, x2), max(x1, x2)
    candidates = []

    # Lines (ax.plot, ax.errorbar data lines)
    for line in ax.get_lines():
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        if xdata is None or ydata is None:
            continue
        xdata = np.asarray(xdata, dtype=float)
        ydata = np.asarray(ydata, dtype=float)
        mask = (xdata >= x_lo) & (xdata <= x_hi)
        if np.any(mask):
            finite_y = ydata[mask & np.isfinite(ydata)]
            if len(finite_y) > 0:
                candidates.append(float(finite_y.max()))

    # Bar containers (ax.bar)
    for container in ax.containers:
        try:
            from matplotlib.container import BarContainer

            if not isinstance(container, BarContainer):
                continue
        except ImportError:
            pass
        for patch in container.patches:
            bx = patch.get_x() + patch.get_width() / 2.0
            if x_lo <= bx <= x_hi:
                top = patch.get_y() + patch.get_height()
                candidates.append(float(top))

    # Collections (e.g. scatter, errorbar caps stored as collections)
    for coll in ax.collections:
        try:
            offsets = coll.get_offsets()
            if offsets is not None and len(offsets) > 0:
                offsets = np.asarray(offsets)
                mask = (offsets[:, 0] >= x_lo) & (offsets[:, 0] <= x_hi)
                if np.any(mask):
                    finite_y = offsets[mask, 1]
                    finite_y = finite_y[np.isfinite(finite_y)]
                    if len(finite_y) > 0:
                        candidates.append(float(finite_y.max()))
        except (AttributeError, IndexError):
            continue

    return max(candidates) if candidates else None


def _get_existing_bracket_max(ax: Any, x1: float, x2: float) -> Optional[float]:
    """Find the maximum y position of brackets overlapping the given range.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to inspect.
    x1 : float
        Left x boundary.
    x2 : float
        Right x boundary.

    Returns
    -------
    float or None
        Highest y position of overlapping brackets, or None.
    """
    if not hasattr(ax, "_stat_brackets"):
        return None

    x_lo, x_hi = min(x1, x2), max(x1, x2)
    candidates = []

    for meta in ax._stat_brackets.values():
        b_lo = min(meta["x1"], meta["x2"])
        b_hi = max(meta["x1"], meta["x2"])
        # Check overlap in x
        if b_lo <= x_hi and b_hi >= x_lo:
            candidates.append(float(meta["y"]))

    return max(candidates) if candidates else None


def auto_y_position(
    ax: Any,
    x1: float,
    x2: float,
    offset_frac: float = 0.05,
) -> float:
    """Compute a y position for a stat bracket above existing content.

    Inspects current data ranges, plotted elements, and already-placed
    brackets in ax._stat_brackets to avoid overlap.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to annotate.
    x1 : float
        Left x position of the bracket.
    x2 : float
        Right x position of the bracket.
    offset_frac : float, optional
        Fraction of the visible y-range to use as padding above data.
        Default: 0.05 (5 percent of y-range).

    Returns
    -------
    float
        Y coordinate suitable for placing the bracket line.
    """
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min
    if y_range == 0:
        y_range = 1.0

    # Start from the highest relevant feature
    data_max = _get_data_max_in_range(ax, x1, x2)
    bracket_max = _get_existing_bracket_max(ax, x1, x2)

    candidates = [y_min + y_range * 0.8]  # fallback: 80% of visible range

    if data_max is not None:
        candidates.append(data_max)
    if bracket_max is not None:
        # Place above existing bracket: bracket line + tick + text offset
        total_bracket_height = y_range * (
            BRACKET_TICK_HEIGHT_FRAC + BRACKET_TEXT_OFFSET_FRAC + 0.06
        )
        candidates.append(bracket_max + total_bracket_height)

    base = max(candidates)
    return base + y_range * offset_frac


# EOF
