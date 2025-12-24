#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper functions for custom plot methods in RecordingAxes."""

from typing import List, Tuple

import numpy as np


def get_colors_from_style(n_colors: int, explicit_colors=None) -> List:
    """Get colors from style or matplotlib defaults.

    Parameters
    ----------
    n_colors : int
        Number of colors needed.
    explicit_colors : list or color, optional
        Explicitly provided colors.

    Returns
    -------
    list
        List of colors.
    """
    if explicit_colors is not None:
        if isinstance(explicit_colors, list):
            return explicit_colors
        return [explicit_colors] * n_colors

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
        return colors

    # Matplotlib default color cycle
    import matplotlib.pyplot as plt

    return [c["color"] for c in plt.rcParams["axes.prop_cycle"]]


def beeswarm_positions(
    data: np.ndarray,
    width: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Calculate beeswarm-style x positions to minimize overlap.

    This is a simplified beeswarm that uses binning and jittering.

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


def compute_joyplot_kdes(arrays: List[np.ndarray], x: np.ndarray) -> Tuple[List, float]:
    """Compute KDEs for joyplot ridges.

    Parameters
    ----------
    arrays : list
        List of data arrays.
    x : array
        X values for KDE evaluation.

    Returns
    -------
    tuple
        (kdes, max_density)
    """
    from scipy import stats

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
    return kdes, max_density


__all__ = [
    "get_colors_from_style",
    "beeswarm_positions",
    "compute_joyplot_kdes",
]

# EOF
