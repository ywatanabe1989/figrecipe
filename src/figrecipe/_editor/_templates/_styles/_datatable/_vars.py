#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS styles for variable assignment with color-coded linking."""

CSS_DATATABLE_VARS = """
/* Variable assignment section - clean minimal design */
.datatable-var-assign {
    padding: 8px 12px;
    background: transparent;
    flex-shrink: 0;
}

.var-assign-header {
    display: none;  /* Hide redundant header */
}

.var-assign-slots {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

/* Color palette for variable-column linking */
.var-color-0 { --var-color: #4a9eff; }
.var-color-1 { --var-color: #ff6b6b; }
.var-color-2 { --var-color: #51cf66; }
.var-color-3 { --var-color: #ffd43b; }
.var-color-4 { --var-color: #cc5de8; }
.var-color-5 { --var-color: #ff922b; }

/* Modern compact variable slot */
.var-assign-slot {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    background: transparent;
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid var(--border-color);
    transition: all 0.15s ease;
}

.var-assign-slot:hover {
    background: var(--bg-tertiary);
}

/* Required: subtle indicator */
.var-assign-slot.required {
    border-color: var(--var-color, var(--border-color));
}

/* Optional: very subtle */
.var-assign-slot.optional {
    border-style: dashed;
    opacity: 0.6;
}

.var-assign-slot.optional:hover {
    opacity: 1;
}

/* Assigned state: colored dot indicator */
.var-assign-slot.assigned {
    background: transparent;
    border-color: var(--var-color);
}

.var-assign-slot.assigned::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--var-color);
    flex-shrink: 0;
}

.var-assign-slot .var-name {
    font-size: 10px;
    font-weight: 600;
    color: var(--text-secondary);
    min-width: 14px;
}

.var-assign-slot.assigned .var-name {
    color: var(--var-color);
}

.var-assign-slot.optional .var-name {
    font-weight: 400;
    font-size: 9px;
}

.var-assign-slot select {
    font-size: 10px;
    padding: 1px 2px;
    border: none;
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
    max-width: 90px;
}

.var-assign-slot select:focus {
    outline: none;
}
"""

__all__ = ["CSS_DATATABLE_VARS"]

# EOF
