#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legend drag-to-move JavaScript for the figure editor.

This module contains the JavaScript code for:
- Detecting mousedown on legend elements
- Handling drag movement with visual feedback
- Updating legend position on drop

Legend coordinates are in axes-relative units (0-1 range).
"""

SCRIPTS_LEGEND_DRAG = """
// ===== LEGEND DRAG-TO-MOVE =====

let isDraggingLegend = false;
let legendDragStartPos = null;
let legendDragStartBbox = null;
let legendDragOverlay = null;
let legendAxIndex = 0;

// Initialize legend drag functionality
function initLegendDrag() {
    console.log('[LegendDrag] initLegendDrag called');
    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) {
        console.error('[LegendDrag] zoom-container not found!');
        return;
    }

    // Create legend drag overlay element
    legendDragOverlay = document.createElement('div');
    legendDragOverlay.id = 'legend-drag-overlay';
    legendDragOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #10b981;
        background: rgba(16, 185, 129, 0.1);
        pointer-events: none;
        display: none;
        z-index: 1001;
    `;
    zoomContainer.appendChild(legendDragOverlay);
    console.log('[LegendDrag] Overlay created');
}

// Handle legend drag start (called from hitmap click handler)
function startLegendDrag(event, legendKey) {
    console.log('[LegendDrag] startLegendDrag called for:', legendKey);

    const img = document.getElementById('preview-image');
    if (!img) return false;

    const bbox = currentBboxes[legendKey];
    if (!bbox) return false;

    event.preventDefault();
    event.stopPropagation();

    // Capture state before drag for undo
    if (typeof pushToHistory === 'function') {
        pushToHistory();
    }

    isDraggingLegend = true;
    legendDragStartPos = { x: event.clientX, y: event.clientY };
    legendDragStartBbox = { ...bbox };

    // Extract axis index from key (e.g., "legend_ax0" -> 0)
    const match = legendKey.match(/ax(\\d+)/);
    legendAxIndex = match ? parseInt(match[1], 10) : 0;

    // Show drag overlay
    if (legendDragOverlay) {
        updateLegendDragOverlay(bbox);
        legendDragOverlay.style.display = 'block';
    }

    // Add temporary event listeners
    document.addEventListener('mousemove', handleLegendDragMove);
    document.addEventListener('mouseup', handleLegendDragEnd);

    document.body.style.cursor = 'move';
    console.log('[LegendDrag] Started dragging legend');
    return true;
}

// Handle mouse move during legend drag
function handleLegendDragMove(event) {
    if (!isDraggingLegend) return;

    event.preventDefault();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();

    // Calculate delta in pixels
    const deltaX = event.clientX - legendDragStartPos.x;
    const deltaY = event.clientY - legendDragStartPos.y;

    // Calculate new position in image pixels
    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;

    const newBbox = {
        x: legendDragStartBbox.x + deltaX * scaleX,
        y: legendDragStartBbox.y + deltaY * scaleY,
        width: legendDragStartBbox.width,
        height: legendDragStartBbox.height
    };

    // Update visual overlay
    updateLegendDragOverlay(newBbox);
}

// Update the legend drag overlay position
function updateLegendDragOverlay(bbox) {
    if (!legendDragOverlay) return;

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();
    const scaleX = rect.width / img.naturalWidth;
    const scaleY = rect.height / img.naturalHeight;

    const left = bbox.x * scaleX;
    const top = bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    legendDragOverlay.style.left = `${left}px`;
    legendDragOverlay.style.top = `${top}px`;
    legendDragOverlay.style.width = `${width}px`;
    legendDragOverlay.style.height = `${height}px`;
}

// Handle mouse up - complete the legend drag
async function handleLegendDragEnd(event) {
    console.log('[LegendDrag] handleLegendDragEnd called');
    if (!isDraggingLegend) return;

    // Remove temporary event listeners
    document.removeEventListener('mousemove', handleLegendDragMove);
    document.removeEventListener('mouseup', handleLegendDragEnd);

    // Hide overlay
    if (legendDragOverlay) {
        legendDragOverlay.style.display = 'none';
    }
    document.body.style.cursor = '';

    const img = document.getElementById('preview-image');
    if (!img) {
        isDraggingLegend = false;
        return;
    }

    const rect = img.getBoundingClientRect();

    // Calculate delta in pixels
    const deltaX = event.clientX - legendDragStartPos.x;
    const deltaY = event.clientY - legendDragStartPos.y;

    // Only update if moved significantly (5px threshold)
    if (Math.abs(deltaX) < 5 && Math.abs(deltaY) < 5) {
        console.log('[LegendDrag] Movement below threshold, not updating');
        isDraggingLegend = false;
        return;
    }

    // Convert to axes-relative coordinates (0-1 range)
    // We need to get the axes position to calculate relative coords
    const axKey = Object.keys(panelPositions).sort()[legendAxIndex];
    const axPos = panelPositions[axKey];

    if (!axPos || !figSize.width_mm || !figSize.height_mm) {
        console.error('[LegendDrag] Cannot calculate axes-relative position');
        isDraggingLegend = false;
        return;
    }

    // Calculate scale factors: screen pixels to image pixels
    const screenToImgX = img.naturalWidth / rect.width;
    const screenToImgY = img.naturalHeight / rect.height;

    // New legend upper-left corner in image pixels
    const newImgX = legendDragStartBbox.x + deltaX * screenToImgX;
    const newImgY = legendDragStartBbox.y + deltaY * screenToImgY;

    // Convert image pixels to mm (upper-left origin)
    const newMmX = newImgX / img.naturalWidth * figSize.width_mm;
    const newMmY = newImgY / img.naturalHeight * figSize.height_mm;

    // Convert to axes-relative (0-1) coordinates
    // Use upper-left corner since we set _loc=2 (upper left) in backend
    const relX = (newMmX - axPos.left) / axPos.width;
    const relY = 1 - (newMmY - axPos.top) / axPos.height;  // Flip Y (matplotlib uses bottom-left origin)

    console.log('[LegendDrag] New legend position (rel):', relX.toFixed(3), relY.toFixed(3));

    // Apply the new position
    await applyLegendPosition(legendAxIndex, relX, relY);

    // Reset state
    isDraggingLegend = false;
    legendDragStartPos = null;
    legendDragStartBbox = null;
    console.log('[LegendDrag] Drag state reset');
}

// Apply the dragged legend position to the server
async function applyLegendPosition(axIndex, x, y) {
    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_legend_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ax_index: axIndex,
                loc: 'custom',
                x: x,
                y: y
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            if (img) {
                await new Promise((resolve) => {
                    img.onload = resolve;
                    img.src = 'data:image/png;base64,' + data.image;
                });
            }

            // Update bboxes and hitmap
            if (data.bboxes) {
                currentBboxes = data.bboxes;
                loadHitmap();
                updateHitRegions();
            }

            console.log('[LegendDrag] Legend position updated successfully');
        } else {
            console.error('[LegendDrag] Failed to update legend:', data.error);
        }
    } catch (error) {
        console.error('[LegendDrag] Failed to update legend:', error);
    }

    document.body.classList.remove('loading');
}

// Check if a key refers to a legend element
function isLegendElement(key) {
    return key && key.startsWith('legend_');
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initLegendDrag);
"""

__all__ = ["SCRIPTS_LEGEND_DRAG"]

# EOF
