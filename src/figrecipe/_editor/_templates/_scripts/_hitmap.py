#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitmap and selection JavaScript for the figure editor.

This module contains the JavaScript code for:
- Loading and displaying hitmap overlay
- Hit region drawing (SVG shapes for clickable elements)
- Element selection and group selection
- Hover highlighting
- Alt+Click cycling through overlapping elements
"""

SCRIPTS_HITMAP = """
// ===== HITMAP AND SELECTION =====

// Load hitmap data from server
async function loadHitmap() {
    try {
        // Load hitmap and calls data in parallel
        const [hitmapResponse, callsResponse] = await Promise.all([
            fetch('/hitmap'),
            fetch('/calls')
        ]);
        const data = await hitmapResponse.json();
        callsData = await callsResponse.json();

        colorMap = data.color_map;
        console.log('Loaded colorMap:', Object.keys(colorMap));

        // Create canvas for hitmap
        const canvas = document.getElementById('hitmap-canvas');
        hitmapCtx = canvas.getContext('2d', { willReadFrequently: true });

        // Load hitmap image
        hitmapImg = new Image();
        hitmapImg.onload = function() {
            canvas.width = hitmapImg.width;
            canvas.height = hitmapImg.height;
            hitmapCtx.drawImage(hitmapImg, 0, 0);
            hitmapLoaded = true;
            console.log('Hitmap loaded:', hitmapImg.width, 'x', hitmapImg.height);

            // Update overlay image source
            const overlay = document.getElementById('hitmap-overlay');
            if (overlay) {
                overlay.src = hitmapImg.src;
            }
        };
        hitmapImg.src = 'data:image/png;base64,' + data.image;
    } catch (error) {
        console.error('Failed to load hitmap:', error);
    }
}

// Toggle hit regions overlay visibility mode
function toggleHitmapOverlay() {
    hitmapVisible = !hitmapVisible;
    const overlay = document.getElementById('hitregion-overlay');
    const btn = document.getElementById('btn-show-hitmap');

    if (hitmapVisible) {
        // Show all hit regions
        overlay.classList.add('visible');
        overlay.classList.remove('hover-mode');
        btn.classList.add('active');
        btn.textContent = 'Hide Hit Regions';
    } else {
        // Hover-only mode: hit regions visible only on hover
        overlay.classList.remove('visible');
        overlay.classList.add('hover-mode');
        btn.classList.remove('active');
        btn.textContent = 'Show Hit Regions';
    }
    // Always draw hit regions for hover detection
    drawHitRegions();
}

// Draw hit region shapes from bboxes (polylines for lines, rectangles for others)
function drawHitRegions() {
    const overlay = document.getElementById('hitregion-overlay');
    overlay.innerHTML = '';

    const img = document.getElementById('preview-image');

    // Wait for image to load before drawing hit regions
    if (!img.naturalWidth || !img.naturalHeight) {
        console.log('Image not loaded yet, deferring hit regions draw');
        return;
    }

    // Set SVG viewBox to match natural image size
    // CSS transform on zoom-container handles all scaling
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // Use scale=1.0 since SVG coordinates match bbox coordinates (both in natural image pixels)
    const offsetX = 0;
    const offsetY = 0;
    const scaleX = 1.0;
    const scaleY = 1.0;

    console.log('Drawing hit regions:', Object.keys(currentBboxes).length, 'elements');

    // Drawing z-order: background first (lower), foreground last (higher = on top visually)
    const zOrderPriority = { 'axes': 0, 'fill': 1, 'spine': 2, 'image': 3, 'contour': 3,
        'bar': 4, 'pie': 4, 'quiver': 4, 'line': 5, 'scatter': 6, 'xticks': 7, 'yticks': 7,
        'title': 8, 'xlabel': 8, 'ylabel': 8, 'legend': 9 };

    // Convert to array, filter, and sort by z-order
    // Include axes (panels) - they have lowest z-order so drawn first (background)
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

        // Add mousedown for drag (legend or panel)
        shape.addEventListener('mousedown', (e) => {
            if (e.button !== 0 || e.ctrlKey || e.metaKey || e.altKey) return;
            if (bbox.type === 'legend' && typeof startLegendDrag === 'function') { startLegendDrag(e, key); return; }
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

// Helper: Create polyline shape for lines
function _createPolylineShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    const points = bbox.points.map(pt => {
        const x = offsetX + pt[0] * scaleX;
        const y = offsetY + pt[1] * scaleY;
        return `${x},${y}`;
    }).join(' ');

    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    shape.setAttribute('points', points);
    shape.setAttribute('class', 'hitregion-polyline');
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }
    return shape;
}

// Helper: Create scatter circles group
function _createScatterShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    shape.setAttribute('class', 'scatter-group');
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }

    const hitRadius = 5;
    const allCircles = [];

    bbox.points.forEach((pt, idx) => {
        const cx = offsetX + pt[0] * scaleX;
        const cy = offsetY + pt[1] * scaleY;

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', hitRadius);
        circle.setAttribute('class', 'hitregion-circle');
        circle.setAttribute('data-key', key);
        circle.setAttribute('data-point-index', idx);

        allCircles.push(circle);
        shape.appendChild(circle);
    });

    // Add event handlers to scatter group
    shape.addEventListener('mouseenter', () => {
        handleHitRegionHover(key, bbox);
        allCircles.forEach(c => c.classList.add('hovered'));
        shape.classList.add('hovered');
    });
    shape.addEventListener('mouseleave', () => {
        handleHitRegionLeave();
        allCircles.forEach(c => c.classList.remove('hovered'));
        shape.classList.remove('hovered');
    });
    shape.addEventListener('click', (e) => handleHitRegionClick(e, key, bbox));

    return shape;
}

// Helper: Create rectangle shape for other elements
function _createRectShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    let regionClass = 'hitregion-rect';
    if (bbox.type === 'axes') {
        regionClass += ' axes-region';  // Special class for axes - lower z-order
    } else if (bbox.type === 'line' || bbox.type === 'scatter') {
        regionClass += ' line-region';
    } else if (['title', 'xlabel', 'ylabel', 'suptitle', 'supxlabel', 'supylabel'].includes(bbox.type)) {
        regionClass += ' text-region';
    } else if (bbox.type === 'legend') {
        regionClass += ' legend-region';
    } else if (bbox.type === 'xticks' || bbox.type === 'yticks') {
        regionClass += ' tick-region';
    }

    const x = offsetX + bbox.x * scaleX;
    const y = offsetY + bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    shape.setAttribute('x', x);
    shape.setAttribute('y', y);
    shape.setAttribute('width', Math.max(width, 5));
    shape.setAttribute('height', Math.max(height, 5));
    shape.setAttribute('class', regionClass);
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }

    return { shape, labelX: x + 2, labelY: y - 3 };
}

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

// Highlight all elements in a group
function highlightGroupElements(keys) {
    keys.forEach(key => {
        const hitRegion = document.querySelector(`[data-key="${key}"]`);
        if (hitRegion) {
            hitRegion.classList.add('group-hovered');
        }
    });
}

// Handle leaving hit region
function handleHitRegionLeave() {
    hoveredElement = null;
    document.querySelectorAll('.group-hovered').forEach(el => {
        el.classList.remove('group-hovered');
    });
}

// Handle click on hit region with Alt+Click cycling support
function handleHitRegionClick(event, key, bbox) {
    // Skip if dragging a panel (isDraggingPanel defined in _panel_drag.py)
    if (typeof isDraggingPanel !== 'undefined' && isDraggingPanel) return;

    event.stopPropagation();
    event.preventDefault();

    const colorMapInfo = (colorMap && colorMap[key]) || {};
    const element = { key, ...bbox, ...colorMapInfo };

    if (event.altKey) {
        // Alt+Click: cycle through overlapping elements
        const clickPos = { x: event.clientX, y: event.clientY };
        const samePosition = lastClickPosition &&
            Math.abs(lastClickPosition.x - clickPos.x) < 5 &&
            Math.abs(lastClickPosition.y - clickPos.y) < 5;

        if (samePosition && overlappingElements.length > 1) {
            cycleIndex = (cycleIndex + 1) % overlappingElements.length;
            selectElement(overlappingElements[cycleIndex]);
        } else {
            overlappingElements = findOverlappingElements(clickPos);
            cycleIndex = 0;
            lastClickPosition = clickPos;

            if (overlappingElements.length > 0) {
                selectElement(overlappingElements[0]);
            } else {
                selectElement(element);
            }
        }
    } else {
        // Normal click: use priority-based selection (pie > axes, etc.)
        const overlapping = findOverlappingElements({ x: event.clientX, y: event.clientY });
        selectElement(overlapping.length > 0 ? overlapping[0] : element);
        lastClickPosition = null; overlappingElements = []; cycleIndex = 0;
    }
}

// Find all elements overlapping at a given screen position
function findOverlappingElements(screenPos) {
    const img = document.getElementById('preview-image');
    const imgRect = img.getBoundingClientRect();

    const imgX = (screenPos.x - imgRect.left) * (img.naturalWidth / imgRect.width);
    const imgY = (screenPos.y - imgRect.top) * (img.naturalHeight / imgRect.height);

    const overlapping = [];

    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;

        if (imgX >= bbox.x && imgX <= bbox.x + bbox.width &&
            imgY >= bbox.y && imgY <= bbox.y + bbox.height) {
            const info = (colorMap && colorMap[key]) || {};
            overlapping.push({ key, ...bbox, ...info });
        }

        // For lines with points, check proximity
        if (bbox.points && bbox.points.length > 1) {
            for (const pt of bbox.points) {
                const dist = Math.sqrt(Math.pow(imgX - pt[0], 2) + Math.pow(imgY - pt[1], 2));
                if (dist < 15) {
                    if (!overlapping.find(e => e.key === key)) {
                        const info = (colorMap && colorMap[key]) || {};
                        overlapping.push({ key, ...bbox, ...info });
                    }
                    break;
                }
            }
        }
    }

    // Click priority: smaller/precise elements first, large background last (lower = higher priority)
    const clickPriority = { 'scatter': 0, 'legend': 1, 'title': 2, 'xlabel': 2, 'ylabel': 2,
        'line': 3, 'bar': 4, 'pie': 4, 'contour': 5, 'quiver': 5, 'image': 5, 'fill': 6,
        'xticks': 7, 'yticks': 7, 'spine': 8, 'axes': 9 };
    overlapping.sort((a, b) => (clickPriority[a.type] ?? 5) - (clickPriority[b.type] ?? 5));

    return overlapping;
}

// Update hit regions when image loads or resizes
function updateHitRegions() {
    drawHitRegions();
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

// Find all elements belonging to the same logical group
function findGroupElements(callId) {
    if (!callId || !colorMap) return [];

    const groupElements = [];
    for (const [key, info] of Object.entries(colorMap)) {
        if (info.call_id === callId) {
            groupElements.push({ key, ...info });
        }
    }
    return groupElements;
}

// Get representative color for a call_id group
function getGroupRepresentativeColor(callId, fallbackColor) {
    if (!callId || !colorMap) return fallbackColor;

    const groupElements = findGroupElements(callId);
    if (groupElements.length === 0) return fallbackColor;

    const firstColor = groupElements[0].original_color;
    if (!firstColor) return fallbackColor;

    const allSameColor = groupElements.every(el => el.original_color === firstColor);
    return allSameColor ? firstColor : firstColor;
}

// Select an element (and its logical group if applicable)
function selectElement(element) {
    selectedElement = element;

    const callId = element.call_id || element.label;
    const groupElements = findGroupElements(callId);

    selectedElement.groupElements = groupElements.length > 1 ? groupElements : null;

    drawSelection(element.key);
    autoSwitchTab(element.type);
    updateTabHints();
    syncPropertiesToElement(element);
    if (callId && typeof syncDatatableToElement === 'function') syncDatatableToElement(callId);

    // Sync panel position; axes switches tab, image (from imshow) syncs position only (fills panel)
    if (['axes', 'image'].includes(element.type) || element.ax_index !== undefined) {
        const axIndex = element.ax_index !== undefined ? element.ax_index : getPanelIndexFromKey(element.key);
        if (axIndex !== null && typeof selectPanelByIndex === 'function') selectPanelByIndex(axIndex, element.type === 'axes');
    }
}
"""

__all__ = ["SCRIPTS_HITMAP"]

# EOF
