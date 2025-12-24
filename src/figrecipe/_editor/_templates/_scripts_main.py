#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript for figure editor.
"""

SCRIPTS = """
// State
let currentBboxes = initialBboxes;
let colorMap = initialColorMap;
let callsData = {};  // Recorded calls with signatures
let selectedElement = null;
let hitmapLoaded = false;
let hitmapCtx = null;
let hitmapImg = null;
let updateTimeout = null;
let currentImgWidth = imgWidth;    // Track current preview dimensions
let currentImgHeight = imgHeight;
let hitmapVisible = true;          // Hitmap overlay visibility (default visible for development)
const UPDATE_DEBOUNCE = 500;  // ms

// Overlapping element cycling state
let lastClickPosition = null;
let overlappingElements = [];
let cycleIndex = 0;
let hoveredElement = null;  // Track currently hovered element for click priority

// View mode: 'all' shows all properties, 'selected' shows only element-specific
let viewMode = 'all';

// Zoom/Pan state
let zoomLevel = 1.0;
const ZOOM_MIN = 0.1;
const ZOOM_MAX = 5.0;
const ZOOM_STEP = 0.25;
let isPanning = false;
let panStartX = 0;
let panStartY = 0;
let scrollStartX = 0;
let scrollStartY = 0;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeValues();
    initializeEventListeners();
    loadHitmap();
    loadLabels();  // Load current axis labels

    // Update hit regions on window resize
    window.addEventListener('resize', updateHitRegions);

    // Update hit regions and overlays when preview image loads
    const previewImg = document.getElementById('preview-image');
    previewImg.addEventListener('load', updateHitRegions);
    previewImg.addEventListener('load', updateOverlays);

    // Initialize hit regions visibility state
    const overlay = document.getElementById('hitregion-overlay');
    const btn = document.getElementById('btn-show-hitmap');

    if (hitmapVisible) {
        if (overlay) overlay.classList.add('visible');
        if (btn) {
            btn.classList.add('active');
            btn.textContent = 'Hide Hit Regions';
        }
    } else {
        // Hover-only mode when hidden
        if (overlay) overlay.classList.add('hover-mode');
    }

    // Always draw hit regions for hover detection
    setTimeout(() => drawHitRegions(), 100);

    // Initialize zoom/pan
    initializeZoomPan();

    // Initialize measurement overlay controls
    initializeOverlayControls();
});

// Theme values are passed from server via initialValues
// These come from the applied theme (SCITEX, MATPLOTLIB, etc.)
// initialValues is populated by the server from the loaded style preset

// Store original theme defaults for comparison
const themeDefaults = {...initialValues};

// Initialize form values and placeholders from applied theme
function initializeValues() {
    // initialValues contains the theme's default values from the server
    // These are the actual values from the applied style preset (not hardcoded)

    for (const [key, value] of Object.entries(initialValues)) {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = Boolean(value);
            } else if (element.type === 'range') {
                element.value = value;
                const valueSpan = document.getElementById(key + '_value');
                if (valueSpan) valueSpan.textContent = value;
            } else {
                // Set the value
                element.value = value;
                // Set placeholder to show theme default (visible when field is cleared)
                if (element.type === 'number' || element.type === 'text') {
                    element.placeholder = value;
                }
            }
        }
    }

    // Log applied theme info
    const styleNameEl = document.getElementById('style-name');
    if (styleNameEl) {
        console.log('Applied theme:', styleNameEl.textContent);
    }
}

// Check if a field value differs from the theme default
function updateModifiedState(element) {
    const key = element.id;
    const defaultValue = themeDefaults[key];
    const formRow = element.closest('.form-row');
    if (!formRow || defaultValue === undefined) return;

    let currentValue;
    if (element.type === 'checkbox') {
        currentValue = element.checked;
    } else if (element.type === 'number') {
        currentValue = parseFloat(element.value);
    } else {
        currentValue = element.value;
    }

    // Compare values (handle type conversion)
    const isModified = String(currentValue) !== String(defaultValue);
    formRow.classList.toggle('value-modified', isModified);
}

// Update all modified states
function updateAllModifiedStates() {
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.id && input.id !== 'dark-mode-toggle') {
            updateModifiedState(input);
        }
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Preview image click for element selection
    const previewImg = document.getElementById('preview-image');
    previewImg.addEventListener('click', handlePreviewClick);

    // SVG overlay click - deselect when clicking on empty area (not on a shape)
    const hitregionOverlay = document.getElementById('hitregion-overlay');
    hitregionOverlay.addEventListener('click', function(event) {
        // Only clear if clicking directly on the SVG (not on a shape inside it)
        if (event.target === hitregionOverlay) {
            clearSelection();
        }
    });

    // Selection overlay click - same behavior
    const selectionOverlay = document.getElementById('selection-overlay');
    selectionOverlay.addEventListener('click', function(event) {
        if (event.target === selectionOverlay) {
            clearSelection();
        }
    });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    darkModeToggle.addEventListener('change', function() {
        document.documentElement.setAttribute('data-theme', this.checked ? 'dark' : 'light');
        scheduleUpdate();
    });

    // Form inputs - auto update on change
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.id === 'dark-mode-toggle') return;

        // Update modified state and trigger preview update
        input.addEventListener('change', function() {
            updateModifiedState(this);
            scheduleUpdate();
        });
        if (input.type === 'number' || input.type === 'text') {
            input.addEventListener('input', function() {
                updateModifiedState(this);
                scheduleUpdate();
            });
        }

        // Range slider value display
        if (input.type === 'range') {
            input.addEventListener('input', function() {
                const valueSpan = document.getElementById(this.id + '_value');
                if (valueSpan) valueSpan.textContent = this.value;
                updateModifiedState(this);
            });
        }
    });

    // Buttons
    document.getElementById('btn-refresh').addEventListener('click', updatePreview);
    document.getElementById('btn-reset').addEventListener('click', resetValues);
    document.getElementById('btn-save').addEventListener('click', saveOverrides);
    document.getElementById('btn-restore').addEventListener('click', restoreOriginal);
    // Hit regions toggle (optional - button may be hidden in production)
    const hitmapBtn = document.getElementById('btn-show-hitmap');
    if (hitmapBtn) hitmapBtn.addEventListener('click', toggleHitmapOverlay);

    // Download dropdown buttons
    initializeDownloadDropdown();

    // Label input handlers
    initializeLabelInputs();

    // View mode toggle buttons (legacy - replaced by tabs)
    const btnAll = document.getElementById('btn-show-all');
    const btnSelected = document.getElementById('btn-show-selected');
    if (btnAll) btnAll.addEventListener('click', () => setViewMode('all'));
    if (btnSelected) btnSelected.addEventListener('click', () => setViewMode('selected'));

    // Tab navigation
    document.getElementById('tab-figure').addEventListener('click', () => switchTab('figure'));
    document.getElementById('tab-axis').addEventListener('click', () => switchTab('axis'));
    document.getElementById('tab-element').addEventListener('click', () => switchTab('element'));

    // Theme modal handlers
    initializeThemeModal();
    initializeShortcutsModal();

    // Check initial override status
    checkOverrideStatus();

    // Check modified states after initial values are set
    setTimeout(updateAllModifiedStates, 100);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Handle keyboard shortcuts
function handleKeyboardShortcuts(event) {
    // Ignore shortcuts when typing in input fields
    const activeElement = document.activeElement;
    const isInputField = activeElement.tagName === 'INPUT' ||
                         activeElement.tagName === 'TEXTAREA' ||
                         activeElement.tagName === 'SELECT';

    // Ctrl+S: Save overrides
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        saveOverrides();
        showToast('Saved!', 'success');
        return;
    }

    // Ctrl+Shift+S: Download PNG
    if (event.ctrlKey && event.shiftKey && event.key === 'S') {
        event.preventDefault();
        downloadFigure('png');
        return;
    }

    // F5 or Ctrl+R: Refresh preview
    if (event.key === 'F5' || (event.ctrlKey && event.key === 'r')) {
        event.preventDefault();
        updatePreview();
        showToast('Refreshed', 'info');
        return;
    }

    // Only handle the following shortcuts if not in an input field
    if (isInputField) return;

    // Escape: Close modals or clear selection
    if (event.key === 'Escape') {
        const shortcutsModal = document.getElementById('shortcuts-modal');
        if (shortcutsModal && shortcutsModal.style.display === 'flex') {
            hideShortcutsModal();
            return;
        }
        clearSelection();
        return;
    }

    // Tab navigation: 1, 2, 3 keys
    if (event.key === '1') {
        switchTab('figure');
        return;
    }
    if (event.key === '2') {
        switchTab('axis');
        return;
    }
    if (event.key === '3') {
        switchTab('element');
        return;
    }

    // R: Reset to theme defaults
    if (event.key === 'r' || event.key === 'R') {
        resetValues();
        showToast('Reset to defaults', 'info');
        return;
    }

    // G: Toggle rulers and grid
    if (event.key === 'g' || event.key === 'G') {
        toggleRulerGrid();
        const state = rulerGridVisible ? 'ON' : 'OFF';
        showToast(`Ruler & Grid: ${state}`, 'info');
        return;
    }

    // ?: Show keyboard shortcuts
    if (event.key === '?') {
        showShortcutsModal();
        return;
    }
}

// Load hitmap for element detection
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

// Load current axis labels from server
async function loadLabels() {
    try {
        const response = await fetch('/get_labels');
        const labels = await response.json();

        // Populate label input fields
        const titleInput = document.getElementById('label_title');
        const xlabelInput = document.getElementById('label_xlabel');
        const ylabelInput = document.getElementById('label_ylabel');
        const suptitleInput = document.getElementById('label_suptitle');

        if (titleInput) titleInput.value = labels.title || '';
        if (xlabelInput) xlabelInput.value = labels.xlabel || '';
        if (ylabelInput) ylabelInput.value = labels.ylabel || '';
        if (suptitleInput) suptitleInput.value = labels.suptitle || '';

        console.log('Loaded labels:', labels);
    } catch (error) {
        console.error('Failed to load labels:', error);
    }
}

// Update axis label on server
async function updateLabel(labelType, text) {
    console.log(`Updating ${labelType} to: "${text}"`);

    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_label', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                label_type: labelType,
                text: text
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            // Update dimensions
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;

            // Redraw hit regions
            updateHitRegions();

            console.log('Label updated successfully');
        } else {
            console.error('Label update failed:', data.error);
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        console.error('Label update failed:', error);
        alert('Update failed: ' + error.message);
    }

    document.body.classList.remove('loading');
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
    // No offset needed since SVG is positioned to match the image
    const offsetX = 0;
    const offsetY = 0;
    const scaleX = 1.0;
    const scaleY = 1.0;

    console.log('Drawing hit regions:', Object.keys(currentBboxes).length, 'elements');
    console.log('Image natural:', img.naturalWidth, 'x', img.naturalHeight);
    console.log('SVG viewBox matches natural size, CSS transform handles zoom');

    // Sort by z-order: background first, foreground last (so foreground is on top)
    // Higher z-order = drawn later = on top = can be clicked first
    const zOrderPriority = {
        'axes': 0,     // Background - lowest priority, drawn first
        'spine': 1,
        'fill': 2,
        'bar': 3,
        'xticks': 4,
        'yticks': 4,
        'line': 5,     // Foreground
        'scatter': 6,
        'title': 7,
        'xlabel': 7,
        'ylabel': 7,
        'legend': 8,   // Topmost - highest priority, drawn last
    };

    // Convert to array, filter, and sort by z-order
    // Skip 'axes' type - users should click on individual elements or spines instead
    const sortedEntries = Object.entries(currentBboxes)
        .filter(([key, bbox]) => key !== '_meta' && bbox && typeof bbox.x !== 'undefined' && bbox.type !== 'axes')
        .sort((a, b) => (zOrderPriority[a[1].type] || 5) - (zOrderPriority[b[1].type] || 5));

    // Draw shapes for each bbox (in z-order)
    for (const [key, bbox] of sortedEntries) {
        // Get original_color from colorMap (bbox doesn't have it)
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
            // Create polyline from points for lines
            const points = bbox.points.map(pt => {
                const x = offsetX + pt[0] * scaleX;
                const y = offsetY + pt[1] * scaleY;
                return `${x},${y}`;
            }).join(' ');

            shape = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            shape.setAttribute('points', points);
            shape.setAttribute('class', 'hitregion-polyline');
            shape.setAttribute('data-key', key);
            // Set element color as CSS custom property for hover effect
            if (originalColor) {
                shape.style.setProperty('--element-color', originalColor);
            }

            // Label position at first point
            const firstPt = bbox.points[0];
            labelX = offsetX + firstPt[0] * scaleX + 5;
            labelY = offsetY + firstPt[1] * scaleY - 5;
        } else if (bbox.type === 'scatter' && bbox.points && bbox.points.length > 0) {
            // Create circles at each scatter point
            shape = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            shape.setAttribute('class', 'scatter-group');
            shape.setAttribute('data-key', key);
            // Set element color as CSS custom property for hover effect
            if (originalColor) {
                shape.style.setProperty('--element-color', originalColor);
            }

            const hitRadius = 5;  // Hit region radius in display pixels
            const allCircles = [];  // Track all circles for group hover effect

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

            // Add event handlers to the scatter group (not individual circles)
            // This ensures all circles highlight together
            shape.addEventListener('mouseenter', () => {
                handleHitRegionHover(key, bbox);
                // Add hovered class to all circles for visual effect
                allCircles.forEach(c => c.classList.add('hovered'));
                shape.classList.add('hovered');
            });
            shape.addEventListener('mouseleave', () => {
                handleHitRegionLeave();
                // Remove hovered class from all circles
                allCircles.forEach(c => c.classList.remove('hovered'));
                shape.classList.remove('hovered');
            });
            shape.addEventListener('click', (e) => handleHitRegionClick(e, key, bbox));

            // Label position at first point
            const firstPt = bbox.points[0];
            labelX = offsetX + firstPt[0] * scaleX + 5;
            labelY = offsetY + firstPt[1] * scaleY - 5;
        } else {
            // Determine region type for styling (rectangles only)
            let regionClass = 'hitregion-rect';
            if (bbox.type === 'line' || bbox.type === 'scatter') {
                regionClass += ' line-region';
            } else if (bbox.type === 'title' || bbox.type === 'xlabel' || bbox.type === 'ylabel' ||
                       bbox.type === 'suptitle' || bbox.type === 'supxlabel' || bbox.type === 'supylabel') {
                regionClass += ' text-region';
            } else if (bbox.type === 'legend') {
                regionClass += ' legend-region';
            } else if (bbox.type === 'xticks' || bbox.type === 'yticks') {
                regionClass += ' tick-region';
            }

            // Create rectangle for other elements
            const x = offsetX + bbox.x * scaleX;
            const y = offsetY + bbox.y * scaleY;
            const width = bbox.width * scaleX;
            const height = bbox.height * scaleY;

            shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            shape.setAttribute('x', x);
            shape.setAttribute('y', y);
            shape.setAttribute('width', Math.max(width, 5));
            shape.setAttribute('height', Math.max(height, 5));
            shape.setAttribute('class', regionClass);
            shape.setAttribute('data-key', key);
            // Set element color as CSS custom property for hover effect
            if (originalColor) {
                shape.style.setProperty('--element-color', originalColor);
            }

            labelX = x + 2;
            labelY = y - 3;
        }

        // Add hover and click handlers (pass colorMapInfo for original_color and call_id)
        const callId = colorMapInfo.call_id || colorMapInfo.label || bbox.label;
        const enrichedBbox = { ...bbox, original_color: originalColor, call_id: callId };
        shape.addEventListener('mouseenter', () => handleHitRegionHover(key, enrichedBbox));
        shape.addEventListener('mouseleave', () => handleHitRegionLeave());
        shape.addEventListener('click', (e) => handleHitRegionClick(e, key, enrichedBbox));

        group.appendChild(shape);

        // Create label - use colorMap type if available (for boxplot, violin detection)
        // colorMapInfo already declared at start of loop
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

    // Also draw colorMap elements (from hitmap)
    // Guard against null/undefined colorMap during initial load
    if (colorMap) {
        for (const [key, info] of Object.entries(colorMap)) {
            // Skip if already in bboxes
            if (currentBboxes[key]) continue;

            // ColorMap entries without bboxes - show as small indicator
            console.log('ColorMap element without bbox:', key, info);
        }
    }
}

// Handle hover on hit region
function handleHitRegionHover(key, bbox) {
    // Merge colorMap info for correct type (boxplot, violin, etc.)
    const colorMapInfo = (colorMap && colorMap[key]) || {};
    hoveredElement = { key, ...bbox, ...colorMapInfo };

    const callId = colorMapInfo.call_id;

    // Check if this element is part of a group and highlight all
    if (callId) {
        const groupElements = findGroupElements(callId);
        if (groupElements.length > 1) {
            highlightGroupElements(groupElements.map(e => e.key));
        }
    }
}

// Highlight all elements in a group (for hover effect)
function highlightGroupElements(keys) {
    // Add hover class to all matching hit regions
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

    // Clear all group hover highlights
    document.querySelectorAll('.group-hovered').forEach(el => {
        el.classList.remove('group-hovered');
    });
}

// Handle click on hit region with Alt+Click cycling support
function handleHitRegionClick(event, key, bbox) {
    event.stopPropagation();
    event.preventDefault();  // Prevent browser default Alt+Click behavior

    // Merge colorMap info (which has correct type like 'boxplot', 'violin')
    // with bbox info (which has geometry)
    const colorMapInfo = (colorMap && colorMap[key]) || {};
    const element = { key, ...bbox, ...colorMapInfo };
    console.log('Hit region click:', key, 'altKey:', event.altKey);

    if (event.altKey) {
        // Alt+Click: cycle through overlapping elements at this position
        const clickPos = { x: event.clientX, y: event.clientY };

        // Check if same position as last click
        const samePosition = lastClickPosition &&
            Math.abs(lastClickPosition.x - clickPos.x) < 5 &&
            Math.abs(lastClickPosition.y - clickPos.y) < 5;

        if (samePosition && overlappingElements.length > 1) {
            // Cycle to next overlapping element
            cycleIndex = (cycleIndex + 1) % overlappingElements.length;
            selectElement(overlappingElements[cycleIndex]);
        } else {
            // Find all overlapping elements at this position
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
        // Normal click: select the hovered element (topmost in z-order)
        selectElement(element);
        // Reset cycling state
        lastClickPosition = null;
        overlappingElements = [];
        cycleIndex = 0;
    }
}

// Find all elements overlapping at a given screen position
function findOverlappingElements(screenPos) {
    const img = document.getElementById('preview-image');
    const imgRect = img.getBoundingClientRect();

    // Convert to image coordinates
    const imgX = (screenPos.x - imgRect.left) * (img.naturalWidth / imgRect.width);
    const imgY = (screenPos.y - imgRect.top) * (img.naturalHeight / imgRect.height);

    const overlapping = [];

    // Check all bboxes for overlap
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;

        // Check if point is inside bbox
        if (imgX >= bbox.x && imgX <= bbox.x + bbox.width &&
            imgY >= bbox.y && imgY <= bbox.y + bbox.height) {
            overlapping.push({ key, ...bbox });
        }

        // For lines with points, check proximity
        if (bbox.points && bbox.points.length > 1) {
            for (const pt of bbox.points) {
                const dist = Math.sqrt(Math.pow(imgX - pt[0], 2) + Math.pow(imgY - pt[1], 2));
                if (dist < 15) {  // 15 pixel tolerance
                    if (!overlapping.find(e => e.key === key)) {
                        overlapping.push({ key, ...bbox });
                    }
                    break;
                }
            }
        }
    }

    // Sort by z-order priority (foreground elements first)
    // Priority: line > scatter > legend > text > ticks > spines > axes
    const priority = { 'line': 0, 'scatter': 1, 'legend': 2, 'title': 3, 'xlabel': 4, 'ylabel': 4,
                       'xticks': 5, 'yticks': 5, 'spine': 6, 'bar': 3, 'fill': 4, 'axes': 7 };
    overlapping.sort((a, b) => (priority[a.type] || 5) - (priority[b.type] || 5));

    return overlapping;
}

// Update hit regions when image loads or resizes
function updateHitRegions() {
    // Always draw hit regions (for hover detection in both modes)
    drawHitRegions();
}

// Handle click on preview image
function handlePreviewClick(event) {
    const img = event.target;
    const rect = img.getBoundingClientRect();

    // Get click position relative to image
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Scale to image coordinates
    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;
    const imgX = Math.floor(x * scaleX);
    const imgY = Math.floor(y * scaleY);

    // Find element at position
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
        console.log('Hitmap not loaded yet');
        return null;
    }

    // Scale to hitmap coordinates (use current dimensions)
    const scaleX = hitmapImg.width / currentImgWidth;
    const scaleY = hitmapImg.height / currentImgHeight;
    const hitmapX = Math.floor(imgX * scaleX);
    const hitmapY = Math.floor(imgY * scaleY);

    console.log(`Click: img(${imgX},${imgY}) -> hitmap(${hitmapX},${hitmapY}), scale(${scaleX.toFixed(2)},${scaleY.toFixed(2)})`);
    console.log(`Hitmap size: ${hitmapImg.width}x${hitmapImg.height}, Current img: ${currentImgWidth}x${currentImgHeight}`);

    // Get pixel color
    try {
        const pixel = hitmapCtx.getImageData(hitmapX, hitmapY, 1, 1).data;
        const [r, g, b, a] = pixel;

        console.log(`Pixel color: rgb(${r},${g},${b}) alpha=${a}`);

        // Skip transparent or background
        if (a < 128) {
            console.log('Skipping: transparent pixel');
            return null;
        }
        if (r === 26 && g === 26 && b === 26) {
            console.log('Skipping: background color');
            return null;
        }
        if (r === 64 && g === 64 && b === 64) {
            console.log('Skipping: axes color');
            return null;
        }

        // Find element by RGB color
        if (colorMap) {
            for (const [key, info] of Object.entries(colorMap)) {
                if (info.rgb[0] === r && info.rgb[1] === g && info.rgb[2] === b) {
                    console.log(`Found element via hitmap: ${key} (${info.type})`);
                    return { key, ...info };
                }
            }
            console.log('No matching element in colorMap for this color');
        }
    } catch (error) {
        console.error('Hitmap pixel read error:', error);
    }

    // Fallback: check bboxes
    console.log('Falling back to bbox detection...');
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === '_meta') continue;
        if (imgX >= bbox.x && imgX <= bbox.x + bbox.width &&
            imgY >= bbox.y && imgY <= bbox.y + bbox.height) {
            console.log(`Found element via bbox: ${key}`);
            return { key, ...bbox };
        }
    }

    console.log('No element found');
    return null;
}

// Find all elements belonging to the same logical group (same call_id)
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
// Returns the common color if all elements have the same color, or fallback
function getGroupRepresentativeColor(callId, fallbackColor) {
    if (!callId || !colorMap) return fallbackColor;

    const groupElements = findGroupElements(callId);
    if (groupElements.length === 0) return fallbackColor;

    // Get first element's color as reference
    const firstColor = groupElements[0].original_color;
    if (!firstColor) return fallbackColor;

    // Check if all elements have the same color
    const allSameColor = groupElements.every(el => el.original_color === firstColor);

    if (allSameColor) {
        return firstColor;
    }

    // Mixed colors - return the first one as representative
    // (this is what the user will see and can change for the whole group)
    return firstColor;
}

// Select an element (and its logical group if applicable)
function selectElement(element) {
    selectedElement = element;

    // Find all elements in the same logical group
    const callId = element.call_id || element.label;  // Fallback to label for backwards compat
    const groupElements = findGroupElements(callId);

    // Store group info for multi-selection rendering
    selectedElement.groupElements = groupElements.length > 1 ? groupElements : null;

    // Draw selection overlay (handles group selection)
    drawSelection(element.key);

    // Auto-switch to appropriate tab based on element type
    autoSwitchTab(element.type);

    // Update tab hints
    updateTabHints();

    // Sync properties panel to show relevant section
    syncPropertiesToElement(element);
}

// Sync properties panel to selected element
function syncPropertiesToElement(element) {
    // In 'selected' mode, skip section management - only show call properties
    if (viewMode === 'selected') {
        // Just show call properties, sections are hidden
        showDynamicCallProperties(element);
        return;
    }

    // Map element types to section IDs (for 'all' mode)
    const sectionMap = {
        'axes': 'section-dimensions',
        'line': 'section-lines',
        'scatter': 'section-markers',
        'bar': 'section-lines',
        'fill': 'section-lines',
        'boxplot': 'section-boxplot',
        'violin': 'section-violin',
        'title': 'section-fonts',
        'xlabel': 'section-fonts',
        'ylabel': 'section-fonts',
        'xticks': 'section-ticks',
        'yticks': 'section-ticks',
        'legend': 'section-legend',
        'spine': 'section-dimensions',
    };

    // Get the relevant section ID
    const sectionId = sectionMap[element.type] || 'section-dimensions';

    // Close all sections and remove highlights (accordion behavior)
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('section-highlighted');
        // Close all sections except Download (which should stay open)
        if (section.id && section.id !== 'section-download') {
            section.removeAttribute('open');
        }
    });

    // Find and highlight the relevant section
    const section = document.getElementById(sectionId);
    if (section) {
        // Open the section
        section.setAttribute('open', '');
        // Add highlight class
        section.classList.add('section-highlighted');
        // Scroll to section with small delay to allow animation
        setTimeout(() => {
            section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 50);
    }

    // Update displayed values for the selected element type
    updateElementProperties(element);
}

// Update property values for selected element
function updateElementProperties(element) {
    // Clear previous field highlights
    document.querySelectorAll('.form-row').forEach(row => {
        row.classList.remove('field-highlighted');
    });

    // Map element types to relevant form field IDs
    const fieldMap = {
        'line': ['lines_trace_mm', 'lines_errorbar_mm', 'lines_errorbar_cap_mm'],
        'scatter': ['markers_size_mm', 'markers_scatter_mm', 'markers_edge_width_mm'],
        'bar': ['lines_trace_mm'],
        'fill': ['lines_trace_mm'],
        'boxplot': ['lines_trace_mm', 'markers_flier_mm', 'boxplot_median_color'],
        'violin': ['lines_trace_mm'],
        'title': ['fonts_title_pt', 'fonts_family'],
        'xlabel': ['fonts_axis_label_pt', 'fonts_family'],
        'ylabel': ['fonts_axis_label_pt', 'fonts_family'],
        'xticks': ['fonts_tick_label_pt', 'ticks_length_mm', 'ticks_thickness_mm', 'ticks_direction'],
        'yticks': ['fonts_tick_label_pt', 'ticks_length_mm', 'ticks_thickness_mm', 'ticks_direction'],
        'legend': ['fonts_legend_pt', 'legend_frameon', 'legend_loc', 'legend_alpha', 'legend_bg', 'legend_edgecolor'],
        'spine': ['axes_thickness_mm'],
        'axes': ['axes_width_mm', 'axes_height_mm', 'axes_thickness_mm', 'margins_left_mm', 'margins_right_mm', 'margins_bottom_mm', 'margins_top_mm'],
    };

    // Get relevant fields for this element type
    const relevantFields = fieldMap[element.type] || [];

    // Highlight relevant form fields
    relevantFields.forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (input) {
            const formRow = input.closest('.form-row');
            if (formRow) {
                formRow.classList.add('field-highlighted');
            }
        }
    });

    console.log('Selected element:', element.type, element.key);
    console.log('Relevant fields:', relevantFields);

    // Apply filtering if in selected mode
    if (viewMode === 'selected') {
        filterPropertiesByElementType(element.type);
    }

    // Show dynamic call properties if element has a call_id
    showDynamicCallProperties(element);
}

// Show dynamic properties based on recorded call
function showDynamicCallProperties(element) {
    const container = document.getElementById('dynamic-call-properties');
    if (!container) return;

    // Clear previous content
    container.innerHTML = '';

    // Get call_id from element (prefer call_id, fallback to label for backwards compat)
    const callId = element.call_id || element.label;
    if (!callId || !callsData[callId]) {
        container.style.display = 'none';
        return;
    }

    const callData = callsData[callId];
    container.style.display = 'block';

    // Create header
    const header = document.createElement('div');
    header.className = 'dynamic-props-header';
    header.innerHTML = `<strong>${callData.function}()</strong> <span class="call-id">${callId}</span>`;
    container.appendChild(header);

    // Get args and kwargs
    const usedArgs = callData.args || [];
    const usedKwargs = { ...callData.kwargs } || {};  // Copy to avoid mutation
    const sigArgs = callData.signature?.args || [];
    const sigKwargs = callData.signature?.kwargs || {};

    // If no color in kwargs, get representative color from call_id group
    // This handles cases where matplotlib auto-assigns colors
    if (!usedKwargs.color && !usedKwargs.c) {
        // Check if signature has a color param
        if ('color' in sigKwargs || 'c' in sigKwargs) {
            // Find color from: 1) element's call_id in colorMap, 2) element's label in colorMap, 3) element's original_color
            // The hitmap's call_id may differ from the recipe's call_id (label)
            const hitmapCallId = element.call_id;
            const groupColor = getGroupRepresentativeColor(hitmapCallId, element.original_color) ||
                               element.original_color;
            if (groupColor) {
                usedKwargs.color = groupColor;
            }
        }
    }

    // Show args (positional arguments) - display only, not editable
    if (usedArgs.length > 0) {
        const argsSection = document.createElement('div');
        argsSection.className = 'dynamic-props-section';
        argsSection.innerHTML = '<div class="dynamic-props-label">Arguments:</div>';

        for (let i = 0; i < usedArgs.length; i++) {
            const arg = usedArgs[i];
            const sigArg = sigArgs[i] || {};
            const row = document.createElement('div');
            row.className = 'form-row dynamic-field arg-field';

            const label = document.createElement('label');
            label.textContent = arg.name;
            if (sigArg.type) {
                label.title = `Type: ${sigArg.type}`;
            }
            if (sigArg.optional) {
                label.textContent += ' (opt)';
            }

            const valueSpan = document.createElement('span');
            valueSpan.className = 'arg-value';
            // Show array shape/type instead of full data
            if (arg.data && Array.isArray(arg.data)) {
                valueSpan.textContent = `[${arg.data.length} items]`;
            } else if (arg.data === '__FILE__') {
                valueSpan.textContent = '[external file]';
            } else {
                valueSpan.textContent = String(arg.data).substring(0, 30);
            }

            row.appendChild(label);
            row.appendChild(valueSpan);
            argsSection.appendChild(row);
        }
        container.appendChild(argsSection);
    }

    // Create form fields for used kwargs
    if (Object.keys(usedKwargs).length > 0) {
        const usedSection = document.createElement('div');
        usedSection.className = 'dynamic-props-section';
        usedSection.innerHTML = '<div class="dynamic-props-label">Used Parameters:</div>';

        for (const [key, value] of Object.entries(usedKwargs)) {
            const field = createDynamicField(callId, key, value, sigKwargs[key]);
            usedSection.appendChild(field);
        }
        container.appendChild(usedSection);
    }

    // Create expandable section for available (unused) params - open by default
    const availableParams = Object.keys(sigKwargs).filter(k => !(k in usedKwargs));
    if (availableParams.length > 0) {
        const availSection = document.createElement('details');
        availSection.className = 'dynamic-props-available';
        availSection.setAttribute('open', '');  // Open by default
        availSection.innerHTML = `<summary>Available Parameters (${availableParams.length})</summary>`;

        const availContent = document.createElement('div');
        availContent.className = 'dynamic-props-section';
        for (const key of availableParams) {  // Show all available parameters
            const sigInfo = sigKwargs[key];
            const field = createDynamicField(callId, key, sigInfo?.default, sigInfo, true);
            availContent.appendChild(field);
        }
        availSection.appendChild(availContent);
        container.appendChild(availSection);
    }
}

// Check if a field is a color field
function isColorField(key, sigInfo) {
    const colorKeywords = ['color', 'facecolor', 'edgecolor', 'markerfacecolor', 'markeredgecolor', 'c'];
    if (colorKeywords.includes(key.toLowerCase())) return true;
    if (sigInfo?.type && sigInfo.type.toLowerCase().includes('color')) return true;
    return false;
}

// Convert color to RGB string for display
function colorToRGB(color) {
    if (!color) return '';
    // Already RGB format
    if (typeof color === 'string' && color.match(/^rgb/i)) return color;
    // Hex format
    if (typeof color === 'string' && color.startsWith('#')) {
        const hex = color.slice(1);
        if (hex.length === 3) {
            const r = parseInt(hex[0] + hex[0], 16);
            const g = parseInt(hex[1] + hex[1], 16);
            const b = parseInt(hex[2] + hex[2], 16);
            return `rgb(${r}, ${g}, ${b})`;
        } else if (hex.length === 6) {
            const r = parseInt(hex.slice(0, 2), 16);
            const g = parseInt(hex.slice(2, 4), 16);
            const b = parseInt(hex.slice(4, 6), 16);
            return `rgb(${r}, ${g}, ${b})`;
        }
    }
    // Return as-is for named colors
    return color;
}

// Convert color to hex for color picker (uses priority-based resolution)
function colorToHex(color) {
    return resolveColorToHex(color);
}

// Color presets from SCITEX theme (priority 1 - highest)
// Format: 'name': { hex: '#rrggbb', rgb: [r, g, b] }
const COLOR_PRESETS = {
    'blue':      { hex: '#0080c0', rgb: [0, 128, 192] },
    'red':       { hex: '#ff4632', rgb: [255, 70, 50] },
    'green':     { hex: '#14b414', rgb: [20, 180, 20] },
    'yellow':    { hex: '#e6a014', rgb: [230, 160, 20] },
    'purple':    { hex: '#c832ff', rgb: [200, 50, 255] },
    'lightblue': { hex: '#14c8c8', rgb: [20, 200, 200] },
    'orange':    { hex: '#e45e32', rgb: [228, 94, 50] },
    'pink':      { hex: '#ff96c8', rgb: [255, 150, 200] },
    'black':     { hex: '#000000', rgb: [0, 0, 0] },
    'white':     { hex: '#ffffff', rgb: [255, 255, 255] },
    'gray':      { hex: '#808080', rgb: [128, 128, 128] }
};

// Matplotlib single-letter colors (priority 2)
// Format: 'name': { hex: '#rrggbb', rgb: [r, g, b] }
const MATPLOTLIB_SINGLE = {
    'b': { hex: '#1f77b4', rgb: [31, 119, 180] },
    'g': { hex: '#2ca02c', rgb: [44, 160, 44] },
    'r': { hex: '#d62728', rgb: [214, 39, 40] },
    'c': { hex: '#17becf', rgb: [23, 190, 207] },
    'm': { hex: '#9467bd', rgb: [148, 103, 189] },
    'y': { hex: '#bcbd22', rgb: [188, 189, 34] },
    'k': { hex: '#000000', rgb: [0, 0, 0] },
    'w': { hex: '#ffffff', rgb: [255, 255, 255] }
};

// Matplotlib/CSS named colors (priority 3 - common subset)
const MATPLOTLIB_NAMED = {
    'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff',
    'aquamarine': '#7fffd4', 'azure': '#f0ffff', 'beige': '#f5f5dc',
    'bisque': '#ffe4c4', 'blanchedalmond': '#ffebcd', 'blueviolet': '#8a2be2',
    'brown': '#a52a2a', 'burlywood': '#deb887', 'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00', 'chocolate': '#d2691e', 'coral': '#ff7f50',
    'cornflowerblue': '#6495ed', 'cornsilk': '#fff8dc', 'crimson': '#dc143c',
    'cyan': '#00ffff', 'darkblue': '#00008b', 'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b', 'darkgray': '#a9a9a9', 'darkgreen': '#006400',
    'darkgrey': '#a9a9a9', 'darkkhaki': '#bdb76b', 'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f', 'darkorange': '#ff8c00', 'darkorchid': '#9932cc',
    'darkred': '#8b0000', 'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b', 'darkslategray': '#2f4f4f', 'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3', 'deeppink': '#ff1493', 'deepskyblue': '#00bfff',
    'dimgray': '#696969', 'dodgerblue': '#1e90ff', 'firebrick': '#b22222',
    'floralwhite': '#fffaf0', 'forestgreen': '#228b22', 'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff', 'gold': '#ffd700',
    'goldenrod': '#daa520', 'greenyellow': '#adff2f', 'honeydew': '#f0fff0',
    'hotpink': '#ff69b4', 'indianred': '#cd5c5c', 'indigo': '#4b0082',
    'ivory': '#fffff0', 'khaki': '#f0e68c', 'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00', 'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6', 'lightcoral': '#f08080', 'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3', 'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1', 'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa', 'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de', 'lightyellow': '#ffffe0', 'lime': '#00ff00',
    'limegreen': '#32cd32', 'linen': '#faf0e6', 'magenta': '#ff00ff',
    'maroon': '#800000', 'mediumaquamarine': '#66cdaa', 'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3', 'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee', 'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585', 'midnightblue': '#191970', 'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1', 'moccasin': '#ffe4b5', 'navajowhite': '#ffdead',
    'navy': '#000080', 'oldlace': '#fdf5e6', 'olive': '#808000',
    'olivedrab': '#6b8e23', 'orangered': '#ff4500', 'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee',
    'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9',
    'peru': '#cd853f', 'plum': '#dda0dd', 'powderblue': '#b0e0e6',
    'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513',
    'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57',
    'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0',
    'skyblue': '#87ceeb', 'slateblue': '#6a5acd', 'slategray': '#708090',
    'snow': '#fffafa', 'springgreen': '#00ff7f', 'steelblue': '#4682b4',
    'tan': '#d2b48c', 'teal': '#008080', 'thistle': '#d8bfd8',
    'tomato': '#ff6347', 'turquoise': '#40e0d0', 'violet': '#ee82ee',
    'wheat': '#f5deb3', 'whitesmoke': '#f5f5f5', 'yellowgreen': '#9acd32'
};

// Resolve color string to hex with priority: theme presets -> matplotlib -> CSS named
// Returns {name, hex, source} or null if not found in any preset
function findPresetColor(input) {
    if (!input) return null;

    // Handle array input (RGB values like [1.0, 0.27, 0.19])
    if (Array.isArray(input)) {
        const r = Math.round(input[0] * 255);
        const g = Math.round(input[1] * 255);
        const b = Math.round(input[2] * 255);
        const hex = '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
        // Search for matching preset by hex
        return findPresetByHex(hex);
    }

    // Ensure input is a string
    if (typeof input !== 'string') {
        return null;
    }

    const trimmed = input.trim();

    // Handle RGB tuple string format: (r, g, b) or r, g, b
    const rgbMatch = trimmed.match(/^\\(?\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)?$/);
    if (rgbMatch) {
        const r = parseInt(rgbMatch[1]);
        const g = parseInt(rgbMatch[2]);
        const b = parseInt(rgbMatch[3]);
        const hex = '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
        // Search for matching preset by hex
        return findPresetByHex(hex);
    }

    const lower = trimmed.toLowerCase();

    // Priority 1: SCITEX theme presets (check name and hex)
    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        if (name === lower || preset.hex.toLowerCase() === lower) {
            return { name, hex: preset.hex, rgb: preset.rgb, source: 'theme' };
        }
    }

    // Priority 2: Matplotlib single-letter colors (check name and hex)
    if (MATPLOTLIB_SINGLE[lower]) {
        const preset = MATPLOTLIB_SINGLE[lower];
        return { name: lower, hex: preset.hex, rgb: preset.rgb, source: 'matplotlib' };
    }
    for (const [name, preset] of Object.entries(MATPLOTLIB_SINGLE)) {
        if (preset.hex.toLowerCase() === lower) {
            return { name, hex: preset.hex, rgb: preset.rgb, source: 'matplotlib' };
        }
    }

    // Priority 3: Matplotlib/CSS named colors (check name and hex)
    if (MATPLOTLIB_NAMED[lower]) {
        return { name: lower, hex: MATPLOTLIB_NAMED[lower], source: 'css' };
    }
    for (const [name, hex] of Object.entries(MATPLOTLIB_NAMED)) {
        if (hex.toLowerCase() === lower) {
            return { name, hex, source: 'css' };
        }
    }

    return null;
}

// Helper: Find preset by hex value (for RGB tuple/array matching)
function findPresetByHex(hexValue) {
    if (!hexValue) return null;
    const lower = hexValue.toLowerCase();

    // Check SCITEX presets
    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        if (preset.hex.toLowerCase() === lower) {
            return { name, hex: preset.hex, rgb: preset.rgb, source: 'theme' };
        }
    }

    // Check matplotlib single-letter
    for (const [name, preset] of Object.entries(MATPLOTLIB_SINGLE)) {
        if (preset.hex.toLowerCase() === lower) {
            return { name, hex: preset.hex, rgb: preset.rgb, source: 'matplotlib' };
        }
    }

    // Check CSS named colors
    for (const [name, hex] of Object.entries(MATPLOTLIB_NAMED)) {
        if (hex.toLowerCase() === lower) {
            return { name, hex, source: 'css' };
        }
    }

    // Not found - return as custom with calculated RGB
    const r = parseInt(hexValue.slice(1, 3), 16);
    const g = parseInt(hexValue.slice(3, 5), 16);
    const b = parseInt(hexValue.slice(5, 7), 16);
    return { name: 'custom', hex: hexValue, rgb: [r, g, b], source: 'custom' };
}

// Convert any color string to hex (handles presets, hex, rgb, and CSS names)
function resolveColorToHex(input) {
    if (!input) return '#000000';

    // Check presets first
    const preset = findPresetColor(input);
    if (preset) return preset.hex;

    // Already hex format
    if (input.startsWith('#')) {
        if (input.length === 4) {
            return '#' + input[1] + input[1] + input[2] + input[2] + input[3] + input[3];
        }
        return input;
    }

    // RGB tuple format: (r, g, b) or r, g, b
    const rgbMatch = input.match(/^\\(?(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\)?$/);
    if (rgbMatch) {
        const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
        const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
        const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
    }

    // Try browser's color parsing as last resort
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = input;
    return ctx.fillStyle;  // Returns hex
}

// Format color for display - prefer preset name, then RGB
function formatColorDisplay(value) {
    if (!value) return '';

    // Check if it matches a preset
    const preset = findPresetColor(value);
    if (preset) {
        return preset.name;  // Show preset name
    }

    // If hex, convert to RGB tuple
    if (value.startsWith('#')) {
        return hexToRGBTuple(value) || value;
    }

    // Return as-is (could be matplotlib color name)
    return value;
}

// Convert hex to RGB tuple string for matplotlib
function hexToRGBTuple(hex) {
    if (!hex || !hex.startsWith('#')) return null;
    const h = hex.slice(1);
    if (h.length === 3) {
        const r = parseInt(h[0] + h[0], 16);
        const g = parseInt(h[1] + h[1], 16);
        const b = parseInt(h[2] + h[2], 16);
        return `(${r}, ${g}, ${b})`;
    } else if (h.length === 6) {
        const r = parseInt(h.slice(0, 2), 16);
        const g = parseInt(h.slice(2, 4), 16);
        const b = parseInt(h.slice(4, 6), 16);
        return `(${r}, ${g}, ${b})`;
    }
    return null;
}

// Create a unified color input with dropdown (presets + custom option)
function createColorInput(callId, key, value) {
    const wrapper = document.createElement('div');
    wrapper.className = 'color-input-wrapper';

    // Resolve initial color to hex for display
    const resolvedHex = resolveColorToHex(value);
    const initialPreset = findPresetColor(value);

    // Color preview swatch (click to open color picker)
    const swatch = document.createElement('div');
    swatch.className = 'color-swatch';
    swatch.style.backgroundColor = resolvedHex;
    swatch.title = 'Click to pick color';

    // Unified dropdown with presets + custom option
    const select = document.createElement('select');
    select.className = 'dynamic-input color-select';
    select.dataset.callId = callId;
    select.dataset.param = key;

    // Add preset options with RGB display
    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = `${name} (${preset.rgb.join(', ')})`;
        opt.style.backgroundColor = preset.hex;
        select.appendChild(opt);
    }

    // Add separator and custom option
    const separator = document.createElement('option');
    separator.disabled = true;
    separator.textContent = '───────────';
    select.appendChild(separator);

    const customOpt = document.createElement('option');
    customOpt.value = '__custom__';
    customOpt.textContent = 'Custom...';
    select.appendChild(customOpt);

    // Set initial selection
    if (initialPreset) {
        // Check if preset name is in COLOR_PRESETS (which are added as options)
        if (initialPreset.name in COLOR_PRESETS) {
            select.value = initialPreset.name;
        } else {
            // Matched matplotlib/CSS color - add as custom option since it's not in dropdown
            const currentOpt = document.createElement('option');
            currentOpt.value = initialPreset.name;
            const rgbStr = initialPreset.rgb ? initialPreset.rgb.join(', ') : hexToRGBTuple(initialPreset.hex);
            currentOpt.textContent = `${initialPreset.name} (${rgbStr})`;
            currentOpt.style.backgroundColor = initialPreset.hex;
            select.insertBefore(currentOpt, separator);
            select.value = initialPreset.name;
        }
    } else if (value) {
        // Add current value as option if not a preset
        const currentOpt = document.createElement('option');
        currentOpt.value = value;
        currentOpt.textContent = formatColorDisplay(value);
        currentOpt.style.backgroundColor = resolvedHex;
        select.insertBefore(currentOpt, separator);
        select.value = value;
    }

    // Custom input (hidden by default, shown when "Custom..." selected)
    const customInput = document.createElement('input');
    customInput.type = 'text';
    customInput.className = 'dynamic-input color-custom-input';
    customInput.placeholder = '(R,G,B) or color name';
    customInput.style.display = 'none';

    // RGB display (show tuple format)
    const rgbDisplay = document.createElement('span');
    rgbDisplay.className = 'rgb-display';
    rgbDisplay.textContent = initialPreset?.rgb ? `(${initialPreset.rgb.join(', ')})` : hexToRGBTuple(resolvedHex);

    // Hidden color picker
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.className = 'color-picker-hidden';
    colorPicker.value = resolvedHex;

    // Update display helper
    function updateDisplay(colorValue) {
        const preset = findPresetColor(colorValue);
        const hex = preset ? preset.hex : resolveColorToHex(colorValue);
        swatch.style.backgroundColor = hex;
        // Show RGB tuple format
        if (preset?.rgb) {
            rgbDisplay.textContent = `(${preset.rgb.join(', ')})`;
        } else {
            rgbDisplay.textContent = hexToRGBTuple(hex) || hex;
        }
        colorPicker.value = hex;
    }

    // Event handlers
    select.addEventListener('change', function() {
        if (this.value === '__custom__') {
            // Hide swatch and rgb display, open color picker
            swatch.style.display = 'none';
            rgbDisplay.style.display = 'none';
            customInput.style.display = 'none';
            colorPicker.click();  // Open color picker dialog
        } else {
            // Show swatch and rgb display
            swatch.style.display = '';
            rgbDisplay.style.display = '';
            customInput.style.display = 'none';
            updateDisplay(this.value);
            // Create a fake input for the handler
            const fakeInput = { value: this.value };
            handleDynamicParamChange(callId, key, fakeInput);
        }
    });

    customInput.addEventListener('change', function() {
        const inputValue = this.value.trim();
        if (inputValue) {
            // Check if it matches a preset
            const preset = findPresetColor(inputValue);
            if (preset) {
                select.value = preset.name;
                customInput.style.display = 'none';
                updateDisplay(preset.hex);
            } else {
                // Add as new option
                let existingOpt = Array.from(select.options).find(o => o.value === inputValue);
                if (!existingOpt) {
                    const newOpt = document.createElement('option');
                    newOpt.value = inputValue;
                    newOpt.textContent = formatColorDisplay(inputValue);
                    select.insertBefore(newOpt, separator);
                }
                select.value = inputValue;
                customInput.style.display = 'none';
                updateDisplay(inputValue);
            }
            const fakeInput = { value: inputValue };
            handleDynamicParamChange(callId, key, fakeInput);
        }
    });

    customInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            customInput.style.display = 'none';
            // Revert to previous selection
            if (select.value === '__custom__') {
                select.selectedIndex = 0;
            }
        }
    });

    swatch.addEventListener('click', function() {
        colorPicker.click();
    });

    colorPicker.addEventListener('input', function() {
        updateDisplay(this.value);
    });

    colorPicker.addEventListener('change', function() {
        const pickedColor = this.value;
        const preset = findPresetColor(pickedColor);
        if (preset) {
            select.value = preset.name;
        } else {
            // Add picked color as option
            const rgbTuple = hexToRGBTuple(pickedColor);
            let existingOpt = Array.from(select.options).find(o => o.value === pickedColor || o.value === rgbTuple);
            if (!existingOpt) {
                const newOpt = document.createElement('option');
                newOpt.value = rgbTuple || pickedColor;
                newOpt.textContent = rgbTuple || pickedColor;
                select.insertBefore(newOpt, separator);
            }
            select.value = rgbTuple || pickedColor;
        }
        // Restore display elements and update
        swatch.style.display = '';
        rgbDisplay.style.display = '';
        customInput.style.display = 'none';
        updateDisplay(select.value);
        const fakeInput = { value: select.value };
        handleDynamicParamChange(callId, key, fakeInput);
    });

    wrapper.appendChild(swatch);
    wrapper.appendChild(select);
    wrapper.appendChild(customInput);
    wrapper.appendChild(rgbDisplay);
    wrapper.appendChild(colorPicker);

    return wrapper;
}

// Create a dynamic form field for call parameter
function createDynamicField(callId, key, value, sigInfo, isUnused = false) {
    const container = document.createElement('div');
    container.className = 'dynamic-field-container' + (isUnused ? ' unused' : '');

    const row = document.createElement('div');
    row.className = 'form-row dynamic-field';

    const label = document.createElement('label');
    label.textContent = key;

    let input;

    // Check if this is a color field
    if (isColorField(key, sigInfo)) {
        input = createColorInput(callId, key, value);
        row.appendChild(label);
        row.appendChild(input);
        container.appendChild(row);
        return container;  // Skip type hint for color fields
    }

    if (typeof value === 'boolean' || value === true || value === false) {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = value === true;
    } else if (typeof value === 'number') {
        input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.value = value;
    } else if (value === null || value === undefined) {
        input = document.createElement('input');
        input.type = 'text';
        input.value = '';
        input.placeholder = 'null';
    } else {
        input = document.createElement('input');
        input.type = 'text';
        input.value = String(value);
    }

    input.dataset.callId = callId;
    input.dataset.param = key;
    input.className = 'dynamic-input';

    // Add change handler
    input.addEventListener('change', function() {
        handleDynamicParamChange(callId, key, this);
    });

    row.appendChild(label);
    row.appendChild(input);
    container.appendChild(row);

    // Add type hint below the field
    if (sigInfo?.type) {
        const typeHint = document.createElement('div');
        typeHint.className = 'type-hint';
        // Clean up matplotlib docstring formatting
        let typeText = sigInfo.type
            .replace(/:mpltype:`([^`]+)`/g, '$1')  // :mpltype:`color` -> color
            .replace(/`~[^`]+`/g, '')              // Remove `~.xxx` references
            .replace(/`([^`]+)`/g, '$1');          // `xxx` -> xxx
        typeHint.textContent = typeText;
        container.appendChild(typeHint);
    }

    return container;
}

// Handle change to dynamic call parameter
async function handleDynamicParamChange(callId, param, input) {
    let value;
    if (input.type === 'checkbox') {
        value = input.checked;
    } else if (input.type === 'number') {
        value = parseFloat(input.value);
        if (isNaN(value)) value = null;
    } else {
        value = input.value || null;
        // Convert string "null" to actual null
        if (value === 'null') value = null;
    }

    // For color parameters, resolve to hex using priority system (theme > matplotlib > CSS)
    // This ensures "red" becomes SCITEX red (#ff4632), not pure red (#ff0000)
    const colorParams = ['color', 'facecolor', 'edgecolor', 'markerfacecolor', 'markeredgecolor', 'c'];
    if (value && typeof value === 'string' && colorParams.includes(param.toLowerCase())) {
        const resolvedHex = resolveColorToHex(value);
        console.log(`Color resolved: ${value} -> ${resolvedHex}`);
        value = resolvedHex;
    }

    console.log(`Dynamic param change: ${callId}.${param} = ${value}`);

    // Show loading state
    document.body.classList.add('loading');
    input.disabled = true;

    try {
        const response = await fetch('/update_call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ call_id: callId, param: param, value: value })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            // Update dimensions for hitmap scaling
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;

            // Reload hitmap
            loadHitmap();

            // Redraw hit regions
            updateHitRegions();

            // Update callsData with new value
            if (callsData[callId]) {
                if (value === null) {
                    delete callsData[callId].kwargs[param];
                } else {
                    callsData[callId].kwargs[param] = value;
                }
            }

            console.log('Call updated successfully');
        } else {
            console.error('Update failed:', data.error);
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        console.error('Update failed:', error);
        alert('Update failed: ' + error.message);
    }

    input.disabled = false;
    document.body.classList.remove('loading');
}

// Set view mode (all or selected)
// Current active tab
let currentTab = 'figure';

// Element type to tab mapping
const AXIS_TYPES = ['title', 'xlabel', 'ylabel', 'suptitle', 'supxlabel', 'supylabel', 'legend'];
const ELEMENT_TYPES = ['line', 'scatter', 'bar', 'hist', 'fill', 'boxplot', 'violin', 'image', 'linecollection', 'quiver', 'pie'];

// Switch between Figure/Axis/Element tabs
function switchTab(tabName) {
    currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id === `tab-${tabName}`);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-content-${tabName}`);
    });

    // Update hints based on selection state
    updateTabHints();
}

// Get appropriate tab for element type
function getTabForElementType(elementType) {
    if (!elementType) return 'figure';
    if (AXIS_TYPES.includes(elementType)) return 'axis';
    if (ELEMENT_TYPES.includes(elementType)) return 'element';
    return 'figure';
}

// Auto-switch to appropriate tab based on selected element
function autoSwitchTab(elementType) {
    const targetTab = getTabForElementType(elementType);
    if (targetTab !== currentTab) {
        switchTab(targetTab);
    }
}

// Update tab hints based on current state
function updateTabHints() {
    const axisHint = document.getElementById('axis-tab-hint');
    const elementHint = document.getElementById('element-tab-hint');
    const elementPanel = document.getElementById('selected-element-panel');
    const dynamicProps = document.getElementById('dynamic-call-properties');

    if (currentTab === 'axis') {
        if (selectedElement && AXIS_TYPES.includes(selectedElement.type)) {
            if (axisHint) axisHint.style.display = 'none';
        } else {
            if (axisHint) axisHint.style.display = 'block';
        }
    }

    if (currentTab === 'element') {
        if (selectedElement && ELEMENT_TYPES.includes(selectedElement.type)) {
            if (elementHint) elementHint.style.display = 'none';
            if (elementPanel) {
                elementPanel.style.display = 'block';
                document.getElementById('element-type-badge').textContent = selectedElement.type;
                document.getElementById('element-name').textContent = selectedElement.label || selectedElement.key;
            }
        } else {
            if (elementHint) elementHint.style.display = 'block';
            if (elementPanel) elementPanel.style.display = 'none';
            if (dynamicProps) dynamicProps.style.display = 'none';
        }
    }
}

function setViewMode(mode) {
    viewMode = mode;

    // Update toggle buttons (legacy)
    const btnAll = document.getElementById('btn-show-all');
    const btnSelected = document.getElementById('btn-show-selected');
    if (btnAll) btnAll.classList.toggle('active', mode === 'all');
    if (btnSelected) btnSelected.classList.toggle('active', mode === 'selected');

    // Update controls sections class
    const controlsSections = document.querySelector('.controls-sections');
    controlsSections.classList.toggle('filter-mode', mode === 'selected');

    // Update selection hint
    const hint = document.getElementById('selection-hint');
    if (mode === 'selected') {
        if (selectedElement) {
            hint.textContent = `Showing: ${selectedElement.type}`;
            hint.style.color = 'var(--accent-color)';
            // Hide all style sections - only show call properties
            hideAllStyleSections();
        } else {
            hint.textContent = '';
            hint.style.color = '';
            // Show all when no selection in filter mode
            showAllProperties();
        }
    } else {
        hint.textContent = '';
        showAllProperties();
    }
}

// Hide all style sections (for Selected mode - only show call properties)
function hideAllStyleSections() {
    const sections = document.querySelectorAll('.section[data-element-types]');
    sections.forEach(section => {
        section.classList.add('section-hidden');
        section.classList.remove('section-visible');
    });
}

// Filter properties by element type
function filterPropertiesByElementType(elementType) {
    const sections = document.querySelectorAll('.section[data-element-types]');

    sections.forEach(section => {
        const types = section.getAttribute('data-element-types').split(',');
        const isGlobal = types.includes('global');
        const matches = isGlobal || types.includes(elementType);

        section.classList.toggle('section-hidden', !matches);
        section.classList.toggle('section-visible', matches);

        // If section matches, filter individual form-rows within it
        if (matches && !isGlobal) {
            const formRows = section.querySelectorAll('.form-row[data-element-types]');
            formRows.forEach(row => {
                const rowTypes = row.getAttribute('data-element-types').split(',');
                const rowMatches = rowTypes.includes(elementType);
                row.classList.toggle('field-hidden', !rowMatches);
            });

            // Open matching sections
            section.setAttribute('open', '');
        }
    });

    // Update hint
    const hint = document.getElementById('selection-hint');
    hint.textContent = `Showing: ${elementType}`;
    hint.style.color = 'var(--accent-color)';
}

// Show all properties (remove filtering)
function showAllProperties() {
    const sections = document.querySelectorAll('.section[data-element-types]');

    sections.forEach(section => {
        section.classList.remove('section-hidden', 'section-visible');

        const formRows = section.querySelectorAll('.form-row[data-element-types]');
        formRows.forEach(row => {
            row.classList.remove('field-hidden');
        });
    });
}

// Clear selection
function clearSelection() {
    selectedElement = null;
    clearSelectionOverlay();

    // Clear section and field highlights
    document.querySelectorAll('.section-highlighted').forEach(s => s.classList.remove('section-highlighted'));
    document.querySelectorAll('.field-highlighted').forEach(f => f.classList.remove('field-highlighted'));

    // Switch back to Figure tab when nothing selected
    switchTab('figure');

    // Update hint and show all if in filter mode (legacy)
    const hint = document.getElementById('selection-hint');
    if (hint && viewMode === 'selected') {
        hint.textContent = '';
        hint.style.color = '';
        showAllProperties();
    }
}

// Draw selection shape(s) - handles lines, scatter, and rectangles like hover effect
function drawSelection(key) {
    const overlay = document.getElementById('selection-overlay');
    overlay.innerHTML = '';

    // Get preview image dimensions
    const img = document.getElementById('preview-image');
    if (!img.naturalWidth || !img.naturalHeight) return;

    // Set SVG viewBox to match natural image size (same as hitregion overlay)
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    // Use scale=1.0 since SVG coordinates match bbox coordinates
    const scaleX = 1.0;
    const scaleY = 1.0;
    const offsetX = 0;
    const offsetY = 0;

    // Determine which elements to highlight
    let elementsToHighlight = [key];

    // If this element has a group, highlight all group elements
    if (selectedElement && selectedElement.groupElements) {
        elementsToHighlight = selectedElement.groupElements.map(e => e.key);
    }

    // Draw selection for each element (same shape as hover)
    for (const elemKey of elementsToHighlight) {
        const bbox = currentBboxes[elemKey];
        if (!bbox) continue;

        // Get element color from bbox or use accent color as fallback
        const elementColor = bbox.original_color || '#2563eb';
        const isPrimary = elemKey === key;

        // Use polyline for lines with points (same as hover)
        if (bbox.type === 'line' && bbox.points && bbox.points.length > 1) {
            const points = bbox.points.map(pt => {
                const x = offsetX + pt[0] * scaleX;
                const y = offsetY + pt[1] * scaleY;
                return `${x},${y}`;
            }).join(' ');

            const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            polyline.setAttribute('points', points);
            polyline.setAttribute('class', 'selection-polyline');
            polyline.style.setProperty('--element-color', elementColor);
            if (isPrimary) {
                polyline.style.strokeWidth = '10';
                polyline.style.strokeOpacity = '0.6';
            }
            overlay.appendChild(polyline);
        }
        // Use subtle circles for scatter points (marker-level selection)
        else if (bbox.type === 'scatter' && bbox.points && bbox.points.length > 0) {
            bbox.points.forEach(pt => {
                const cx = offsetX + pt[0] * scaleX;
                const cy = offsetY + pt[1] * scaleY;

                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', cx);
                circle.setAttribute('cy', cy);
                circle.setAttribute('r', isPrimary ? 4 : 3);
                circle.setAttribute('class', 'selection-circle-subtle');
                circle.style.setProperty('--element-color', elementColor);
                overlay.appendChild(circle);
            });
        }
        // Use rectangle for other elements
        else {
            const x = offsetX + bbox.x * scaleX;
            const y = offsetY + bbox.y * scaleY;
            const width = bbox.width * scaleX;
            const height = bbox.height * scaleY;

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', Math.max(width, 2));
            rect.setAttribute('height', Math.max(height, 2));
            rect.setAttribute('class', 'selection-rect');
            rect.style.setProperty('--element-color', elementColor);

            // Mark the primary selection differently
            if (isPrimary) {
                rect.classList.add('selection-primary');
            }

            overlay.appendChild(rect);
        }
    }
}

// Clear selection overlay
function clearSelectionOverlay() {
    document.getElementById('selection-overlay').innerHTML = '';
}

// Schedule update with debounce
function scheduleUpdate() {
    if (updateTimeout) {
        clearTimeout(updateTimeout);
    }
    updateTimeout = setTimeout(updatePreview, UPDATE_DEBOUNCE);
}

// Collect current overrides from form
function collectOverrides() {
    const overrides = {};

    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.id === 'dark-mode-toggle') return;
        if (!input.id) return;

        let value;
        if (input.type === 'checkbox') {
            value = input.checked;
        } else if (input.type === 'number' || input.type === 'range') {
            value = parseFloat(input.value);
            if (isNaN(value)) return;
        } else {
            value = input.value;
        }

        overrides[input.id] = value;
    });

    return overrides;
}

// Update preview
async function updatePreview() {
    const overrides = collectOverrides();
    const darkMode = document.getElementById('dark-mode-toggle').checked;

    document.body.classList.add('loading');

    try {
        const response = await fetch('/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ overrides, dark_mode: darkMode })
        });

        const data = await response.json();

        // Update preview image
        const img = document.getElementById('preview-image');
        img.src = 'data:image/png;base64,' + data.image;

        // Update dimensions for hitmap scaling
        if (data.img_size) {
            currentImgWidth = data.img_size.width;
            currentImgHeight = data.img_size.height;
        }

        // Update bboxes
        currentBboxes = data.bboxes;

        // Redraw selection if element still exists
        if (selectedElement && currentBboxes[selectedElement.key]) {
            drawSelection(selectedElement.key);
        } else {
            clearSelection();
        }

        // Reload hitmap
        loadHitmap();

        // Redraw hit regions if visible
        updateHitRegions();

    } catch (error) {
        console.error('Update failed:', error);
    }

    document.body.classList.remove('loading');
}

// Reset values to initial
function resetValues() {
    initializeValues();
    updatePreview();
}

// Save overrides
async function saveOverrides() {
    const overrides = collectOverrides();

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ overrides })
        });

        const data = await response.json();
        if (data.success) {
            // Update override status indicator
            if (data.has_overrides) {
                showOverrideStatus(data.timestamp);
            }
            alert('Saved successfully!' + (data.path ? '\\nPath: ' + data.path : ''));
        }
    } catch (error) {
        console.error('Save failed:', error);
        alert('Save failed: ' + error.message);
    }
}

// Download dropdown state
let currentDownloadFormat = 'png';

// Initialize download dropdown
function initializeDownloadDropdown() {
    const mainBtn = document.getElementById('btn-download-main');
    const toggleBtn = document.getElementById('btn-download-toggle');
    const menu = document.getElementById('download-menu');

    // Main button click - download with current format
    mainBtn.addEventListener('click', () => {
        downloadFigure(currentDownloadFormat);
    });

    // Toggle button click - show/hide menu
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('open');
    });

    // Menu option clicks
    document.querySelectorAll('.download-option').forEach(option => {
        option.addEventListener('click', (e) => {
            const format = option.dataset.format;
            currentDownloadFormat = format;

            // Update main button text
            mainBtn.textContent = 'Download ' + format.toUpperCase();

            // Update active state
            document.querySelectorAll('.download-option').forEach(opt => {
                opt.classList.toggle('active', opt.dataset.format === format);
            });

            // Close menu
            menu.classList.remove('open');

            // Download immediately
            downloadFigure(format);
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.download-dropdown')) {
            menu.classList.remove('open');
        }
    });
}

// Initialize label input event handlers
function initializeLabelInputs() {
    const labelMap = {
        'label_title': 'title',
        'label_xlabel': 'xlabel',
        'label_ylabel': 'ylabel',
        'label_suptitle': 'suptitle'
    };

    for (const [inputId, labelType] of Object.entries(labelMap)) {
        const input = document.getElementById(inputId);
        if (input) {
            // Debounced update on input
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    updateLabel(labelType, this.value);
                }, UPDATE_DEBOUNCE);
            });

            // Immediate update on Enter key
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    clearTimeout(timeout);
                    updateLabel(labelType, this.value);
                }
            });

            // Immediate update on blur
            input.addEventListener('blur', function() {
                clearTimeout(timeout);
                updateLabel(labelType, this.value);
            });
        }
    }

    // Initialize axis type toggles
    initializeAxisTypeToggles();

    // Initialize legend position controls
    initializeLegendPosition();
}

// Initialize theme modal handlers
function initializeThemeModal() {
    const modal = document.getElementById('theme-modal');
    const themeSelector = document.getElementById('theme-selector');
    const btnView = document.getElementById('btn-view-theme');
    const btnDownload = document.getElementById('btn-download-theme');
    const btnCopy = document.getElementById('btn-copy-theme');
    const modalClose = document.getElementById('theme-modal-close');
    const modalDownload = document.getElementById('theme-modal-download');
    const modalCopy = document.getElementById('theme-modal-copy');
    const themeContent = document.getElementById('theme-content');
    const themeModalName = document.getElementById('theme-modal-name');

    // Theme selector change handler
    if (themeSelector) {
        // Load current theme and set selector
        loadCurrentTheme();

        themeSelector.addEventListener('change', function() {
            switchTheme(this.value);
        });
    }

    // View button opens modal
    if (btnView) {
        btnView.addEventListener('click', showThemeModal);
    }

    // Download button
    if (btnDownload) {
        btnDownload.addEventListener('click', downloadTheme);
    }

    // Copy button
    if (btnCopy) {
        btnCopy.addEventListener('click', copyTheme);
    }

    // Modal close
    if (modalClose) {
        modalClose.addEventListener('click', hideThemeModal);
    }

    // Modal buttons
    if (modalDownload) {
        modalDownload.addEventListener('click', downloadTheme);
    }
    if (modalCopy) {
        modalCopy.addEventListener('click', copyTheme);
    }

    // Close modal on outside click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideThemeModal();
            }
        });
    }
}

// Show theme modal
async function showThemeModal() {
    const modal = document.getElementById('theme-modal');
    const themeContent = document.getElementById('theme-content');
    const themeModalName = document.getElementById('theme-modal-name');
    const themeSelector = document.getElementById('theme-selector');

    try {
        const response = await fetch('/theme');
        const data = await response.json();

        // Use selector value if available, otherwise use data.name
        const themeName = themeSelector ? themeSelector.value : data.name;
        if (themeModalName) themeModalName.textContent = themeName;
        if (themeContent) themeContent.textContent = data.content;
        if (modal) modal.style.display = 'flex';
    } catch (error) {
        console.error('Failed to load theme:', error);
    }
}

// Hide theme modal
function hideThemeModal() {
    const modal = document.getElementById('theme-modal');
    if (modal) modal.style.display = 'none';
}

// Initialize shortcuts modal handlers
function initializeShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    const btnShortcuts = document.getElementById('btn-shortcuts');
    const modalClose = document.getElementById('shortcuts-modal-close');

    // Button click handler
    if (btnShortcuts) {
        btnShortcuts.addEventListener('click', showShortcutsModal);
    }

    // Close button handler
    if (modalClose) {
        modalClose.addEventListener('click', hideShortcutsModal);
    }

    // Click outside to close
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideShortcutsModal();
            }
        });
    }
}

// Show shortcuts modal
function showShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) modal.style.display = 'flex';
}

// Hide shortcuts modal
function hideShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) modal.style.display = 'none';
}

// Download theme as YAML
async function downloadTheme() {
    try {
        const response = await fetch('/theme');
        const data = await response.json();

        const blob = new Blob([data.content], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.name + '.yaml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Failed to download theme:', error);
    }
}

// Copy theme to clipboard
async function copyTheme() {
    try {
        const response = await fetch('/theme');
        const data = await response.json();

        await navigator.clipboard.writeText(data.content);

        // Visual feedback
        const btn = document.getElementById('btn-copy-theme');
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = originalText; }, 1500);
    } catch (error) {
        console.error('Failed to copy theme:', error);
    }
}

// Load current theme and set selector
async function loadCurrentTheme() {
    try {
        const response = await fetch('/list_themes');
        const data = await response.json();

        const selector = document.getElementById('theme-selector');
        if (selector && data.current) {
            selector.value = data.current;
        }

        console.log('Current theme:', data.current);
    } catch (error) {
        console.error('Failed to load current theme:', error);
    }
}

// Switch to a different theme preset
async function switchTheme(themeName) {
    console.log('Switching theme to:', themeName);

    // Show loading state
    document.body.classList.add('loading');

    try {
        const response = await fetch('/switch_theme', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: themeName })
        });

        const result = await response.json();

        if (result.success) {
            // Update preview with new image
            const previewImg = document.getElementById('preview-image');
            previewImg.src = 'data:image/png;base64,' + result.image;

            // Update dimensions
            if (result.img_size) {
                currentImgWidth = result.img_size.width;
                currentImgHeight = result.img_size.height;
            }

            // Update form values from new theme
            if (result.values) {
                for (const [key, value] of Object.entries(result.values)) {
                    const element = document.getElementById(key);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = Boolean(value);
                        } else {
                            element.value = value;
                        }
                        // Update placeholder as well for theme defaults
                        if (element.placeholder !== undefined) {
                            element.placeholder = value;
                        }
                    }
                }
                // Update theme defaults for modified state comparison
                Object.assign(themeDefaults, result.values);
                updateAllModifiedStates();
            }

            // Update bboxes and redraw hit regions
            if (result.bboxes) {
                currentBboxes = result.bboxes;
                previewImg.onload = () => {
                    updateHitRegions();
                    loadHitmap();
                };
            }

            console.log('Theme switched to:', themeName);
        } else {
            console.error('Theme switch failed:', result.error);
            // Reset selector to previous value
            loadCurrentTheme();
        }
    } catch (error) {
        console.error('Failed to switch theme:', error);
        // Reset selector to previous value
        loadCurrentTheme();
    } finally {
        document.body.classList.remove('loading');
    }
}

// Initialize axis type toggle buttons
function initializeAxisTypeToggles() {
    const xNumerical = document.getElementById('xaxis-numerical');
    const xCategorical = document.getElementById('xaxis-categorical');
    const yNumerical = document.getElementById('yaxis-numerical');
    const yCategorical = document.getElementById('yaxis-categorical');
    const xLabelsRow = document.getElementById('xaxis-labels-row');
    const yLabelsRow = document.getElementById('yaxis-labels-row');
    const xLabelsInput = document.getElementById('xaxis_labels');
    const yLabelsInput = document.getElementById('yaxis_labels');

    // X-axis buttons
    if (xNumerical) {
        xNumerical.addEventListener('click', () => {
            xNumerical.classList.add('active');
            xCategorical.classList.remove('active');
            xLabelsRow.style.display = 'none';
            updateAxisType('x', 'numerical');
        });
    }

    if (xCategorical) {
        xCategorical.addEventListener('click', () => {
            xCategorical.classList.add('active');
            xNumerical.classList.remove('active');
            xLabelsRow.style.display = 'flex';
        });
    }

    // Y-axis buttons
    if (yNumerical) {
        yNumerical.addEventListener('click', () => {
            yNumerical.classList.add('active');
            yCategorical.classList.remove('active');
            yLabelsRow.style.display = 'none';
            updateAxisType('y', 'numerical');
        });
    }

    if (yCategorical) {
        yCategorical.addEventListener('click', () => {
            yCategorical.classList.add('active');
            yNumerical.classList.remove('active');
            yLabelsRow.style.display = 'flex';
        });
    }

    // Labels input handlers
    if (xLabelsInput) {
        let timeout;
        xLabelsInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                if (labels.length > 0) {
                    updateAxisType('x', 'categorical', labels);
                }
            }, UPDATE_DEBOUNCE);
        });

        xLabelsInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                clearTimeout(timeout);
                const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                if (labels.length > 0) {
                    updateAxisType('x', 'categorical', labels);
                }
            }
        });
    }

    if (yLabelsInput) {
        let timeout;
        yLabelsInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                if (labels.length > 0) {
                    updateAxisType('y', 'categorical', labels);
                }
            }, UPDATE_DEBOUNCE);
        });

        yLabelsInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                clearTimeout(timeout);
                const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                if (labels.length > 0) {
                    updateAxisType('y', 'categorical', labels);
                }
            }
        });
    }

    // Load current axis info
    loadAxisInfo();
}

// Load current axis type info
async function loadAxisInfo() {
    try {
        const response = await fetch('/get_axis_info');
        const info = await response.json();

        // Update X axis toggle
        if (info.x_type === 'categorical') {
            document.getElementById('xaxis-categorical').classList.add('active');
            document.getElementById('xaxis-numerical').classList.remove('active');
            document.getElementById('xaxis-labels-row').style.display = 'flex';
            if (info.x_labels && info.x_labels.length > 0) {
                document.getElementById('xaxis_labels').value = info.x_labels.join(', ');
            }
        }

        // Update Y axis toggle
        if (info.y_type === 'categorical') {
            document.getElementById('yaxis-categorical').classList.add('active');
            document.getElementById('yaxis-numerical').classList.remove('active');
            document.getElementById('yaxis-labels-row').style.display = 'flex';
            if (info.y_labels && info.y_labels.length > 0) {
                document.getElementById('yaxis_labels').value = info.y_labels.join(', ');
            }
        }

        console.log('Loaded axis info:', info);
    } catch (error) {
        console.error('Failed to load axis info:', error);
    }
}

// Update axis type on server
async function updateAxisType(axis, type, labels = []) {
    console.log(`Updating ${axis} axis to ${type}`, labels);

    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_axis_type', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                axis: axis,
                type: type,
                labels: labels
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            // Update dimensions
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;

            // Redraw hit regions
            updateHitRegions();

            console.log('Axis type updated successfully');
        } else {
            console.error('Axis type update failed:', data.error);
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        console.error('Axis type update failed:', error);
        alert('Update failed: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Initialize legend position controls
function initializeLegendPosition() {
    const locSelect = document.getElementById('legend_loc');
    const customPosDiv = document.getElementById('legend-custom-pos');
    const xInput = document.getElementById('legend_x');
    const yInput = document.getElementById('legend_y');
    const visibleCheckbox = document.getElementById('legend_visible');

    if (!locSelect) return;

    // Legend visibility toggle
    if (visibleCheckbox) {
        visibleCheckbox.addEventListener('change', function() {
            updateLegendVisibility(this.checked);
        });
    }

    // Show/hide custom position inputs based on selection
    locSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customPosDiv.style.display = 'block';
        } else {
            customPosDiv.style.display = 'none';
            // Update legend with new location
            updateLegendPosition(this.value);
        }
    });

    // Custom x/y coordinate handlers
    if (xInput && yInput) {
        let timeout;
        const updateCustomPos = () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const x = parseFloat(xInput.value);
                const y = parseFloat(yInput.value);
                if (!isNaN(x) && !isNaN(y)) {
                    updateLegendPosition('custom', x, y);
                }
            }, UPDATE_DEBOUNCE);
        };

        xInput.addEventListener('input', updateCustomPos);
        yInput.addEventListener('input', updateCustomPos);

        xInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                clearTimeout(timeout);
                const x = parseFloat(xInput.value);
                const y = parseFloat(yInput.value);
                if (!isNaN(x) && !isNaN(y)) {
                    updateLegendPosition('custom', x, y);
                }
            }
        });

        yInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                clearTimeout(timeout);
                const x = parseFloat(xInput.value);
                const y = parseFloat(yInput.value);
                if (!isNaN(x) && !isNaN(y)) {
                    updateLegendPosition('custom', x, y);
                }
            }
        });
    }

    // Load current legend info
    loadLegendInfo();
}

// Load current legend position info
async function loadLegendInfo() {
    try {
        const response = await fetch('/get_legend_info');
        const info = await response.json();

        if (!info.has_legend) {
            console.log('No legend found');
            return;
        }

        const locSelect = document.getElementById('legend_loc');
        const customPosDiv = document.getElementById('legend-custom-pos');
        const xInput = document.getElementById('legend_x');
        const yInput = document.getElementById('legend_y');
        const visibleCheckbox = document.getElementById('legend_visible');

        // Set visibility checkbox
        if (visibleCheckbox) {
            visibleCheckbox.checked = info.visible !== false;
        }

        if (locSelect) {
            locSelect.value = info.loc;
        }

        if (info.loc === 'custom' && customPosDiv) {
            customPosDiv.style.display = 'block';
            if (xInput && info.x !== null) xInput.value = info.x;
            if (yInput && info.y !== null) yInput.value = info.y;
        }

        console.log('Loaded legend info:', info);
    } catch (error) {
        console.error('Failed to load legend info:', error);
    }
}

// Update legend visibility
async function updateLegendVisibility(visible) {
    console.log('Updating legend visibility:', visible);

    try {
        const response = await fetch('/update_legend_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ visible: visible })
        });

        const result = await response.json();

        if (result.success) {
            // Update preview with new image
            const previewImg = document.getElementById('preview-image');
            previewImg.src = 'data:image/png;base64,' + result.image;

            // Update dimensions
            if (result.img_size) {
                currentImgWidth = result.img_size.width;
                currentImgHeight = result.img_size.height;
            }

            // Update bboxes and redraw hit regions
            if (result.bboxes) {
                currentBboxes = result.bboxes;
                previewImg.onload = () => {
                    updateHitRegions();
                    loadHitmap();
                };
            }
        } else {
            console.error('Legend visibility update failed:', result.error);
        }
    } catch (error) {
        console.error('Failed to update legend visibility:', error);
    }
}

// Update legend position on server
async function updateLegendPosition(loc, x = null, y = null) {
    console.log(`Updating legend position: loc=${loc}, x=${x}, y=${y}`);

    document.body.classList.add('loading');

    try {
        const body = { loc };
        if (loc === 'custom' && x !== null && y !== null) {
            body.x = x;
            body.y = y;
        }

        const response = await fetch('/update_legend_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            // Update dimensions
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            // Update bboxes
            currentBboxes = data.bboxes;

            // Redraw hit regions
            updateHitRegions();

            console.log('Legend position updated successfully');
        } else {
            console.error('Legend position update failed:', data.error);
            // Don't show alert for "No legend found" - it's expected for some figures
            if (!data.error.includes('No legend')) {
                alert('Update failed: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Legend position update failed:', error);
    }

    document.body.classList.remove('loading');
}

// ==================== ZOOM/PAN FUNCTIONS ====================

function initializeZoomPan() {
    const wrapper = document.getElementById('preview-wrapper');
    const container = document.getElementById('zoom-container');

    if (!wrapper || !container) return;

    // Zoom buttons
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => setZoom(zoomLevel + ZOOM_STEP));
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => setZoom(zoomLevel - ZOOM_STEP));
    document.getElementById('btn-zoom-reset')?.addEventListener('click', () => setZoom(1.0));
    document.getElementById('btn-zoom-fit')?.addEventListener('click', zoomToFit);

    // Mouse wheel zoom
    wrapper.addEventListener('wheel', (e) => {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
            setZoom(zoomLevel + delta);
        }
    }, { passive: false });

    // Pan with middle mouse or space+drag
    wrapper.addEventListener('mousedown', (e) => {
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            e.preventDefault();
            startPan(e);
        }
    });

    wrapper.addEventListener('mousemove', (e) => {
        if (isPanning) {
            doPan(e);
        }
    });

    wrapper.addEventListener('mouseup', endPan);
    wrapper.addEventListener('mouseleave', endPan);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === '+' || e.key === '=') {
            e.preventDefault();
            setZoom(zoomLevel + ZOOM_STEP);
        } else if (e.key === '-' || e.key === '_') {
            e.preventDefault();
            setZoom(zoomLevel - ZOOM_STEP);
        } else if (e.key === '0') {
            e.preventDefault();
            setZoom(1.0);
        } else if (e.key === 'f' || e.key === 'F') {
            e.preventDefault();
            zoomToFit();
        }
    });

    // Initialize fit to view
    setTimeout(zoomToFit, 200);
}

function setZoom(newLevel) {
    zoomLevel = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, newLevel));

    const container = document.getElementById('zoom-container');
    if (container) {
        container.style.transform = `scale(${zoomLevel})`;
    }

    // Update zoom level display
    const levelDisplay = document.getElementById('zoom-level');
    if (levelDisplay) {
        levelDisplay.textContent = Math.round(zoomLevel * 100) + '%';
    }
}

function zoomToFit() {
    const wrapper = document.getElementById('preview-wrapper');
    const img = document.getElementById('preview-image');

    if (!wrapper || !img || !img.naturalWidth) return;

    const wrapperRect = wrapper.getBoundingClientRect();
    const padding = 40;

    const scaleX = (wrapperRect.width - padding) / img.naturalWidth;
    const scaleY = (wrapperRect.height - padding) / img.naturalHeight;

    setZoom(Math.min(scaleX, scaleY, 1.0));
}

function startPan(e) {
    const wrapper = document.getElementById('preview-wrapper');
    isPanning = true;
    panStartX = e.clientX;
    panStartY = e.clientY;
    scrollStartX = wrapper.scrollLeft;
    scrollStartY = wrapper.scrollTop;
    wrapper.classList.add('panning');
}

function doPan(e) {
    if (!isPanning) return;

    const wrapper = document.getElementById('preview-wrapper');
    const dx = e.clientX - panStartX;
    const dy = e.clientY - panStartY;

    wrapper.scrollLeft = scrollStartX - dx;
    wrapper.scrollTop = scrollStartY - dy;
}

function endPan() {
    if (isPanning) {
        const wrapper = document.getElementById('preview-wrapper');
        wrapper.classList.remove('panning');
        isPanning = false;
    }
}

// ==================== END ZOOM/PAN ====================

// Download figure
function downloadFigure(format) {
    window.location.href = '/download/' + format;
}

// Restore to original programmatic style (clear manual overrides)
async function restoreOriginal() {
    if (!confirm('Restore to original programmatic style? This will clear all manual overrides.')) {
        return;
    }

    document.body.classList.add('loading');

    try {
        const response = await fetch('/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            // Update bboxes
            currentBboxes = data.bboxes;

            // Reset form values to original style
            if (data.original_style) {
                for (const [key, value] of Object.entries(data.original_style)) {
                    const element = document.getElementById(key);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = Boolean(value);
                        } else if (element.type === 'range') {
                            element.value = value;
                            const valueSpan = document.getElementById(key + '_value');
                            if (valueSpan) valueSpan.textContent = value;
                        } else {
                            element.value = value;
                        }
                    }
                }
            }

            // Clear selection
            clearSelection();

            // Hide override status
            hideOverrideStatus();

            // Reload hitmap
            loadHitmap();
        }
    } catch (error) {
        console.error('Restore failed:', error);
        alert('Restore failed: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Check and display override status
async function checkOverrideStatus() {
    try {
        const response = await fetch('/style');
        const data = await response.json();

        if (data.has_overrides) {
            showOverrideStatus(data.manual_timestamp);
        } else {
            hideOverrideStatus();
        }
    } catch (error) {
        console.error('Failed to check override status:', error);
    }
}

// Show override status indicator
function showOverrideStatus(timestamp) {
    const statusEl = document.getElementById('override-status');
    const timestampEl = document.getElementById('override-timestamp');

    if (statusEl) {
        statusEl.style.display = 'flex';
    }

    if (timestampEl && timestamp) {
        const date = new Date(timestamp);
        timestampEl.textContent = 'Last modified: ' + date.toLocaleString();
    }
}

// Hide override status indicator
function hideOverrideStatus() {
    const statusEl = document.getElementById('override-status');
    if (statusEl) {
        statusEl.style.display = 'none';
    }
}

// Update override status after save
async function updateOverrideStatusAfterSave(data) {
    if (data.has_overrides) {
        showOverrideStatus(data.timestamp);
    }
}

// Show toast notification for keyboard shortcuts feedback
function showToast(message, type = 'info') {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast-notification toast-' + type;
    toast.textContent = message;

    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        padding: '10px 20px',
        borderRadius: '4px',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        opacity: '0',
        transition: 'opacity 0.3s ease',
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
    });

    // Set background color based on type
    const colors = {
        success: '#4CAF50',
        info: '#2196F3',
        warning: '#ff9800',
        error: '#f44336'
    };
    toast.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(toast);

    // Fade in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
    });

    // Remove after delay
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

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

// ==================== ELEMENT INSPECTOR ====================
// Visual debugging tool for DOM elements (Alt+I to toggle)
let elementInspectorActive = false;
let elementInspectorOverlay = null;
const inspectorColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
];

function toggleElementInspector() {
    if (elementInspectorActive) {
        deactivateElementInspector();
    } else {
        activateElementInspector();
    }
}

function activateElementInspector() {
    console.log('[ElementInspector] Activating...');
    elementInspectorActive = true;

    // Create overlay container
    elementInspectorOverlay = document.createElement('div');
    elementInspectorOverlay.id = 'element-inspector-overlay';
    elementInspectorOverlay.className = 'element-inspector-overlay';
    document.body.appendChild(elementInspectorOverlay);

    // Scan and visualize elements
    scanInspectorElements();

    console.log('[ElementInspector] Active - Press Alt+I to deactivate');
}

function deactivateElementInspector() {
    console.log('[ElementInspector] Deactivating...');
    elementInspectorActive = false;

    if (elementInspectorOverlay) {
        elementInspectorOverlay.remove();
        elementInspectorOverlay = null;
    }
}

function scanInspectorElements() {
    if (!elementInspectorOverlay) return;

    // Clear existing overlays
    elementInspectorOverlay.innerHTML = '';

    // Get all visible elements
    const allElements = document.querySelectorAll('*');
    let colorIndex = 0;

    allElements.forEach(element => {
        // Skip non-visible, overlay, and script/style elements
        if (element.tagName === 'SCRIPT' || element.tagName === 'STYLE' ||
            element.tagName === 'HEAD' || element.tagName === 'META' ||
            element.tagName === 'LINK' || element.tagName === 'TITLE' ||
            element.id === 'element-inspector-overlay' ||
            element.closest('#element-inspector-overlay')) {
            return;
        }

        const rect = element.getBoundingClientRect();

        // Skip invisible or zero-size elements
        if (rect.width < 5 || rect.height < 5 ||
            rect.bottom < 0 || rect.right < 0 ||
            rect.top > window.innerHeight || rect.left > window.innerWidth) {
            return;
        }

        // Create element box
        const box = document.createElement('div');
        box.className = 'element-inspector-box';
        const color = inspectorColors[colorIndex % inspectorColors.length];
        box.style.cssText = `
            left: ${rect.left + window.scrollX}px;
            top: ${rect.top + window.scrollY}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            border-color: ${color};
        `;

        // Create label
        const label = document.createElement('div');
        label.className = 'element-inspector-label';
        label.style.backgroundColor = color;

        // Build element identifier
        let identifier = element.tagName.toLowerCase();
        if (element.id) identifier += '#' + element.id;
        if (element.className && typeof element.className === 'string') {
            const classes = element.className.split(' ').filter(c => c && !c.startsWith('element-inspector')).slice(0, 2);
            if (classes.length) identifier += '.' + classes.join('.');
        }

        label.textContent = identifier;
        box.appendChild(label);

        // Add click handler to show element info
        box.addEventListener('click', (e) => {
            e.stopPropagation();
            showInspectorElementInfo(element, color);
        });

        // Right-click to copy element path
        box.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            e.stopPropagation();
            copyInspectorElementPath(element);
        });

        elementInspectorOverlay.appendChild(box);
        colorIndex++;
    });

    console.log('[ElementInspector] Scanned ' + colorIndex + ' elements');
}

function showInspectorElementInfo(element, color) {
    // Log element info to console
    console.group('%cElement Info', 'color: ' + color + '; font-weight: bold;');
    console.log('Tag:', element.tagName);
    console.log('ID:', element.id || '(none)');
    console.log('Classes:', element.className || '(none)');
    console.log('Size:', element.offsetWidth + 'x' + element.offsetHeight);
    console.log('Position:', element.getBoundingClientRect());
    console.log('Element:', element);
    console.groupEnd();
}

function copyInspectorElementPath(element) {
    // Build CSS selector path
    const path = [];
    let current = element;

    while (current && current !== document.body) {
        let selector = current.tagName.toLowerCase();
        if (current.id) {
            selector = '#' + current.id;
            path.unshift(selector);
            break;
        } else if (current.className && typeof current.className === 'string') {
            const classes = current.className.split(' ').filter(c => c).slice(0, 2);
            if (classes.length) selector += '.' + classes.join('.');
        }
        path.unshift(selector);
        current = current.parentElement;
    }

    const selectorPath = path.join(' > ');
    navigator.clipboard.writeText(selectorPath).then(() => {
        console.log('[ElementInspector] Copied selector:', selectorPath);
        showToast('Copied: ' + selectorPath, 'success');
    });
}

// Add keyboard shortcut for element inspector
document.addEventListener('keydown', (e) => {
    // Skip if typing in input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    // Alt+I: Toggle element inspector
    if (e.altKey && !e.ctrlKey && !e.shiftKey && e.key.toLowerCase() === 'i') {
        e.preventDefault();
        toggleElementInspector();
    }

    // Alt+Shift+I: Capture debug info (screenshot + console logs)
    if (e.altKey && !e.ctrlKey && e.shiftKey && (e.key === 'i' || e.key === 'I')) {
        e.preventDefault();
        e.stopPropagation();
        console.log('[DebugCapture] Alt+Shift+I pressed');
        captureDebugInfo();
        return;
    }

    // Escape: Deactivate element inspector
    if (e.key === 'Escape' && elementInspectorActive) {
        e.preventDefault();
        deactivateElementInspector();
    }
});

// Shutter effect for screenshot feedback
function showShutterEffect() {
    const shutter = document.createElement('div');
    shutter.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: white;
        opacity: 0.8;
        z-index: 99999;
        pointer-events: none;
        animation: shutterFlash 0.3s ease-out forwards;
    `;

    // Add keyframes if not exists
    if (!document.getElementById('shutter-keyframes')) {
        const style = document.createElement('style');
        style.id = 'shutter-keyframes';
        style.textContent = `
            @keyframes shutterFlash {
                0% { opacity: 0.8; }
                100% { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(shutter);
    setTimeout(() => shutter.remove(), 300);
}

// Capture debug info: figure image first, then console logs after delay
async function captureDebugInfo() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Show shutter effect
    showShutterEffect();

    // Step 1: Copy figure image to clipboard first
    try {
        const img = document.getElementById('preview-image');
        if (img && img.src) {
            const response = await fetch(img.src);
            const blob = await response.blob();
            await navigator.clipboard.write([
                new ClipboardItem({ [blob.type]: blob })
            ]);
            showToast('Image copied! Paste now. Text in 2s...', 'success');
            console.log('[DebugCapture] Image copied to clipboard');
        } else {
            showToast('No figure found, copying text only...', 'warning');
        }
    } catch (err) {
        console.error('[DebugCapture] Image copy failed:', err);
        showToast('Image copy failed, copying text...', 'warning');
    }

    // Step 2: Wait 2 seconds, then copy debug text
    setTimeout(async () => {
        let debugInfo = `=== Debug Capture: ${timestamp} ===\\n\\n`;

        // Collect console logs
        debugInfo += '=== Console Logs ===\\n';
        if (window.consoleLogs && window.consoleLogs.length > 0) {
            window.consoleLogs.forEach(log => {
                debugInfo += `[${log.type}] ${log.message}\\n`;
            });
        } else {
            debugInfo += '(No logs captured)\\n';
        }

        // Add current state info
        debugInfo += '\\n=== Current State ===\\n';
        debugInfo += `URL: ${window.location.href}\\n`;
        debugInfo += `Selected Element: ${selectedElement ? selectedElement.key : 'None'}\\n`;
        debugInfo += `Zoom Level: ${Math.round(zoomLevel * 100)}%\\n`;
        debugInfo += `Theme: ${document.body.getAttribute('data-theme') || 'light'}\\n`;

        try {
            await navigator.clipboard.writeText(debugInfo);
            showToast('Debug text copied! Paste now.', 'success');
            console.log('[DebugCapture] Text copied:', debugInfo);
        } catch (err) {
            console.error('[DebugCapture] Text copy failed:', err);
            showToast('Text copy failed: ' + err.message, 'error');
        }
    }, 2000);
}

// Console log interceptor (captures logs for debug export)
window.consoleLogs = [];
const originalConsole = {
    log: console.log,
    warn: console.warn,
    error: console.error
};

console.log = function(...args) {
    window.consoleLogs.push({ type: 'LOG', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.log.apply(console, args);
};

console.warn = function(...args) {
    window.consoleLogs.push({ type: 'WARN', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.warn.apply(console, args);
};

console.error = function(...args) {
    window.consoleLogs.push({ type: 'ERROR', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.error.apply(console, args);
};

console.log('[ElementInspector] Loaded - Press Alt+I to toggle');
console.log('[DebugCapture] Loaded - Press Alt+Shift+I for screenshot + logs');

// ==================== FILE SWITCHER ====================
// Allows switching between recipe files without restarting the server

let currentFilePath = null;

async function loadFileList() {
    const selector = document.getElementById('file-selector');
    if (!selector) return;

    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            selector.innerHTML = '<option value="">No files found</option>';
            return;
        }

        const data = await response.json();
        const files = data.files || [];
        currentFilePath = data.current_file;

        if (files.length === 0) {
            selector.innerHTML = '<option value="">(No recipe files in directory)</option>';
            return;
        }

        // Build options
        let optionsHtml = '';
        if (!currentFilePath) {
            optionsHtml += '<option value="" selected>(Unsaved figure)</option>';
        }

        files.forEach(file => {
            const isCurrent = file.is_current;
            const icon = file.has_image ? '📊 ' : '📄 ';
            const selected = isCurrent ? ' selected' : '';
            optionsHtml += `<option value="${file.path}"${selected}>${icon}${file.name}</option>`;
        });

        selector.innerHTML = optionsHtml;

        console.log('[FileSwitcher] Loaded', files.length, 'files');

    } catch (error) {
        console.error('[FileSwitcher] Error loading files:', error);
        selector.innerHTML = '<option value="">Error loading files</option>';
    }
}

async function switchToFile(filePath) {
    if (!filePath || filePath === currentFilePath) return;

    showToast('Loading figure...', 'info');

    try {
        const response = await fetch('/api/switch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to switch file');
        }

        const data = await response.json();

        // Update preview image
        const img = document.getElementById('preview-image');
        if (img && data.image) {
            img.src = 'data:image/png;base64,' + data.image;
        }

        // Update bboxes
        if (data.bboxes) {
            window.currentBboxes = data.bboxes;
        }

        // Update color map for hitmap
        if (data.color_map) {
            window.currentColorMap = data.color_map;
        }

        // Update current file path
        currentFilePath = filePath;

        // Clear selection
        clearElementHighlights();
        document.getElementById('selected-element-panel')?.style.setProperty('display', 'none');

        showToast('Loaded: ' + filePath, 'success');
        console.log('[FileSwitcher] Switched to:', filePath);

        // Reload file list to update selection state
        loadFileList();

    } catch (error) {
        console.error('[FileSwitcher] Error switching file:', error);
        showToast('Error: ' + error.message, 'error');
        // Revert selector
        loadFileList();
    }
}

function initFileSwitcher() {
    const selector = document.getElementById('file-selector');
    const newBtn = document.getElementById('btn-new-figure');

    if (selector) {
        selector.addEventListener('change', (e) => {
            const filePath = e.target.value;
            if (filePath) {
                switchToFile(filePath);
            }
        });
    }

    if (newBtn) {
        newBtn.addEventListener('click', () => {
            showToast('New figure: Use fr.edit() to create a new figure', 'info');
            // Future: could implement creating a new blank figure via API
        });
    }

    // Load file list on init
    loadFileList();
}

// Initialize file switcher after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFileSwitcher);
} else {
    initFileSwitcher();
}

console.log('[FileSwitcher] Loaded - Use dropdown to switch figures');
"""

__all__ = ["SCRIPTS"]
