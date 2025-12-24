#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dynamic call properties CSS styles for the figure editor.

This module contains CSS for:
- Dynamic call properties panel
- Property sections and fields
- Type hints and argument display
"""

STYLES_DYNAMIC_PROPS = """
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
"""

__all__ = ["STYLES_DYNAMIC_PROPS"]

# EOF
