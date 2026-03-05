#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel drag-to-move JavaScript for the figure editor.

This module contains the JavaScript code for:
- Detecting mousedown on axes/panel elements
- Handling drag movement with visual feedback
- Updating panel position on drop

Coordinates are in mm with upper-left origin.
"""

SCRIPTS_PANEL_DRAG = """
// ===== PANEL DRAG-TO-MOVE (mm, upper-left origin) =====

let isDraggingPanel = false;
let draggedPanelIndex = null;
let dragStartPos = null;
let dragStartPanelPos = null;
let panelDragOverlay = null;
let panelBboxDragOverlay = null;  // Outer panel bbox overlay
let panelHoverOverlay = null;
let hoveredPanelIndex = null;
let dragStartPanelBbox = null;  // Initial panel bbox in pixels
let panelBboxOffset = null;  // Offset from axis to panel bbox (in mm)

// Initialize panel drag functionality
function initPanelDrag() {
    console.log('[PanelDrag] initPanelDrag called');
    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) {
        console.error('[PanelDrag] zoom-container not found!');
        return;
    }

    // Add mouse event listeners to zoom container
    zoomContainer.addEventListener('mousedown', handlePanelDragStart);
    document.addEventListener('mousemove', handlePanelDragMove);
    document.addEventListener('mouseup', handlePanelDragEnd);
    console.log('[PanelDrag] Event listeners attached');

    // Create drag overlay for axis bbox (inner, subtle orange)
    panelDragOverlay = document.createElement('div');
    panelDragOverlay.id = 'panel-drag-overlay';
    panelDragOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #f59e0b;
        background: rgba(245, 158, 11, 0.08);
        pointer-events: none;
        display: none;
        z-index: 999;
    `;
    zoomContainer.appendChild(panelDragOverlay);

    // Create outer panel bbox overlay (prominent blue)
    panelBboxDragOverlay = document.createElement('div');
    panelBboxDragOverlay.id = 'panel-bbox-drag-overlay';
    panelBboxDragOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #2563eb;
        background: rgba(37, 99, 235, 0.05);
        pointer-events: none;
        display: none;
        z-index: 1000;
    `;
    zoomContainer.appendChild(panelBboxDragOverlay);

    // Create hover overlay element for visual feedback
    panelHoverOverlay = document.createElement('div');
    panelHoverOverlay.id = 'panel-hover-overlay';
    panelHoverOverlay.style.cssText = `
        position: absolute;
        border: 2px solid rgba(37, 99, 235, 0.5);
        background: rgba(37, 99, 235, 0.05);
        pointer-events: none;
        display: none;
        z-index: 999;
        transition: opacity 0.15s ease-in-out;
    `;
    zoomContainer.appendChild(panelHoverOverlay);

    // Add hover detection on zoom container
    zoomContainer.addEventListener('mousemove', handlePanelHover);
    zoomContainer.addEventListener('mouseleave', hidePanelHover);

    console.log('[PanelDrag] Overlays created');
}

// Handle mouse down - check if on a panel/axes (only drag from empty panel area)
function handlePanelDragStart(event) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;  // Skip modifier keys

    // Only allow drag from axes/imshow/contour/quadmesh/quiver (fills panel area)
    const target = event.target;
    const targetKey = target.getAttribute ? target.getAttribute('data-key') : null;
    if (targetKey && typeof currentBboxes !== 'undefined' && currentBboxes[targetKey]) {
        const elemType = currentBboxes[targetKey].type;
        const dragAllowedTypes = ['axes', 'image', 'contour', 'quadmesh', 'quiver'];
        if (elemType && !dragAllowedTypes.includes(elemType)) return;
    }

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    const rect = img.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Convert to mm coordinates (upper-left origin)
    const mmX = (x / rect.width) * figSize.width_mm;
    const mmY = (y / rect.height) * figSize.height_mm;

    // Find which panel was clicked (using expanded bounds including labels)
    const panelIndex = findPanelAtPositionMm(mmX, mmY);
    console.log('[PanelDrag] Click at mm:', mmX.toFixed(1), mmY.toFixed(1), '-> panel:', panelIndex);

    if (panelIndex !== null) {
        event.preventDefault();
        event.stopPropagation();

        // Capture state before drag for undo
        if (typeof pushToHistory === 'function') {
            pushToHistory();
        }

        isDraggingPanel = true;
        draggedPanelIndex = panelIndex;
        dragStartPos = { x: event.clientX, y: event.clientY };

        // Hide hover overlay when starting drag
        hidePanelHover();

        // Get current panel position (in mm)
        const axKey = Object.keys(panelPositions).sort()[panelIndex];
        const pos = panelPositions[axKey];
        dragStartPanelPos = { ...pos };

        // Get panel bbox (outer bounds including labels) and calculate offset from axis
        const panelBboxes = currentBboxes?._meta?.panel_bboxes;
        if (panelBboxes && panelBboxes[panelIndex] && img.naturalWidth) {
            dragStartPanelBbox = { ...panelBboxes[panelIndex] };
            // Convert panel bbox to mm and calculate offset from axis position
            const pxToMmX = figSize.width_mm / img.naturalWidth;
            const pxToMmY = figSize.height_mm / img.naturalHeight;
            panelBboxOffset = {
                left: dragStartPanelBbox.x * pxToMmX - pos.left,
                top: dragStartPanelBbox.y * pxToMmY - pos.top,
                width: dragStartPanelBbox.width * pxToMmX,
                height: dragStartPanelBbox.height * pxToMmY
            };
        } else {
            dragStartPanelBbox = null;
            panelBboxOffset = null;
        }

        // Create overlay if it doesn't exist
        if (!panelDragOverlay) {
            console.log('[PanelDrag] Creating overlay on-demand');
            const zoomContainer = document.getElementById('zoom-container');
            if (zoomContainer) {
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
                zoomContainer.appendChild(panelDragOverlay);
                console.log('[PanelDrag] Overlay created on-demand');
            }
        }

        // Show drag overlay (axis bbox)
        if (panelDragOverlay) {
            updateDragOverlayMm(pos, rect);
            panelDragOverlay.style.display = 'block';
            console.log('[PanelDrag] Axis overlay shown');
        } else {
            console.warn('[PanelDrag] Overlay still null after creation attempt');
        }

        // Show panel bbox overlay (outer bounds) - follows snapped axis position
        if (panelBboxDragOverlay && panelBboxOffset) {
            updatePanelBboxDragOverlayMm(pos, rect);
            panelBboxDragOverlay.style.display = 'block';
            console.log('[PanelDrag] Panel bbox overlay shown');
        }

        // Create and show panel snapshot for visual feedback
        if (typeof startSnapshotDrag === 'function') {
            startSnapshotDrag(panelIndex, rect, pos);
        }

        // Change cursor
        document.body.style.cursor = 'move';

        console.log('Started dragging panel', panelIndex);
    }
}

// Find which panel contains the given position (in mm, upper-left origin)
// Uses expanded bounds to include title, labels, and tick areas
function findPanelAtPositionMm(mmX, mmY) {
    const axKeys = Object.keys(panelPositions).sort();

    // Margins in mm to expand panel bounds for labels/title/ticks
    const marginLeft = 15;   // Space for y-axis label and ticks
    const marginRight = 5;   // Small buffer on right
    const marginTop = 8;     // Space for title
    const marginBottom = 12; // Space for x-axis label and ticks

    for (let i = 0; i < axKeys.length; i++) {
        const pos = panelPositions[axKeys[i]];

        // Expanded bounds including label/title areas
        const expandedLeft = Math.max(0, pos.left - marginLeft);
        const expandedTop = Math.max(0, pos.top - marginTop);
        const expandedRight = Math.min(figSize.width_mm, pos.left + pos.width + marginRight);
        const expandedBottom = Math.min(figSize.height_mm, pos.top + pos.height + marginBottom);

        // Check if point is within expanded panel bounds
        if (mmX >= expandedLeft && mmX <= expandedRight &&
            mmY >= expandedTop && mmY <= expandedBottom) {
            return i;
        }
    }
    return null;
}

// Handle mouse hover over panels - show visual feedback
function handlePanelHover(event) {
    // Skip if dragging
    if (isDraggingPanel) {
        hidePanelHover();
        return;
    }

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    const rect = img.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if mouse is within image bounds
    if (x < 0 || x > rect.width || y < 0 || y > rect.height) {
        hidePanelHover();
        return;
    }

    // Convert to mm coordinates
    const mmX = (x / rect.width) * figSize.width_mm;
    const mmY = (y / rect.height) * figSize.height_mm;

    // Find panel at position
    const panelIndex = findPanelAtPositionMm(mmX, mmY);

    if (panelIndex !== null && panelIndex !== hoveredPanelIndex) {
        showPanelHover(panelIndex, rect);
    } else if (panelIndex === null) {
        hidePanelHover();
    }
}

// Show hover feedback for a panel
// Uses natural image dimensions since overlay is inside zoom-container (CSS-transformed)
function showPanelHover(panelIndex, imgRect) {
    if (!panelHoverOverlay) return;

    hoveredPanelIndex = panelIndex;

    // Get panel position
    const axKey = Object.keys(panelPositions).sort()[panelIndex];
    const pos = panelPositions[axKey];
    if (!pos) return;

    // Use natural (unscaled) dimensions - overlays are in container's local coordinate space
    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth) return;
    const scaleX = img.naturalWidth / figSize.width_mm;
    const scaleY = img.naturalHeight / figSize.height_mm;

    const left = pos.left * scaleX;
    const top = pos.top * scaleY;
    const width = pos.width * scaleX;
    const height = pos.height * scaleY;

    panelHoverOverlay.style.left = `${left}px`;
    panelHoverOverlay.style.top = `${top}px`;
    panelHoverOverlay.style.width = `${width}px`;
    panelHoverOverlay.style.height = `${height}px`;
    panelHoverOverlay.style.display = 'block';

    // Change cursor to indicate draggable
    document.body.style.cursor = 'move';
}

// Hide hover feedback
function hidePanelHover() {
    if (panelHoverOverlay) {
        panelHoverOverlay.style.display = 'none';
    }
    hoveredPanelIndex = null;

    // Reset cursor if not dragging
    if (!isDraggingPanel) {
        document.body.style.cursor = '';
    }
}

// Handle mouse move during drag
function handlePanelDragMove(event) {
    if (!isDraggingPanel) return;

    event.preventDefault();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();

    // Calculate delta in mm
    const deltaMmX = (event.clientX - dragStartPos.x) / rect.width * figSize.width_mm;
    const deltaMmY = (event.clientY - dragStartPos.y) / rect.height * figSize.height_mm;

    // Calculate raw new position (clamped to figure bounds)
    let newLeft = Math.max(0, Math.min(figSize.width_mm - dragStartPanelPos.width, dragStartPanelPos.left + deltaMmX));
    let newTop = Math.max(0, Math.min(figSize.height_mm - dragStartPanelPos.height, dragStartPanelPos.top + deltaMmY));

    // Apply snapping (Alt key disables snapping for fine control)
    let snapResult = { pos: { left: newLeft, top: newTop }, guides: [] };
    if (typeof applySnapping === 'function' && !event.altKey) {
        snapResult = applySnapping(newLeft, newTop, dragStartPanelPos.width, dragStartPanelPos.height, draggedPanelIndex);
        newLeft = snapResult.pos.left;
        newTop = snapResult.pos.top;
    }

    const newPos = {
        left: newLeft,
        top: newTop,
        width: dragStartPanelPos.width,
        height: dragStartPanelPos.height
    };

    // Update visual overlays - both use snapped position in mm
    updateDragOverlayMm(newPos, rect);
    updatePanelBboxDragOverlayMm(newPos, rect);

    // Update snapshot position
    if (typeof updateSnapshotPosition === 'function') {
        updateSnapshotPosition(newPos, rect);
    }

    // Show/hide alignment guides
    if (typeof showSnapGuides === 'function') {
        showSnapGuides(snapResult.guides, rect);
    }
}

// Update axis drag overlay (mm to local container pixels)
// Uses natural image dimensions since overlay is inside zoom-container (CSS-transformed)
function updateDragOverlayMm(pos, imgRect) {
    if (!panelDragOverlay || !figSize.width_mm) return;
    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth) return;
    // Use natural (unscaled) dimensions - overlays are in container's local coordinate space
    const scaleX = img.naturalWidth / figSize.width_mm;
    const scaleY = img.naturalHeight / figSize.height_mm;
    panelDragOverlay.style.left = `${pos.left * scaleX}px`;
    panelDragOverlay.style.top = `${pos.top * scaleY}px`;
    panelDragOverlay.style.width = `${pos.width * scaleX}px`;
    panelDragOverlay.style.height = `${pos.height * scaleY}px`;
}

// Update panel bbox overlay based on snapped axis position (in mm)
// Uses natural image dimensions since overlay is inside zoom-container (CSS-transformed)
function updatePanelBboxDragOverlayMm(axisPos, imgRect) {
    if (!panelBboxDragOverlay || !panelBboxOffset || !figSize.width_mm) return;
    const img = document.getElementById('preview-image');
    if (!img || !img.naturalWidth) return;
    // Use natural (unscaled) dimensions - overlays are in container's local coordinate space
    const scaleX = img.naturalWidth / figSize.width_mm;
    const scaleY = img.naturalHeight / figSize.height_mm;
    // Panel bbox position = axis position + offset (both in mm, converted to local container pixels)
    panelBboxDragOverlay.style.left = `${(axisPos.left + panelBboxOffset.left) * scaleX}px`;
    panelBboxDragOverlay.style.top = `${(axisPos.top + panelBboxOffset.top) * scaleY}px`;
    panelBboxDragOverlay.style.width = `${panelBboxOffset.width * scaleX}px`;
    panelBboxDragOverlay.style.height = `${panelBboxOffset.height * scaleY}px`;
}

// Handle mouse up - complete the drag
async function handlePanelDragEnd(event) {
    console.log('[PanelDrag] handlePanelDragEnd called, isDraggingPanel:', isDraggingPanel);
    if (!isDraggingPanel) return;

    // Hide overlays, snapshot, and snap guides
    if (panelDragOverlay) panelDragOverlay.style.display = 'none';
    if (panelBboxDragOverlay) panelBboxDragOverlay.style.display = 'none';
    if (typeof endSnapshotDrag === 'function') endSnapshotDrag();
    if (typeof hideSnapGuides === 'function') hideSnapGuides();
    document.body.style.cursor = '';
    dragStartPanelBbox = null;
    panelBboxOffset = null;

    const img = document.getElementById('preview-image');
    if (!img) {
        isDraggingPanel = false;
        return;
    }

    const rect = img.getBoundingClientRect();

    // Calculate final position in mm
    const deltaMmX = (event.clientX - dragStartPos.x) / rect.width * figSize.width_mm;
    const deltaMmY = (event.clientY - dragStartPos.y) / rect.height * figSize.height_mm;

    let newLeft = Math.max(0, Math.min(figSize.width_mm - dragStartPanelPos.width, dragStartPanelPos.left + deltaMmX));
    let newTop = Math.max(0, Math.min(figSize.height_mm - dragStartPanelPos.height, dragStartPanelPos.top + deltaMmY));

    // Apply snapping to final position (unless Alt was held)
    if (typeof applySnapping === 'function' && !event.altKey) {
        const snapResult = applySnapping(newLeft, newTop, dragStartPanelPos.width, dragStartPanelPos.height, draggedPanelIndex);
        newLeft = snapResult.pos.left;
        newTop = snapResult.pos.top;
    }

    // Only update if position actually changed (threshold in mm)
    const threshold = 1.0;  // 1mm threshold
    const deltaLeft = Math.abs(newLeft - dragStartPanelPos.left);
    const deltaTop = Math.abs(newTop - dragStartPanelPos.top);
    console.log('[PanelDrag] Delta: left=', deltaLeft.toFixed(2), 'top=', deltaTop.toFixed(2), 'threshold=', threshold);

    if (deltaLeft > threshold || deltaTop > threshold) {
        console.log('[PanelDrag] Applying new position:', newLeft.toFixed(2), newTop.toFixed(2));
        // Apply the new position (in mm)
        await applyDraggedPanelPosition(
            draggedPanelIndex,
            newLeft,
            newTop,
            dragStartPanelPos.width,
            dragStartPanelPos.height
        );
    } else {
        console.log('[PanelDrag] Movement below threshold, not updating');
    }

    // Reset state
    isDraggingPanel = false;
    draggedPanelIndex = null;
    dragStartPos = null;
    dragStartPanelPos = null;
    console.log('[PanelDrag] Drag state reset');
}

// Apply the dragged panel position to the server (values in mm)
async function applyDraggedPanelPosition(axIndex, left, top, width, height) {
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

            // Update bboxes and hitmap
            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Reload positions (now with correct image dimensions)
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
