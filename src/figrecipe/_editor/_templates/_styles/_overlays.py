#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ruler, grid, and column overlay CSS styles for the figure editor.

This module contains CSS for:
- Ruler overlay with measurements
- Grid overlay (1mm and 5mm lines)
- Column guide overlay
"""

STYLES_OVERLAYS = """
/* Ruler & Grid toggle button */
.btn-ruler {
    padding: 6px 12px;
    font-size: 13px;
}

.btn-ruler.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

/* Ruler, Grid, Column overlays */
.ruler-overlay,
.grid-overlay,
.column-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 5;
    display: none;
}

.ruler-overlay.visible,
.grid-overlay.visible,
.column-overlay.visible {
    display: block;
}

/* Ruler styles */
.ruler-line {
    stroke: #ff6600;
    stroke-width: 1;
}

.ruler-line-major {
    stroke: #ff6600;
    stroke-width: 1.5;
}

.ruler-text {
    fill: #ff6600;
    font-size: 10px;
    font-family: monospace;
}

.ruler-bg {
    fill: rgba(255, 255, 255, 0.85);
}

[data-theme="dark"] .ruler-bg {
    fill: rgba(30, 30, 30, 0.85);
}

[data-theme="dark"] .ruler-line,
[data-theme="dark"] .ruler-line-major {
    stroke: #ff9944;
}

[data-theme="dark"] .ruler-text {
    fill: #ff9944;
}

/* Grid styles */
.grid-line-1mm {
    stroke: rgba(100, 100, 255, 0.2);
    stroke-width: 0.5;
}

.grid-line-5mm {
    stroke: rgba(100, 100, 255, 0.5);
    stroke-width: 1;
}

[data-theme="dark"] .grid-line-1mm {
    stroke: rgba(150, 150, 255, 0.2);
}

[data-theme="dark"] .grid-line-5mm {
    stroke: rgba(150, 150, 255, 0.5);
}

/* Column guide styles */
.column-line {
    stroke: #22cc22;
    stroke-width: 2;
    stroke-dasharray: 8, 4;
}

.column-text {
    fill: #22cc22;
    font-size: 12px;
    font-family: monospace;
    font-weight: bold;
}

.column-bg {
    fill: rgba(255, 255, 255, 0.8);
}

[data-theme="dark"] .column-line {
    stroke: #44ff44;
}

[data-theme="dark"] .column-text {
    fill: #44ff44;
}

[data-theme="dark"] .column-bg {
    fill: rgba(30, 30, 30, 0.8);
}
"""

__all__ = ["STYLES_OVERLAYS"]

# EOF
