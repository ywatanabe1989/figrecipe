#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event handlers for hitmap interactions."""

SCRIPTS_HITMAP_HANDLERS = """
// ===== EVENT HANDLERS =====

// Handle hover on hit region
function handleHitRegionHover(key, bbox) {
    const colorMapInfo = (colorMap && colorMap[key]) || {};
    hoveredElement = { key, ...bbox, ...colorMapInfo };

    const callId = colorMapInfo.call_id;
    if (callId) {
        const groupElements = findGroupElements(callId);
        if (groupElements.length > 1) {
            highlightGroupElements(groupElements.map(e => e.key));
        }
    }
}

function highlightGroupElements(keys) {
    keys.forEach(key => { const el = document.querySelector(`[data-key="${key}"]`); if (el) el.classList.add('group-hovered'); });
}

function handleHitRegionLeave() {
    hoveredElement = null;
    document.querySelectorAll('.group-hovered').forEach(el => el.classList.remove('group-hovered'));
}

// Handle click on hit region with Alt+Click cycling support
// Uses pixel-perfect hitmap detection for accurate element selection
function handleHitRegionClick(event, key, bbox) {
    // Skip if dragging a panel (isDraggingPanel defined in _panel_drag.py)
    if (typeof isDraggingPanel !== 'undefined' && isDraggingPanel) return;

    event.stopPropagation();
    event.preventDefault();

    // Try pixel-perfect hitmap detection first
    const pixelElement = getElementAtScreenPosition(event.clientX, event.clientY);
    const colorMapInfo = (colorMap && colorMap[key]) || {};
    const bboxElement = { key, ...bbox, ...colorMapInfo };
    // Use pixel-detected element if available, otherwise fall back to bbox
    const element = pixelElement || bboxElement;

    if (event.ctrlKey || event.metaKey) {
        // Ctrl+Click: toggle multi-selection
        if (typeof toggleInSelection === 'function') {
            toggleInSelection(element);
            if (typeof drawMultiSelection === 'function') drawMultiSelection();
        } else { selectElement(element); }
    } else if (event.altKey) {
        // Alt+Click: cycle through overlapping elements
        const clickPos = { x: event.clientX, y: event.clientY };
        const samePosition = lastClickPosition && Math.abs(lastClickPosition.x - clickPos.x) < 5 && Math.abs(lastClickPosition.y - clickPos.y) < 5;
        if (samePosition && overlappingElements.length > 1) {
            cycleIndex = (cycleIndex + 1) % overlappingElements.length;
            selectElement(overlappingElements[cycleIndex]);
        } else {
            overlappingElements = findOverlappingElements(clickPos);
            cycleIndex = 0; lastClickPosition = clickPos;
            selectElement(overlappingElements.length > 0 ? overlappingElements[0] : element);
        }
    } else {
        // Normal click: clear multi-selection, use priority-based selection
        if (typeof clearMultiSelection === 'function') clearMultiSelection();
        const overlapping = findOverlappingElements({ x: event.clientX, y: event.clientY });
        selectElement(overlapping.length > 0 ? overlapping[0] : element);
        lastClickPosition = null; overlappingElements = []; cycleIndex = 0;
    }
}

// Handle click on preview image
function handlePreviewClick(event) {
    const img = event.target;
    const rect = img.getBoundingClientRect();

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;
    const imgX = Math.floor(x * scaleX);
    const imgY = Math.floor(y * scaleY);

    const element = getElementAtPosition(imgX, imgY);

    if (element) {
        selectElement(element);
    } else {
        clearSelection();
    }
}
"""

__all__ = ["SCRIPTS_HITMAP_HANDLERS"]

# EOF
