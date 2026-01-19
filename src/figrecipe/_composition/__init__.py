#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composition module for combining multiple figures.

This module provides functionality to:
- Compose new figures from multiple recipe sources or raw images
- Import axes from external recipes into existing figures
- Hide/show panels for visual composition
- Align and distribute panels

Supported image formats for composition:
PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP, SVG (SVG requires cairosvg)

Phase 1-3 of the composition feature.
"""

from ._alignment import AlignmentMode, align_panels, distribute_panels, smart_align
from ._compose import IMAGE_EXTENSIONS, VECTOR_EXTENSIONS, compose
from ._import_axes import import_axes
from ._visibility import hide_panel, show_panel, toggle_panel

__all__ = [
    # Phase 1: Composition
    "compose",
    "import_axes",
    # Image formats supported for composition
    "IMAGE_EXTENSIONS",
    "VECTOR_EXTENSIONS",
    # Phase 2: Visibility
    "hide_panel",
    "show_panel",
    "toggle_panel",
    # Phase 3: Alignment
    "AlignmentMode",
    "align_panels",
    "distribute_panels",
    "smart_align",
]
