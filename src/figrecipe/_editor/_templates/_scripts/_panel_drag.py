#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel drag-to-move JavaScript for the figure editor.

This module contains the JavaScript code for:
- Detecting mousedown on axes/panel elements
- Handling drag movement with visual feedback
- Updating panel position on drop
"""

SCRIPTS_PANEL_DRAG = """
// ===== PANEL DRAG-TO-MOVE =====

let isDraggingPanel = false;
let draggedPanelIndex = null;
let dragStartPos = null;
let dragStartPanelPos = null;
let panelDragOverlay = null;

// Initialize panel drag functionality
function initPanelDrag() {
    const previewContainer = document.getElementById('preview-container');
    if (!previewContainer) return;

    // Add mouse event listeners
    previewContainer.addEventListener('mousedown', handlePanelDragStart);
    document.addEventListener('mousemove', handlePanelDragMove);
    document.addEventListener('mouseup', handlePanelDragEnd);

    // Create drag overlay element
    panelDragOverlay = document.createElement('div');
    panelDragOverlay.id = 'panel-drag-overlay';
    panelDragOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #2563eb;
        background: rgba(37, 99, 235, 0.1);
        pointer-events: none;
        display: none;
        z-index: 1000;
    `;
    previewContainer.appendChild(panelDragOverlay);
}

// Handle mouse down - check if on a panel/axes
function handlePanelDragStart(event) {
    // Only start drag on Shift+Click
    if (!event.shiftKey) return;

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert to figure coordinates (0-1)
    const figX = x / rect.width;
    const figY = 1 - (y / rect.height);  // Flip Y axis for matplotlib coords

    // Find which panel was clicked
    const panelIndex = findPanelAtPosition(figX, figY);

    if (panelIndex !== null) {
        event.preventDefault();
        event.stopPropagation();

        isDraggingPanel = true;
        draggedPanelIndex = panelIndex;
        dragStartPos = { x: event.clientX, y: event.clientY };

        // Get current panel position
        const axKey = Object.keys(panelPositions).sort()[panelIndex];
        const pos = panelPositions[axKey];
        dragStartPanelPos = { ...pos };

        // Show drag overlay
        updateDragOverlay(pos, rect);
        panelDragOverlay.style.display = 'block';

        // Change cursor
        document.body.style.cursor = 'move';

        console.log('Started dragging panel', panelIndex);
    }
}

// Find which panel contains the given position
function findPanelAtPosition(figX, figY) {
    const axKeys = Object.keys(panelPositions).sort();

    for (let i = 0; i < axKeys.length; i++) {
        const pos = panelPositions[axKeys[i]];

        if (figX >= pos.left && figX <= pos.right &&
            figY >= pos.bottom && figY <= pos.top) {
            return i;
        }
    }
    return null;
}

// Handle mouse move during drag
function handlePanelDragMove(event) {
    if (!isDraggingPanel) return;

    event.preventDefault();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();

    // Calculate delta in figure coordinates
    const deltaX = (event.clientX - dragStartPos.x) / rect.width;
    const deltaY = -(event.clientY - dragStartPos.y) / rect.height;  // Flip Y

    // Calculate new position (clamped to 0-1)
    const newLeft = Math.max(0, Math.min(1 - dragStartPanelPos.width, dragStartPanelPos.left + deltaX));
    const newBottom = Math.max(0, Math.min(1 - dragStartPanelPos.height, dragStartPanelPos.bottom + deltaY));

    const newPos = {
        left: newLeft,
        bottom: newBottom,
        width: dragStartPanelPos.width,
        height: dragStartPanelPos.height,
        right: newLeft + dragStartPanelPos.width,
        top: newBottom + dragStartPanelPos.height
    };

    // Update visual overlay
    updateDragOverlay(newPos, rect);
}

// Update the drag overlay position
function updateDragOverlay(pos, imgRect) {
    if (!panelDragOverlay) return;

    // Convert figure coords to screen coords
    const left = pos.left * imgRect.width;
    const bottom = pos.bottom * imgRect.height;
    const width = pos.width * imgRect.width;
    const height = pos.height * imgRect.height;

    // SVG/CSS uses top-left origin, matplotlib uses bottom-left
    const top = imgRect.height - bottom - height;

    panelDragOverlay.style.left = `${left}px`;
    panelDragOverlay.style.top = `${top}px`;
    panelDragOverlay.style.width = `${width}px`;
    panelDragOverlay.style.height = `${height}px`;
}

// Handle mouse up - complete the drag
async function handlePanelDragEnd(event) {
    if (!isDraggingPanel) return;

    // Hide overlay
    panelDragOverlay.style.display = 'none';
    document.body.style.cursor = '';

    const img = document.getElementById('preview-image');
    if (!img) {
        isDraggingPanel = false;
        return;
    }

    const rect = img.getBoundingClientRect();

    // Calculate final position
    const deltaX = (event.clientX - dragStartPos.x) / rect.width;
    const deltaY = -(event.clientY - dragStartPos.y) / rect.height;

    const newLeft = Math.max(0, Math.min(1 - dragStartPanelPos.width, dragStartPanelPos.left + deltaX));
    const newBottom = Math.max(0, Math.min(1 - dragStartPanelPos.height, dragStartPanelPos.bottom + deltaY));

    // Only update if position actually changed
    const threshold = 0.005;
    if (Math.abs(newLeft - dragStartPanelPos.left) > threshold ||
        Math.abs(newBottom - dragStartPanelPos.bottom) > threshold) {

        // Apply the new position
        await applyDraggedPanelPosition(
            draggedPanelIndex,
            newLeft,
            newBottom,
            dragStartPanelPos.width,
            dragStartPanelPos.height
        );
    }

    // Reset state
    isDraggingPanel = false;
    draggedPanelIndex = null;
    dragStartPos = null;
    dragStartPanelPos = null;
}

// Apply the dragged panel position to the server
async function applyDraggedPanelPosition(axIndex, left, bottom, width, height) {
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

            // Update bboxes and hitmap
            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Reload positions
            await loadPanelPositions();

            console.log('Panel position updated via drag');
        } else {
            console.error('Failed to update position:', data.error);
        }
    } catch (error) {
        console.error('Failed to update position:', error);
    }

    document.body.classList.remove('loading');
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPanelDrag);
"""

__all__ = ["SCRIPTS_PANEL_DRAG"]

# EOF
