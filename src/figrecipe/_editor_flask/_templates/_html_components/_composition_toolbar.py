#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML component for composition toolbar."""

HTML_COMPOSITION_TOOLBAR = """
<!-- Composition Toolbar -->
<div id="composition-toolbar" class="composition-toolbar">
    <span class="toolbar-label">Align:</span>
    <button onclick="alignPanels('left')" title="Align Left" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="2" y="2" width="2" height="12"/>
            <rect x="6" y="4" width="8" height="3"/>
            <rect x="6" y="9" width="5" height="3"/>
        </svg>
    </button>
    <button onclick="alignPanels('center_h')" title="Center Horizontal" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="7" y="2" width="2" height="12"/>
            <rect x="3" y="4" width="10" height="3"/>
            <rect x="4" y="9" width="8" height="3"/>
        </svg>
    </button>
    <button onclick="alignPanels('right')" title="Align Right" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="12" y="2" width="2" height="12"/>
            <rect x="2" y="4" width="8" height="3"/>
            <rect x="5" y="9" width="5" height="3"/>
        </svg>
    </button>
    <span class="toolbar-separator"></span>
    <button onclick="alignPanels('top')" title="Align Top" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="2" y="2" width="12" height="2"/>
            <rect x="3" y="6" width="3" height="8"/>
            <rect x="9" y="6" width="3" height="5"/>
        </svg>
    </button>
    <button onclick="alignPanels('center_v')" title="Center Vertical" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="2" y="7" width="12" height="2"/>
            <rect x="3" y="2" width="3" height="12"/>
            <rect x="9" y="4" width="3" height="8"/>
        </svg>
    </button>
    <button onclick="alignPanels('bottom')" title="Align Bottom" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="2" y="12" width="12" height="2"/>
            <rect x="3" y="2" width="3" height="8"/>
            <rect x="9" y="5" width="3" height="5"/>
        </svg>
    </button>
    <span class="toolbar-separator"></span>
    <span class="toolbar-label">Distribute:</span>
    <button onclick="distributePanels('horizontal')" title="Distribute Horizontally" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="2" y="4" width="3" height="8"/>
            <rect x="6.5" y="4" width="3" height="8"/>
            <rect x="11" y="4" width="3" height="8"/>
        </svg>
    </button>
    <button onclick="distributePanels('vertical')" title="Distribute Vertically" class="toolbar-btn">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <rect x="4" y="2" width="8" height="3"/>
            <rect x="4" y="6.5" width="8" height="3"/>
            <rect x="4" y="11" width="8" height="3"/>
        </svg>
    </button>
    <span class="toolbar-separator"></span>
    <button onclick="smartAlign()" title="Smart Align (auto-align rows and columns)" class="toolbar-btn toolbar-btn-primary">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 1l2 3H6l2-3zm0 14l-2-3h4l-2 3zM1 8l3-2v4l-3-2zm14 0l-3 2V6l3 2z"/>
            <rect x="6" y="6" width="4" height="4"/>
        </svg>
        <span>Smart</span>
    </button>
</div>
"""

__all__ = ["HTML_COMPOSITION_TOOLBAR"]
