#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel accordion JavaScript for the figure editor.

This module handles collapsing/expanding of panels:
- File browser panel (left)
- Data panel (second from left)
- Properties panel (right)
- State persistence in localStorage
"""

SCRIPTS_ACCORDION = """
// ==================== PANEL ACCORDION ====================
// Enables collapsing/expanding panels with state persistence

let propertiesPanelCollapsed = false;
let dataPanelCollapsed = false;
let previewPanelCollapsed = false;
// Note: fileBrowserCollapsed is declared in _files.py

// Smart expansion: when a panel collapses, expand collapsed neighbors to fill space
function checkSmartExpansion(collapsedPanelId) {
    // Panel order: Files | Data | Canvas | Properties
    // When one collapses, adjacent collapsed panels should expand

    const filePanel = document.getElementById('file-browser-panel');
    const dataPanel = document.getElementById('datatable-panel');
    const previewPanel = document.getElementById('preview-panel');
    const propsPanel = document.getElementById('controls-panel');

    const isFileCollapsed = filePanel?.classList.contains('collapsed');
    const isDataCollapsed = dataPanel?.classList.contains('collapsed');
    const isPreviewCollapsed = previewPanel?.classList.contains('collapsed');
    const isPropsCollapsed = propsPanel?.classList.contains('collapsed');

    console.log('[SmartExpansion] Checking after', collapsedPanelId, 'collapsed');
    console.log('[SmartExpansion] States - Files:', isFileCollapsed, 'Data:', isDataCollapsed,
                'Preview:', isPreviewCollapsed, 'Props:', isPropsCollapsed);

    // When Canvas collapses -> expand Data if collapsed
    if (collapsedPanelId === 'preview-panel' && isDataCollapsed) {
        console.log('[SmartExpansion] Canvas collapsed, expanding Data panel');
        expandDataPanel();
    }

    // When Data collapses -> expand Canvas if collapsed (prioritize canvas for viewing)
    if (collapsedPanelId === 'datatable-panel' && isPreviewCollapsed) {
        console.log('[SmartExpansion] Data collapsed, expanding Canvas panel');
        expandPreviewPanel();
    }

    // When Properties collapses -> expand Canvas if collapsed
    if (collapsedPanelId === 'controls-panel' && isPreviewCollapsed) {
        console.log('[SmartExpansion] Properties collapsed, expanding Canvas panel');
        expandPreviewPanel();
    }

    // When Files collapses -> expand Data if collapsed
    if (collapsedPanelId === 'file-browser-panel' && isDataCollapsed) {
        console.log('[SmartExpansion] Files collapsed, expanding Data panel');
        expandDataPanel();
    }
}

// Helper functions to expand without toggling
function expandDataPanel() {
    const panel = document.getElementById('datatable-panel');
    const collapseBtn = document.getElementById('btn-collapse-datatable');
    if (!panel || !panel.classList.contains('collapsed')) return;

    dataPanelCollapsed = false;
    panel.classList.remove('collapsed');
    if (collapseBtn) collapseBtn.title = 'Collapse panel';
    localStorage.setItem('figrecipe_data_collapsed', 'false');
    console.log('[PanelAccordion] Data panel auto-expanded');
}

function expandPreviewPanel() {
    const panel = document.getElementById('preview-panel');
    const collapseBtn = document.getElementById('btn-collapse-preview');
    if (!panel || !panel.classList.contains('collapsed')) return;

    previewPanelCollapsed = false;
    panel.classList.remove('collapsed');
    if (collapseBtn) collapseBtn.title = 'Collapse canvas';
    localStorage.setItem('figrecipe_preview_collapsed', 'false');
    console.log('[PanelAccordion] Preview panel auto-expanded');
}

function expandPropertiesPanel() {
    const panel = document.getElementById('controls-panel');
    const collapseBtn = document.getElementById('btn-collapse-properties');
    if (!panel || !panel.classList.contains('collapsed')) return;

    propertiesPanelCollapsed = false;
    panel.classList.remove('collapsed');
    if (collapseBtn) collapseBtn.title = 'Collapse panel';
    localStorage.setItem('figrecipe_properties_collapsed', 'false');
    console.log('[PanelAccordion] Properties panel auto-expanded');
}

function expandFileBrowserPanel() {
    const panel = document.getElementById('file-browser-panel');
    const collapseBtn = document.getElementById('btn-collapse-browser');
    if (!panel || !panel.classList.contains('collapsed')) return;

    // fileBrowserCollapsed is defined in _files.py
    if (typeof fileBrowserCollapsed !== 'undefined') fileBrowserCollapsed = false;
    panel.classList.remove('collapsed');
    if (collapseBtn) {
        collapseBtn.innerHTML = '&#x276E;';
        collapseBtn.title = 'Collapse panel';
    }
    localStorage.setItem('figrecipe_filebrowser_collapsed', 'false');
    console.log('[PanelAccordion] File browser auto-expanded');
}

function initPanelAccordion() {
    // Properties panel collapse button
    const propertiesCollapseBtn = document.getElementById('btn-collapse-properties');
    const propertiesPanel = document.getElementById('controls-panel');

    if (propertiesCollapseBtn && propertiesPanel) {
        propertiesCollapseBtn.addEventListener('click', togglePropertiesPanel);

        // Restore collapsed state from localStorage
        const wasCollapsed = localStorage.getItem('figrecipe_properties_collapsed');
        if (wasCollapsed === 'true') {
            propertiesPanelCollapsed = true;
            propertiesPanel.classList.add('collapsed');
            propertiesCollapseBtn.title = 'Expand panel';
        }
    }

    // Data panel collapse button
    const dataCollapseBtn = document.getElementById('btn-collapse-datatable');
    const dataPanel = document.getElementById('datatable-panel');

    if (dataCollapseBtn && dataPanel) {
        dataCollapseBtn.addEventListener('click', toggleDataPanel);

        // Restore collapsed state from localStorage
        const wasDataCollapsed = localStorage.getItem('figrecipe_data_collapsed');
        if (wasDataCollapsed === 'true') {
            dataPanelCollapsed = true;
            dataPanel.classList.add('collapsed');
            dataCollapseBtn.title = 'Expand panel';
        }
    }

    // File browser accordion - add localStorage persistence
    const fileBrowserPanel = document.getElementById('file-browser-panel');
    if (fileBrowserPanel) {
        const wasFileBrowserCollapsed = localStorage.getItem('figrecipe_filebrowser_collapsed');
        if (wasFileBrowserCollapsed === 'true') {
            fileBrowserPanel.classList.add('collapsed');
            const collapseBtn = document.getElementById('btn-collapse-browser');
            if (collapseBtn) {
                collapseBtn.innerHTML = '&#x276F;';
                collapseBtn.title = 'Expand panel';
            }
        }
    }

    // Preview/canvas panel collapse button
    const previewCollapseBtn = document.getElementById('btn-collapse-preview');
    const previewPanel = document.getElementById('preview-panel');

    if (previewCollapseBtn && previewPanel) {
        previewCollapseBtn.addEventListener('click', togglePreviewPanel);

        // Restore collapsed state from localStorage
        const wasPreviewCollapsed = localStorage.getItem('figrecipe_preview_collapsed');
        if (wasPreviewCollapsed === 'true') {
            previewPanelCollapsed = true;
            previewPanel.classList.add('collapsed');
            previewCollapseBtn.title = 'Expand canvas';
        }
    }

    // Add keyboard shortcuts for toggling panels
    document.addEventListener('keydown', (e) => {
        // Alt+1: Toggle file browser
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            if (typeof toggleFileBrowser === 'function') {
                toggleFileBrowser();
                saveFileBrowserState();
            }
        }
        // Alt+2: Toggle data panel
        if (e.altKey && e.key === '2') {
            e.preventDefault();
            toggleDataPanel();
        }
        // Alt+3: Toggle canvas/preview panel
        if (e.altKey && e.key === '3') {
            e.preventDefault();
            togglePreviewPanel();
        }
        // Alt+4: Toggle properties panel
        if (e.altKey && e.key === '4') {
            e.preventDefault();
            togglePropertiesPanel();
        }
    });

    console.log('[PanelAccordion] Initialized');
}

function toggleDataPanel() {
    const panel = document.getElementById('datatable-panel');
    const collapseBtn = document.getElementById('btn-collapse-datatable');
    if (!panel) return;

    dataPanelCollapsed = !dataPanelCollapsed;
    panel.classList.toggle('collapsed', dataPanelCollapsed);

    if (collapseBtn) {
        collapseBtn.title = dataPanelCollapsed ? 'Expand panel' : 'Collapse panel';
    }

    // Persist state
    localStorage.setItem('figrecipe_data_collapsed', dataPanelCollapsed);

    console.log('[PanelAccordion] Data panel', dataPanelCollapsed ? 'collapsed' : 'expanded');

    // Smart expansion: if collapsing, check if neighbors should expand
    if (dataPanelCollapsed) {
        checkSmartExpansion('datatable-panel');
    }
}

function togglePropertiesPanel() {
    const panel = document.getElementById('controls-panel');
    const collapseBtn = document.getElementById('btn-collapse-properties');
    if (!panel) return;

    propertiesPanelCollapsed = !propertiesPanelCollapsed;
    panel.classList.toggle('collapsed', propertiesPanelCollapsed);

    if (collapseBtn) {
        collapseBtn.title = propertiesPanelCollapsed ? 'Expand panel' : 'Collapse panel';
    }

    // Persist state
    localStorage.setItem('figrecipe_properties_collapsed', propertiesPanelCollapsed);

    console.log('[PanelAccordion] Properties panel', propertiesPanelCollapsed ? 'collapsed' : 'expanded');

    // Smart expansion: if collapsing, check if neighbors should expand
    if (propertiesPanelCollapsed) {
        checkSmartExpansion('controls-panel');
    }
}

function togglePreviewPanel() {
    const panel = document.getElementById('preview-panel');
    const collapseBtn = document.getElementById('btn-collapse-preview');
    if (!panel) return;

    previewPanelCollapsed = !previewPanelCollapsed;
    panel.classList.toggle('collapsed', previewPanelCollapsed);

    if (collapseBtn) {
        collapseBtn.title = previewPanelCollapsed ? 'Expand canvas' : 'Collapse canvas';
    }

    // Persist state
    localStorage.setItem('figrecipe_preview_collapsed', previewPanelCollapsed);

    console.log('[PanelAccordion] Preview panel', previewPanelCollapsed ? 'collapsed' : 'expanded');

    // Smart expansion: if collapsing, check if neighbors should expand
    if (previewPanelCollapsed) {
        checkSmartExpansion('preview-panel');
    }
}

function saveFileBrowserState() {
    const panel = document.getElementById('file-browser-panel');
    if (panel) {
        const isCollapsed = panel.classList.contains('collapsed');
        localStorage.setItem('figrecipe_filebrowser_collapsed', isCollapsed);
    }
}

// Hook into existing toggleFileBrowser to save state
const originalToggleFileBrowser = typeof window.toggleFileBrowser === 'function'
    ? window.toggleFileBrowser
    : null;

window.toggleFileBrowser = function() {
    if (originalToggleFileBrowser) {
        originalToggleFileBrowser();
    } else {
        // Fallback implementation
        const panel = document.getElementById('file-browser-panel');
        const collapseBtn = document.getElementById('btn-collapse-browser');
        if (!panel) return;

        panel.classList.toggle('collapsed');
        if (collapseBtn) {
            const isCollapsed = panel.classList.contains('collapsed');
            collapseBtn.innerHTML = isCollapsed ? '&#x276F;' : '&#x276E;';
            collapseBtn.title = isCollapsed ? 'Expand panel' : 'Collapse panel';
        }
    }
    saveFileBrowserState();

    // Smart expansion: if collapsing, check if neighbors should expand
    const panel = document.getElementById('file-browser-panel');
    if (panel && panel.classList.contains('collapsed')) {
        checkSmartExpansion('file-browser-panel');
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanelAccordion);
} else {
    initPanelAccordion();
}
"""

__all__ = ["SCRIPTS_ACCORDION"]

# EOF
