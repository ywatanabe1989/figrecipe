#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controls panel CSS styles for the figure editor.

This module contains CSS for:
- Controls panel layout
- Tab navigation
- Sections and form elements
- Field highlighting
"""

STYLES_CONTROLS = """
/* Controls Panel */
.controls-panel {
    width: 350px;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    overflow: hidden;
}

.controls-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
}

.controls-header h2 {
    font-size: 16px;
    font-weight: 600;
}

.controls-actions {
    display: flex;
    gap: 8px;
}

.controls-sections {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

/* Tab Navigation */
.tab-navigation {
    display: flex;
    gap: 0;
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 4px;
    margin-bottom: 12px;
}

.tab-btn {
    flex: 1;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    color: var(--text-secondary);
}

.tab-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.tab-btn.active {
    background: var(--accent-color);
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Tab Content */
.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.tab-hint {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    border-radius: 8px;
    margin-bottom: 12px;
}

.tab-hint p {
    margin: 0;
}

.tab-hint .hint-sub {
    font-size: 12px;
    margin-top: 8px;
    opacity: 0.7;
}

/* Selected element panel in Element tab */
.selected-element-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
    margin-bottom: 12px;
}

.element-type-badge {
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    background: var(--accent-color);
    color: white;
    border-radius: 4px;
}

.element-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}

/* Legacy toggle styles for backward compatibility */
.view-mode-toggle {
    display: none;  /* Hidden - replaced by tabs */
}

.btn-toggle {
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-toggle:hover {
    background: var(--bg-tertiary);
}

.btn-toggle.active {
    background: var(--accent-color);
    border-color: var(--accent-color);
    color: white;
}

.selection-hint {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-secondary);
    font-style: italic;
}

/* Filtering mode: hide non-matching sections */
.controls-sections.filter-mode .section.section-hidden {
    display: none;
}

.controls-sections.filter-mode .form-row.field-hidden {
    display: none;
}

/* Show matching sections with highlight in filter mode */
.controls-sections.filter-mode .section.section-visible {
    border-color: var(--accent-color);
}

.controls-sections.filter-mode .section.section-visible summary {
    background: rgba(37, 99, 235, 0.08);
}

[data-theme="dark"] .controls-sections.filter-mode .section.section-visible summary {
    background: rgba(59, 130, 246, 0.12);
}

/* Sections */
.section {
    margin-bottom: 8px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    overflow: hidden;
}

.section summary {
    padding: 10px 14px;
    background: var(--bg-secondary);
    cursor: pointer;
    font-weight: 500;
    user-select: none;
    list-style: none;
    display: flex;
    align-items: center;
}

.section summary::before {
    content: '\\25B6';
    font-size: 10px;
    margin-right: 8px;
    transition: transform 0.2s;
}

.section[open] summary::before {
    transform: rotate(90deg);
}

.section-highlighted {
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.section-highlighted summary {
    background: rgba(37, 99, 235, 0.1);
    border-left: 3px solid var(--accent-color);
}

[data-theme="dark"] .section-highlighted {
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

[data-theme="dark"] .section-highlighted summary {
    background: rgba(59, 130, 246, 0.15);
}

/* Field highlighting for selected element */
.field-highlighted {
    background: rgba(37, 99, 235, 0.08);
    border-radius: 4px;
    padding: 6px 8px;
    margin: -6px -8px;
    margin-bottom: 8px;
    border-left: 3px solid var(--accent-color);
}

.field-highlighted:last-child {
    margin-bottom: 0;
}

[data-theme="dark"] .field-highlighted {
    background: rgba(59, 130, 246, 0.12);
}

.section-content {
    padding: 12px 14px;
    background: var(--bg-primary);
}
"""

__all__ = ["STYLES_CONTROLS"]

# EOF
