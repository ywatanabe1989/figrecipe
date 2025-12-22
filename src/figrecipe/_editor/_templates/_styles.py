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
