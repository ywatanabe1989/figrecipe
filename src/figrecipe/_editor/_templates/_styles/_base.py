#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base CSS styles for the figure editor.

This module contains CSS for:
- CSS variables (light and dark theme)
- Reset and base styles
- Main container layout
"""

STYLES_BASE = """
/* CSS Variables for theming */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f5;
    --bg-tertiary: #e8e8e8;
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
    --border-color: #d0d0d0;
    --accent-color: #2563eb;
    --accent-hover: #1d4ed8;
    --success-color: #10b981;
    --error-color: #ef4444;
    --selection-color: rgba(37, 99, 235, 0.3);
    /* Solid selection colors for tables (opaque, theme-aware) */
    --cell-selected-bg: #dbeafe;
    --cell-hover-bg: #f0f4f8;
    --header-bg: #e8e8e8;
    --header-input-bg: #f5f5f5;
    --row-num-bg: #f0f0f0;
    /* Variable-linked column colors (light mode) */
    --var-linked-bg: #c7d9f0;
    --var-linked-cell-bg: #e8f0fa;
    /* Consistent panel header styling */
    --panel-header-height: 42px;
    --panel-header-bg: var(--bg-tertiary);
}

[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #252525;
    --bg-tertiary: #333333;
    --text-primary: #e8e8e8;
    --text-secondary: #a0a0a0;
    --border-color: #404040;
    --accent-color: #3b82f6;
    --accent-hover: #60a5fa;
    --selection-color: rgba(59, 130, 246, 0.3);
    /* Solid selection colors for tables (opaque, theme-aware) */
    --cell-selected-bg: #1e3a5f;
    --cell-hover-bg: #2a2a35;
    --header-bg: #2a2a2a;
    --header-input-bg: #333333;
    --row-num-bg: #1e1e1e;
    /* Variable-linked column colors (dark mode) */
    --var-linked-bg: #2a4a6a;
    --var-linked-cell-bg: #1a3045;
}

/* Reset and base */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    background: var(--bg-primary);
    color: var(--text-primary);
    height: 100vh;
    overflow: hidden;
}

/* Main container */
.editor-container {
    display: flex;
    height: 100vh;
}

/* Global scrollbar styling - thin and theme-responsive */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Firefox scrollbar */
* {
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) var(--bg-secondary);
}
"""

__all__ = ["STYLES_BASE"]

# EOF
