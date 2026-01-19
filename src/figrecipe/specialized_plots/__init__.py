#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Specialized plot types for scientific visualization.

This module provides specialized plotting functions for common scientific
use cases including:

- Heatmaps and confusion matrices
- Statistical plots (ECDF, shaded lines with uncertainty)
- Neuroscience plots (spike rasters)
- Annotation helpers (vertical/horizontal fills, rectangles)

Usage
-----
>>> import figrecipe as fr
>>> fig, ax = fr.subplots()
>>> # Create a heatmap
>>> ax, im, cbar = fr.heatmap(ax, data, x_labels=x_labels, y_labels=y_labels)
>>> # Or use module directly
>>> from figrecipe.specialized_plots import heatmap, ecdf, raster
"""

from ._annotation import fillh, fillv, hline, rectangle, vline
from ._heatmap import conf_mat, heatmap
from ._neuroscience import raster
from ._statistical import (
    ecdf,
    mean_ci_line,
    mean_std_line,
    median_iqr_line,
    shaded_line,
)

__all__ = [
    # Heatmap plots
    "heatmap",
    "conf_mat",
    # Statistical plots
    "ecdf",
    "shaded_line",
    "mean_std_line",
    "mean_ci_line",
    "median_iqr_line",
    # Neuroscience plots
    "raster",
    # Annotation helpers
    "fillv",
    "fillh",
    "rectangle",
    "vline",
    "hline",
]
