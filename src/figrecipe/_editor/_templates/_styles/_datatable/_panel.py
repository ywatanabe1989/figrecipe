#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for datatable panel layout."""

CSS_DATATABLE_PANEL = """
/* Datatable panel - collapsible left panel */
.datatable-panel {
    width: 0;
    min-width: 0;
    max-width: 400px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: width 0.2s ease, min-width 0.2s ease;
}

.datatable-panel.expanded {
    width: 320px;
    min-width: 320px;
}

.datatable-toggle {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-left: none;
    border-radius: 0 4px 4px 0;
    padding: 8px 4px;
    cursor: pointer;
    color: var(--text-secondary);
    font-size: 12px;
    writing-mode: vertical-rl;
    text-orientation: mixed;
}

.datatable-toggle:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.datatable-panel.expanded + .preview-panel .datatable-toggle {
    display: none;
}

/* Datatable header */
.datatable-header {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
}

.datatable-header h3 {
    font-size: 13px;
    font-weight: 600;
    margin: 0;
}

.datatable-header-actions {
    display: flex;
    gap: 4px;
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
    padding: 6px 12px;
    font-size: 11px;
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
