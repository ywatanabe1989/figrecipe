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

// Draw visual highlight around selected panel (axis bbox only)
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

// Draw full panel bbox (union of all elements belonging to the panel)
function drawPanelBbox(axIndex) {
    const overlay = document.getElementById('selection-overlay');
    if (!overlay) return;

    // Clear previous panel bbox
    const existingBbox = document.getElementById('panel-bbox-highlight');
    if (existingBbox) existingBbox.remove();

    // Get panel_bboxes from currentBboxes metadata
    const panelBboxes = currentBboxes?._meta?.panel_bboxes;
    if (!panelBboxes || !panelBboxes[axIndex]) {
        console.log('[PanelBbox] No panel bbox for ax', axIndex);
        return;
    }

    const panelBbox = panelBboxes[axIndex];
    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth || !img.naturalHeight) return;

    // Ensure viewBox is set
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // panel bbox is already in pixel coordinates
    const x = panelBbox.x;
    const y = panelBbox.y;
    const width = panelBbox.width;
    const height = panelBbox.height;

    // Create panel bbox rectangle (different style from axis highlight)
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.id = 'panel-bbox-highlight';
    rect.setAttribute('x', x - 2);  // Small padding
    rect.setAttribute('y', y - 2);
    rect.setAttribute('width', width + 4);
    rect.setAttribute('height', height + 4);
    rect.setAttribute('fill', 'rgba(59, 130, 246, 0.05)');  // Very light blue fill
    rect.setAttribute('stroke', '#3b82f6');  // Blue stroke
    rect.setAttribute('stroke-width', '2');
    rect.setAttribute('stroke-dasharray', '6,3');
    rect.style.pointerEvents = 'none';

    overlay.appendChild(rect);
    console.log('[PanelBbox] Drew bbox for panel', axIndex, panelBbox);
}

// Clear panel bbox highlight
function clearPanelBbox() {
    const existingBbox = document.getElementById('panel-bbox-highlight');
    if (existingBbox) existingBbox.remove();
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

    // Draw panel bbox (union of all elements)
    drawPanelBbox(axIndex);

    // Update panel caption input
    if (typeof updatePanelCaptionInput === 'function') {
        updatePanelCaptionInput(axIndex);
    }

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
    clearPanelBbox();
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

    // Initialize debug toolbar if in debug mode
    if (typeof DEBUG_MODE !== 'undefined' && DEBUG_MODE) {
        initDebugToolbar();
    }
}

// ===== DEBUG MODE: SHOW ALL BBOXES =====

let allBboxesVisible = false;

// Toggle showing all panel bboxes at once
function toggleAllBboxes() {
    allBboxesVisible = !allBboxesVisible;

    const overlay = document.getElementById('selection-overlay');
    if (!overlay) return;

    // Remove existing debug bboxes
    document.querySelectorAll('.debug-panel-bbox').forEach(el => el.remove());

    if (!allBboxesVisible) {
        console.log('[Debug] All bboxes hidden');
        updateDebugButton(false);
        return;
    }

    const panelBboxes = currentBboxes?._meta?.panel_bboxes;
    if (!panelBboxes) {
        console.warn('[Debug] No panel bboxes available');
        showToast('No panel bboxes available', 'warning');
        return;
    }

    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth || !img.naturalHeight) return;

    // Ensure viewBox is set
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // Colors for different panels
    const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316'];

    // Draw bbox for each panel
    Object.entries(panelBboxes).forEach(([axIdx, bbox], idx) => {
        const color = colors[idx % colors.length];
        const label = String.fromCharCode(65 + parseInt(axIdx)); // A, B, C...

        // Create bbox rectangle
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.classList.add('debug-panel-bbox');
        rect.setAttribute('x', bbox.x);
        rect.setAttribute('y', bbox.y);
        rect.setAttribute('width', bbox.width);
        rect.setAttribute('height', bbox.height);
        rect.setAttribute('fill', 'none');
        rect.setAttribute('stroke', color);
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('stroke-dasharray', '5,3');
        rect.style.pointerEvents = 'none';
        overlay.appendChild(rect);

        // Create label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.classList.add('debug-panel-bbox');
        text.setAttribute('x', bbox.x + 5);
        text.setAttribute('y', bbox.y + 15);
        text.setAttribute('fill', color);
        text.setAttribute('font-size', '14');
        text.setAttribute('font-weight', 'bold');
        text.style.pointerEvents = 'none';
        text.textContent = `Panel ${label}`;
        overlay.appendChild(text);
    });

    console.log('[Debug] Showing all panel bboxes:', Object.keys(panelBboxes).length);
    updateDebugButton(true);
}

// Update debug button state
function updateDebugButton(active) {
    const btn = document.getElementById('btn-debug-bboxes');
    if (btn) {
        btn.classList.toggle('active', active);
        btn.title = active ? 'Hide All Bboxes (Alt+B)' : 'Show All Bboxes (Alt+B)';
    }
}

// Initialize debug toolbar
function initDebugToolbar() {
    // Find the preview controls area
    const previewControls = document.querySelector('.preview-controls');
    if (!previewControls) return;

    // Create debug button
    const debugBtn = document.createElement('button');
    debugBtn.id = 'btn-debug-bboxes';
    debugBtn.className = 'btn-icon btn-debug';
    debugBtn.title = 'Show All Bboxes (Alt+B)';
    debugBtn.innerHTML = '🔲';
    debugBtn.style.cssText = 'margin-left: 8px; background: #374151; border: 1px dashed #f59e0b; color: #f59e0b;';
    debugBtn.onclick = toggleAllBboxes;

    // Add to controls
    previewControls.appendChild(debugBtn);

    console.log('[Debug] Debug toolbar initialized (FIGRECIPE_DEBUG_MODE=1)');
    console.log('[Debug] Shortcuts: Alt+I = Element Inspector, Alt+B = Show All Bboxes');
}

// Call initialization on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPanelPositionControls);
"""

__all__ = ["SCRIPTS_PANEL_POSITION"]

# EOF
