#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS styles for figure editor.
"""

STYLES = """
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

/* Preview Panel */
.preview-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border-color);
    min-width: 400px;
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
}

.preview-header h2 {
    font-size: 16px;
    font-weight: 600;
}

.preview-controls {
    display: flex;
    gap: 12px;
    align-items: center;
}

.preview-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: var(--bg-tertiary);
    position: relative;
    overflow: auto;
    /* Checkerboard pattern for transparency */
    background-image:
        linear-gradient(45deg, #ccc 25%, transparent 25%),
        linear-gradient(-45deg, #ccc 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #ccc 75%),
        linear-gradient(-45deg, transparent 75%, #ccc 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

[data-theme="dark"] .preview-wrapper {
    background-image:
        linear-gradient(45deg, #333 25%, transparent 25%),
        linear-gradient(-45deg, #333 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #333 75%),
        linear-gradient(-45deg, transparent 75%, #333 75%);
}

#preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    cursor: crosshair;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hitregion-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 10;  /* Above the preview image */
}

/* Always display overlay for hover detection, but control visibility via children */
.hitregion-overlay.visible .hitregion-rect,
.hitregion-overlay.visible .hitregion-polyline {
    opacity: 1;
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
    fill: transparent;
    stroke: rgba(100, 180, 255, 0.5);
    stroke-width: 2;
    stroke-dasharray: 6, 3;
    pointer-events: all;
    cursor: pointer;
    transition: fill 0.2s, stroke 0.2s, filter 0.2s, opacity 0.15s;
}

.hitregion-rect:hover {
    fill: rgba(100, 180, 255, 0.15);
    stroke: rgba(100, 180, 255, 1);
    stroke-width: 3;
    filter: drop-shadow(0 0 4px rgba(100, 180, 255, 0.8));
}

.hitregion-polyline {
    fill: none !important;
    stroke: rgba(255, 200, 100, 0.6);
    stroke-width: 8;
    stroke-linecap: round;
    stroke-linejoin: round;
    pointer-events: stroke;
    cursor: pointer;
    transition: stroke 0.2s, stroke-width 0.2s, filter 0.2s, opacity 0.15s;
}

.hitregion-polyline:hover {
    fill: none !important;
    stroke: rgba(255, 200, 50, 0.95);
    stroke-width: 14;
    filter: drop-shadow(0 0 8px rgba(255, 200, 50, 0.9));
}

.hitregion-rect.line-region {
    stroke: rgba(255, 200, 100, 0.6);
}

.hitregion-rect.line-region:hover {
    fill: rgba(255, 200, 100, 0.15);
    stroke: rgba(255, 200, 100, 1);
    filter: drop-shadow(0 0 3px rgba(255, 200, 100, 0.6));
}

.hitregion-rect.text-region {
    stroke: rgba(100, 220, 150, 0.6);
}

.hitregion-rect.text-region:hover {
    fill: rgba(100, 220, 150, 0.15);
    stroke: rgba(100, 220, 150, 1);
    filter: drop-shadow(0 0 3px rgba(100, 220, 150, 0.6));
}

.hitregion-rect.legend-region {
    stroke: rgba(220, 180, 100, 0.6);
}

.hitregion-rect.legend-region:hover {
    fill: rgba(220, 180, 100, 0.15);
    stroke: rgba(220, 180, 100, 1);
    filter: drop-shadow(0 0 3px rgba(220, 180, 100, 0.6));
}

.hitregion-rect.tick-region {
    stroke: rgba(180, 100, 220, 0.6);
}

.hitregion-rect.tick-region:hover {
    fill: rgba(180, 100, 220, 0.15);
    stroke: rgba(180, 100, 220, 1);
    filter: drop-shadow(0 0 3px rgba(180, 100, 220, 0.6));
}

.hitregion-label {
    font-size: 10px;
    fill: var(--text-primary);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s;
}

.hitregion-rect:hover + .hitregion-label,
.hitregion-group:hover .hitregion-label {
    opacity: 1;
}

#btn-show-hitmap.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.selection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.selection-rect {
    fill: var(--selection-color);
    stroke: var(--accent-color);
    stroke-width: 2;
    stroke-dasharray: 5, 3;
}

.selected-element-info {
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    font-size: 13px;
    color: var(--text-secondary);
}

/* Controls Panel */
.controls-panel {
    width: 350px;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    overflow: hidden;
}

.controls-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
}

.controls-header h2 {
    font-size: 16px;
    font-weight: 600;
}

.controls-actions {
    display: flex;
    gap: 8px;
}

.controls-sections {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

/* Sections */
.section {
    margin-bottom: 8px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    overflow: hidden;
}

.section summary {
    padding: 10px 14px;
    background: var(--bg-secondary);
    cursor: pointer;
    font-weight: 500;
    user-select: none;
    list-style: none;
    display: flex;
    align-items: center;
}

.section summary::before {
    content: '\\25B6';
    font-size: 10px;
    margin-right: 8px;
    transition: transform 0.2s;
}

.section[open] summary::before {
    transform: rotate(90deg);
}

.section-highlighted {
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.section-highlighted summary {
    background: rgba(37, 99, 235, 0.1);
    border-left: 3px solid var(--accent-color);
}

[data-theme="dark"] .section-highlighted {
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

[data-theme="dark"] .section-highlighted summary {
    background: rgba(59, 130, 246, 0.15);
}

/* Field highlighting for selected element */
.field-highlighted {
    background: rgba(37, 99, 235, 0.08);
    border-radius: 4px;
    padding: 6px 8px;
    margin: -6px -8px;
    margin-bottom: 8px;
    border-left: 3px solid var(--accent-color);
}

.field-highlighted:last-child {
    margin-bottom: 0;
}

[data-theme="dark"] .field-highlighted {
    background: rgba(59, 130, 246, 0.12);
}

.section-content {
    padding: 12px 14px;
    background: var(--bg-primary);
}

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

/* Form elements */
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

.override-status {
    padding: 8px 16px;
    background: rgba(245, 158, 11, 0.1);
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.override-indicator {
    color: #f59e0b;
    font-weight: 500;
}

.override-timestamp {
    color: var(--text-secondary);
    font-size: 11px;
}

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

/* Scrollbar styling */
.controls-sections::-webkit-scrollbar {
    width: 8px;
}

.controls-sections::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

.controls-sections::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

.controls-sections::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
    .editor-container {
        flex-direction: column;
    }

    .preview-panel {
        min-width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border-color);
    }

    .controls-panel {
        width: 100%;
        max-height: 50vh;
    }
}
"""

__all__ = ['STYLES']
