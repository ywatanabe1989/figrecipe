#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for composition toolbar."""

STYLES_COMPOSITION = """
/* Composition Toolbar */
.composition-toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    flex-wrap: wrap;
}

.composition-toolbar .toolbar-label {
    font-size: 11px;
    color: var(--text-secondary);
    margin-right: 4px;
}

.composition-toolbar .toolbar-separator {
    width: 1px;
    height: 20px;
    background: var(--border-color);
    margin: 0 6px;
}

.composition-toolbar .toolbar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 4px 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.15s ease;
    min-width: 28px;
    height: 28px;
}

.composition-toolbar .toolbar-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent-color);
}

.composition-toolbar .toolbar-btn:active {
    transform: scale(0.95);
}

.composition-toolbar .toolbar-btn svg {
    width: 16px;
    height: 16px;
}

.composition-toolbar .toolbar-btn-primary {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
    padding: 4px 10px;
}

.composition-toolbar .toolbar-btn-primary:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
}

.composition-toolbar .toolbar-btn span {
    font-size: 11px;
    font-weight: 500;
}

/* Dark mode adjustments */
[data-theme="dark"] .composition-toolbar {
    background: var(--bg-secondary);
}

[data-theme="dark"] .composition-toolbar .toolbar-btn {
    background: var(--bg-tertiary);
}
"""

__all__ = ["STYLES_COMPOSITION"]
