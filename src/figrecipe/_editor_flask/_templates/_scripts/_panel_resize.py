#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel resize JavaScript for the figure editor.

This module handles resizing of panels by dragging dividers:
- File browser panel (left)
- Data panel (left)
- Properties panel (right)

Features smart accordion:
- Auto-collapse when dragged below threshold
- Auto-expand when dragging from collapsed state
"""

SCRIPTS_PANEL_RESIZE = """
// ==================== PANEL RESIZE ====================
// Enables dragging panel dividers to resize panels with smart accordion

// Store default widths for each panel
const panelDefaultWidths = {
    'file-browser-panel': 200,
    'datatable-panel': 280,
    'controls-panel': 350
};

// Collapse threshold - panels collapse when dragged below this width
const COLLAPSE_THRESHOLD = 60;

// Expand threshold - collapsed panels expand when dragged beyond this
const EXPAND_THRESHOLD = 50;

function initPanelResize() {
    // File browser resize handle
    const fileBrowserResize = document.getElementById('file-browser-resize');
    const fileBrowserPanel = document.getElementById('file-browser-panel');

    // Datatable resize handle
    const datatableResize = document.getElementById('datatable-resize');
    const datatablePanel = document.getElementById('datatable-panel');

    // Properties panel resize handle (will be added to controls-panel)
    const controlsPanel = document.querySelector('.controls-panel');

    if (fileBrowserResize && fileBrowserPanel) {
        initSmartResizer(fileBrowserResize, fileBrowserPanel, 'left', 'file-browser-panel');
    }

    if (datatableResize && datatablePanel) {
        initSmartResizer(datatableResize, datatablePanel, 'left', 'datatable-panel');
    }

    // Add resize handle for properties panel
    if (controlsPanel) {
        let propertiesResize = document.getElementById('properties-resize');
        if (!propertiesResize) {
            propertiesResize = document.createElement('div');
            propertiesResize.id = 'properties-resize';
            propertiesResize.className = 'properties-resize';
            controlsPanel.insertBefore(propertiesResize, controlsPanel.firstChild);
        }
        initSmartResizer(propertiesResize, controlsPanel, 'right', 'controls-panel');
    }

    console.log('[PanelResize] Initialized with smart accordion');
}

function initSmartResizer(resizeHandle, panel, side, panelId) {
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    let wasCollapsed = false;

    // Handle click on resize handle when panel is collapsed - expand it
    resizeHandle.addEventListener('click', (e) => {
        if (panel.classList.contains('collapsed')) {
            e.stopPropagation();
            expandPanel(panel, panelId);
        }
    });

    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        wasCollapsed = panel.classList.contains('collapsed');

        // If collapsed, start with minimal width
        if (wasCollapsed) {
            startWidth = panel.offsetWidth;
        } else {
            startWidth = panel.offsetWidth;
            // Save current width as default if it's reasonable
            if (startWidth > COLLAPSE_THRESHOLD) {
                panelDefaultWidths[panelId] = startWidth;
            }
        }

        resizeHandle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const deltaX = e.clientX - startX;
        let newWidth;

        if (side === 'left') {
            // For left panel, positive delta increases width
            newWidth = startWidth + deltaX;
        } else {
            // For right panel, negative delta increases width
            newWidth = startWidth - deltaX;
        }

        // Smart accordion behavior
        if (wasCollapsed) {
            // Expanding from collapsed state
            if (Math.abs(deltaX) > EXPAND_THRESHOLD) {
                // Expand to default width
                expandPanel(panel, panelId);
                // Continue resizing from expanded state
                startX = e.clientX;
                startWidth = panelDefaultWidths[panelId];
                wasCollapsed = false;
            }
        } else {
            // Normal resize - check for collapse threshold
            if (newWidth < COLLAPSE_THRESHOLD) {
                // Collapse the panel
                collapsePanel(panel, panelId);
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
                return;
            }

            // Clamp to min/max (but above collapse threshold)
            const minWidth = Math.max(COLLAPSE_THRESHOLD, parseInt(getComputedStyle(panel).minWidth) || 160);
            const maxWidth = parseInt(getComputedStyle(panel).maxWidth) || 500;
            newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

            panel.style.width = newWidth + 'px';
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            resizeHandle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';

            // Save width if not collapsed
            if (!panel.classList.contains('collapsed')) {
                const currentWidth = panel.offsetWidth;
                if (currentWidth > COLLAPSE_THRESHOLD) {
                    panelDefaultWidths[panelId] = currentWidth;
                    localStorage.setItem(`figrecipe_${panelId}_width`, currentWidth);
                }
            }
        }
    });

    // Also handle mouse leaving window
    document.addEventListener('mouseleave', () => {
        if (isResizing) {
            isResizing = false;
            resizeHandle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

function collapsePanel(panel, panelId) {
    panel.classList.add('collapsed');

    // Update localStorage
    const storageKey = getStorageKey(panelId);
    if (storageKey) {
        localStorage.setItem(storageKey, 'true');
    }

    // Dispatch custom event for accordion sync
    panel.dispatchEvent(new CustomEvent('panelCollapsed', { bubbles: true }));
    console.log(`[PanelResize] ${panelId} collapsed via drag`);
}

function expandPanel(panel, panelId) {
    panel.classList.remove('collapsed');

    // Restore saved width or default
    const savedWidth = localStorage.getItem(`figrecipe_${panelId}_width`);
    const width = savedWidth ? parseInt(savedWidth) : panelDefaultWidths[panelId];
    panel.style.width = width + 'px';

    // Update localStorage
    const storageKey = getStorageKey(panelId);
    if (storageKey) {
        localStorage.setItem(storageKey, 'false');
    }

    // Dispatch custom event for accordion sync
    panel.dispatchEvent(new CustomEvent('panelExpanded', { bubbles: true }));
    console.log(`[PanelResize] ${panelId} expanded via drag to ${width}px`);
}

function getStorageKey(panelId) {
    const keyMap = {
        'file-browser-panel': 'figrecipe_filebrowser_collapsed',
        'datatable-panel': 'figrecipe_data_collapsed',
        'controls-panel': 'figrecipe_properties_collapsed'
    };
    return keyMap[panelId];
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanelResize);
} else {
    initPanelResize();
}
"""

__all__ = ["SCRIPTS_PANEL_RESIZE"]

# EOF
