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
"""

__all__ = ["STYLES_FORMS"]

# EOF
