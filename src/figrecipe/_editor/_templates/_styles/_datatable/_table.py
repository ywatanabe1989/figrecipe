#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for datatable spreadsheet table."""

CSS_DATATABLE_TABLE = """
/* Spreadsheet container */
.datatable-content {
    flex: 1;
    overflow: auto;
    padding: 0;
}

/* Spreadsheet table styles */
.datatable-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    table-layout: auto;
}

.datatable-table th,
.datatable-table td {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    text-align: left;
    white-space: nowrap;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datatable-table th {
    background: var(--header-bg) !important;  /* Theme-aware solid background */
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 10;
}

/* Ensure all elements inside header have opaque backgrounds */
.datatable-table th * {
    background-color: inherit;
}

.datatable-table th input,
.datatable-table th select {
    background: var(--header-input-bg) !important;
}

/* Corner cell (row-num in header) needs highest z-index */
.datatable-table thead th.row-num {
    z-index: 20;
}

.datatable-table th.selected {
    background: var(--accent-color) !important;
    color: white;
}

/* Highlight entire column when header is selected */
.datatable-table td.col-selected {
    background: var(--cell-selected-bg) !important;  /* Theme-aware selection */
}

.datatable-table td {
    background: var(--bg-primary);
}

.datatable-table tr:hover td {
    background: var(--cell-hover-bg);
}

/* Column header with checkbox */
.datatable-col-header {
    display: flex;
    align-items: center;
    gap: 4px;
}

.datatable-col-header input[type="checkbox"] {
    margin: 0;
    width: 14px;
    height: 14px;
    cursor: pointer;
}

.datatable-col-header .col-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datatable-col-header .col-type {
    font-size: 9px;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    padding: 1px 4px;
    border-radius: 2px;
    font-weight: normal;
}

/* Row number column - sticky for horizontal scroll */
.datatable-table th.row-num,
.datatable-table td.row-num {
    width: 40px;
    min-width: 40px;
    max-width: 40px;
    text-align: center;
    background: var(--row-num-bg) !important;  /* Theme-aware solid background */
    color: var(--text-secondary);
    font-size: 10px;
    position: sticky;
    left: 0;
    z-index: 5;
}

/* Ensure header row-num is above data row-num */
.datatable-table th.row-num {
    z-index: 15;
}

/* Column header color linking with variables - theme-aware monochrome */
.datatable-table th.var-linked {
    position: relative;
    background: var(--var-linked-bg) !important;
    color: var(--text-primary);
    box-shadow: inset 0 -4px 0 var(--accent-color);
}

/* Also highlight cells in linked columns - theme-aware */
.datatable-table td.var-linked-cell {
    background: var(--var-linked-cell-bg) !important;
}

/* Color classes for column headers - disabled for cleaner monochrome design */
.datatable-table th.var-color-0,
.datatable-table th.var-color-1,
.datatable-table th.var-color-2,
.datatable-table th.var-color-3,
.datatable-table th.var-color-4,
.datatable-table th.var-color-5 {
    /* No color overrides - uses accent-color via var-linked class */
}

/* box-shadow is used for bottom border color in var-linked headers */

/* Canvas-linked column highlight */
.datatable-table th.canvas-linked {
    background: var(--accent-color) !important;
    color: white !important;
    animation: canvas-link-pulse 1s ease-in-out;
}

.datatable-table th.canvas-linked .col-name,
.datatable-table th.canvas-linked .col-name-input,
.datatable-table th.canvas-linked .col-type {
    color: white !important;
}

.datatable-table th.canvas-linked .col-type {
    background: rgba(255,255,255,0.2);
}

/* Highlighted data cells */
.datatable-table td.canvas-linked {
    background: rgba(59, 130, 246, 0.15) !important;
}

[data-theme="dark"] .datatable-table td.canvas-linked {
    background: rgba(59, 130, 246, 0.2) !important;
}

@keyframes canvas-link-pulse {
    0% { box-shadow: 0 0 0 0 rgba(74, 158, 255, 0.7); }
    50% { box-shadow: 0 0 0 4px rgba(74, 158, 255, 0.4); }
    100% { box-shadow: 0 0 0 0 rgba(74, 158, 255, 0); }
}

/* Smart cell truncation with span wrapper (vis_app pattern) */
.datatable-table td .cell-text {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Cell selection styles - theme-aware solid colors */
.datatable-table td.cell-selected {
    background: var(--cell-selected-bg) !important;
}

.datatable-table td.cell-current {
    background: var(--cell-selected-bg) !important;
    outline: 2px solid var(--accent-color);
    outline-offset: -2px;
    z-index: 5;
    position: relative;
}

.datatable-table td:focus {
    outline: 2px solid var(--accent-color);
    outline-offset: -2px;
}

/* Cell editing mode */
.datatable-table td.cell-editing {
    padding: 0;
    background: var(--bg-primary) !important;
}

.datatable-table td .cell-edit-input {
    width: 100%;
    height: 100%;
    padding: 4px 8px;
    border: none;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 11px;
    font-family: inherit;
    box-sizing: border-box;
}

.datatable-table td .cell-edit-input:focus {
    outline: none;
    box-shadow: inset 0 0 0 2px var(--accent-color);
}

/* Make cells focusable for keyboard navigation */
.datatable-table td[tabindex] {
    cursor: cell;
}

/* Visual feedback - copy flash animation */
.datatable-table td.copy-flash {
    animation: copy-flash 0.3s ease-out;
}

@keyframes copy-flash {
    0% { background: var(--accent-color); }
    100% { background: inherit; }
}

/* Marching ants border for copied cells (Excel-style) */
.datatable-table td.copy-border-top {
    border-top: 2px dashed #4a9eff !important;
    animation: march-top 0.4s linear infinite;
}

.datatable-table td.copy-border-bottom {
    border-bottom: 2px dashed #4a9eff !important;
    animation: march-bottom 0.4s linear infinite;
}

.datatable-table td.copy-border-left {
    border-left: 2px dashed #4a9eff !important;
    animation: march-left 0.4s linear infinite;
}

.datatable-table td.copy-border-right {
    border-right: 2px dashed #4a9eff !important;
    animation: march-right 0.4s linear infinite;
}

/* Marching ants animation keyframes */
@keyframes march-top {
    0% { border-top-style: dashed; }
    50% { border-top-style: dotted; }
    100% { border-top-style: dashed; }
}

@keyframes march-bottom {
    0% { border-bottom-style: dashed; }
    50% { border-bottom-style: dotted; }
    100% { border-bottom-style: dashed; }
}

@keyframes march-left {
    0% { border-left-style: dashed; }
    50% { border-left-style: dotted; }
    100% { border-left-style: dashed; }
}

@keyframes march-right {
    0% { border-right-style: dashed; }
    50% { border-right-style: dotted; }
    100% { border-right-style: dashed; }
}

/* Cut cells appear faded */
.datatable-table td.cut-pending {
    opacity: 0.5;
}

/* Editable table styles - uses span cells with contenteditable for editing */
.datatable-table.editable td {
    padding: 4px 8px;
    cursor: cell;
    position: relative;
    user-select: none;
}

/* Cell content span for truncation */
.datatable-table.editable td .cell-text {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    pointer-events: none;  /* Let clicks pass through to td */
}

.datatable-table.editable td:hover {
    background: var(--cell-hover-bg) !important;
}

/* Cell selection highlight - theme-aware */
.datatable-table.editable td.cell-selected {
    background: var(--cell-selected-bg) !important;
}

/* Current cell (keyboard focus target) */
.datatable-table.editable td.cell-current {
    background: var(--cell-selected-bg) !important;
    outline: 2px solid var(--accent-color);
    outline-offset: -2px;
    z-index: 5;
}

/* Focus state for keyboard navigation */
.datatable-table.editable td:focus {
    outline: 2px solid var(--accent-color);
    outline-offset: -2px;
    z-index: 5;
}

/* Cell editing mode - contenteditable active */
.datatable-table.editable td.cell-editing {
    background: var(--bg-primary) !important;
    user-select: text;
    cursor: text;
}

.datatable-table.editable td.cell-editing .cell-text {
    display: none;  /* Hide span during edit */
}

/* Input element created during editing */
.datatable-table.editable td .cell-edit-input {
    width: 100%;
    height: 100%;
    padding: 4px 8px;
    margin: -4px -8px;
    border: none;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 11px;
    font-family: inherit;
    box-sizing: content-box;
}

.datatable-table.editable td .cell-edit-input:focus {
    outline: none;
    box-shadow: inset 0 0 0 2px var(--accent-color);
}

/* Row hover highlighting for editable table */
.datatable-table.editable tr:hover td {
    background: rgba(74, 158, 255, 0.05);
}

/* Row number highlight on row hover */
.datatable-table.editable tr:hover td.row-num {
    background: var(--accent-color) !important;
    color: white !important;
}

/* Column header editable styles */
.editable-header {
    display: flex;
    align-items: center;
    gap: 4px;
}

.editable-header .col-name-input {
    flex: 1;
    min-width: 40px;
    padding: 2px 4px;
    border: 1px solid transparent;
    border-radius: 2px;
    background: transparent;
    font-size: 11px;
    font-weight: 600;
}

.editable-header .col-name-input:hover {
    border-color: var(--border-color);
}

.editable-header .col-name-input:focus {
    outline: none;
    border-color: var(--accent-color);
    background: var(--bg-primary);
}

.editable-header .col-type-select {
    padding: 2px 4px;
    border: 1px solid var(--border-color);
    border-radius: 2px;
    background: var(--bg-secondary);
    font-size: 10px;
    cursor: pointer;
    min-width: 42px;
    color: var(--text-primary);
}

/* Context menu styles */
.datatable-context-menu {
    position: fixed;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 160px;
    padding: 4px 0;
    font-size: 12px;
}

.datatable-context-menu .context-menu-item {
    padding: 6px 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}

.datatable-context-menu .context-menu-item:hover {
    background: var(--bg-secondary);
}

.datatable-context-menu .context-menu-item .shortcut {
    margin-left: auto;
    color: var(--text-secondary);
    font-size: 10px;
}

.datatable-context-menu .context-menu-divider {
    height: 1px;
    background: var(--border-color);
    margin: 4px 0;
}

/* Load status indicator for infinite scroll */
.datatable-load-status {
    padding: 6px 12px;
    font-size: 11px;
    color: var(--text-secondary);
    text-align: center;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
}

/* Editable table scroll container */
.editable-table-scroll {
    flex: 1;
    overflow: auto;
    min-height: 0;  /* Allow flex shrinking */
}

.editable-table-wrapper {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;  /* Allow flex shrinking */
}
"""

__all__ = ["CSS_DATATABLE_TABLE"]

# EOF
