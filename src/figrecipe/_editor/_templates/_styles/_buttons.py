#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Button CSS styles for the figure editor.

This module contains CSS for:
- Base button styles
- Primary, secondary, warning buttons
- Theme toggle and style info
- Download dropdown
"""

STYLES_BUTTONS = """
/* Buttons */
button {
    padding: 8px 16px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
}

button:hover {
    background: var(--bg-secondary);
}

.btn-primary {
    background: var(--accent-color);
    border-color: var(--accent-color);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
}

.btn-secondary {
    background: var(--bg-secondary);
}

.btn-warning {
    background: #f59e0b;
    border-color: #f59e0b;
    color: white;
}

.btn-warning:hover {
    background: #d97706;
    border-color: #d97706;
}

.style-info {
    padding: 8px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.style-label {
    color: var(--text-secondary);
}

.style-name {
    color: var(--accent-color);
    font-weight: 600;
    font-family: monospace;
}

.theme-selector {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--accent-color);
    font-weight: 600;
    font-family: monospace;
    font-size: 12px;
    cursor: pointer;
}

.theme-selector:hover {
    border-color: var(--accent-color);
}

.theme-selector:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.theme-actions {
    display: flex;
    gap: 4px;
    margin-left: auto;
}

.btn-small {
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 3px;
}

/* Split dropdown for download button */
.download-dropdown {
    position: relative;
    display: flex;
}

.download-main {
    border-radius: 4px 0 0 4px;
    padding: 8px 16px;
    font-weight: 500;
}

.download-toggle {
    border-radius: 0 4px 4px 0;
    padding: 8px 8px;
    border-left: 1px solid rgba(255, 255, 255, 0.2);
    font-size: 10px;
}

.download-menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 100;
    margin-top: 4px;
    overflow: hidden;
}

.download-menu.open {
    display: block;
}

.download-option {
    display: block;
    width: 100%;
    padding: 10px 16px;
    text-align: left;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 13px;
    border-radius: 0;
}

.download-option:hover {
    background: var(--bg-secondary);
}

.download-option.active {
    background: var(--accent-color);
    color: white;
}

.download-option.active:hover {
    background: var(--accent-hover);
}

/* Legacy download buttons (kept for compatibility) */
.download-buttons {
    display: flex;
    gap: 8px;
}

.download-buttons button {
    flex: 1;
}

/* Theme toggle */
.theme-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 13px;
}

.theme-toggle input {
    width: 18px;
    height: 18px;
}

/* Loading state */
.loading {
    opacity: 0.6;
    pointer-events: none;
}
"""

__all__ = ["STYLES_BUTTONS"]

# EOF
