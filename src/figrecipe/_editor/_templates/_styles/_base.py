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
"""

__all__ = ["STYLES_BASE"]

# EOF
