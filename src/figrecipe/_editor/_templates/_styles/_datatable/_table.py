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
    background: var(--bg-tertiary);
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 10;
}

.datatable-table th.selected {
    background: var(--accent-color);
    color: white;
}

.datatable-table td {
    background: var(--bg-primary);
}

.datatable-table tr:hover td {
    background: var(--bg-secondary);
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

/* Row number column */
.datatable-table th.row-num,
.datatable-table td.row-num {
    width: 40px;
    min-width: 40px;
    max-width: 40px;
    text-align: center;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-size: 10px;
}

/* Column header color linking with variables */
.datatable-table th.var-linked {
    position: relative;
}

.datatable-table th.var-linked::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--var-color, var(--accent-color));
}

/* Color classes for column headers */
.datatable-table th.var-color-0 { --var-color: #4a9eff; }
.datatable-table th.var-color-1 { --var-color: #ff6b6b; }
.datatable-table th.var-color-2 { --var-color: #51cf66; }
.datatable-table th.var-color-3 { --var-color: #ffd43b; }
.datatable-table th.var-color-4 { --var-color: #cc5de8; }
.datatable-table th.var-color-5 { --var-color: #ff922b; }

.datatable-table th.var-color-0::after { background: #4a9eff; }
.datatable-table th.var-color-1::after { background: #ff6b6b; }
.datatable-table th.var-color-2::after { background: #51cf66; }
.datatable-table th.var-color-3::after { background: #ffd43b; }
.datatable-table th.var-color-4::after { background: #cc5de8; }
.datatable-table th.var-color-5::after { background: #ff922b; }

/* Canvas-linked column highlight */
.datatable-table th.canvas-linked {
    background: var(--accent-color) !important;
    color: white;
    animation: canvas-link-pulse 1s ease-in-out;
}

.datatable-table th.canvas-linked .col-type {
    background: rgba(255,255,255,0.2);
    color: white;
}

@keyframes canvas-link-pulse {
    0% { box-shadow: 0 0 0 0 rgba(74, 158, 255, 0.7); }
    50% { box-shadow: 0 0 0 4px rgba(74, 158, 255, 0.4); }
    100% { box-shadow: 0 0 0 0 rgba(74, 158, 255, 0); }
}
"""

__all__ = ["CSS_DATATABLE_TABLE"]

# EOF
