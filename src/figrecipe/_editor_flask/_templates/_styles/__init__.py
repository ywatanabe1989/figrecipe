#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for the figure editor.

This package contains modular CSS styles organized by component:
- base: CSS variables, reset, container
- preview: Preview panel, branding, zoom controls
- hitmap: Hitregion overlay shapes
- selection: Selection overlay shapes
- dynamic_props: Dynamic call properties panel
- controls: Controls panel, tabs, sections
- forms: Form elements and inputs
- buttons: Button styles, download dropdown
- color_input: Color picker components
- labels: Axis type toggle, label inputs, legend
- overlays: Ruler, grid, column overlays
- modals: Shortcuts modal, kbd styling
- inspector: Element inspector overlay
"""

from ._base import STYLES_BASE
from ._buttons import STYLES_BUTTONS
from ._color_input import STYLES_COLOR_INPUT
from ._controls import STYLES_CONTROLS
from ._datatable import STYLES_DATATABLE
from ._dynamic_props import STYLES_DYNAMIC_PROPS
from ._file_browser import STYLES_FILE_BROWSER
from ._forms import STYLES_FORMS
from ._hitmap import STYLES_HITMAP
from ._inspector import STYLES_INSPECTOR
from ._labels import STYLES_LABELS
from ._modals import STYLES_MODALS
from ._overlays import STYLES_OVERLAYS
from ._preview import STYLES_PREVIEW
from ._selection import STYLES_SELECTION
from ._spinner import STYLES_SPINNER

# Combined STYLES constant for backward compatibility
STYLES = (
    STYLES_BASE
    + STYLES_FILE_BROWSER
    + STYLES_PREVIEW
    + STYLES_HITMAP
    + STYLES_SELECTION
    + STYLES_DYNAMIC_PROPS
    + STYLES_CONTROLS
    + STYLES_FORMS
    + STYLES_BUTTONS
    + STYLES_COLOR_INPUT
    + STYLES_LABELS
    + STYLES_OVERLAYS
    + STYLES_MODALS
    + STYLES_INSPECTOR
    + STYLES_SPINNER
    + STYLES_DATATABLE
)

__all__ = [
    "STYLES",
    "STYLES_BASE",
    "STYLES_FILE_BROWSER",
    "STYLES_PREVIEW",
    "STYLES_HITMAP",
    "STYLES_SELECTION",
    "STYLES_DYNAMIC_PROPS",
    "STYLES_CONTROLS",
    "STYLES_FORMS",
    "STYLES_BUTTONS",
    "STYLES_COLOR_INPUT",
    "STYLES_LABELS",
    "STYLES_OVERLAYS",
    "STYLES_MODALS",
    "STYLES_INSPECTOR",
    "STYLES_SPINNER",
    "STYLES_DATATABLE",
]

# EOF
