#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color input component CSS styles for the figure editor.

This module contains CSS for:
- Color swatches and pickers
- RGB display
- Custom color inputs
"""

STYLES_COLOR_INPUT = """
/* Color Input Component */
.color-input-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    flex-wrap: wrap;
}

.color-swatch {
    width: 28px;
    height: 28px;
    border: 2px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
    flex-shrink: 0;
    transition: border-color 0.15s;
}

.color-swatch:hover {
    border-color: var(--accent-color);
}

.color-text-input {
    flex: 1;
    min-width: 80px;
}

.rgb-display {
    font-size: 10px;
    color: var(--text-secondary);
    font-family: monospace;
    white-space: nowrap;
}

.color-preset-select {
    padding: 4px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    font-size: 10px;
    cursor: pointer;
}

.color-picker-hidden {
    position: absolute;
    opacity: 0;
    pointer-events: none;
    width: 0;
    height: 0;
}

.color-custom-input {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    font-size: 11px;
    min-width: 100px;
}

.color-custom-input:focus {
    outline: none;
    border-color: var(--accent-color);
}

.color-select {
    padding: 4px 6px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    font-size: 11px;
    min-width: 70px;
    cursor: pointer;
}

/* Color List Component (for pie chart colors array) */
.color-list-wrapper {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
}

.color-list-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.color-list-index {
    font-size: 10px;
    color: var(--text-secondary);
    min-width: 18px;
}

.color-swatch-small {
    width: 18px;
    height: 18px;
    border-width: 1px;
}

.color-select-small {
    padding: 2px 4px;
    font-size: 10px;
    min-width: 60px;
}
"""

__all__ = ["STYLES_COLOR_INPUT"]

# EOF
