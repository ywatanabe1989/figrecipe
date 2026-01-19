#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for hitmap operations."""

SCRIPTS_HITMAP_UTILS = """
// ===== HITMAP UTILITIES =====

// Get element at screen position using pixel-perfect hitmap detection
function getElementAtScreenPosition(screenX, screenY) {
    if (!hitmapLoaded) return null;

    const img = document.getElementById('preview-image');
    const rect = img.getBoundingClientRect();

    // Convert screen coords to image coords
    const x = screenX - rect.left;
    const y = screenY - rect.top;

    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;
    const imgX = Math.floor(x * scaleX);
    const imgY = Math.floor(y * scaleY);

    return getElementAtPosition(imgX, imgY);
}

// Get element at image position using hitmap
function getElementAtPosition(imgX, imgY) {
    if (!hitmapLoaded) {
        return null;
    }

    const scaleX = hitmapImg.width / currentImgWidth;
    const scaleY = hitmapImg.height / currentImgHeight;
    const hitmapX = Math.floor(imgX * scaleX);
    const hitmapY = Math.floor(imgY * scaleY);

    try {
        const pixel = hitmapCtx.getImageData(hitmapX, hitmapY, 1, 1).data;
        const [r, g, b, a] = pixel;

        // Skip transparent or background
        if (a < 128) return null;
        if (r === 26 && g === 26 && b === 26) return null;
        if (r === 64 && g === 64 && b === 64) return null;

        // Find element by RGB color
        if (colorMap) {
            for (const [key, info] of Object.entries(colorMap)) {
                if (info.rgb[0] === r && info.rgb[1] === g && info.rgb[2] === b) {
                    return { key, ...info };
                }
            }
        }
    } catch (error) {
        console.error('Hitmap pixel read error:', error);
    }

    // Fallback: check bboxes
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;
        if (imgX >= bbox.x && imgX <= bbox.x + bbox.width &&
            imgY >= bbox.y && imgY <= bbox.y + bbox.height) {
            return { key, ...bbox };
        }
    }

    return null;
}

// Find all elements overlapping at a given screen position
function findOverlappingElements(screenPos) {
    const img = document.getElementById('preview-image');
    const imgRect = img.getBoundingClientRect();
    const imgX = (screenPos.x - imgRect.left) * (img.naturalWidth / imgRect.width);
    const imgY = (screenPos.y - imgRect.top) * (img.naturalHeight / imgRect.height);

    // First, try pixel-perfect detection for the exact clicked pixel
    const pixelElement = getElementAtPosition(Math.floor(imgX), Math.floor(imgY));
    const overlapping = [];
    if (pixelElement) {
        overlapping.push(pixelElement);
    }

    // Also check bboxes for elements that might not have rendered pixels at this exact point
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;
        // Skip if already found via pixel detection
        if (overlapping.find(e => e.key === key)) continue;

        if (imgX >= bbox.x && imgX <= bbox.x + bbox.width && imgY >= bbox.y && imgY <= bbox.y + bbox.height) {
            overlapping.push({ key, ...bbox, ...(colorMap?.[key] || {}) });
        }
        // For lines with points, check proximity
        if (bbox.points?.length > 1) {
            for (const pt of bbox.points) {
                if (Math.hypot(imgX - pt[0], imgY - pt[1]) < 15 && !overlapping.find(e => e.key === key)) {
                    overlapping.push({ key, ...bbox, ...(colorMap?.[key] || {}) }); break;
                }
            }
        }
    }
    // Panel bboxes as fallback - catches empty space within panels
    const panelBboxes = currentBboxes?._meta?.panel_bboxes;
    if (panelBboxes) {
        for (const [axIdx, pb] of Object.entries(panelBboxes)) {
            if (imgX >= pb.x && imgX <= pb.x + pb.width && imgY >= pb.y && imgY <= pb.y + pb.height) {
                const axKey = `ax${axIdx}_axes`;
                if (!overlapping.find(e => e.key === axKey)) {
                    overlapping.push({ key: axKey, type: 'panel', label: `Panel ${axIdx}`, ax_index: parseInt(axIdx), ...pb });
                }
            }
        }
    }
    // Click priority (lower = higher priority). 'panel' lowest - selected only in empty space
    const clickPriority = { 'scatter': 0, 'legend': 1, 'panel_label': 2, 'text': 2, 'title': 3, 'xlabel': 3, 'ylabel': 3,
        'line': 4, 'bar': 5, 'pie': 5, 'hist': 5, 'contour': 6, 'quiver': 6, 'image': 6, 'fill': 7,
        'xticks': 8, 'yticks': 8, 'spine': 9, 'axes': 10, 'panel': 11 };
    overlapping.forEach(e => {
        e._d = Infinity; const bb = currentBboxes[e.key];
        if (bb?.points?.length) { for (const p of bb.points) { const d = Math.hypot(imgX - p[0], imgY - p[1]); if (d < e._d) e._d = d; } }
        else { e._d = Math.hypot(imgX - (e.x + e.width/2), imgY - (e.y + e.height/2)); }
    });
    overlapping.sort((a, b) => { const p = (clickPriority[a.type] ?? 6) - (clickPriority[b.type] ?? 6); return p !== 0 ? p : a._d - b._d; });
    return overlapping;
}

// Update hit regions when image loads or resizes
function updateHitRegions() {
    drawHitRegions();
}
"""

__all__ = ["SCRIPTS_HITMAP_UTILS"]

# EOF
