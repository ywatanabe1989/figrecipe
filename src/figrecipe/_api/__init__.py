#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API helper modules for figrecipe.

This package contains helper functions extracted from the main __init__.py
to reduce file size and improve maintainability.
"""

from ._extract import DECORATION_FUNCS, extract_call_data, to_array
from ._panel import calculate_panel_position, get_panel_label_fontsize
from ._save import (
    IMAGE_EXTENSIONS,
    YAML_EXTENSIONS,
    get_save_dpi,
    get_save_transparency,
    resolve_save_paths,
)
from ._subplots import (
    _apply_mm_layout_to_figure,
    _apply_style_to_axes,
    _calculate_mm_layout,
    _check_mm_layout,
    _get_mm_value,
)

__all__ = [
    # Subplots helpers
    "_get_mm_value",
    "_check_mm_layout",
    "_calculate_mm_layout",
    "_apply_mm_layout_to_figure",
    "_apply_style_to_axes",
    # Save helpers
    "IMAGE_EXTENSIONS",
    "YAML_EXTENSIONS",
    "resolve_save_paths",
    "get_save_dpi",
    "get_save_transparency",
    # Extract helpers
    "DECORATION_FUNCS",
    "to_array",
    "extract_call_data",
    # Panel helpers
    "get_panel_label_fontsize",
    "calculate_panel_position",
]

# EOF
