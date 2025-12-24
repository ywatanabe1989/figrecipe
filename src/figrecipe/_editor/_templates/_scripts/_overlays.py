#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ruler, grid, and column overlay JavaScript for the figure editor."""

SCRIPTS_OVERLAYS = """
// ============================================
// MEASUREMENT OVERLAYS (Ruler, Grid, Columns)
// ============================================

// State for overlays
let rulerVisible = false;
let gridVisible = false;
let columnsVisible = false;

// Get figure DPI from server (default 300 for preview at 150)
// Preview DPI is 150, which is half of output DPI
const PREVIEW_DPI = 150;
const MM_PER_INCH = 25.4;

// Pixels per mm at preview resolution
function getPxPerMm() {
    return PREVIEW_DPI / MM_PER_INCH;
}

// Unified ruler & grid state
let rulerGridVisible = false;

// Initialize overlay controls (single toggle button)
function initializeOverlayControls() {
    const btn = document.getElementById('btn-ruler-grid');
    if (btn) {
        btn.addEventListener('click', toggleRulerGrid);
    }
}

// Toggle all ruler/grid overlays together
function toggleRulerGrid() {
    rulerGridVisible = !rulerGridVisible;

    // Sync all three visibility states
    rulerVisible = rulerGridVisible;
    gridVisible = rulerGridVisible;
    columnsVisible = rulerGridVisible;

    // Update overlays
    const rulerOverlay = document.getElementById('ruler-overlay');
    const gridOverlay = document.getElementById('grid-overlay');
    const columnOverlay = document.getElementById('column-overlay');

    if (rulerOverlay) rulerOverlay.classList.toggle('visible', rulerGridVisible);
    if (gridOverlay) gridOverlay.classList.toggle('visible', rulerGridVisible);
    if (columnOverlay) columnOverlay.classList.toggle('visible', rulerGridVisible);

    // Draw overlays if visible
    if (rulerGridVisible) {
        drawRuler();
        drawGrid();
        drawColumnGuides();
    }

    // Update button state
    const btn = document.getElementById('btn-ruler-grid');
    if (btn) {
        btn.classList.toggle('active', rulerGridVisible);
    }
}

// Legacy functions for backward compatibility
function toggleRuler() { toggleRulerGrid(); }
function toggleGrid() { toggleRulerGrid(); }
function toggleColumns() { toggleRulerGrid(); }

// Draw ruler overlay (top and left edges)
function drawRuler() {
    const overlay = document.getElementById('ruler-overlay');
    const img = document.getElementById('preview-image');
    if (!overlay || !img) return;

    // Clear existing
    overlay.innerHTML = '';

    const imgWidth = img.naturalWidth || img.width;
    const imgHeight = img.naturalHeight || img.height;
    const pxPerMm = getPxPerMm();

    // Set SVG size
    overlay.setAttribute('viewBox', `0 0 ${imgWidth} ${imgHeight}`);
    overlay.style.width = imgWidth + 'px';
    overlay.style.height = imgHeight + 'px';

    const rulerThickness = 15;  // pixels

    // Background for horizontal ruler (top)
    const hBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    hBg.setAttribute('x', 0);
    hBg.setAttribute('y', 0);
    hBg.setAttribute('width', imgWidth);
    hBg.setAttribute('height', rulerThickness);
    hBg.setAttribute('class', 'ruler-bg');
    overlay.appendChild(hBg);

    // Background for vertical ruler (left)
    const vBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    vBg.setAttribute('x', 0);
    vBg.setAttribute('y', 0);
    vBg.setAttribute('width', rulerThickness);
    vBg.setAttribute('height', imgHeight);
    vBg.setAttribute('class', 'ruler-bg');
    overlay.appendChild(vBg);

    const widthMm = imgWidth / pxPerMm;
    const heightMm = imgHeight / pxPerMm;

    // Draw horizontal ruler ticks (every 1mm, labels every 5mm)
    for (let mm = 0; mm <= widthMm; mm++) {
        const x = mm * pxPerMm;
        const isMajor = mm % 5 === 0;
        const tickLen = isMajor ? 10 : 5;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', 0);
        line.setAttribute('x2', x);
        line.setAttribute('y2', tickLen);
        line.setAttribute('class', isMajor ? 'ruler-line-major' : 'ruler-line');
        overlay.appendChild(line);

        // Label every 10mm
        if (mm % 10 === 0 && mm > 0) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', 13);
            text.setAttribute('class', 'ruler-text');
            text.setAttribute('text-anchor', 'middle');
            text.textContent = mm.toString();
            overlay.appendChild(text);
        }
    }

    // Draw vertical ruler ticks (every 1mm, labels every 5mm)
    for (let mm = 0; mm <= heightMm; mm++) {
        const y = mm * pxPerMm;
        const isMajor = mm % 5 === 0;
        const tickLen = isMajor ? 10 : 5;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', 0);
        line.setAttribute('y1', y);
        line.setAttribute('x2', tickLen);
        line.setAttribute('y2', y);
        line.setAttribute('class', isMajor ? 'ruler-line-major' : 'ruler-line');
        overlay.appendChild(line);

        // Label every 10mm
        if (mm % 10 === 0 && mm > 0) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', 2);
            text.setAttribute('y', y + 3);
            text.setAttribute('class', 'ruler-text');
            text.setAttribute('text-anchor', 'start');
            text.setAttribute('transform', `rotate(-90, 2, ${y})`);
            text.textContent = mm.toString();
            overlay.appendChild(text);
        }
    }
}

// Draw grid overlay (1mm and 5mm intervals)
function drawGrid() {
    const overlay = document.getElementById('grid-overlay');
    const img = document.getElementById('preview-image');
    if (!overlay || !img) return;

    // Clear existing
    overlay.innerHTML = '';

    const imgWidth = img.naturalWidth || img.width;
    const imgHeight = img.naturalHeight || img.height;
    const pxPerMm = getPxPerMm();

    // Set SVG size
    overlay.setAttribute('viewBox', `0 0 ${imgWidth} ${imgHeight}`);
    overlay.style.width = imgWidth + 'px';
    overlay.style.height = imgHeight + 'px';

    const widthMm = imgWidth / pxPerMm;
    const heightMm = imgHeight / pxPerMm;

    // Draw vertical lines (every 1mm)
    for (let mm = 0; mm <= widthMm; mm++) {
        const x = mm * pxPerMm;
        const is5mm = mm % 5 === 0;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', 0);
        line.setAttribute('x2', x);
        line.setAttribute('y2', imgHeight);
        line.setAttribute('class', is5mm ? 'grid-line-5mm' : 'grid-line-1mm');
        overlay.appendChild(line);
    }

    // Draw horizontal lines (every 1mm)
    for (let mm = 0; mm <= heightMm; mm++) {
        const y = mm * pxPerMm;
        const is5mm = mm % 5 === 0;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', 0);
        line.setAttribute('y1', y);
        line.setAttribute('x2', imgWidth);
        line.setAttribute('y2', y);
        line.setAttribute('class', is5mm ? 'grid-line-5mm' : 'grid-line-1mm');
        overlay.appendChild(line);
    }
}

// Draw column guide lines (45mm intervals: 0, 45, 90, 135, 180mm)
function drawColumnGuides() {
    const overlay = document.getElementById('column-overlay');
    const img = document.getElementById('preview-image');
    if (!overlay || !img) return;

    // Clear existing
    overlay.innerHTML = '';

    const imgWidth = img.naturalWidth || img.width;
    const imgHeight = img.naturalHeight || img.height;
    const pxPerMm = getPxPerMm();

    // Set SVG size
    overlay.setAttribute('viewBox', `0 0 ${imgWidth} ${imgHeight}`);
    overlay.style.width = imgWidth + 'px';
    overlay.style.height = imgHeight + 'px';

    // Journal column width: 45mm
    // Lines at 0, 45, 90, 135, 180mm for 0, 1, 2, 3, 4 columns
    const columnPositions = [
        { mm: 0, label: '0' },
        { mm: 45, label: '1 col' },
        { mm: 90, label: '2 col' },
        { mm: 135, label: '3 col' },
        { mm: 180, label: '4 col' }
    ];

    for (const col of columnPositions) {
        const x = col.mm * pxPerMm;

        // Skip if beyond image width
        if (x > imgWidth) continue;

        // Draw vertical line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', 0);
        line.setAttribute('x2', x);
        line.setAttribute('y2', imgHeight);
        line.setAttribute('class', 'column-line');
        overlay.appendChild(line);

        // Label background
        const labelBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        const labelText = `${col.label} (${col.mm}mm)`;
        const labelWidth = labelText.length * 7 + 8;
        labelBg.setAttribute('x', x + 3);
        labelBg.setAttribute('y', 3);
        labelBg.setAttribute('width', labelWidth);
        labelBg.setAttribute('height', 18);
        labelBg.setAttribute('rx', 3);
        labelBg.setAttribute('class', 'column-bg');
        overlay.appendChild(labelBg);

        // Label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x + 6);
        text.setAttribute('y', 16);
        text.setAttribute('class', 'column-text');
        text.setAttribute('text-anchor', 'start');
        text.textContent = labelText;
        overlay.appendChild(text);
    }
}

// Update all overlays when image changes
function updateOverlays() {
    if (rulerVisible) drawRuler();
    if (gridVisible) drawGrid();
    if (columnsVisible) drawColumnGuides();
}
"""

__all__ = ["SCRIPTS_OVERLAYS"]
