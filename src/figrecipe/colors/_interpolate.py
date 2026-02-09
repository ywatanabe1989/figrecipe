#!/usr/bin/env python3
# Timestamp: 2026-02-09
# File: src/figrecipe/colors/_interpolate.py

"""Color interpolation utilities."""

import warnings

import matplotlib.colors as mcolors
import numpy as np


def gen_interpolate(color_start, color_end, num_points, round=3):
    color_start_rgba = np.array(mcolors.to_rgba(color_start))
    color_end_rgba = np.array(mcolors.to_rgba(color_end))
    rgba_values = np.linspace(color_start_rgba, color_end_rgba, num_points).round(round)
    return [list(color) for color in rgba_values]


def interpolate(color_start, color_end, num_points, round=3):
    warnings.warn(
        "interpolate is deprecated. Use gen_interpolate instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return gen_interpolate(color_start, color_end, num_points, round=round)


# EOF
