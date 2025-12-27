#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel position JavaScript for the figure editor.

This module contains the JavaScript code for:
- Loading and displaying panel positions
- Updating panel positions via numerical inputs
"""

SCRIPTS_PANEL_POSITION = r"""
// ===== PANEL POSITION (mm, upper-left origin) =====

let panelPositions = {};
let figSize = { width_mm: 0, height_mm: 0 };
let currentSelectedPanelIndex = null;  // Track currently selected panel

// Load panel positions from server
async function loadPanelPositions() {
    try {
        const response = await fetch('/get_axes_positions');
        const data = await response.json();

        // Extract figure size
        if (data._figsize) {
            figSize = data._figsize;
            delete data._figsize;
        }

        panelPositions = data;
        // Update inputs if a panel is selected
        if (currentSelectedPanelIndex !== null) {
            updatePanelPositionInputs();
        }
    } catch (error) {
        console.error('Failed to load panel positions:', error);
    }
}

// Update position input fields based on currently selected panel
function updatePanelPositionInputs(showHighlight = true) {
    const indicator = document.getElementById('current_panel_indicator');
    const leftInput = document.getElementById('panel_left');
    const topInput = document.getElementById('panel_top');
    const widthInput = document.getElementById('panel_width');
    const heightInput = document.getElementById('panel_height');
    const applyBtn = document.getElementById('apply_panel_position');

    // If no panel selected, show placeholder and disable inputs
    if (currentSelectedPanelIndex === null) {
        if (indicator) {
            indicator.textContent = 'Select an element';
            indicator.classList.remove('panel-selected');
        }
        [leftInput, topInput, widthInput, heightInput].forEach(input => {
            if (input) {
                input.value = '';
                input.disabled = true;
            }
        });
        if (applyBtn) applyBtn.disabled = true;
        return;
    }

    const axKey = Object.keys(panelPositions).sort()[currentSelectedPanelIndex];
    const pos = panelPositions[axKey];

    if (!pos) return;

    // Update indicator
    if (indicator) {
        const label = String.fromCharCode(65 + currentSelectedPanelIndex); // A, B, C...
        indicator.textContent = `Panel ${label}`;
        indicator.classList.add('panel-selected');
    }

    // Enable inputs and update values
    [leftInput, topInput, widthInput, heightInput].forEach(input => {
        if (input) input.disabled = false;
    });
    if (applyBtn) applyBtn.disabled = false;

    // Values are already in mm from server
    if (leftInput) leftInput.value = pos.left;
    if (topInput) topInput.value = pos.top;
    if (widthInput) widthInput.value = pos.width;
    if (heightInput) heightInput.value = pos.height;

    // Draw highlight
    if (showHighlight) {
        drawPanelSelectionHighlight(pos);
    }
}

// Draw visual highlight around selected panel
function drawPanelSelectionHighlight(pos) {
    const overlay = document.getElementById('selection-overlay');
    if (!overlay) return;

    // Clear previous panel highlight (but keep element selections)
    const existingHighlight = document.getElementById('panel-selection-highlight');
    if (existingHighlight) existingHighlight.remove();

    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth || !img.naturalHeight) return;

    // Ensure viewBox is set
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // Convert mm coords (upper-left origin) to image pixel coords
    // pos.left, pos.top, pos.width, pos.height are in mm
    const scaleX = img.naturalWidth / figSize.width_mm;
    const scaleY = img.naturalHeight / figSize.height_mm;

    const x = pos.left * scaleX;
    const y = pos.top * scaleY;  // Already in upper-left origin
    const width = pos.width * scaleX;
    const height = pos.height * scaleY;

    // Create highlight rectangle
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.id = 'panel-selection-highlight';
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('fill', 'none');
    rect.setAttribute('stroke', '#f59e0b');
    rect.setAttribute('stroke-width', '3');
    rect.setAttribute('stroke-dasharray', '8,4');
    rect.style.pointerEvents = 'none';

    overlay.appendChild(rect);
}

// Clear panel selection highlight
function clearPanelSelectionHighlight() {
    const existingHighlight = document.getElementById('panel-selection-highlight');
    if (existingHighlight) existingHighlight.remove();
}

// Select panel by index (called when clicking on axes in canvas)
function selectPanelByIndex(axIndex, switchToAxisTab = true) {
    // Update the current selected panel index
    currentSelectedPanelIndex = axIndex;

    // Update inputs and highlight
    updatePanelPositionInputs();

    // Switch to Axis tab only if requested (default true for backwards compat)
    if (switchToAxisTab) {
        switchTab('axis');
    }

    console.log('Selected panel', axIndex);
}

// Clear panel selection (called when selection is cleared)
function clearPanelSelection() {
    currentSelectedPanelIndex = null;
    updatePanelPositionInputs(false);
    clearPanelSelectionHighlight();
}

// Find panel index from axes key (e.g., "ax_0" -> 0)
function getPanelIndexFromKey(key) {
    if (!key) return null;

    // Handle "ax_N" format
    const match = key.match(/ax_(\d+)/);
    if (match) {
        return parseInt(match[1], 10);
    }

    // Handle axes type elements - find by checking bboxes
    const axKeys = Object.keys(panelPositions).sort();
    for (let i = 0; i < axKeys.length; i++) {
        if (axKeys[i] === key) {
            return i;
        }
    }

    return null;
}

// Apply panel position changes
async function applyPanelPosition() {
    const leftInput = document.getElementById('panel_left');
    const topInput = document.getElementById('panel_top');
    const widthInput = document.getElementById('panel_width');
    const heightInput = document.getElementById('panel_height');

    if (currentSelectedPanelIndex === null) {
        console.error('No panel selected');
        return;
    }

    if (!leftInput || !topInput || !widthInput || !heightInput) {
        console.error('Panel position inputs not found');
        return;
    }

    const axIndex = currentSelectedPanelIndex;
    const left = parseFloat(leftInput.value);
    const top = parseFloat(topInput.value);
    const width = parseFloat(widthInput.value);
    const height = parseFloat(heightInput.value);

    // Validate values (mm, must be positive and within figure bounds)
    if ([left, top, width, height].some(v => isNaN(v) || v < 0)) {
        alert('Position values must be positive numbers in mm');
        return;
    }

    if (left + width > figSize.width_mm || top + height > figSize.height_mm) {
        alert(`Panel extends beyond figure bounds (${figSize.width_mm.toFixed(1)} x ${figSize.height_mm.toFixed(1)} mm)`);
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
                top: top,
                width: width,
                height: height
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image and wait for it to load
            const img = document.getElementById('preview-image');
            if (img) {
                await new Promise((resolve) => {
                    img.onload = resolve;
                    img.src = 'data:image/png;base64,' + data.image;
                });
            }

            // Update image size
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Reload positions to reflect any adjustments (now with correct image dimensions)
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
