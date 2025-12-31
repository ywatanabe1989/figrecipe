#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tri-directional synchronization between Data/Canvas/Properties panes.

This module coordinates selection state across:
- Data pane (datatable tabs)
- Canvas pane (figure preview with hit regions)
- Properties pane (Figure/Axis/Element tabs)

Sync directions:
- Canvas → Data: Selecting element highlights datatable tab
- Canvas → Properties: Selecting element switches to appropriate tab
- Data → Canvas: Clicking datatable tab selects element on canvas
- Data → Properties: Clicking datatable tab switches to Element tab
- Properties → Canvas: Clicking tab filters/selects canvas elements
- Properties → Data: Clicking tab highlights relevant data
"""

SCRIPTS_SYNC = """
// ============================================================================
// Tri-directional Pane Synchronization
// ============================================================================

// Sync state flags to prevent infinite loops
let _syncingFromCanvas = false;
let _syncingFromData = false;
let _syncingFromProperties = false;

// ============================================================================
// Initialize Sync Hooks
// ============================================================================
function initPaneSync() {
    console.log('[PaneSync] Initializing tri-directional synchronization');

    // Hook datatable tab selection
    hookDatatableTabSync();

    // Hook properties tab clicks
    hookPropertiesTabSync();

    // Canvas selection is already hooked via hookCanvasSelection() in datatable core
}

// ============================================================================
// Data Pane -> Canvas/Properties Sync
// ============================================================================
function hookDatatableTabSync() {
    // Wrap selectTab to add canvas/properties sync
    if (typeof window.selectTab === 'function') {
        const originalSelectTab = window.selectTab;
        window.selectTab = function(tabId) {
            originalSelectTab(tabId);

            // Avoid infinite loops
            if (_syncingFromCanvas || _syncingFromProperties) return;
            _syncingFromData = true;

            try {
                syncCanvasFromDatatableTab(tabId);
                syncPropertiesFromDatatableTab(tabId);
            } finally {
                _syncingFromData = false;
            }
        };
        console.log('[PaneSync] Datatable tab sync hooked');
    }
}

function syncCanvasFromDatatableTab(tabId) {
    if (!tabId || typeof datatableTabs === 'undefined') return;
    const tabState = datatableTabs[tabId];
    if (!tabState || !tabState.callId) return;

    // Find the element on canvas matching this callId
    const callId = tabState.callId;

    // Search currentBboxes for matching element
    if (typeof currentBboxes !== 'undefined' && currentBboxes) {
        for (const [key, bbox] of Object.entries(currentBboxes)) {
            if (key === '_meta') continue;
            // Match by call_id or key containing the callId
            if (bbox.call_id === callId || key.includes(callId) || bbox.label === callId) {
                // Select this element on canvas
                if (typeof selectElement === 'function') {
                    const element = { key, ...bbox };
                    selectElement(element);
                    console.log('[PaneSync] Data->Canvas: Selected', key, 'for callId', callId);
                }
                return;
            }
        }
    }

    // If no direct match, try selecting the panel associated with this tab
    if (tabState.targetAxis !== null && tabState.targetAxis !== undefined) {
        const axKey = `ax${tabState.targetAxis}_axes`;
        if (typeof currentBboxes !== 'undefined' && currentBboxes[axKey]) {
            const bbox = currentBboxes[axKey];
            if (typeof selectElement === 'function') {
                selectElement({ key: axKey, ...bbox, type: 'axes', ax_index: tabState.targetAxis });
                console.log('[PaneSync] Data->Canvas: Selected panel', tabState.targetAxis);
            }
        }
    }
}

function syncPropertiesFromDatatableTab(tabId) {
    if (!tabId || typeof datatableTabs === 'undefined') return;
    const tabState = datatableTabs[tabId];
    if (!tabState) return;

    // Data tabs represent plot elements, so switch to Element tab
    if (typeof switchTab === 'function') {
        switchTab('element');
        console.log('[PaneSync] Data->Properties: Switched to Element tab');
    }
}

// ============================================================================
// Properties Pane -> Canvas/Data Sync
// ============================================================================
function hookPropertiesTabSync() {
    // Add click listeners to Figure/Axis/Element tab buttons
    document.addEventListener('DOMContentLoaded', () => {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Avoid infinite loops
                if (_syncingFromCanvas || _syncingFromData) return;
                _syncingFromProperties = true;

                try {
                    const tabName = btn.id.replace('tab-', '');
                    syncCanvasFromPropertiesTab(tabName);
                    syncDataFromPropertiesTab(tabName);
                } finally {
                    _syncingFromProperties = false;
                }
            });
        });
        console.log('[PaneSync] Properties tab sync hooked');
    });
}

function syncCanvasFromPropertiesTab(tabName) {
    // When switching to a properties tab, optionally clear or filter canvas selection
    // For now, we'll just log - actual behavior depends on UX requirements
    console.log('[PaneSync] Properties->Canvas: Tab', tabName, 'clicked');

    // If Figure tab, clear element selection (show figure-level props)
    if (tabName === 'figure' && typeof clearSelection === 'function') {
        // Don't auto-clear as it might be disruptive
        // clearSelection();
    }
}

function syncDataFromPropertiesTab(tabName) {
    // When switching to Element tab, try to highlight the currently selected element's data
    if (tabName === 'element' && typeof selectedElement !== 'undefined' && selectedElement) {
        if (typeof syncDatatableToElement === 'function') {
            syncDatatableToElement(selectedElement);
        }
    }
    console.log('[PaneSync] Properties->Data: Tab', tabName, 'clicked');
}

// ============================================================================
// Enhanced Canvas -> Data/Properties Sync (augments existing hooks)
// ============================================================================
function enhanceCanvasSync() {
    // Wrap selectElement to add enhanced sync
    if (typeof window.selectElement === 'function') {
        const originalSelectElement = window.selectElement;
        window.selectElement = function(element) {
            // Avoid infinite loops
            if (_syncingFromData || _syncingFromProperties) {
                originalSelectElement(element);
                return;
            }
            _syncingFromCanvas = true;

            try {
                originalSelectElement(element);

                // Auto-switch Properties tab based on element type
                if (element && typeof autoSwitchTab === 'function') {
                    autoSwitchTab(element.type);
                }

                // Sync datatable to element (already done in hookCanvasSelection, but ensure it happens)
                if (element && typeof syncDatatableToElement === 'function') {
                    syncDatatableToElement(element);
                }
            } finally {
                _syncingFromCanvas = false;
            }
        };
        console.log('[PaneSync] Canvas selection sync enhanced');
    }
}

// Initialize sync on page load
document.addEventListener('DOMContentLoaded', () => {
    // Delay to ensure other modules are loaded
    setTimeout(() => {
        initPaneSync();
        enhanceCanvasSync();
    }, 100);
});
"""

__all__ = ["SCRIPTS_SYNC"]

# EOF
