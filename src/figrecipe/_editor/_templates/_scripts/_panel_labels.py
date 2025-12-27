#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel labels JavaScript for the figure editor.

This module contains the JavaScript code for:
- Rendering draggable panel labels (A, B, C...) on the canvas
- Label positioning with snap support
- Saving/loading label positions
"""

SCRIPTS_PANEL_LABELS = """
// ===== PANEL LABELS (A, B, C...) =====

// Label configuration
const LABEL_CONFIG = {
    fontSize: 14,
    fontWeight: 'bold',
    fontFamily: 'Arial, sans-serif',
    offsetX: -2,  // Default offset from panel corner (mm)
    offsetY: -2,
    snapOffsets: [-2, 0, 2, 5],  // Common snap positions (mm)
    snapThreshold: 1.5  // Snap if within this distance (mm)
};

// Label state
let labelsVisible = true;
let labelPositions = {};  // {ax_0: {offsetX, offsetY}, ...}
let draggingLabel = null;
let labelDragStart = null;

// Initialize panel labels
function initPanelLabels() {
    console.log('[PanelLabels] Initializing panel labels');

    // Load saved positions from server
    loadLabelPositions();

    // Create label overlay
    createLabelOverlay();
}

// Create the label overlay SVG
function createLabelOverlay() {
    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) return;

    // Remove existing overlay
    const existing = document.getElementById('panel-labels-overlay');
    if (existing) existing.remove();

    // Create new overlay
    const overlay = document.createElement('div');
    overlay.id = 'panel-labels-overlay';
    overlay.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:50;';

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;overflow:visible;';
    overlay.appendChild(svg);

    zoomContainer.appendChild(overlay);
}

// Draw panel labels on the canvas
function drawPanelLabels() {
    if (!labelsVisible) return;

    const overlay = document.getElementById('panel-labels-overlay');
    if (!overlay) return;

    const svg = overlay.querySelector('svg');
    if (!svg) return;

    // Clear existing labels
    svg.innerHTML = '';

    const img = document.getElementById('preview-image');
    if (!img || !figSize.width_mm || !figSize.height_mm) return;

    const imgRect = img.getBoundingClientRect();
    const containerRect = overlay.parentElement.getBoundingClientRect();

    // Position SVG over the image
    svg.style.left = (imgRect.left - containerRect.left) + 'px';
    svg.style.top = (imgRect.top - containerRect.top) + 'px';
    svg.style.width = imgRect.width + 'px';
    svg.style.height = imgRect.height + 'px';

    // Get axes from bboxes
    const axes = [];
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key.includes('_axes') && bbox) {
            const match = key.match(/ax(\\d+)_axes/);
            if (match) {
                axes.push({ key, index: parseInt(match[1], 10), bbox });
            }
        }
    }

    // Sort by index
    axes.sort((a, b) => a.index - b.index);

    // Scale factors
    const scaleX = imgRect.width / img.naturalWidth;
    const scaleY = imgRect.height / img.naturalHeight;
    const mmToPixelX = imgRect.width / figSize.width_mm;
    const mmToPixelY = imgRect.height / figSize.height_mm;

    // Draw labels
    axes.forEach((ax, i) => {
        const label = String.fromCharCode(65 + i);  // A, B, C...
        const posKey = `ax_${ax.index}`;

        // Get custom position or default
        const pos = labelPositions[posKey] || { offsetX: LABEL_CONFIG.offsetX, offsetY: LABEL_CONFIG.offsetY };

        // Calculate label position (top-left of panel + offset)
        const panelX = ax.bbox.x * scaleX;
        const panelY = ax.bbox.y * scaleY;
        const labelX = panelX + (pos.offsetX * mmToPixelX);
        const labelY = panelY + (pos.offsetY * mmToPixelY);

        // Create label group
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'panel-label-group');
        g.setAttribute('data-panel', posKey);
        g.style.cursor = 'move';
        g.style.pointerEvents = 'all';

        // Create text element
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', labelX);
        text.setAttribute('y', labelY);
        text.setAttribute('font-size', LABEL_CONFIG.fontSize);
        text.setAttribute('font-weight', LABEL_CONFIG.fontWeight);
        text.setAttribute('font-family', LABEL_CONFIG.fontFamily);
        text.setAttribute('fill', '#333');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.textContent = label;

        g.appendChild(text);
        svg.appendChild(g);

        // Add drag handlers
        g.addEventListener('mousedown', (e) => handleLabelDragStart(e, posKey, ax.bbox));
    });

    console.log('[PanelLabels] Drew', axes.length, 'labels');
}

// Handle label drag start
function handleLabelDragStart(event, posKey, panelBbox) {
    event.preventDefault();
    event.stopPropagation();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const imgRect = img.getBoundingClientRect();

    draggingLabel = posKey;
    labelDragStart = {
        mouseX: event.clientX,
        mouseY: event.clientY,
        pos: labelPositions[posKey] || { offsetX: LABEL_CONFIG.offsetX, offsetY: LABEL_CONFIG.offsetY },
        imgRect,
        panelBbox
    };

    document.addEventListener('mousemove', handleLabelDragMove);
    document.addEventListener('mouseup', handleLabelDragEnd);
}

// Handle label drag move
function handleLabelDragMove(event) {
    if (!draggingLabel || !labelDragStart) return;

    const dx = event.clientX - labelDragStart.mouseX;
    const dy = event.clientY - labelDragStart.mouseY;

    // Convert pixel delta to mm
    const mmPerPixelX = figSize.width_mm / labelDragStart.imgRect.width;
    const mmPerPixelY = figSize.height_mm / labelDragStart.imgRect.height;

    let newOffsetX = labelDragStart.pos.offsetX + (dx * mmPerPixelX);
    let newOffsetY = labelDragStart.pos.offsetY + (dy * mmPerPixelY);

    // Apply snapping
    const snapped = applyLabelSnapping(newOffsetX, newOffsetY);
    newOffsetX = snapped.x;
    newOffsetY = snapped.y;

    // Update position
    labelPositions[draggingLabel] = { offsetX: newOffsetX, offsetY: newOffsetY };

    // Redraw labels
    drawPanelLabels();
}

// Handle label drag end
function handleLabelDragEnd(event) {
    if (draggingLabel) {
        // Save positions to server
        saveLabelPositions();
    }

    draggingLabel = null;
    labelDragStart = null;

    document.removeEventListener('mousemove', handleLabelDragMove);
    document.removeEventListener('mouseup', handleLabelDragEnd);
}

// Apply snapping to label position
function applyLabelSnapping(x, y) {
    const snapTo = (val, targets, threshold) => {
        for (const target of targets) {
            if (Math.abs(val - target) < threshold) {
                return target;
            }
        }
        return val;
    };

    return {
        x: snapTo(x, LABEL_CONFIG.snapOffsets, LABEL_CONFIG.snapThreshold),
        y: snapTo(y, LABEL_CONFIG.snapOffsets, LABEL_CONFIG.snapThreshold)
    };
}

// Handle double-click to reset label position
function handleLabelDoubleClick(event, posKey) {
    labelPositions[posKey] = { offsetX: LABEL_CONFIG.offsetX, offsetY: LABEL_CONFIG.offsetY };
    drawPanelLabels();
    saveLabelPositions();
}

// Save label positions to server
function saveLabelPositions() {
    fetch('/api/label-positions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ positions: labelPositions })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            console.log('[PanelLabels] Positions saved');
        }
    })
    .catch(err => console.error('[PanelLabels] Save error:', err));
}

// Load label positions from server
function loadLabelPositions() {
    fetch('/api/label-positions')
    .then(r => r.json())
    .then(data => {
        labelPositions = data.positions || {};
        console.log('[PanelLabels] Loaded positions:', Object.keys(labelPositions).length);
        drawPanelLabels();
    })
    .catch(err => console.error('[PanelLabels] Load error:', err));
}

// Toggle panel labels visibility
function togglePanelLabels() {
    labelsVisible = !labelsVisible;
    const overlay = document.getElementById('panel-labels-overlay');
    if (overlay) {
        overlay.style.display = labelsVisible ? 'block' : 'none';
    }
    console.log('[PanelLabels] Labels visibility:', labelsVisible);
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPanelLabels);

// Redraw labels when figure updates
document.addEventListener('figureUpdated', drawPanelLabels);
"""

__all__ = ["SCRIPTS_PANEL_LABELS"]

# EOF
