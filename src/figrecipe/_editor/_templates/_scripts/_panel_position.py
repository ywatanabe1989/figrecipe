#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel position JavaScript for the figure editor.

This module contains the JavaScript code for:
- Loading and displaying panel positions
- Updating panel positions via numerical inputs
"""

SCRIPTS_PANEL_POSITION = """
// ===== PANEL POSITION =====

let panelPositions = {};

// Load panel positions from server
async function loadPanelPositions() {
    try {
        const response = await fetch('/get_axes_positions');
        panelPositions = await response.json();
        updatePanelSelector();
        updatePanelPositionInputs();
    } catch (error) {
        console.error('Failed to load panel positions:', error);
    }
}

// Update panel selector dropdown
function updatePanelSelector() {
    const selector = document.getElementById('panel_selector');
    if (!selector) return;

    selector.innerHTML = '';
    const axKeys = Object.keys(panelPositions).sort();

    axKeys.forEach((key, index) => {
        const opt = document.createElement('option');
        opt.value = index;
        // Show panel label (A, B, C...) if available
        const label = String.fromCharCode(65 + index); // A, B, C...
        opt.textContent = `Panel ${label} (${key})`;
        selector.appendChild(opt);
    });

    // Add change event listener
    selector.addEventListener('change', updatePanelPositionInputs);
}

// Update position input fields based on selected panel
function updatePanelPositionInputs() {
    const selector = document.getElementById('panel_selector');
    if (!selector) return;

    const axIndex = parseInt(selector.value, 10);
    const axKey = Object.keys(panelPositions).sort()[axIndex];
    const pos = panelPositions[axKey];

    if (!pos) return;

    const leftInput = document.getElementById('panel_left');
    const bottomInput = document.getElementById('panel_bottom');
    const widthInput = document.getElementById('panel_width');
    const heightInput = document.getElementById('panel_height');

    if (leftInput) leftInput.value = pos.left;
    if (bottomInput) bottomInput.value = pos.bottom;
    if (widthInput) widthInput.value = pos.width;
    if (heightInput) heightInput.value = pos.height;
}

// Apply panel position changes
async function applyPanelPosition() {
    const selector = document.getElementById('panel_selector');
    const leftInput = document.getElementById('panel_left');
    const bottomInput = document.getElementById('panel_bottom');
    const widthInput = document.getElementById('panel_width');
    const heightInput = document.getElementById('panel_height');

    if (!selector || !leftInput || !bottomInput || !widthInput || !heightInput) {
        console.error('Panel position inputs not found');
        return;
    }

    const axIndex = parseInt(selector.value, 10);
    const left = parseFloat(leftInput.value);
    const bottom = parseFloat(bottomInput.value);
    const width = parseFloat(widthInput.value);
    const height = parseFloat(heightInput.value);

    // Validate values
    if ([left, bottom, width, height].some(v => isNaN(v) || v < 0 || v > 1)) {
        alert('Position values must be between 0 and 1');
        return;
    }

    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_axes_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ax_index: axIndex,
                left: left,
                bottom: bottom,
                width: width,
                height: height
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            if (img) img.src = 'data:image/png;base64,' + data.image;

            // Update image size
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Reload positions to reflect any adjustments
            await loadPanelPositions();

            console.log('Panel position updated successfully');
        } else {
            alert('Failed to update position: ' + data.error);
        }
    } catch (error) {
        alert('Failed to update position: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Initialize panel position controls
function initPanelPositionControls() {
    const applyBtn = document.getElementById('apply_panel_position');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyPanelPosition);
    }

    // Load initial positions
    loadPanelPositions();
}

// Call initialization on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPanelPositionControls);
"""

__all__ = ["SCRIPTS_PANEL_POSITION"]

# EOF
