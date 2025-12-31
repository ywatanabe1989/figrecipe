#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preview panel CSS styles for the figure editor.

This module contains CSS for:
- Preview panel and header
- SciTeX branding
- File switcher
- Zoom controls
- Preview wrapper and checkerboard background
"""

STYLES_PREVIEW = """
/* Preview Panel */
.preview-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border-color);
    min-width: 400px;
    max-width: none;
    width: auto;
    order: 0;  /* Default order when expanded */
    transition: flex 0.2s ease-out, min-width 0.2s ease-out, width 0.2s ease-out, order 0s;
    position: relative;
}

/* Collapsed preview panel - collapses to RIGHT side */
.preview-panel.collapsed {
    flex: 0 0 42px !important;
    min-width: 42px !important;
    max-width: 42px !important;
    width: 42px !important;
    order: 10;  /* Move to end (after data panel expands) */
}

/* When canvas collapses, data panel expands to fill space */
.editor-container:has(.preview-panel.collapsed) .datatable-panel {
    flex: 1 !important;
    max-width: none !important;
    width: auto !important;
}

.preview-panel.collapsed .preview-wrapper,
.preview-panel.collapsed .preview-controls,
.preview-panel.collapsed .scitex-branding,
.preview-panel.collapsed #server-start-time {
    display: none;
}

.preview-panel.collapsed .preview-header {
    flex-direction: column;
    justify-content: flex-start;
    padding: 12px 8px;
    height: 100%;
}

/* Flip button to point right (expand direction) when collapsed */
.preview-panel.collapsed .btn-collapse {
    transform: rotate(180deg);
}

.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 12px;
    height: var(--panel-header-height);
    min-height: var(--panel-header-height);
    background: var(--panel-header-bg);
    border-bottom: 1px solid var(--border-color);
}

/* Preview header collapse button */
.preview-header .btn-collapse {
    width: 28px;
    height: 28px;
    padding: 0;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
    flex-shrink: 0;
    margin-right: 8px;
}

.preview-header .btn-collapse:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.preview-header h2 {
    font-size: 16px;
    font-weight: 600;
}

/* Panel label for CANVAS */
.preview-header .panel-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
    margin-right: auto;
}

.preview-panel.collapsed .panel-label {
    display: none;
}

/* SciTeX branding */
.scitex-branding {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-primary);
    transition: opacity 0.2s;
}

.scitex-branding:hover {
    opacity: 0.8;
}

.scitex-icon {
    width: 28px;
    height: 28px;
    border-radius: 4px;
}

.figrecipe-title {
    font-size: 16px;
    font-weight: 600;
}

/* File Switcher */
.file-switcher {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: 16px;
}

.file-selector {
    padding: 6px 10px;
    font-size: 13px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-width: 180px;
    max-width: 280px;
    cursor: pointer;
}

.file-selector:hover {
    border-color: var(--accent-color);
}

.file-selector:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 2px var(--selection-color);
}

.file-selector option {
    padding: 4px 8px;
}

.file-selector option[data-current="true"] {
    font-weight: bold;
}

.btn-new {
    width: 28px;
    height: 28px;
    padding: 0;
    font-size: 18px;
    font-weight: bold;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.btn-new:hover {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.preview-controls {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.zoom-controls {
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 2px 6px;
}

.zoom-controls button {
    width: 28px;
    height: 28px;
    padding: 0;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Text buttons in zoom controls need smaller font */
.zoom-controls #btn-zoom-fit {
    width: auto;
    padding: 0 8px;
    font-size: 12px;
}

/* Zoom dropdown select */
.zoom-controls select {
    height: 28px;
    padding: 0 8px;
    font-size: 12px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
}

.zoom-controls select:hover {
    border-color: var(--accent-color);
}

/* Toolbar separator */
.toolbar-separator {
    width: 1px;
    height: 24px;
    background: var(--border-color);
    margin: 0 4px;
}

.preview-wrapper {
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
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

/* Dark checkerboard in dark mode */
[data-theme="dark"] .preview-wrapper {
    background-color: #2a2a2a;
    background-image:
        linear-gradient(45deg, #333333 25%, transparent 25%),
        linear-gradient(-45deg, #333333 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #333333 75%),
        linear-gradient(-45deg, transparent 75%, #333333 75%);
}

#preview-image {
    max-width: none;
    max-height: none;
    object-fit: contain;
    cursor: crosshair;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    position: relative;
    z-index: 1;
    transform-origin: center center;
    transition: transform 0.1s ease-out;
}

/* Zoom container for coordinated transform of image and overlays */
.zoom-container {
    display: inline-block;
    position: relative;
    transform-origin: top left;
    transition: transform 0.1s ease-out;
}

/* Show grab cursor hint when zoomed in */
.preview-wrapper.zoomed-in {
    cursor: grab;
    /* Disable centering when zoomed to allow proper scrolling from top-left */
    align-items: flex-start;
    justify-content: flex-start;
}

/* Pan cursor when dragging */
.preview-wrapper.panning {
    cursor: grabbing !important;
}

.preview-wrapper.panning * {
    cursor: grabbing !important;
}

/* Welcome Overlay - covers the entire preview area */
.welcome-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    pointer-events: none;
    background: var(--bg-tertiary);
}

.welcome-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 32px 40px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    max-width: 360px;
}

.welcome-content h2 {
    margin: 0 0 24px 0;
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
}

.welcome-steps {
    display: flex;
    flex-direction: column;
    gap: 16px;
    text-align: left;
}

.welcome-step {
    display: flex;
    align-items: center;
    gap: 12px;
}

.step-number {
    width: 28px;
    height: 28px;
    background: var(--accent-color);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    flex-shrink: 0;
}

.step-text {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.4;
}

.step-text strong {
    color: var(--text-primary);
}

.welcome-hint {
    margin: 20px 0 0 0;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
    color: var(--text-tertiary);
    font-size: 13px;
}

/* Caption Pane (below canvas) */
.caption-pane {
    padding: 10px 20px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    font-size: 13px;
    line-height: 1.5;
    color: var(--text-primary);
    min-height: 32px;
}

.caption-pane b {
    font-weight: 600;
}

.caption-pane .panel-caption {
    color: var(--text-secondary);
}

/* Hide caption pane when canvas collapsed */
.preview-panel.collapsed .caption-pane {
    display: none;
}
"""

__all__ = ["STYLES_PREVIEW"]

# EOF
