#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Element inspector CSS styles for the figure editor.

This module contains CSS for:
- Element inspector overlay
- Inspector box hover states
- Inspector labels and notifications
"""

STYLES_INSPECTOR = """
/* ==================== ELEMENT INSPECTOR ==================== */
.element-inspector-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 999999;
}

.element-inspector-box {
    position: absolute;
    border: 2px solid;
    box-sizing: border-box;
    pointer-events: auto;
    cursor: pointer;
    transition: all 0.15s;
    background: rgba(255, 255, 255, 0.01);
}

.element-inspector-box:hover {
    border-width: 3px;
    background: rgba(59, 130, 246, 0.15);
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.6), 0 0 12px rgba(59, 130, 246, 0.4);
}

.element-inspector-label {
    position: absolute;
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 2px 6px;
    font-size: 10px;
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    border-radius: 3px;
    white-space: nowrap;
    pointer-events: auto;
    cursor: pointer;
    z-index: 1000000;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
    line-height: 1.4;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
}

.element-inspector-label:hover {
    background: rgba(40, 40, 40, 0.95);
    transform: scale(1.05);
}

.element-inspector-label .tag { color: #CE9178; }
.element-inspector-label .id { color: #4EC9B0; font-weight: bold; }
.element-inspector-label .class { color: #9CDCFE; }

.element-inspector-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 10000000;
    animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
    from { transform: translateX(100px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
"""

__all__ = ["STYLES_INSPECTOR"]

# EOF
