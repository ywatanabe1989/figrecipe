#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Label and legend CSS styles for the figure editor.

This module contains CSS for:
- Axis type toggle buttons
- Label input fields
- Legend position and label styling
"""

STYLES_LABELS = """
/* Axis Type Toggle */
.axis-type-toggle {
    display: flex;
    gap: 0;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    overflow: hidden;
    flex: 1;
}

.axis-type-btn {
    flex: 1;
    padding: 6px 12px;
    font-size: 12px;
    border: none;
    background: var(--bg-primary);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s;
    border-radius: 0;
}

.axis-type-btn:first-child {
    border-right: 1px solid var(--border-color);
}

.axis-type-btn:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.axis-type-btn.active {
    background: var(--accent-color);
    color: white;
}

/* Label input styling */
.label-input {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 13px;
}

.label-input:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

/* Legend custom position */
.legend-custom-pos {
    margin-top: 8px;
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
}

.form-hint {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
    font-style: italic;
}

/* Legend labels editor */
.legend-labels-container {
    margin-top: 8px;
}

.legend-label-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.legend-label-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid var(--border-color);
    flex-shrink: 0;
}

.legend-label-input {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 12px;
}

.legend-label-input:focus {
    outline: none;
    border-color: var(--accent-color);
}
"""

__all__ = ["STYLES_LABELS"]

# EOF
