#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composition module for combining multiple figures.

This module provides functionality to:
- Compose new figures from multiple recipe sources
- Import axes from external recipes into existing figures
- Hide/show panels for visual composition
- Align and distribute panels

Phase 1-3 of the composition feature.
"""

from ._alignment import AlignmentMode, align_panels, distribute_panels, smart_align
from ._compose import compose
from ._import_axes import import_axes
from ._visibility import hide_panel, show_panel, toggle_panel

__all__ = [
    # Phase 1: Composition
    "compose",
    "import_axes",
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
