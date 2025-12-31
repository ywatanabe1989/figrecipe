#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML template component for the datatable panel.

This module contains the HTML for the collapsible datatable panel
that appears on the left side of the editor.
Plot type options are generated dynamically from the registry.
"""

from .._plot_types_registry import generate_html_options


def get_html_datatable_panel() -> str:
    """Generate HTML for datatable panel with dynamic plot type options."""
    plot_options = generate_html_options()

    return f"""
        <!-- Datatable Panel (always visible, collapsible) -->
        <div id="datatable-panel" class="datatable-panel">
            <div class="datatable-header">
                <div class="header-title">
                    <span>DATA</span>
                </div>
                <div class="datatable-header-actions">
                    <button id="btn-shortcuts-info" class="btn-small btn-icon" title="Keyboard shortcuts">&#x2328;</button>
                    <button id="btn-collapse-datatable" class="btn-collapse" title="Collapse panel">&#x276E;</button>
                </div>
            </div>

            <!-- Tab bar for multiple datatables -->
            <div class="datatable-tabs">
                <div id="datatable-tab-list" class="datatable-tab-list">
                    <!-- Tabs dynamically populated -->
                </div>
                <button id="btn-new-tab" class="btn-new-tab" title="New data tab">+</button>
            </div>

            <!-- Tab content container -->
            <div id="datatable-tab-content" class="datatable-tab-content">
                <!-- Import dropzone -->
                <div class="datatable-import" id="datatable-import-section">
                    <div id="datatable-dropzone" class="datatable-import-dropzone">
                        <p>Drop CSV, TSV, or JSON file here</p>
                        <p class="hint">or click to browse</p>
                        <input type="file" id="datatable-file-input" accept=".csv,.tsv,.txt,.json">
                        <div class="dropzone-divider">or</div>
                        <button class="btn-create-new" onclick="event.stopPropagation(); createNewCSV()">Create New Table</button>
                    </div>
                </div>

                <!-- Toolbar (hidden until data loaded) -->
                <div class="datatable-toolbar" style="display: none;">
                    <select id="datatable-plot-type" class="plot-type-select" title="Plot type">
{plot_options}
                    </select>
                    <div class="split-btn">
                        <button id="btn-datatable-plot" class="btn-plot" disabled title="Create new plot">New</button>
                        <button id="btn-plot-dropdown" class="btn-plot-dropdown" title="Add to panel">▼</button>
                        <div id="plot-dropdown-menu" class="plot-dropdown-menu">
                            <!-- Panels populated dynamically -->
                        </div>
                    </div>
                </div>

                <!-- Variable assignment (dynamic based on plot type) -->
                <div id="datatable-var-assign" class="datatable-var-assign" style="display: none;">
                    <div class="var-assign-header">Assign columns to variables:</div>
                    <div id="var-assign-slots" class="var-assign-slots">
                        <!-- Slots dynamically populated by JS -->
                    </div>
                </div>

                <!-- Spreadsheet content -->
                <div id="datatable-content" class="datatable-content"></div>

                <!-- Selection info -->
                <div id="datatable-selection-info" class="datatable-selection-info">
                    <span class="selected-count">0</span> columns selected
                </div>
            </div>
            <!-- Resize handle -->
            <div class="datatable-resize" id="datatable-resize"></div>
        </div>
"""


# For backward compatibility
HTML_DATATABLE_PANEL = get_html_datatable_panel()

__all__ = ["HTML_DATATABLE_PANEL", "get_html_datatable_panel"]

# EOF
