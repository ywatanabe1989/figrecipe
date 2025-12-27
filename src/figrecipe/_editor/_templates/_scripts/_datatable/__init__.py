#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable JavaScript modules - orchestrator.

Combines all datatable JavaScript modules:
- _core.py: State, panel toggle, initialization
- _tabs.py: Multi-tab management for multiple datasets
- _import.py: Drag-drop, file parsing
- _table.py: Table rendering
- _plot.py: Plot type hints, variable assignment, plotting
- _editable.py: Create and edit tables manually
"""

from ._core import JS_DATATABLE_CORE
from ._editable import JS_DATATABLE_EDITABLE
from ._import import JS_DATATABLE_IMPORT
from ._plot import get_js_datatable_plot
from ._table import JS_DATATABLE_TABLE
from ._tabs import JS_DATATABLE_TABS


def get_scripts_datatable() -> str:
    """Generate combined datatable JavaScript."""
    return (
        JS_DATATABLE_CORE
        + "\n"
        + JS_DATATABLE_TABS
        + "\n"
        + JS_DATATABLE_IMPORT
        + "\n"
        + JS_DATATABLE_TABLE
        + "\n"
        + JS_DATATABLE_EDITABLE
        + "\n"
        + get_js_datatable_plot()
    )


# For backward compatibility
SCRIPTS_DATATABLE = get_scripts_datatable()

__all__ = ["SCRIPTS_DATATABLE", "get_scripts_datatable"]

# EOF
