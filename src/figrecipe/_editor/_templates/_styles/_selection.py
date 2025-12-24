#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selection overlay CSS styles for the figure editor.

This module contains CSS for:
- Selection overlay container
- Selection rectangles, polylines, circles
- Primary selection highlights
"""

STYLES_SELECTION = """
/* Selection Overlay */
.selection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.selection-rect {
    --element-color: #2563eb;  /* Default fallback to accent color */
    fill: var(--element-color);
    fill-opacity: 0.15;
    stroke: var(--element-color);
    stroke-opacity: 0.6;
    stroke-width: 2;
    stroke-dasharray: 5, 3;
}

/* Primary selection in a group - solid border */
.selection-rect.selection-primary {
    fill-opacity: 0.2;
    stroke-opacity: 0.8;
    stroke-width: 3;
    stroke-dasharray: none;
}

/* Selection for lines - show stroke along the path */
.selection-polyline {
    --element-color: #2563eb;
    fill: none !important;
    stroke: var(--element-color);
    stroke-width: 8;
    stroke-opacity: 0.5;
    stroke-linecap: round;
    stroke-linejoin: round;
}

/* Selection for scatter points */
.selection-circle {
    --element-color: #2563eb;
    fill: var(--element-color);
    fill-opacity: 0.3;
    stroke: var(--element-color);
    stroke-opacity: 0.7;
    stroke-width: 2;
}

/* Subtle selection for scatter points (less visually overwhelming) */
.selection-circle-subtle {
    --element-color: #2563eb;
    fill: none;
    stroke: var(--element-color);
    stroke-opacity: 0.4;
    stroke-width: 1.5;
}
"""

__all__ = ["STYLES_SELECTION"]

# EOF
