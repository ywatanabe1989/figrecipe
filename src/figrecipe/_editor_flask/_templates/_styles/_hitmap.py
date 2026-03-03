#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitmap overlay CSS styles for the figure editor.

This module contains CSS for:
- Hitregion overlay and visibility modes
- Hitregion rectangles, polylines, circles
- Scatter groups and labels
- Group hover highlights
"""

STYLES_HITMAP = """
/* Hit Region Overlay */
.hitregion-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: auto;  /* Allow clicks on empty areas to deselect */
    z-index: 10;  /* Above the preview image */
}

/* Always display overlay for hover detection, but control visibility via children */
.hitregion-overlay.visible .hitregion-rect,
.hitregion-overlay.visible .hitregion-polyline {
    opacity: 1;
    stroke: rgba(128, 128, 128, 0.3);  /* Slight visible stroke in visible mode */
}

.hitregion-overlay.visible .hitregion-polyline {
    stroke: rgba(128, 128, 128, 0.2);
    stroke-width: 6;
}

/* Hover-only mode: invisible until hovered */
.hitregion-overlay.hover-mode .hitregion-rect,
.hitregion-overlay.hover-mode .hitregion-polyline {
    opacity: 0;
}

.hitregion-overlay.hover-mode .hitregion-rect:hover,
.hitregion-overlay.hover-mode .hitregion-polyline:hover {
    opacity: 1;
}

.hitregion-rect {
    --element-color: #888888;  /* Default fallback */
    fill: transparent;
    stroke: transparent;
    stroke-width: 2;
    stroke-dasharray: 6, 3;
    pointer-events: all;
    cursor: pointer;
    transition: fill 0.2s, stroke 0.2s, filter 0.2s, opacity 0.15s;
}

.hitregion-rect:hover {
    fill: var(--element-color);
    fill-opacity: 0.2;
    stroke: var(--element-color);
    stroke-opacity: 0.8;
    stroke-width: 3;
    stroke-dasharray: none;
    filter: none;
}

/* Axes regions: disable pointer events to let clicks pass through to
   elements inside (pie, scatter, bar, etc.). Axes selection happens via
   the panel drag system which uses mousedown on the preview area. */
.hitregion-rect.axes-region {
    pointer-events: none;
}

.hitregion-polyline {
    --element-color: #888888;  /* Default fallback */
    fill: none !important;
    stroke: transparent;
    stroke-width: 8;
    stroke-linecap: round;
    stroke-linejoin: round;
    pointer-events: stroke;
    cursor: pointer;
    transition: stroke 0.15s, opacity 0.15s;
}

.hitregion-polyline:hover {
    fill: none !important;
    stroke: var(--element-color);
    stroke-width: 8;
    stroke-opacity: 0.4;
    filter: none;
}

/* Scatter point circles */
.scatter-group {
    --element-color: #888888;  /* Default fallback */
    pointer-events: all;
}

.hitregion-circle {
    fill: transparent;
    stroke: transparent;
    stroke-width: 1;
    pointer-events: all;
    cursor: pointer;
    opacity: 1;  /* Explicit default */
    transition: fill 0.15s, stroke 0.15s, opacity 0.15s;
}

.hitregion-circle:hover,
.hitregion-circle.hovered {
    fill: var(--element-color);
    fill-opacity: 0.2;
    stroke: var(--element-color);
    stroke-opacity: 0.5;
    stroke-width: 1;
    filter: none;
}

/* When any circle in the group is hovered, highlight ALL circles in the group */
.scatter-group:hover .hitregion-circle,
.scatter-group.hovered .hitregion-circle {
    fill: var(--element-color);
    fill-opacity: 0.15;
    stroke: var(--element-color);
    stroke-opacity: 0.4;
    stroke-width: 1;
    filter: none;
}

/* Scatter circles visibility modes */
.hitregion-overlay.visible .hitregion-circle,
.hitregion-overlay.visible .scatter-group {
    opacity: 1;
}

.hitregion-overlay.hover-mode .hitregion-circle {
    opacity: 0;
}

.hitregion-overlay.hover-mode .scatter-group:hover .hitregion-circle,
.hitregion-overlay.hover-mode .hitregion-circle:hover {
    opacity: 1;
}

.hitregion-label {
    font-size: 10px;
    fill: var(--text-primary);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s;
}

.hitregion-rect:hover + .hitregion-label,
.hitregion-group:hover .hitregion-label,
.hitregion-group.hovered .hitregion-label,
.scatter-group:hover ~ .hitregion-label,
.scatter-group.hovered ~ .hitregion-label,
.hitregion-polyline:hover + .hitregion-label {
    opacity: 1;
}

#btn-show-hitmap.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

/* Group hover highlight - all elements in same logical group */
.group-hovered {
    opacity: 1 !important;
}

.group-hovered .hitregion-polyline,
.group-hovered .hitregion-rect,
.group-hovered .hitregion-circle {
    stroke: var(--accent-color) !important;
    stroke-width: 3 !important;
    fill: var(--selection-color) !important;
}

.hitregion-group.group-hovered .hitregion-label {
    opacity: 1 !important;
    font-weight: bold;
}
"""

__all__ = ["STYLES_HITMAP"]

# EOF
