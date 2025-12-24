#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom plot replay functions (joyplot, swarmplot) for figure reproduction."""

from typing import Any, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from .._recorder import CallRecord


def replay_joyplot_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a joyplot call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The joyplot call to replay.

    Returns
    -------
    Any
        Result of the joyplot call.
    """
    from scipy import stats

    from ._core import _reconstruct_kwargs, _reconstruct_value

    # Reconstruct args
    arrays = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        if isinstance(value, list):
            # Could be a list of arrays
            arrays = [np.asarray(arr) for arr in value]
        else:
            arrays.append(np.asarray(value))

    if not arrays:
        return None

    # Get kwargs
    kwargs = _reconstruct_kwargs(call.kwargs)
    overlap = kwargs.get("overlap", 0.5)
    fill_alpha = kwargs.get("fill_alpha", 0.7)
    line_alpha = kwargs.get("line_alpha", 1.0)
    labels = kwargs.get("labels")

    n_ridges = len(arrays)

    # Get colors from style
    from ..styles import get_style

    style = get_style()
    if style and "colors" in style and "palette" in style.colors:
        palette = list(style.colors.palette)
        colors = []
        for c in palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    colors.append(tuple(c))
                else:
                    colors.append(tuple(v / 255.0 for v in c))
            else:
                colors.append(c)
    else:
        colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    # Calculate global x range
    all_data = np.concatenate([np.asarray(arr) for arr in arrays])
    x_min, x_max = np.min(all_data), np.max(all_data)
    x_range = x_max - x_min
    x_padding = x_range * 0.1
    x = np.linspace(x_min - x_padding, x_max + x_padding, 200)

    # Calculate KDEs and find max density for scaling
    kdes = []
    max_density = 0
    for arr in arrays:
        arr = np.asarray(arr)
        if len(arr) > 1:
            kde = stats.gaussian_kde(arr)
            density = kde(x)
            kdes.append(density)
            max_density = max(max_density, np.max(density))
        else:
            kdes.append(np.zeros_like(x))

    # Scale factor for ridge height
    ridge_height = 1.0 / (1.0 - overlap * 0.5) if overlap < 1 else 2.0

    # Get line width from style
    from .._utils._units import mm_to_pt

    lw = mm_to_pt(0.2)  # Default
    if style and "lines" in style:
        lw = mm_to_pt(style.lines.get("trace_mm", 0.2))

    # Plot each ridge from back to front
    for i in range(n_ridges - 1, -1, -1):
        color = colors[i % len(colors)]
        baseline = i * (1.0 - overlap)

        # Scale density to fit nicely
        scaled_density = (
            kdes[i] / max_density * ridge_height if max_density > 0 else kdes[i]
        )

        # Fill
        ax.fill_between(
            x,
            baseline,
            baseline + scaled_density,
            facecolor=color,
            edgecolor="none",
            alpha=fill_alpha,
        )
        # Line on top
        ax.plot(
            x, baseline + scaled_density, color=color, alpha=line_alpha, linewidth=lw
        )

    # Set y limits
    ax.set_ylim(-0.1, n_ridges * (1.0 - overlap) + ridge_height)

    # Set y-axis labels if provided
    if labels:
        y_positions = [(i * (1.0 - overlap)) + 0.3 for i in range(n_ridges)]
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
    else:
        ax.set_yticks([])

    return ax


def replay_swarmplot_call(ax: Axes, call: CallRecord) -> List[Any]:
    """Replay a swarmplot call on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes.
    call : CallRecord
        The swarmplot call to replay.

    Returns
    -------
    list
        List of PathCollection objects.
    """
    from ._core import _reconstruct_kwargs, _reconstruct_value

    # Reconstruct args
    data = []
    for arg_data in call.args:
        value = _reconstruct_value(arg_data)
        if isinstance(value, list):
            # Could be a list of arrays
            data = [np.asarray(arr) for arr in value]
        else:
            data.append(np.asarray(value))

    if not data:
        return []

    # Get kwargs
    kwargs = _reconstruct_kwargs(call.kwargs)
    positions = kwargs.get("positions")
    size = kwargs.get("size", 0.8)
    alpha = kwargs.get("alpha", 0.7)
    jitter = kwargs.get("jitter", 0.3)

    if positions is None:
        positions = list(range(1, len(data) + 1))

    # Get style
    from .._utils._units import mm_to_pt
    from ..styles import get_style

    style = get_style()
    size_pt = mm_to_pt(size) ** 2  # matplotlib uses area

    # Get colors
    if style and "colors" in style and "palette" in style.colors:
        palette = list(style.colors.palette)
        colors = []
        for c in palette:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                if all(v <= 1.0 for v in c):
                    colors.append(tuple(c))
                else:
                    colors.append(tuple(v / 255.0 for v in c))
            else:
                colors.append(c)
    else:
        colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    # Random generator for reproducible jitter
    rng = np.random.default_rng(42)

    results = []
    for i, (arr, pos) in enumerate(zip(data, positions)):
        arr = np.asarray(arr)

        # Create jittered x positions using simplified beeswarm
        x_offsets = _beeswarm_positions(arr, jitter, rng)
        x_positions = pos + x_offsets

        c = colors[i % len(colors)]
        result = ax.scatter(
            x_positions,
            arr,
            s=size_pt,
            c=[c],
            alpha=alpha,
        )
        results.append(result)

    return results


def _beeswarm_positions(
    data: np.ndarray,
    width: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Calculate beeswarm-style x positions to minimize overlap.

    Parameters
    ----------
    data : array
        Y values of points.
    width : float
        Maximum jitter width.
    rng : Generator
        Random number generator.

    Returns
    -------
    array
        X offsets for each point.
    """
    n = len(data)
    if n == 0:
        return np.array([])

    # Sort data and get order
    order = np.argsort(data)
    sorted_data = data[order]

    # Group nearby points and offset them
    x_offsets = np.zeros(n)

    # Simple approach: bin by quantiles and spread within each bin
    n_bins = max(1, int(np.sqrt(n)))
    bin_edges = np.percentile(sorted_data, np.linspace(0, 100, n_bins + 1))

    for i in range(n_bins):
        mask = (sorted_data >= bin_edges[i]) & (sorted_data <= bin_edges[i + 1])
        n_in_bin = mask.sum()
        if n_in_bin > 0:
            # Spread points evenly within bin width
            offsets = np.linspace(-width / 2, width / 2, n_in_bin)
            # Add small random noise
            offsets += rng.uniform(-width * 0.1, width * 0.1, n_in_bin)
            x_offsets[mask] = offsets

    # Restore original order
    result = np.zeros(n)
    result[order] = x_offsets
    return result


__all__ = ["replay_joyplot_call", "replay_swarmplot_call"]
