#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-09
# File: src/figrecipe/_utils/_calc_nice_ticks.py

"""Calculate nice tick positions for matplotlib axes."""

import matplotlib.ticker as mticker
import numpy as np


def calc_nice_ticks(
    min_val,
    max_val,
    allow_edge_min=True,
    allow_edge_max=False,
    pad_perc=5,
    num_ticks=4,
    prefer_integer=True,
):
    """Calculate nice tick values for axes based on data range.

    Parameters
    ----------
    min_val : float
        Minimum data value
    max_val : float
        Maximum data value
    allow_edge_min : bool, optional
        Whether to allow a tick at the min value, defaults to True
    allow_edge_max : bool, optional
        Whether to allow a tick at the max value, defaults to False
    pad_perc : float, optional
        Percentage of data range to pad, defaults to 5%
    num_ticks : int, optional
        Target number of ticks to display, defaults to 4
    prefer_integer : bool, optional
        If True, convert ticks to integers when possible, defaults to True

    Returns
    -------
    list
        List of nicely spaced tick positions
    """
    # Handle edge cases
    if min_val == max_val:
        if min_val == 0:
            return [0, 1, 2, 3]
        else:
            margin = abs(min_val) * 0.1
            min_val -= margin
            max_val += margin

    original_min = min_val
    original_max = max_val

    range_size = max_val - min_val
    if not allow_edge_min:
        min_val -= range_size * pad_perc / 100
    if not allow_edge_max:
        max_val += range_size * pad_perc / 100

    locator = mticker.MaxNLocator(
        nbins=num_ticks,
        steps=[1, 2, 5, 10],
        integer=False,
        symmetric=False,
        prune=None,
        min_n_ticks=3,
    )

    tick_locations = locator.tick_values(min_val, max_val)

    if len(tick_locations) > num_ticks + 1:
        locator = mticker.MaxNLocator(nbins=num_ticks - 1)
        tick_locations = locator.tick_values(min_val, max_val)

    if not allow_edge_min:
        tick_locations = [tick for tick in tick_locations if tick >= original_min]
    if not allow_edge_max:
        tick_locations = [tick for tick in tick_locations if tick <= original_max]

    if prefer_integer and all(float(int(tick)) == tick for tick in tick_locations):
        tick_locations = [int(tick) for tick in tick_locations]

    return np.array(tick_locations).tolist()


# EOF
