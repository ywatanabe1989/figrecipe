#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hit region drawing JavaScript for the figure editor."""

SCRIPTS_HITMAP_REGIONS = """
// ===== HIT REGION DRAWING =====

// Draw hit region shapes from bboxes (polylines for lines, rectangles for others)
function drawHitRegions() {
    const overlay = document.getElementById('hitregion-overlay');
    overlay.innerHTML = '';

    // Context menu on overlay (pointer-events: auto captures right-clicks)
    if (!overlay._ctxInit) {
        overlay.addEventListener('contextmenu', (e) => { if (typeof showCanvasContextMenu === 'function') showCanvasContextMenu(e); });
        overlay._ctxInit = true;
    }

    const img = document.getElementById('preview-image');
    if (!img.naturalWidth || !img.naturalHeight) { console.log('Image not loaded yet'); return; }

    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // Use scale=1.0 since SVG coordinates match bbox coordinates (both in natural image pixels)
    const offsetX = 0;
    const offsetY = 0;
    const scaleX = 1.0;
    const scaleY = 1.0;

    console.log('Drawing hit regions:', Object.keys(currentBboxes).length, 'elements');

    // Draw panel hit regions FIRST (lowest z-order) to catch empty space clicks
    const panelBboxes = currentBboxes?._meta?.panel_bboxes;
    if (panelBboxes) { for (const [axIdx, pb] of Object.entries(panelBboxes)) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', pb.x); rect.setAttribute('y', pb.y);
        rect.setAttribute('width', pb.width); rect.setAttribute('height', pb.height);
        rect.setAttribute('class', 'hitregion-rect panel-region'); rect.setAttribute('data-key', `ax${axIdx}_axes`);
        rect.addEventListener('click', (e) => { e.stopPropagation();
            const el = { key: `ax${axIdx}_axes`, type: 'panel', label: `Panel ${axIdx}`, ax_index: parseInt(axIdx), ...pb };
            if (e.ctrlKey || e.metaKey) { if (typeof toggleInSelection === 'function') toggleInSelection(el); }
            else { if (typeof clearMultiSelection === 'function') clearMultiSelection(); selectElement(el); }
        });
        rect.addEventListener('mousedown', (e) => { if (e.button === 0 && !e.ctrlKey && !e.metaKey && !e.altKey && typeof handlePanelDragStart === 'function') handlePanelDragStart(e); });
        overlay.appendChild(rect);
    }}
    // Drawing z-order: axes lowest (background), panel_label/text highest (foreground)
    const zOrderPriority = { 'axes': 0, 'fill': 1, 'spine': 2, 'image': 3, 'contour': 3, 'bar': 4, 'pie': 4,
        'quiver': 4, 'line': 5, 'scatter': 6, 'xticks': 7, 'yticks': 7, 'title': 8, 'xlabel': 8, 'ylabel': 8, 'legend': 9, 'panel_label': 10, 'text': 10 };
    // Convert to array, filter, and sort by z-order (axes lowest, panel_label highest)
    const sortedEntries = Object.entries(currentBboxes)
        .filter(([key, bbox]) => key !== '_meta' && bbox && typeof bbox.x !== 'undefined')
        .sort((a, b) => (zOrderPriority[a[1].type] || 5) - (zOrderPriority[b[1].type] || 5));

    // Draw shapes for each bbox (in z-order)
    for (const [key, bbox] of sortedEntries) {
        const colorMapInfo = (colorMap && colorMap[key]) || {};
        const originalColor = colorMapInfo.original_color || bbox.original_color;

        // Create group for shape and label
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'hitregion-group');
        group.setAttribute('data-key', key);

        let shape;
        let labelX, labelY;

        // Use polyline for lines with points, circles for scatter, rectangle for others
        if (bbox.type === 'line' && bbox.points && bbox.points.length > 1) {
            shape = _createPolylineShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY);
            const firstPt = bbox.points[0];
            labelX = offsetX + firstPt[0] * scaleX + 5;
            labelY = offsetY + firstPt[1] * scaleY - 5;
        } else if (bbox.type === 'scatter' && bbox.points && bbox.points.length > 0) {
            shape = _createScatterShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY);
            const firstPt = bbox.points[0];
            labelX = offsetX + firstPt[0] * scaleX + 5;
            labelY = offsetY + firstPt[1] * scaleY - 5;
        } else {
            const result = _createRectShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY);
            shape = result.shape;
            labelX = result.labelX;
            labelY = result.labelY;
        }

        // Add hover and click handlers
        const callId = colorMapInfo.call_id || colorMapInfo.label || bbox.label;
        const enrichedBbox = { ...bbox, original_color: originalColor, call_id: callId };
        shape.addEventListener('mouseenter', () => handleHitRegionHover(key, enrichedBbox));
        shape.addEventListener('mouseleave', () => handleHitRegionLeave());
        shape.addEventListener('click', (e) => handleHitRegionClick(e, key, enrichedBbox));

        // Add mousedown for drag (legend, annotation, or panel)
        shape.addEventListener('mousedown', (e) => {
            if (e.button !== 0 || e.ctrlKey || e.metaKey || e.altKey) return;
            if (bbox.type === 'legend' && typeof startLegendDrag === 'function') { startLegendDrag(e, key); return; }
            if ((bbox.type === 'panel_label' || bbox.type === 'text') && typeof startAnnotationDrag === 'function') { startAnnotationDrag(e, key); return; }
            if (typeof handlePanelDragStart === 'function') handlePanelDragStart(e);
        });

        group.appendChild(shape);

        // Create label
        const elemType = colorMapInfo.type || bbox.type || 'element';
        const elemLabel = colorMapInfo.label || bbox.label || key;
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', labelX);
        label.setAttribute('y', labelY);
        label.setAttribute('class', 'hitregion-label');
        label.textContent = `${elemType}: ${elemLabel}`;
        group.appendChild(label);

        overlay.appendChild(group);
    }
}
"""

__all__ = ["SCRIPTS_HITMAP_REGIONS"]

# EOF
