#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for datatable panel layout."""

CSS_DATATABLE_PANEL = """
/* Datatable panel - always visible, collapsible */
.datatable-panel {
    width: 280px;
    min-width: 200px;
    max-width: 450px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: width 0.2s ease-out, min-width 0.2s ease-out;
    position: relative;
}

/* Collapsed state */
.datatable-panel.collapsed {
    width: 36px;
    min-width: 36px;
}

.datatable-panel.collapsed .datatable-tabs,
.datatable-panel.collapsed .datatable-tab-content,
.datatable-panel.collapsed .datatable-resize {
    display: none;
}

.datatable-panel.collapsed .datatable-header {
    padding: 10px 6px;
    justify-content: center;
}

.datatable-panel.collapsed .datatable-header .header-title {
    display: none;
}

.datatable-panel.collapsed .datatable-header h3,
.datatable-panel.collapsed .datatable-header span {
    display: none;
}

.datatable-panel.collapsed .datatable-header-actions {
    display: flex;
}

.datatable-panel.collapsed .datatable-header-actions button:not(.btn-collapse) {
    display: none;
}

/* Flip collapse button when collapsed (now points right to expand) */
.datatable-panel.collapsed .btn-collapse {
    transform: rotate(180deg);
}

/* Resize handle */
.datatable-resize {
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

.datatable-resize:hover,
.datatable-resize.resizing {
    background: var(--accent-color);
}

/* Datatable header */
.datatable-header {
    padding: 0 10px;
    height: var(--panel-header-height);
    min-height: var(--panel-header-height);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    background: var(--panel-header-bg);
}

.datatable-header .header-title {
    display: flex;
    align-items: center;
    gap: 6px;
}

.datatable-header h3,
.datatable-header span {
    font-size: 11px;
    font-weight: 600;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
}

.datatable-header-actions {
    display: flex;
    gap: 4px;
    align-items: center;
}

.datatable-header-actions button {
    padding: 4px 8px;
    font-size: 11px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 3px;
    cursor: pointer;
    color: var(--text-primary);
}

.datatable-header-actions button:hover {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.datatable-header-actions .btn-collapse {
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

.datatable-header-actions .btn-collapse:hover {
    background: var(--bg-primary);
    color: var(--text-primary);
}

.btn-close-datatable {
    background: transparent !important;
    border: none !important;
    font-size: 16px !important;
    padding: 2px 6px !important;
    color: var(--text-secondary) !important;
}

.btn-close-datatable:hover {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

/* Tab bar for multiple datatables */
.datatable-tabs {
    display: flex;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    flex-shrink: 0;
    overflow-x: auto;
    scrollbar-width: thin;
}

.datatable-tab-list {
    display: flex;
    flex: 1;
    overflow-x: auto;
    gap: 0;
}

.datatable-tab {
    padding: 8px 14px;
    font-size: 12px;
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    cursor: pointer;
    color: var(--text-secondary);
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
}

.datatable-tab:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.datatable-tab.active {
    background: var(--bg-secondary);
    color: var(--element-color, var(--accent-color));
    border-left-color: var(--element-color, var(--accent-color));
}

.datatable-tab .tab-name {
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datatable-tab .tab-close {
    font-size: 14px;
    line-height: 1;
    opacity: 0.5;
    padding: 0 2px;
}

.datatable-tab .tab-close:hover {
    opacity: 1;
    color: #ff6b6b;
}

.datatable-tab .tab-axis {
    font-size: 9px;
    background: var(--element-color, var(--accent-color));
    color: white;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 600;
}

.btn-new-tab {
    padding: 6px 10px;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
    border: none;
    cursor: pointer;
    color: var(--text-secondary);
    flex-shrink: 0;
}

.btn-new-tab:hover {
    background: var(--bg-secondary);
    color: var(--accent-color);
}

.datatable-tab-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;  /* Allow flex shrinking */
}

/* Responsive adjustments */
@media (max-width: 1200px) {
    .datatable-panel.expanded {
        width: 280px;
        min-width: 280px;
    }
}
"""

__all__ = ["CSS_DATATABLE_PANEL"]

# EOF
