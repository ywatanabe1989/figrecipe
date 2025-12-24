#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined JavaScript modules for the figure editor.

This module provides the main SCRIPTS constant and extracted modules.

Main Export:
- SCRIPTS: Complete JavaScript code (from _scripts_main.py)

Extracted Modules (for incremental refactoring):
- _core.py - State variables and initialization
- _zoom.py - Zoom/pan functionality
- _overlays.py - Measurement overlays (ruler, grid, columns)
- _inspector.py - Element inspector debugging
- _files.py - File switching functionality
- _hitmap.py - Hitmap loading and hit region drawing
- _selection.py - Selection drawing and property sync
"""

# Re-export SCRIPTS from the main file for backward compatibility
from .._scripts_main import SCRIPTS

# Import extracted modules
from ._core import SCRIPTS_CORE
from ._files import SCRIPTS_FILES
from ._hitmap import SCRIPTS_HITMAP
from ._inspector import SCRIPTS_INSPECTOR
from ._overlays import SCRIPTS_OVERLAYS
from ._selection import SCRIPTS_SELECTION
from ._zoom import SCRIPTS_ZOOM

# Export SCRIPTS as the primary export for backward compatibility
__all__ = [
    "SCRIPTS",
    "SCRIPTS_CORE",
    "SCRIPTS_ZOOM",
    "SCRIPTS_OVERLAYS",
    "SCRIPTS_INSPECTOR",
    "SCRIPTS_FILES",
    "SCRIPTS_HITMAP",
    "SCRIPTS_SELECTION",
]
