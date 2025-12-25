#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel snapping JavaScript for the figure editor.

This module contains the JavaScript code for:
- Grid snapping (snap to mm grid)
- Edge alignment (snap to other panel edges)
- Center alignment (snap to other panel centers)
- Visual alignment guides
"""

SCRIPTS_PANEL_SNAP = """
// ===== PANEL SNAPPING =====

// Snapping configuration
const SNAP_CONFIG = {
    enabled: true,
    gridSize: 5,         // mm - snap to 5mm grid
    snapThreshold: 3,    // mm - distance to trigger snap
    showGuides: true     // Show visual alignment guides
};

// Alignment guide elements
let snapGuides = [];

// Initialize snapping UI
function initPanelSnap() {
    console.log('[PanelSnap] initPanelSnap called');
    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) return;

    // Create guide line elements (2 horizontal, 2 vertical for edges/centers)
    for (let i = 0; i < 4; i++) {
        const guide = document.createElement('div');
        guide.className = 'snap-guide';
        guide.style.cssText = `
            position: absolute;
            background: #f59e0b;
            pointer-events: none;
            display: none;
            z-index: 999;
        `;
        zoomContainer.appendChild(guide);
        snapGuides.push(guide);
    }
    console.log('[PanelSnap] Created', snapGuides.length, 'guide elements');
}

// Find snap targets from other panels (excluding the panel being dragged)
function getSnapTargets(excludeIndex) {
    const targets = { h: [], v: [] };  // horizontal and vertical snap lines
    const axKeys = Object.keys(panelPositions).sort();

    for (let i = 0; i < axKeys.length; i++) {
        if (i === excludeIndex) continue;

        const pos = panelPositions[axKeys[i]];
        const left = pos.left;
        const right = pos.left + pos.width;
        const top = pos.top;
        const bottom = pos.top + pos.height;
        const centerX = pos.left + pos.width / 2;
        const centerY = pos.top + pos.height / 2;

        // Vertical lines (for left/right/centerX alignment)
        targets.v.push({ pos: left, type: 'edge-left', panel: i });
        targets.v.push({ pos: right, type: 'edge-right', panel: i });
        targets.v.push({ pos: centerX, type: 'center', panel: i });

        // Horizontal lines (for top/bottom/centerY alignment)
        targets.h.push({ pos: top, type: 'edge-top', panel: i });
        targets.h.push({ pos: bottom, type: 'edge-bottom', panel: i });
        targets.h.push({ pos: centerY, type: 'center', panel: i });
    }

    // Add figure edges and center
    targets.v.push({ pos: 0, type: 'figure-edge', panel: -1 });
    targets.v.push({ pos: figSize.width_mm, type: 'figure-edge', panel: -1 });
    targets.v.push({ pos: figSize.width_mm / 2, type: 'figure-center', panel: -1 });
    targets.h.push({ pos: 0, type: 'figure-edge', panel: -1 });
    targets.h.push({ pos: figSize.height_mm, type: 'figure-edge', panel: -1 });
    targets.h.push({ pos: figSize.height_mm / 2, type: 'figure-center', panel: -1 });

    return targets;
}

// Apply snapping to a position
// Returns { pos: {left, top}, snapped: {h: bool, v: bool}, guides: [...] }
function applySnapping(left, top, width, height, excludeIndex) {
    if (!SNAP_CONFIG.enabled) {
        return { pos: { left, top }, snapped: { h: false, v: false }, guides: [] };
    }

    const result = {
        pos: { left, top },
        snapped: { h: false, v: false },
        guides: []
    };

    // Panel edges and center
    const panelLeft = left;
    const panelRight = left + width;
    const panelCenterX = left + width / 2;
    const panelTop = top;
    const panelBottom = top + height;
    const panelCenterY = top + height / 2;

    const targets = getSnapTargets(excludeIndex);
    const threshold = SNAP_CONFIG.snapThreshold;

    // Find best vertical snap (for X position)
    let bestVSnap = null;
    let bestVDist = threshold + 1;

    for (const target of targets.v) {
        // Check left edge
        const distLeft = Math.abs(panelLeft - target.pos);
        if (distLeft < bestVDist) {
            bestVDist = distLeft;
            bestVSnap = { offset: target.pos - panelLeft, target };
        }
        // Check right edge
        const distRight = Math.abs(panelRight - target.pos);
        if (distRight < bestVDist) {
            bestVDist = distRight;
            bestVSnap = { offset: target.pos - panelRight, target };
        }
        // Check center
        const distCenter = Math.abs(panelCenterX - target.pos);
        if (distCenter < bestVDist) {
            bestVDist = distCenter;
            bestVSnap = { offset: target.pos - panelCenterX, target };
        }
    }

    if (bestVSnap && bestVDist <= threshold) {
        result.pos.left = left + bestVSnap.offset;
        result.snapped.v = true;
        result.guides.push({
            type: 'vertical',
            pos: bestVSnap.target.pos,
            targetType: bestVSnap.target.type
        });
    }

    // Find best horizontal snap (for Y position)
    let bestHSnap = null;
    let bestHDist = threshold + 1;

    for (const target of targets.h) {
        // Check top edge
        const distTop = Math.abs(panelTop - target.pos);
        if (distTop < bestHDist) {
            bestHDist = distTop;
            bestHSnap = { offset: target.pos - panelTop, target };
        }
        // Check bottom edge
        const distBottom = Math.abs(panelBottom - target.pos);
        if (distBottom < bestHDist) {
            bestHDist = distBottom;
            bestHSnap = { offset: target.pos - panelBottom, target };
        }
        // Check center
        const distCenter = Math.abs(panelCenterY - target.pos);
        if (distCenter < bestHDist) {
            bestHDist = distCenter;
            bestHSnap = { offset: target.pos - panelCenterY, target };
        }
    }

    if (bestHSnap && bestHDist <= threshold) {
        result.pos.top = top + bestHSnap.offset;
        result.snapped.h = true;
        result.guides.push({
            type: 'horizontal',
            pos: bestHSnap.target.pos,
            targetType: bestHSnap.target.type
        });
    }

    // Apply grid snapping if no edge/center snap
    if (!result.snapped.v) {
        result.pos.left = snapToGrid(result.pos.left);
    }
    if (!result.snapped.h) {
        result.pos.top = snapToGrid(result.pos.top);
    }

    return result;
}

// Snap value to grid
function snapToGrid(value) {
    const grid = SNAP_CONFIG.gridSize;
    return Math.round(value / grid) * grid;
}

// Show alignment guides
function showSnapGuides(guides, imgRect) {
    if (!SNAP_CONFIG.showGuides) {
        hideSnapGuides();
        return;
    }

    const scaleX = imgRect.width / figSize.width_mm;
    const scaleY = imgRect.height / figSize.height_mm;

    // Hide all guides first
    snapGuides.forEach(g => g.style.display = 'none');

    // Show active guides
    let guideIndex = 0;
    for (const guide of guides) {
        if (guideIndex >= snapGuides.length) break;

        const el = snapGuides[guideIndex];
        if (guide.type === 'vertical') {
            el.style.left = `${guide.pos * scaleX}px`;
            el.style.top = '0';
            el.style.width = '2px';
            el.style.height = `${imgRect.height}px`;
            el.style.background = guide.targetType.includes('center') ? '#8b5cf6' : '#f59e0b';
        } else {
            el.style.left = '0';
            el.style.top = `${guide.pos * scaleY}px`;
            el.style.width = `${imgRect.width}px`;
            el.style.height = '2px';
            el.style.background = guide.targetType.includes('center') ? '#8b5cf6' : '#f59e0b';
        }
        el.style.display = 'block';
        guideIndex++;
    }
}

// Hide all alignment guides
function hideSnapGuides() {
    snapGuides.forEach(g => g.style.display = 'none');
}

// Toggle snapping on/off
function toggleSnapping(enabled) {
    SNAP_CONFIG.enabled = enabled;
    console.log('[PanelSnap] Snapping', enabled ? 'enabled' : 'disabled');
    if (!enabled) hideSnapGuides();
}

// Set grid size
function setSnapGridSize(size) {
    SNAP_CONFIG.gridSize = size;
    console.log('[PanelSnap] Grid size set to', size, 'mm');
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPanelSnap);
"""

__all__ = ["SCRIPTS_PANEL_SNAP"]

# EOF
