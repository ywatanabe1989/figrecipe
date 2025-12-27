#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS for editable datatable functionality."""

CSS_DATATABLE_EDITABLE = """
/* ============================================================================
   Create New Table Button
   ============================================================================ */
.datatable-create-new {
    text-align: center;
    padding: 8px;
    border-top: 1px solid var(--dt-border);
}

.btn-create-csv {
    background: var(--dt-accent);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background 0.2s;
}

.btn-create-csv:hover {
    background: var(--dt-accent-hover);
}

/* ============================================================================
   Editable Table Styles
   ============================================================================ */
.editable-table-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.editable-table-actions {
    display: flex;
    gap: 4px;
    padding: 4px;
    background: var(--dt-header-bg);
    border-bottom: 1px solid var(--dt-border);
    flex-shrink: 0;
}

.editable-table-actions .btn-small {
    padding: 2px 8px;
    font-size: 11px;
    background: var(--dt-bg);
    border: 1px solid var(--dt-border);
    border-radius: 3px;
    cursor: pointer;
    color: var(--dt-text);
}

.editable-table-actions .btn-small:hover {
    background: var(--dt-row-hover);
}

.editable-table-actions .btn-danger {
    color: #dc3545;
}

.editable-table-actions .btn-danger:hover {
    background: rgba(220, 53, 69, 0.1);
}

/* ============================================================================
   Large Table Performance (inspired by vis_app patterns)
   ============================================================================ */
/* Table container with scrolling */
.editable-table-scroll {
    overflow: auto;
    max-height: calc(100% - 40px);
    flex: 1;
}

/* Fixed row height for predictable scrolling */
.datatable-table.editable {
    border-collapse: separate;
    border-spacing: 0;
}

.datatable-table.editable tr {
    height: 28px;
}

/* Sticky header row */
.datatable-table.editable thead th {
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--dt-header-bg);
}

/* Sticky row numbers column */
.datatable-table.editable .row-num {
    position: sticky;
    left: 0;
    z-index: 5;
    background: var(--dt-header-bg);
}

/* Corner cell (row # header) - highest z-index */
.datatable-table.editable thead th.row-num {
    z-index: 11;
}

/* Editable table specific styles */
.datatable-table.editable th {
    padding: 2px;
}

.editable-header {
    display: flex;
    align-items: center;
    gap: 2px;
}

.col-name-input {
    flex: 1;
    min-width: 40px;
    max-width: 80px;
    padding: 2px 4px;
    font-size: 11px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--dt-text);
    border-radius: 2px;
}

.col-name-input:hover,
.col-name-input:focus {
    border-color: var(--dt-accent);
    background: var(--dt-bg);
    outline: none;
}

.col-type-select {
    width: 28px;
    padding: 1px;
    font-size: 10px;
    border: 1px solid var(--dt-border);
    background: var(--dt-bg);
    color: var(--dt-text-muted);
    border-radius: 2px;
    cursor: pointer;
}

.editable-cell {
    padding: 0 !important;
}

.editable-cell input {
    width: 100%;
    padding: 4px 6px;
    font-size: 12px;
    border: none;
    background: transparent;
    color: var(--dt-text);
    box-sizing: border-box;
}

.editable-cell input:hover {
    background: var(--dt-row-hover);
}

.editable-cell input:focus {
    outline: 2px solid var(--dt-accent);
    outline-offset: -2px;
    background: var(--dt-bg);
}

.editable-cell input[type="number"] {
    text-align: right;
    -moz-appearance: textfield;  /* Firefox */
}

/* Hide number spinbuttons completely */
.editable-cell input[type="number"]::-webkit-inner-spin-button,
.editable-cell input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
    display: none;
}
"""

__all__ = ["CSS_DATATABLE_EDITABLE"]

# EOF
