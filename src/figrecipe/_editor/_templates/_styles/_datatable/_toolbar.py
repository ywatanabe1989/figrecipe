#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for datatable toolbar and import section."""

CSS_DATATABLE_TOOLBAR = """
/* Datatable toolbar */
.datatable-toolbar {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
    flex-shrink: 0;
}

.datatable-toolbar select {
    padding: 4px 8px;
    font-size: 11px;
    border: 1px solid var(--border-color);
    border-radius: 3px;
    background: var(--bg-primary);
    color: var(--text-primary);
}

/* Split button for New/Add to panel */
.split-btn {
    position: relative;
    display: inline-flex;
}

.split-btn .btn-plot {
    padding: 4px 10px;
    font-size: 11px;
    background: var(--accent-color);
    color: white;
    border: none;
    border-radius: 3px 0 0 3px;
    cursor: pointer;
    font-weight: 500;
}

.split-btn .btn-plot:hover {
    background: var(--accent-hover);
}

.split-btn .btn-plot:disabled {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    cursor: not-allowed;
}

.split-btn .btn-plot-dropdown {
    padding: 4px 6px;
    font-size: 9px;
    background: var(--accent-color);
    color: white;
    border: none;
    border-left: 1px solid rgba(255,255,255,0.3);
    border-radius: 0 3px 3px 0;
    cursor: pointer;
}

.split-btn .btn-plot-dropdown:hover {
    background: var(--accent-hover);
}

.split-btn .btn-plot:disabled + .btn-plot-dropdown {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    cursor: not-allowed;
}

.plot-dropdown-menu {
    display: none;
    position: absolute;
    top: 100%;
    right: 0;
    min-width: 120px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 3px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    z-index: 100;
}

.plot-dropdown-menu.show {
    display: block;
}

.plot-dropdown-menu .dropdown-item {
    display: block;
    width: 100%;
    padding: 6px 10px;
    font-size: 11px;
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-primary);
}

.plot-dropdown-menu .dropdown-item:hover {
    background: var(--bg-tertiary);
}

.plot-type-select {
    padding: 4px 8px;
    font-size: 11px;
    border: 1px solid var(--border-color);
    border-radius: 3px;
    min-width: 70px;
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
}

.datatable-toolbar label {
    font-size: 11px;
    color: var(--text-secondary);
}

/* Import data section */
.datatable-import {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;
}

.datatable-import-dropzone {
    border: 2px dashed var(--border-color);
    border-radius: 4px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
}

.datatable-import-dropzone:hover,
.datatable-import-dropzone.drag-over {
    border-color: var(--accent-color);
    background: var(--selection-color);
}

.datatable-import-dropzone p {
    margin: 0;
    font-size: 11px;
    color: var(--text-secondary);
}

.datatable-import-dropzone input[type="file"] {
    display: none;
}

/* Selection info - hidden for cleaner UI */
.datatable-selection-info {
    display: none;
}

/* Empty state */
.datatable-empty {
    padding: 24px 16px;
    text-align: center;
    color: var(--text-secondary);
}

.datatable-empty p {
    margin: 0 0 8px 0;
    font-size: 12px;
}

.datatable-empty .hint {
    font-size: 11px;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* Plot type selector in toolbar */
.plot-type-group {
    display: flex;
    align-items: center;
    gap: 4px;
}

.plot-type-btn {
    padding: 3px 8px;
    font-size: 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    cursor: pointer;
    color: var(--text-secondary);
}

.plot-type-btn:first-child {
    border-radius: 3px 0 0 3px;
}

.plot-type-btn:last-child {
    border-radius: 0 3px 3px 0;
}

.plot-type-btn:not(:last-child) {
    border-right: none;
}

.plot-type-btn.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.plot-type-btn:hover:not(.active) {
    background: var(--bg-tertiary);
}
"""

__all__ = ["CSS_DATATABLE_TOOLBAR"]

# EOF
