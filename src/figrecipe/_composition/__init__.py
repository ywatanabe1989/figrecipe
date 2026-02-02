#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composition module for combining multiple figures.

This module provides functionality to:
- Compose new figures from multiple recipe sources or raw images
- Import axes from external recipes into existing figures
- Hide/show panels for visual composition
- Align and distribute panels

Supports two composition modes (automatically detected):
1. Grid-based: sources={(row, col): path} with layout=(nrows, ncols)
2. Mm-based: sources={path: {"xy_mm": ..., "size_mm": ...}} with canvas_size_mm

All composition is matplotlib-native for reproducibility - no PIL image pasting.

Supported image formats for composition:
PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP, SVG (SVG requires cairosvg)
"""

from ._alignment import AlignmentMode, align_panels, distribute_panels, smart_align
from ._compose import IMAGE_EXTENSIONS, VECTOR_EXTENSIONS, compose
from ._import_axes import import_axes
from ._layout_solver import solve_layout_to_mm
from ._visibility import hide_panel, show_panel, toggle_panel

__all__ = [
    # Composition (grid-based and mm-based)
    "compose",
    "import_axes",
    "solve_layout_to_mm",
    # Image formats supported for composition
    "IMAGE_EXTENSIONS",
    "VECTOR_EXTENSIONS",
    # Visibility
    "hide_panel",
    "show_panel",
    "toggle_panel",
    # Alignment
    "AlignmentMode",
    "align_panels",
    "distribute_panels",
    "smart_align",
]
