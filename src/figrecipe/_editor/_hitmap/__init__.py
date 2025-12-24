#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitmap generation package.

This package provides hitmap generation for interactive element selection.
The main entry point is `generate_hitmap`.
"""

# Re-export main functions from _hitmap_main
from .._hitmap_main import generate_hitmap, hitmap_to_base64

# Re-export from artist processing
from ._artists import (
    process_collections,
    process_figure_text,
    process_images,
    process_legend,
    process_lines,
    process_patches,
    process_text,
)

# Re-export from color utilities
from ._colors import (
    AXES_COLOR,
    BACKGROUND_COLOR,
    DISTINCT_COLORS,
    hsv_to_rgb,
    id_to_rgb,
    mpl_color_to_hex,
    normalize_color,
    rgb_to_id,
)

# Re-export from detection utilities
from ._detect import detect_plot_types, is_boxplot_element, is_violin_element

# Re-export from restoration utilities
from ._restore import (
    restore_axes_properties,
    restore_backgrounds,
    restore_figure_text,
)

__all__ = [
    # Main functions
    "generate_hitmap",
    "hitmap_to_base64",
    # Color utilities
    "id_to_rgb",
    "rgb_to_id",
    "DISTINCT_COLORS",
    "BACKGROUND_COLOR",
    "AXES_COLOR",
    "hsv_to_rgb",
    "normalize_color",
    "mpl_color_to_hex",
    # Detection utilities
    "detect_plot_types",
    "is_boxplot_element",
    "is_violin_element",
    # Artist processing
    "process_collections",
    "process_figure_text",
    "process_images",
    "process_legend",
    "process_lines",
    "process_patches",
    "process_text",
    # Restoration utilities
    "restore_axes_properties",
    "restore_backgrounds",
    "restore_figure_text",
]

# EOF
