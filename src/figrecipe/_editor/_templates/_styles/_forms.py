#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Form elements CSS styles for the figure editor.

This module contains CSS for:
- Form rows and labels
- Input fields (number, text, checkbox, color, range)
- Override indicators for modified values
"""

STYLES_FORMS = """
/* Form elements */
.subsection {
    margin-bottom: 12px;
}

.subsection:last-child {
    margin-bottom: 0;
}

.subsection h4 {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.form-row:last-child {
    margin-bottom: 0;
}

.form-row label {
    flex: 0 0 120px;
    font-size: 13px;
    color: var(--text-secondary);
}

.form-row input[type="number"],
.form-row input[type="text"],
.form-row select {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 13px;
    min-width: 0;  /* Allow shrinking below content size */
    max-width: calc(100% - 130px);  /* Leave space for label + margin */
}

.form-row input[type="number"]:focus,
.form-row input[type="text"]:focus,
.form-row select:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

/* Override indicator for modified values */
.form-row.value-modified input,
.form-row.value-modified select {
    border-color: #f59e0b;
    background: rgba(245, 158, 11, 0.05);
}

.form-row.value-modified label::after {
    content: '●';
    color: #f59e0b;
    margin-left: 4px;
    font-weight: bold;
}

[data-theme="dark"] .form-row.value-modified input,
[data-theme="dark"] .form-row.value-modified select {
    border-color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
}

.form-row input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.form-row input[type="color"] {
    width: 50px;
    height: 30px;
    padding: 2px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
}

.form-row input[type="range"] {
    flex: 1;
    margin-right: 8px;
}

.form-row input[type="range"] + span {
    min-width: 30px;
    text-align: right;
    font-size: 12px;
    color: var(--text-secondary);
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.form-grid .form-row label {
    flex: 0 0 60px;
}

/* Spine visibility grid - 2x2 layout */
.spine-visibility-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 12px;
    margin: 8px 0;
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 6px;
}

.spine-visibility-grid .form-row {
    margin-bottom: 0;
}

.spine-visibility-grid .form-row label {
    flex: 0 0 80px;
    font-size: 12px;
}

/* Caption textarea styling */
.caption-textarea {
    flex: 1;
    padding: 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 12px;
    font-family: inherit;
    resize: vertical;
    min-height: 40px;
}

.caption-textarea:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.caption-row {
    align-items: flex-start !important;
}

.caption-row label {
    padding-top: 8px;
}

.caption-preview {
    font-size: 11px;
    font-style: italic;
    color: var(--text-secondary);
    margin-top: 4px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
}

.caption-preview span {
    color: var(--text-primary);
    font-weight: 500;
}

/* Composed caption preview */
.composed-caption-preview {
    margin-top: 12px;
    padding: 10px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
}

.composed-caption-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.composed-caption-text {
    font-size: 12px;
    line-height: 1.5;
    color: var(--text-primary);
}

.composed-caption-text b {
    font-weight: 600;
}

.composed-caption-text .panel-caption {
    color: var(--text-secondary);
    margin-left: 4px;
}
"""

__all__ = ["STYLES_FORMS"]

# EOF
