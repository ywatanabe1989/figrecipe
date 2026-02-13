#!/usr/bin/env python3
# Timestamp: 2026-02-09
# File: src/figrecipe/colors/_colormap.py

"""Colormap utilities — sample colors from matplotlib colormaps."""

from typing import List, Optional, Tuple, Union

import matplotlib
import numpy as np


def get_color_from_cmap(
    cmap_name: str,
    value: float,
    value_range: Optional[Tuple[float, float]] = None,
    alpha: float = 1.0,
) -> Tuple[float, float, float, float]:
    """Get a color from a colormap at a specific value.

    Parameters
    ----------
    cmap_name : str
        Name of the colormap (e.g., 'viridis', 'plasma', 'Blues')
    value : float
        Value to map to a color in the colormap
    value_range : tuple of (float, float), optional
        Range of values to map to the colormap. If None, uses (0, 1)
    alpha : float, optional
        Alpha value for the color (0.0 to 1.0), by default 1.0

    Returns
    -------
    tuple
        RGBA color tuple with values from 0 to 1
    """
    cmap = matplotlib.colormaps[cmap_name]

    if value_range is None:
        norm_value = value
    else:
        min_val, max_val = value_range
        norm_value = (value - min_val) / (max_val - min_val)

    norm_value = np.clip(norm_value, 0.0, 1.0)
    rgba_color = list(cmap(norm_value))
    rgba_color[3] = alpha

    return tuple(rgba_color)


def get_colors_from_cmap(
    cmap_name: str,
    n_colors: int,
    value_range: Optional[Tuple[float, float]] = None,
    alpha: float = 1.0,
) -> List[Tuple[float, float, float, float]]:
    """Get a list of evenly spaced colors from a colormap.

    Parameters
    ----------
    cmap_name : str
        Name of the colormap (e.g., 'viridis', 'plasma', 'Blues')
    n_colors : int
        Number of colors to sample from the colormap
    value_range : tuple of (float, float), optional
        Range of values to map to the colormap. If None, uses (0, 1)
    alpha : float, optional
        Alpha value for the colors (0.0 to 1.0), by default 1.0

    Returns
    -------
    list
        List of RGBA color tuples with values from 0 to 1
    """
    if value_range is None:
        values = np.linspace(0, 1, n_colors)
    else:
        values = np.linspace(value_range[0], value_range[1], n_colors)

    return [get_color_from_cmap(cmap_name, val, value_range, alpha) for val in values]


def get_categorical_colors_from_cmap(
    cmap_name: str, categories: Union[List, np.ndarray], alpha: float = 1.0
) -> dict:
    """Map categorical values to colors from a colormap.

    Parameters
    ----------
    cmap_name : str
        Name of the colormap (e.g., 'viridis', 'plasma', 'Blues')
    categories : list or np.ndarray
        List of categories to map to colors
    alpha : float, optional
        Alpha value for the colors (0.0 to 1.0), by default 1.0

    Returns
    -------
    dict
        Dictionary mapping categories to RGBA color tuples
    """
    unique_categories = np.unique(categories)
    n_categories = len(unique_categories)
    colors = get_colors_from_cmap(cmap_name, n_categories, alpha=alpha)
    return {cat: colors[idx] for idx, cat in enumerate(unique_categories)}


# Backward compatibility aliases
get_color_from_conf_matap = get_color_from_cmap
get_colors_from_conf_matap = get_colors_from_cmap
get_categorical_colors_from_conf_matap = get_categorical_colors_from_cmap

# EOF
