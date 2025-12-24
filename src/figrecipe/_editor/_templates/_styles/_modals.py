#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modal and shortcuts CSS styles for the figure editor.

This module contains CSS for:
- Shortcuts button
- Shortcuts modal layout
- Keyboard key (kbd) styling
"""

STYLES_MODALS = """
/* Keyboard Shortcuts Button */
.btn-shortcuts {
    padding: 6px 10px;
    font-size: 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
}

.btn-shortcuts:hover {
    background: var(--bg-secondary);
    border-color: var(--accent-color);
}

/* Shortcuts Modal */
.shortcuts-modal-content {
    max-width: 500px;
    width: 90%;
}

.shortcuts-content {
    padding: 20px;
    max-height: 60vh;
    overflow-y: auto;
}

.shortcut-section {
    margin-bottom: 20px;
}

.shortcut-section:last-child {
    margin-bottom: 0;
}

.shortcut-section h4 {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent-color);
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-color);
}

.shortcut-row {
    display: flex;
    align-items: center;
    padding: 6px 0;
    gap: 16px;
}

.shortcut-keys {
    flex: 0 0 180px;
    text-align: left;
    white-space: nowrap;
}

.shortcut-desc {
    flex: 1;
    color: var(--text-secondary);
    font-size: 13px;
    text-align: left;
}

kbd {
    display: inline-block;
    padding: 3px 8px;
    font-size: 12px;
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    color: var(--text-primary);
    margin: 0 2px;
}

[data-theme="dark"] kbd {
    background: var(--bg-tertiary);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
"""

__all__ = ["STYLES_MODALS"]

# EOF
