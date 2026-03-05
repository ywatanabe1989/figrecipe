#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-selection JavaScript for the figure editor.

This module contains the JavaScript code for:
- Ctrl+Click to add/remove elements from selection
- Managing multiple selected elements
- Drawing multi-selection highlights
"""

SCRIPTS_MULTI_SELECT = """
// ===== MULTI-SELECTION (Ctrl+Click) =====

// Array of selected elements (each element is {key, type, x, y, width, height, ...})
let selectedElements = [];

// Check if multi-select mode is active (Ctrl or Cmd key held)
function isMultiSelectMode(event) {
    return event && (event.ctrlKey || event.metaKey);
}

// Check if an element is currently selected
function isElementSelected(key) {
    return selectedElements.some(el => el.key === key);
}

// Add element to selection (if not already selected)
function addToSelection(element) {
    if (!element || !element.key) return;
    if (isElementSelected(element.key)) return;

    selectedElements.push(element);
    console.log('[MultiSelect] Added to selection:', element.key, '- total:', selectedElements.length);
}

// Remove element from selection
function removeFromSelection(key) {
    const idx = selectedElements.findIndex(el => el.key === key);
    if (idx >= 0) {
        selectedElements.splice(idx, 1);
        console.log('[MultiSelect] Removed from selection:', key, '- total:', selectedElements.length);
    }
}

// Toggle element in selection
function toggleInSelection(element) {
    if (!element || !element.key) return;

    if (isElementSelected(element.key)) {
        removeFromSelection(element.key);
    } else {
        addToSelection(element);
    }
}

// Clear all selections
function clearMultiSelection() {
    selectedElements = [];
    console.log('[MultiSelect] Selection cleared');

    // Clear visual selection
    const selOverlay = document.getElementById('selection-overlay');
    if (selOverlay) {
        const svg = selOverlay.querySelector('svg');
        if (svg) {
            // Remove multi-selection highlights
            svg.querySelectorAll('.multi-select-highlight').forEach(el => el.remove());
        }
    }
}

// Draw multi-selection highlights on the selection overlay
function drawMultiSelection() {
    const selOverlay = document.getElementById('selection-overlay');
    if (!selOverlay) return;

    let svg = selOverlay.querySelector('svg');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;';
        selOverlay.appendChild(svg);
    }

    // Remove existing multi-selection highlights
    svg.querySelectorAll('.multi-select-highlight').forEach(el => el.remove());

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    const imgRect = img.getBoundingClientRect();
    const containerRect = selOverlay.getBoundingClientRect();

    // Update SVG viewBox to match image
    svg.setAttribute('viewBox', `0 0 ${imgRect.width} ${imgRect.height}`);
    svg.style.width = imgRect.width + 'px';
    svg.style.height = imgRect.height + 'px';
    svg.style.left = (imgRect.left - containerRect.left) + 'px';
    svg.style.top = (imgRect.top - containerRect.top) + 'px';

    // Draw highlight for each selected element
    selectedElements.forEach(element => {
        if (!element.x || !element.width) return;

        // Convert from image pixels to display pixels
        const scaleX = imgRect.width / img.naturalWidth;
        const scaleY = imgRect.height / img.naturalHeight;

        const x = element.x * scaleX;
        const y = element.y * scaleY;
        const w = element.width * scaleX;
        const h = element.height * scaleY;

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('class', 'multi-select-highlight');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', w);
        rect.setAttribute('height', h);
        rect.setAttribute('fill', 'rgba(37, 99, 235, 0.15)');
        rect.setAttribute('stroke', '#2563eb');
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('stroke-dasharray', '4,2');
        svg.appendChild(rect);
    });

    console.log('[MultiSelect] Drew selection for', selectedElements.length, 'elements');
}

// Select all elements of a specific type
function selectAllOfType(type) {
    clearMultiSelection();

    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;
        if (!bbox || typeof bbox.x === 'undefined') continue;

        const info = (colorMap && colorMap[key]) || {};
        if (info.type === type || bbox.type === type) {
            addToSelection({ key, ...bbox, ...info });
        }
    }

    drawMultiSelection();
    console.log('[MultiSelect] Selected all', type, 'elements:', selectedElements.length);
}

// Get indices of selected panels (axes)
function getSelectedPanelIndices() {
    return selectedElements
        .filter(el => el.key && el.key.includes('_axes'))
        .map(el => {
            const match = el.key.match(/ax(\\d+)_axes/);
            return match ? parseInt(match[1], 10) : -1;
        })
        .filter(idx => idx >= 0);
}

// Update UI to show multi-selection state
function updateMultiSelectionUI() {
    const countEl = document.getElementById('multi-select-count');
    if (countEl) {
        countEl.textContent = selectedElements.length > 1
            ? `${selectedElements.length} selected`
            : '';
    }
}

// Handle keyboard shortcuts for multi-selection
function handleMultiSelectKeyboard(event) {
    // Ctrl+A: Select all panels
    if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
        // Only if not in an input field
        if (event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
            event.preventDefault();
            selectAllOfType('axes');
        }
    }

    // Escape: Clear selection
    if (event.key === 'Escape') {
        clearMultiSelection();
        drawMultiSelection();
    }
}

// Initialize multi-selection support
function initMultiSelect() {
    console.log('[MultiSelect] Initializing multi-selection support');
    document.addEventListener('keydown', handleMultiSelectKeyboard);
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initMultiSelect);
"""

__all__ = ["SCRIPTS_MULTI_SELECT"]

# EOF
