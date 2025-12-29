#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Region selection (marquee) JavaScript for the figure editor.

This module contains the JavaScript code for:
- Drawing selection rectangle by dragging on the canvas
- Selecting all elements within the rectangle
- Combining with multi-select (Ctrl+drag to add to selection)
"""

SCRIPTS_REGION_SELECT = """
// ===== REGION SELECTION (Marquee/Rectangle Selection) =====

// Region selection state
let isRegionSelecting = false;
let regionSelectStart = null;  // { x, y } in mm
let regionSelectRect = null;   // { x, y, width, height } in mm

// Region selection overlay element
let regionSelectOverlay = null;

// Initialize region selection
function initRegionSelect() {
    console.log('[RegionSelect] Initializing region selection');

    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) return;

    // Create selection rectangle overlay
    regionSelectOverlay = document.createElement('div');
    regionSelectOverlay.id = 'region-select-overlay';
    regionSelectOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #2563eb;
        background: rgba(37, 99, 235, 0.1);
        pointer-events: none;
        display: none;
        z-index: 100;
    `;
    zoomContainer.appendChild(regionSelectOverlay);

    // Add event listeners to zoom container
    zoomContainer.addEventListener('mousedown', handleRegionSelectStart);
    document.addEventListener('mousemove', handleRegionSelectMove);
    document.addEventListener('mouseup', handleRegionSelectEnd);
}

// Handle mousedown to start region selection
function handleRegionSelectStart(event) {
    // Only start region select on left-click
    if (event.button !== 0) return;

    // Skip if clicking on a hit region, label, or other interactive element
    const target = event.target;
    if (target.closest('.hitregion-group') ||
        target.closest('.panel-label-group') ||
        target.closest('.hitregion-polyline') ||
        target.closest('.hitregion-rect') ||
        target.closest('.hitregion-circle')) {
        return;
    }

    // Skip if modifier keys suggest other operations (Alt for cycling)
    if (event.altKey) return;

    // Skip if clicking directly on the preview image (handled by hitmap)
    if (target.id === 'preview-image') return;

    // Check if click is on empty area of zoom container or overlays
    const zoomContainer = document.getElementById('zoom-container');
    const hitOverlay = document.getElementById('hitregion-overlay');
    const selOverlay = document.getElementById('selection-overlay');

    if (target !== zoomContainer && target !== hitOverlay && target !== selOverlay) {
        // Not on container/overlay background - might be clicking on shape
        return;
    }

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    const imgRect = img.getBoundingClientRect();

    // Check if click is within image bounds
    const x = event.clientX - imgRect.left;
    const y = event.clientY - imgRect.top;
    if (x < 0 || x > imgRect.width || y < 0 || y > imgRect.height) return;

    // Start region selection
    event.preventDefault();
    event.stopPropagation();

    isRegionSelecting = true;

    // Convert to mm coordinates
    const mmX = (x / imgRect.width) * figSize.width_mm;
    const mmY = (y / imgRect.height) * figSize.height_mm;

    regionSelectStart = { x: mmX, y: mmY };
    regionSelectRect = { x: mmX, y: mmY, width: 0, height: 0 };

    // Clear selection unless Ctrl is held (add mode)
    if (!isMultiSelectMode(event)) {
        clearMultiSelection();
    }

    // Show overlay
    updateRegionSelectOverlay(imgRect);
    regionSelectOverlay.style.display = 'block';

    console.log('[RegionSelect] Started at', mmX.toFixed(1), mmY.toFixed(1));
}

// Handle mousemove during region selection
function handleRegionSelectMove(event) {
    if (!isRegionSelecting) return;

    event.preventDefault();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const imgRect = img.getBoundingClientRect();

    // Convert current position to mm
    const x = event.clientX - imgRect.left;
    const y = event.clientY - imgRect.top;
    const mmX = Math.max(0, Math.min(figSize.width_mm, (x / imgRect.width) * figSize.width_mm));
    const mmY = Math.max(0, Math.min(figSize.height_mm, (y / imgRect.height) * figSize.height_mm));

    // Update rect (handle negative width/height by using min/max)
    regionSelectRect = {
        x: Math.min(regionSelectStart.x, mmX),
        y: Math.min(regionSelectStart.y, mmY),
        width: Math.abs(mmX - regionSelectStart.x),
        height: Math.abs(mmY - regionSelectStart.y)
    };

    // Update visual overlay
    updateRegionSelectOverlay(imgRect);
}

// Handle mouseup to end region selection
function handleRegionSelectEnd(event) {
    if (!isRegionSelecting) return;

    isRegionSelecting = false;
    regionSelectOverlay.style.display = 'none';

    // Only select if rectangle has meaningful size (> 2mm)
    if (regionSelectRect.width < 2 || regionSelectRect.height < 2) {
        console.log('[RegionSelect] Rectangle too small, ignored');
        regionSelectStart = null;
        regionSelectRect = null;
        return;
    }

    // Select elements within the rectangle
    selectElementsInRegion(regionSelectRect, isMultiSelectMode(event));

    regionSelectStart = null;
    regionSelectRect = null;

    console.log('[RegionSelect] Ended, selected', selectedElements.length, 'elements');
}

// Update the visual selection rectangle overlay
function updateRegionSelectOverlay(imgRect) {
    if (!regionSelectOverlay || !regionSelectRect) return;

    // Convert mm to pixels
    const scaleX = imgRect.width / figSize.width_mm;
    const scaleY = imgRect.height / figSize.height_mm;

    const left = regionSelectRect.x * scaleX;
    const top = regionSelectRect.y * scaleY;
    const width = regionSelectRect.width * scaleX;
    const height = regionSelectRect.height * scaleY;

    regionSelectOverlay.style.left = `${left}px`;
    regionSelectOverlay.style.top = `${top}px`;
    regionSelectOverlay.style.width = `${width}px`;
    regionSelectOverlay.style.height = `${height}px`;
}

// Select all elements whose bounding boxes intersect with the selection rectangle
function selectElementsInRegion(rectMm, addToExisting) {
    if (!addToExisting) {
        clearMultiSelection();
    }

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    // Convert selection rect from mm to image pixels for bbox comparison
    const scaleX = img.naturalWidth / figSize.width_mm;
    const scaleY = img.naturalHeight / figSize.height_mm;

    const selRect = {
        x: rectMm.x * scaleX,
        y: rectMm.y * scaleY,
        width: rectMm.width * scaleX,
        height: rectMm.height * scaleY
    };

    // Check each element's bbox for intersection
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;
        if (!bbox || typeof bbox.x === 'undefined') continue;

        // Check intersection between selection rect and element bbox
        if (rectsIntersect(selRect, bbox)) {
            const info = (colorMap && colorMap[key]) || {};
            addToSelection({ key, ...bbox, ...info });
        }

        // Also check line/scatter points
        if ((bbox.type === 'line' || bbox.type === 'scatter') && bbox.points) {
            const hasPointInRegion = bbox.points.some(pt =>
                pt[0] >= selRect.x && pt[0] <= selRect.x + selRect.width &&
                pt[1] >= selRect.y && pt[1] <= selRect.y + selRect.height
            );
            if (hasPointInRegion && !isElementSelected(key)) {
                const info = (colorMap && colorMap[key]) || {};
                addToSelection({ key, ...bbox, ...info });
            }
        }
    }

    // Draw selection and update UI
    drawMultiSelection();
    updateMultiSelectionUI();
}

// Check if two rectangles intersect
function rectsIntersect(rect1, rect2) {
    return !(rect1.x + rect1.width < rect2.x ||
             rect2.x + rect2.width < rect1.x ||
             rect1.y + rect1.height < rect2.y ||
             rect2.y + rect2.height < rect1.y);
}

// Check if a point is inside a rectangle
function pointInRect(px, py, rect) {
    return px >= rect.x && px <= rect.x + rect.width &&
           py >= rect.y && py <= rect.y + rect.height;
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initRegionSelect);
"""

__all__ = ["SCRIPTS_REGION_SELECT"]

# EOF
