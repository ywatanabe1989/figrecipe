#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable CSS styles - orchestrator.

Combines all datatable CSS modules:
- _panel.py: Panel layout, header, toggle
- _toolbar.py: Toolbar, import, hints
- _table.py: Spreadsheet table
- _vars.py: Variable assignment with color linking
- _editable.py: Editable table styles
"""

from ._editable import CSS_DATATABLE_EDITABLE
from ._panel import CSS_DATATABLE_PANEL
from ._table import CSS_DATATABLE_TABLE
from ._toolbar import CSS_DATATABLE_TOOLBAR
from ._vars import CSS_DATATABLE_VARS


def get_styles_datatable() -> str:
    """Generate combined datatable CSS."""
    return (
        CSS_DATATABLE_PANEL
        + "\n"
        + CSS_DATATABLE_TOOLBAR
        + "\n"
        + CSS_DATATABLE_TABLE
        + "\n"
        + CSS_DATATABLE_VARS
        + "\n"
        + CSS_DATATABLE_EDITABLE
    )


# For backward compatibility
STYLES_DATATABLE = get_styles_datatable()

__all__ = ["STYLES_DATATABLE", "get_styles_datatable"]

# EOF
