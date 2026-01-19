#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Axis helper utilities for matplotlib axes.

This module provides functions for common axis styling operations including:
- Label rotation with automatic alignment
- Spine visibility management
- Tick customization (number, positions, labels)
- Scientific notation formatting
- Axis geometry (aspect ratio, size)

Usage:
    from figrecipe.styles.axis_helpers import rotate_labels, hide_spines

    # Or import all utilities
    from figrecipe.styles import axis_helpers

Examples:
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> fr.hide_spines(ax)  # Hide top and right spines
    >>> fr.rotate_labels(ax, x=45)  # Rotate x-axis labels
"""

# Base utilities (internal)
from ._base import get_axis_from_wrapper, validate_axis

# Geometry utilities
from ._geometry import extend, force_aspect

# Label rotation
from ._rotate_labels import rotate_labels

# Scientific notation
from ._sci_note import OOMFormatter, sci_note

# Spine visibility
from ._spines import (
    hide_spines,
    show_all_spines,
    show_classic_spines,
    show_spines,
    toggle_spines,
)

# Tick utilities
from ._ticks import map_ticks, set_n_ticks, set_ticks, set_x_ticks, set_y_ticks

__all__ = [
    # Base utilities
    "validate_axis",
    "get_axis_from_wrapper",
    # Label rotation
    "rotate_labels",
    # Spine visibility
    "hide_spines",
    "show_spines",
    "show_all_spines",
    "show_classic_spines",
    "toggle_spines",
    # Tick utilities
    "set_n_ticks",
    "set_ticks",
    "set_x_ticks",
    "set_y_ticks",
    "map_ticks",
    # Scientific notation
    "OOMFormatter",
    "sci_note",
    # Geometry
    "force_aspect",
    "extend",
]
