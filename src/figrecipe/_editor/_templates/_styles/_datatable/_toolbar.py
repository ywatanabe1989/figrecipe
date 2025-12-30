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

/* Theme-aware dropdown options */
.datatable-toolbar select option,
.plot-type-select option {
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 4px 8px;
}

.datatable-toolbar select option:checked,
.plot-type-select option:checked {
    background: var(--accent-color);
    color: white;
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

/* Import data section - larger dropzone */
.datatable-import {
    padding: 12px 12px;
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
}

/* Hide entire import section when dropzone is hidden */
.datatable-import:has(.datatable-import-dropzone[style*="display: none"]) {
    display: none;
}

.datatable-import-dropzone {
    border: 2px dashed var(--border-color);
    border-radius: 6px;
    padding: 32px 16px;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 200px;
}

.datatable-import-dropzone:hover,
.datatable-import-dropzone.drag-over {
    border-color: var(--accent-color);
    background: var(--selection-color);
}

.datatable-import-dropzone p {
    margin: 4px 0;
    font-size: 12px;
    color: var(--text-secondary);
}

.datatable-import-dropzone .hint {
    font-size: 10px;
    opacity: 0.7;
}

.datatable-import-dropzone input[type="file"] {
    display: none;
}

/* Dropzone divider between file drop and create new */
.dropzone-divider {
    margin: 16px 0;
    font-size: 11px;
    color: var(--text-secondary);
    opacity: 0.6;
    position: relative;
}

.dropzone-divider::before,
.dropzone-divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 40px;
    height: 1px;
    background: var(--border-color);
}

.dropzone-divider::before {
    right: calc(100% + 8px);
}

.dropzone-divider::after {
    left: calc(100% + 8px);
}

/* Create New Table button in dropzone */
.btn-create-new {
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 500;
    background: var(--accent-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
}

.btn-create-new:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
}

.btn-create-new:active {
    transform: translateY(0);
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

/* Shortcuts info button */
.btn-icon {
    font-size: 14px;
    padding: 4px 6px;
    min-width: 28px;
}

/* Shortcuts popup */
.shortcuts-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    min-width: 300px;
    max-width: 400px;
    display: none;
}

.shortcuts-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
}

.shortcuts-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}

.shortcuts-header .btn-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 0;
    line-height: 1;
}

.shortcuts-header .btn-close:hover {
    color: var(--text-primary);
}

.shortcuts-content {
    padding: 12px 16px;
}

.shortcut-group {
    margin-bottom: 12px;
}

.shortcut-group:last-child {
    margin-bottom: 0;
}

.shortcut-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    padding: 4px 0;
    color: var(--text-secondary);
}

.shortcut-row kbd {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 3px;
    padding: 2px 6px;
    font-size: 11px;
    font-family: monospace;
    min-width: 60px;
    text-align: center;
    color: var(--text-primary);
}
"""

__all__ = ["CSS_DATATABLE_TOOLBAR"]

# EOF
