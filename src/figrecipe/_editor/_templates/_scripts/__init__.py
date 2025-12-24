#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaScript modules for the figure editor.

This package contains modular JavaScript organized by functionality:
- _core.py: State variables and initialization
- _zoom.py: Zoom/pan functionality
- _overlays.py: Measurement overlays (ruler, grid, columns)
- _inspector.py: Element inspector debugging
- _files.py: File switching functionality
- _hitmap.py: Hitmap loading and hit region drawing
- _selection.py: Selection drawing and property sync
- _colors.py: Color presets and conversion utilities
- _element_editor.py: Dynamic form fields and call properties
- _tabs.py: Tab navigation (Figure/Axis/Element)
- _view_mode.py: View mode management (all/selected)
- _modals.py: Theme and shortcuts modals
- _api.py: API calls (save, load, update, download)
- _labels.py: Label inputs and axis/legend controls
"""

from ._api import SCRIPTS_API
from ._colors import SCRIPTS_COLORS
from ._core import SCRIPTS_CORE
from ._element_editor import SCRIPTS_ELEMENT_EDITOR
from ._files import SCRIPTS_FILES
from ._hitmap import SCRIPTS_HITMAP
from ._inspector import SCRIPTS_INSPECTOR
from ._labels import SCRIPTS_LABELS
from ._modals import SCRIPTS_MODALS
from ._overlays import SCRIPTS_OVERLAYS
from ._selection import SCRIPTS_SELECTION
from ._tabs import SCRIPTS_TABS
from ._view_mode import SCRIPTS_VIEW_MODE
from ._zoom import SCRIPTS_ZOOM

# Combined SCRIPTS constant for backward compatibility
# Order matters: core/state first, then features, then UI controls
SCRIPTS = (
    SCRIPTS_CORE
    + SCRIPTS_TABS
    + SCRIPTS_VIEW_MODE
    + SCRIPTS_COLORS
    + SCRIPTS_HITMAP
    + SCRIPTS_SELECTION
    + SCRIPTS_ELEMENT_EDITOR
    + SCRIPTS_LABELS
    + SCRIPTS_API
    + SCRIPTS_MODALS
    + SCRIPTS_ZOOM
    + SCRIPTS_OVERLAYS
    + SCRIPTS_INSPECTOR
    + SCRIPTS_FILES
)

__all__ = [
    "SCRIPTS",
    "SCRIPTS_CORE",
    "SCRIPTS_ZOOM",
    "SCRIPTS_OVERLAYS",
    "SCRIPTS_INSPECTOR",
    "SCRIPTS_FILES",
    "SCRIPTS_HITMAP",
    "SCRIPTS_SELECTION",
    "SCRIPTS_COLORS",
    "SCRIPTS_ELEMENT_EDITOR",
    "SCRIPTS_TABS",
    "SCRIPTS_VIEW_MODE",
    "SCRIPTS_MODALS",
    "SCRIPTS_API",
    "SCRIPTS_LABELS",
]
