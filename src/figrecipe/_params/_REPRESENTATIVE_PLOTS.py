#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_params/_REPRESENTATIVE_PLOTS.py

"""Representative plot types for development demos and testing.

These are a curated subset of all plotting methods, chosen to cover
the main categories without being exhaustive. Useful for quick demos
and smoke tests.

Can be filtered via environment variable:
    FIGRECIPE_DEV_REPRESENTATIVE_PLOTS=plot,scatter,bar
"""

import os

# Default representative plot types (curated for demos)
_DEFAULT_REPRESENTATIVE_PLOTS = {
    # Line/curve
    "plot",
    "fill_between",
    "stackplot",
    "errorbar",
    # Scatter/points
    "scatter",
    # Bar/categorical
    "bar",
    "boxplot",
    "violinplot",
    # Distribution
    "hist",
    "hist2d",
    "ecdf",
    # Image/matrix
    "imshow",
    "matshow",
    # Contour/surface
    "contourf",
    # Spectral/signal
    "specgram",
    # Special
    "pie",
    "eventplot",
    "graph",
}


def get_representative_plots():
    """Get representative plot types, optionally filtered by env var.

    Environment variable FIGRECIPE_DEV_REPRESENTATIVE_PLOTS can override
    the default set with a comma-separated list.

    Returns
    -------
    set
        Set of representative plot type names.
    """
    env_val = os.environ.get("FIGRECIPE_DEV_REPRESENTATIVE_PLOTS")
    if env_val:
        return {p.strip() for p in env_val.split(",") if p.strip()}
    return _DEFAULT_REPRESENTATIVE_PLOTS.copy()


REPRESENTATIVE_PLOTS = _DEFAULT_REPRESENTATIVE_PLOTS

# EOF
