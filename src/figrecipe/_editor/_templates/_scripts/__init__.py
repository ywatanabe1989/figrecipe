#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaScript modules for the figure editor.

This package contains modular JavaScript organized by functionality:
- _api.py: API calls (save, load, update, download)
- _colors.py: Color presets and conversion utilities
- _core.py: State variables and initialization
- _debug_snapshot.py: Screenshot + console log capture (Ctrl+Alt+I)
- _element_editor.py: Dynamic form fields and call properties
- _files.py: File switching functionality
- _hitmap.py: Hitmap loading and hit region drawing
- _inspector.py: Element inspector debugging
- _labels.py: Label inputs and axis/legend controls
- _modals.py: Theme and shortcuts modals
- _panel_position.py: Panel position editing (left, bottom, width, height)
- _overlays.py: Measurement overlays (ruler, grid, columns)
- _selection.py: Selection drawing and property sync
- _tabs.py: Tab navigation (Figure/Axis/Element)
- _view_mode.py: View mode management (all/selected)
- _zoom.py: Zoom/pan functionality
"""

from ._api import SCRIPTS_API
from ._colors import SCRIPTS_COLORS
from ._core import SCRIPTS_CORE
from ._debug_snapshot import SCRIPTS_DEBUG_SNAPSHOT
from ._element_editor import SCRIPTS_ELEMENT_EDITOR
from ._files import SCRIPTS_FILES
from ._hitmap import SCRIPTS_HITMAP
from ._inspector import SCRIPTS_INSPECTOR
from ._labels import SCRIPTS_LABELS
from ._modals import SCRIPTS_MODALS
from ._overlays import SCRIPTS_OVERLAYS
from ._panel_position import SCRIPTS_PANEL_POSITION
from ._selection import SCRIPTS_SELECTION
from ._tabs import SCRIPTS_TABS
from ._view_mode import SCRIPTS_VIEW_MODE
from ._zoom import SCRIPTS_ZOOM

# Combined SCRIPTS constant for backward compatibility
# Order matters: debug snapshot first (for console interception), then core/state, then features
SCRIPTS = (
    SCRIPTS_DEBUG_SNAPSHOT
    + SCRIPTS_CORE
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
    + SCRIPTS_PANEL_POSITION
)


def get_all_scripts():
    """Return all scripts as a dictionary for testing.

    Returns
    -------
    dict
        Mapping of script name to script content.
    """
    return {
        "api": SCRIPTS_API,
        "colors": SCRIPTS_COLORS,
        "core": SCRIPTS_CORE,
        "debug_snapshot": SCRIPTS_DEBUG_SNAPSHOT,
        "element_editor": SCRIPTS_ELEMENT_EDITOR,
        "files": SCRIPTS_FILES,
        "hitmap": SCRIPTS_HITMAP,
        "inspector": SCRIPTS_INSPECTOR,
        "labels": SCRIPTS_LABELS,
        "modals": SCRIPTS_MODALS,
        "overlays": SCRIPTS_OVERLAYS,
        "panel_position": SCRIPTS_PANEL_POSITION,
        "selection": SCRIPTS_SELECTION,
        "tabs": SCRIPTS_TABS,
        "view_mode": SCRIPTS_VIEW_MODE,
        "zoom": SCRIPTS_ZOOM,
    }


__all__ = [
    "SCRIPTS",
    "SCRIPTS_API",
    "SCRIPTS_COLORS",
    "SCRIPTS_CORE",
    "SCRIPTS_DEBUG_SNAPSHOT",
    "SCRIPTS_ELEMENT_EDITOR",
    "SCRIPTS_FILES",
    "SCRIPTS_HITMAP",
    "SCRIPTS_INSPECTOR",
    "SCRIPTS_LABELS",
    "SCRIPTS_MODALS",
    "SCRIPTS_OVERLAYS",
    "SCRIPTS_PANEL_POSITION",
    "SCRIPTS_SELECTION",
    "SCRIPTS_TABS",
    "SCRIPTS_VIEW_MODE",
    "SCRIPTS_ZOOM",
    "get_all_scripts",
]
