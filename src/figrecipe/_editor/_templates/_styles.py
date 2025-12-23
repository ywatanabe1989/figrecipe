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
    position: relative;
    z-index: 1;  /* Below the hit region overlay */
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
    fill-opacity: 0.15;
    stroke: var(--element-color);
    stroke-opacity: 0.6;
    stroke-width: 2;
    filter: none;
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

/* Dynamic Call Properties (in right panel) */
.dynamic-call-properties {
    padding: 12px 16px;
    margin: 8px 0 16px 0;
    background: var(--bg-tertiary);
    border: 1px solid var(--accent-color);
    border-radius: 8px;
    font-size: 12px;
    max-height: 400px;
    overflow-y: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dynamic-props-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}

.dynamic-props-header strong {
    color: var(--accent-color);
}

.dynamic-props-header .call-id {
    color: var(--text-secondary);
    font-size: 11px;
    margin-left: 8px;
}

.dynamic-props-label {
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 4px;
    font-size: 11px;
}

.dynamic-props-section {
    margin-bottom: 8px;
}

.dynamic-field {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
}

.dynamic-field label {
    flex: 0 0 120px;
    font-size: 11px;
    color: var(--text-primary);
}

.dynamic-field.unused label {
    color: var(--text-secondary);
}

.dynamic-input {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    font-size: 11px;
}

.dynamic-input[type="checkbox"] {
    flex: 0 0 auto;
    width: 16px;
    height: 16px;
}

.dynamic-props-available {
    margin-top: 8px;
}

.dynamic-props-available summary {
    cursor: pointer;
    font-size: 11px;
    color: var(--text-secondary);
    padding: 4px 0;
}

.dynamic-props-available summary:hover {
    color: var(--accent-color);
}

.more-params {
    font-size: 10px;
    color: var(--text-secondary);
    font-style: italic;
    padding: 4px 0;
}

.arg-field {
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 4px 8px;
    margin: 2px 0;
}

.arg-value {
    flex: 1;
    font-family: monospace;
    font-size: 11px;
    color: var(--text-secondary);
    text-align: right;
}

.dynamic-field-container {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}

.dynamic-field-container.unused {
    opacity: 0.7;
}

.type-hint {
    font-size: 10px;
    color: var(--text-secondary);
    font-family: monospace;
    padding: 2px 0 0 0;
    margin-left: 125px;
    word-break: break-word;
    line-height: 1.3;
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

/* View mode toggle */
.view-mode-toggle {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 6px;
    margin-bottom: 8px;
}

.btn-toggle {
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-toggle:hover {
    background: var(--bg-tertiary);
}

.btn-toggle.active {
    background: var(--accent-color);
    border-color: var(--accent-color);
    color: white;
}

.selection-hint {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-secondary);
    font-style: italic;
}

/* Filtering mode: hide non-matching sections */
.controls-sections.filter-mode .section.section-hidden {
    display: none;
}

.controls-sections.filter-mode .form-row.field-hidden {
    display: none;
}

/* Show matching sections with highlight in filter mode */
.controls-sections.filter-mode .section.section-visible {
    border-color: var(--accent-color);
}

.controls-sections.filter-mode .section.section-visible summary {
    background: rgba(37, 99, 235, 0.08);
}

[data-theme="dark"] .controls-sections.filter-mode .section.section-visible summary {
    background: rgba(59, 130, 246, 0.12);
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
}

.style-label {
    color: var(--text-secondary);
}

.style-name {
    color: var(--accent-color);
    font-weight: 600;
    font-family: monospace;
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

__all__ = ["STYLES"]
