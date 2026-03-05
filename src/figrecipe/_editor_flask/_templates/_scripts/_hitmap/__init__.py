#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitmap and selection JavaScript for the figure editor.

This module contains the JavaScript code for:
- Loading and displaying hitmap overlay
- Hit region drawing (SVG shapes for clickable elements)
- Element selection and group selection
- Hover highlighting
- Alt+Click cycling through overlapping elements
- Pixel-perfect hit detection using hitmap colors
"""

from ._handlers import SCRIPTS_HITMAP_HANDLERS
from ._load import SCRIPTS_HITMAP_LOAD
from ._regions import SCRIPTS_HITMAP_REGIONS
from ._selection import SCRIPTS_HITMAP_SELECTION
from ._shapes import SCRIPTS_HITMAP_SHAPES
from ._utils import SCRIPTS_HITMAP_UTILS

# Combine all hitmap scripts in correct order
SCRIPTS_HITMAP = (
    SCRIPTS_HITMAP_LOAD
    + SCRIPTS_HITMAP_SHAPES
    + SCRIPTS_HITMAP_REGIONS
    + SCRIPTS_HITMAP_HANDLERS
    + SCRIPTS_HITMAP_UTILS
    + SCRIPTS_HITMAP_SELECTION
)

__all__ = ["SCRIPTS_HITMAP"]

# EOF
