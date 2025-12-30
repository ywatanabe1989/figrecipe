#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caption controls JavaScript for the figure editor.

This module contains the JavaScript code for:
- Scientific figure captions (Fig. 1. Description...)
- Panel captions for multi-panel figures
- Caption preview and backend synchronization
"""

SCRIPTS_CAPTIONS = """
// ===== CAPTION CONTROLS (Scientific Figure Captions) =====

// Initialize caption input event handlers
function initializeCaptionInputs() {
    const figNumInput = document.getElementById('caption_figure_number');
    const figTextInput = document.getElementById('caption_figure_text');
    const panelTextInput = document.getElementById('caption_panel_text');
    const previewEl = document.getElementById('caption-preview-text');

    // Update caption preview when figure number changes
    if (figNumInput) {
        figNumInput.addEventListener('input', function() {
            updateCaptionPreview();
        });
    }

    // Update caption preview and send to backend when caption text changes
    if (figTextInput) {
        let timeout;
        figTextInput.addEventListener('input', function() {
            updateCaptionPreview();
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                updateFigureCaption();
            }, UPDATE_DEBOUNCE);
        });
    }

    // Update panel caption on input
    if (panelTextInput) {
        let timeout;
        panelTextInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                updatePanelCaption();
            }, UPDATE_DEBOUNCE);
        });
    }

    // Initial preview update
    updateCaptionPreview();
    loadCaptions();
}

// Update the caption preview text (composed caption in both properties panel and canvas pane)
function updateCaptionPreview() {
    const figNumInput = document.getElementById('caption_figure_number');
    const figTextInput = document.getElementById('caption_figure_text');
    const composedEl = document.getElementById('composed-caption-text');
    const canvasCaptionEl = document.getElementById('canvas-caption-text');

    const figNum = figNumInput?.value || '1';
    const figText = figTextInput?.value || '';

    // Build composed caption HTML
    let html = `<b>Fig. ${figNum}.</b>`;
    if (figText) {
        html += ` ${figText}`;
    }

    // Add panel captions if available
    const panelCaptions = getPanelCaptions();
    if (panelCaptions.length > 0) {
        const panelHtml = panelCaptions
            .map((pc, i) => pc ? `<span class="panel-caption">(${String.fromCharCode(65 + i)}) ${pc}</span>` : '')
            .filter(s => s)  // Filter empty strings
            .join(' ');
        if (panelHtml) {
            html += ' ' + panelHtml;
        }
    }

    // Update both preview locations
    if (composedEl) composedEl.innerHTML = html;
    if (canvasCaptionEl) canvasCaptionEl.innerHTML = html;
}

// Get all panel captions from stored state
function getPanelCaptions() {
    // Start with loaded panel captions from server
    const captions = [...loadedPanelCaptions];

    // Check for UI overrides
    for (let i = 0; i < 9; i++) {  // Support up to 9 panels (A-I)
        const input = document.querySelector(`[data-panel-caption="${i}"]`);
        if (input && input.value) {
            captions[i] = input.value;
        }
    }
    // Also check current panel caption input
    const currentPanel = document.getElementById('caption_panel_text');
    if (currentPanel && currentPanel.value && selectedElement?.ax_index !== undefined) {
        captions[selectedElement.ax_index] = currentPanel.value;
    }
    return captions;  // Keep all entries (including empty) for proper indexing
}

// Store loaded panel captions globally
let loadedPanelCaptions = [];

// Update panel caption input when panel is selected
function updatePanelCaptionInput(axIndex) {
    const panelTextInput = document.getElementById('caption_panel_text');
    if (!panelTextInput) return;

    // Get caption for this panel index
    const caption = loadedPanelCaptions[axIndex] || '';
    panelTextInput.value = caption;
}

// Load existing captions from server
async function loadCaptions() {
    try {
        const response = await fetch('/get_captions');
        const data = await response.json();

        if (data.figure_number) {
            const figNumInput = document.getElementById('caption_figure_number');
            if (figNumInput) figNumInput.value = data.figure_number;
        }

        if (data.figure_caption) {
            const figTextInput = document.getElementById('caption_figure_text');
            if (figTextInput) figTextInput.value = data.figure_caption;
        }

        // Store panel captions for composed caption
        if (data.panel_captions && Array.isArray(data.panel_captions)) {
            loadedPanelCaptions = data.panel_captions;
        }

        updateCaptionPreview();
        console.log('Loaded captions:', data);
    } catch (error) {
        console.log('Captions not loaded (endpoint may not exist yet):', error.message);
    }
}

// Update figure caption on server
async function updateFigureCaption() {
    const figNumInput = document.getElementById('caption_figure_number');
    const figTextInput = document.getElementById('caption_figure_text');

    const figNum = parseInt(figNumInput?.value) || 1;
    const figText = figTextInput?.value || '';

    console.log(`Updating figure caption: Fig. ${figNum}. ${figText}`);

    try {
        const response = await fetch('/update_caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'figure',
                figure_number: figNum,
                text: figText
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log('Figure caption updated');
        } else {
            console.error('Figure caption update failed:', data.error);
        }
    } catch (error) {
        console.error('Figure caption update failed:', error);
    }
}

// Update panel caption on server
async function updatePanelCaption() {
    const panelTextInput = document.getElementById('caption_panel_text');
    const panelText = panelTextInput?.value || '';

    // Get current panel index - prefer currentSelectedPanelIndex, fallback to selectedElement
    let panelIndex = 0;
    if (typeof currentSelectedPanelIndex !== 'undefined' && currentSelectedPanelIndex !== null) {
        panelIndex = currentSelectedPanelIndex;
    } else if (selectedElement && selectedElement.ax_index !== undefined) {
        panelIndex = selectedElement.ax_index;
    }

    // Update local cache
    while (loadedPanelCaptions.length <= panelIndex) {
        loadedPanelCaptions.push('');
    }
    loadedPanelCaptions[panelIndex] = panelText;

    console.log(`Updating panel ${panelIndex} caption: ${panelText}`);

    try {
        const response = await fetch('/update_caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'panel',
                panel_index: panelIndex,
                text: panelText
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log('Panel caption updated');
            updateCaptionPreview();  // Update composed caption preview
        } else {
            console.error('Panel caption update failed:', data.error);
        }
    } catch (error) {
        console.error('Panel caption update failed:', error);
    }
}
"""

__all__ = ["SCRIPTS_CAPTIONS"]

# EOF
