#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File browser panel CSS styles for the figure editor.

This module contains CSS for:
- File browser panel and header
- File tree structure
- File items and icons
- Collapse/expand functionality
"""

STYLES_FILE_BROWSER = """
/* File Browser Panel */
.file-browser-panel {
    width: 200px;
    min-width: 160px;
    max-width: 280px;
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    transition: width 0.2s ease-out;
    position: relative;
}

.file-browser-panel.collapsed {
    width: 36px;
    min-width: 36px;
}

.file-browser-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    height: var(--panel-header-height);
    min-height: var(--panel-header-height);
    background: var(--panel-header-bg);
    border-bottom: 1px solid var(--border-color);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
}

.file-browser-header .header-title {
    display: flex;
    align-items: center;
    gap: 6px;
}

.file-browser-header .btn-collapse {
    width: 24px;
    height: 24px;
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
}

.file-browser-header .btn-collapse:hover {
    background: var(--bg-primary);
    color: var(--text-primary);
}

.file-browser-panel.collapsed .file-browser-header {
    padding: 10px 6px;
    justify-content: center;
}

.file-browser-panel.collapsed .header-title {
    justify-content: center;
}

.file-browser-panel.collapsed .header-title span {
    display: none;
}

.file-browser-actions {
    display: flex;
    gap: 4px;
}

.file-browser-panel.collapsed .file-browser-actions {
    display: flex;
}

.file-browser-panel.collapsed .file-browser-actions button:not(.btn-collapse) {
    display: none;
}

/* Flip collapse button when collapsed (now points right to expand) */
.file-browser-panel.collapsed .btn-collapse {
    display: flex;
    transform: rotate(180deg);
}

.file-browser-actions button {
    width: 24px;
    height: 24px;
    padding: 0;
    font-size: 14px;
    border: none;
    border-radius: 4px;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.file-browser-actions button:hover {
    background: var(--bg-primary);
    color: var(--accent-color);
}

.file-browser-actions button.btn-new-file:hover {
    color: var(--success-color);
}

/* File Tree Container */
.file-tree-container {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 8px 0;
}

.file-browser-panel.collapsed .file-tree-container {
    display: none;
}

/* File Tree */
.file-tree {
    list-style: none;
    margin: 0;
    padding: 0;
}

.file-tree-item {
    margin: 0;
    padding: 0;
}

.file-tree-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    cursor: pointer;
    color: var(--text-primary);
    font-size: 12px;
    border-left: 3px solid transparent;
    transition: all 0.12s ease-out;
    user-select: none;
}

.file-tree-entry:hover {
    background: var(--bg-tertiary);
    border-left-color: var(--border-color);
}

.file-tree-entry.selected {
    background: var(--selection-color);
    border-left-color: var(--accent-color);
}

.file-tree-entry.current {
    background: var(--selection-color);
    border-left-color: var(--accent-color);
    font-weight: 600;
}

.file-tree-entry.current .file-tree-name {
    color: var(--accent-color);
}

.file-tree-icon {
    width: 16px;
    height: 16px;
    font-size: 14px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.file-tree-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-tree-badge {
    font-size: 9px;
    padding: 2px 5px;
    border-radius: 3px;
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    flex-shrink: 0;
    font-weight: 500;
    letter-spacing: 0.3px;
}

.file-tree-entry.has-image .file-tree-badge {
    background: var(--success-color);
    color: white;
    opacity: 0.9;
}

/* File action buttons (rename, delete) */
.file-tree-actions {
    display: none;
    gap: 2px;
    margin-left: auto;
    flex-shrink: 0;
}

.file-tree-entry:hover .file-tree-actions {
    display: flex;
}

.file-action-btn {
    width: 20px;
    height: 20px;
    padding: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 11px;
    border-radius: 3px;
    opacity: 0.6;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.file-action-btn:hover {
    opacity: 1;
    background: var(--bg-primary);
}

.file-action-btn.btn-delete:hover {
    background: rgba(239, 68, 68, 0.2);
}

.file-action-btn.btn-rename:hover {
    background: rgba(59, 130, 246, 0.2);
}

/* Folder items */
.file-tree-folder > .file-tree-entry {
    font-weight: 500;
    cursor: pointer;
}

.file-tree-folder > .file-tree-entry:hover {
    background: var(--bg-tertiary);
}

/* Folder chevron indicator */
.file-tree-folder > .file-tree-entry .file-tree-icon {
    position: relative;
}

.file-tree-folder > .file-tree-entry .file-tree-icon::before {
    content: "";
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 5px solid var(--text-secondary);
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    position: absolute;
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
    transition: transform 0.15s ease;
}

.file-tree-folder.expanded > .file-tree-entry .file-tree-icon::before {
    transform: translateY(-50%) rotate(90deg);
}

/* Folder badge (item count) */
.file-tree-badge.folder-badge {
    background: var(--bg-primary);
    color: var(--text-secondary);
    font-size: 9px;
    min-width: 16px;
    text-align: center;
}

/* File tree children container */
.file-tree-children {
    list-style: none;
    margin: 0;
    padding: 0;
    display: none;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
}

.file-tree-folder.expanded > .file-tree-children {
    display: block;
}

/* Tree indentation guide lines */
.file-tree-folder > .file-tree-children {
    position: relative;
}

.file-tree-folder > .file-tree-children::before {
    content: "";
    position: absolute;
    left: 18px;
    top: 0;
    bottom: 8px;
    width: 1px;
    background: var(--border-color);
    opacity: 0.5;
}

/* Empty state */
.file-tree-empty {
    padding: 24px 16px;
    text-align: center;
    color: var(--text-secondary);
    font-size: 11px;
    line-height: 1.5;
}

.file-tree-empty p {
    margin: 6px 0;
}

.file-tree-empty p:first-child {
    font-size: 12px;
    color: var(--text-primary);
    opacity: 0.7;
}

/* Scrollbar styling */
.file-tree-container::-webkit-scrollbar {
    width: 6px;
}

.file-tree-container::-webkit-scrollbar-track {
    background: transparent;
}

.file-tree-container::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

.file-tree-container::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Resize handle */
.file-browser-resize {
    width: 4px;
    cursor: col-resize;
    background: transparent;
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 10;
    transition: background 0.2s;
}

.file-browser-resize:hover,
.file-browser-resize.resizing {
    background: var(--accent-color);
}

/* File Browser Footer - Brand Info */
.file-browser-footer {
    padding: 10px 12px;
    border-top: 1px solid var(--border-color);
    background: var(--bg-secondary);
}

.brand-link {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text-secondary);
    transition: all 0.15s;
    padding: 4px;
    border-radius: 4px;
    margin: -4px;
}

.brand-link:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.brand-icon {
    width: 28px;
    height: 28px;
    flex-shrink: 0;
    opacity: 0.8;
}

.brand-link:hover .brand-icon {
    opacity: 1;
}

.brand-info {
    display: flex;
    flex-direction: column;
    gap: 1px;
    overflow: hidden;
}

.brand-name {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
}

.brand-version {
    font-size: 9px;
    color: var(--text-secondary);
    white-space: nowrap;
}

.brand-meta {
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--border-color);
}

.server-time {
    font-size: 9px;
    color: var(--text-tertiary);
    font-family: monospace;
}

/* Hide footer when collapsed */
.file-browser-panel.collapsed .file-browser-footer {
    display: none;
}
"""

__all__ = ["STYLES_FILE_BROWSER"]

# EOF
