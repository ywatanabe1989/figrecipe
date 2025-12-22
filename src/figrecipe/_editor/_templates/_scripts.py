#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript for figure editor.
"""

SCRIPTS = """
// State
let currentBboxes = initialBboxes;
let colorMap = initialColorMap;
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

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeValues();
    initializeEventListeners();
    loadHitmap();

    // Update hit regions on window resize
    window.addEventListener('resize', updateHitRegions);

    // Update hit regions when preview image loads
    const previewImg = document.getElementById('preview-image');
    previewImg.addEventListener('load', updateHitRegions);

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
    document.getElementById('btn-show-hitmap').addEventListener('click', toggleHitmapOverlay);

    // Download buttons
    document.getElementById('btn-download-png').addEventListener('click', () => downloadFigure('png'));
    document.getElementById('btn-download-svg').addEventListener('click', () => downloadFigure('svg'));
    document.getElementById('btn-download-pdf').addEventListener('click', () => downloadFigure('pdf'));

    // Check initial override status
    checkOverrideStatus();

    // Check modified states after initial values are set
    setTimeout(updateAllModifiedStates, 100);
}

// Load hitmap for element detection
async function loadHitmap() {
    try {
        const response = await fetch('/hitmap');
        const data = await response.json();

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
            overlay.src = hitmapImg.src;
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
    const imgRect = img.getBoundingClientRect();
    const wrapperRect = img.parentElement.getBoundingClientRect();

    // Calculate offset of image within wrapper
    const offsetX = imgRect.left - wrapperRect.left;
    const offsetY = imgRect.top - wrapperRect.top;

    // Scale factors from image natural size to display size
    const scaleX = imgRect.width / img.naturalWidth;
    const scaleY = imgRect.height / img.naturalHeight;

    console.log('Drawing hit regions:', Object.keys(currentBboxes).length, 'elements');
    console.log('Image natural:', img.naturalWidth, 'x', img.naturalHeight);
    console.log('Image display:', imgRect.width, 'x', imgRect.height);
    console.log('Scale:', scaleX, scaleY);

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
            if (bbox.original_color) {
                shape.style.setProperty('--element-color', bbox.original_color);
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
            if (bbox.original_color) {
                shape.style.setProperty('--element-color', bbox.original_color);
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
            } else if (bbox.type === 'title' || bbox.type === 'xlabel' || bbox.type === 'ylabel') {
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
            if (bbox.original_color) {
                shape.style.setProperty('--element-color', bbox.original_color);
            }

            labelX = x + 2;
            labelY = y - 3;
        }

        // Add hover and click handlers
        shape.addEventListener('mouseenter', () => handleHitRegionHover(key, bbox));
        shape.addEventListener('mouseleave', () => handleHitRegionLeave());
        shape.addEventListener('click', (e) => handleHitRegionClick(e, key, bbox));

        group.appendChild(shape);

        // Create label
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', labelX);
        label.setAttribute('y', labelY);
        label.setAttribute('class', 'hitregion-label');
        label.textContent = `${bbox.type || 'element'}: ${bbox.label || key}`;
        group.appendChild(label);

        overlay.appendChild(group);
    }

    // Also draw colorMap elements (from hitmap)
    for (const [key, info] of Object.entries(colorMap)) {
        // Skip if already in bboxes
        if (currentBboxes[key]) continue;

        // ColorMap entries without bboxes - show as small indicator
        console.log('ColorMap element without bbox:', key, info);
    }
}

// Handle hover on hit region
function handleHitRegionHover(key, bbox) {
    // Track hovered element for click priority
    hoveredElement = { key, ...bbox };

    const info = document.getElementById('selected-info');
    info.textContent = `Hover: ${bbox.type || 'element'} (${bbox.label || key})`;
}

// Handle leaving hit region
function handleHitRegionLeave() {
    hoveredElement = null;

    const info = document.getElementById('selected-info');
    if (selectedElement) {
        info.textContent = `Selected: ${selectedElement.type} (${selectedElement.label || selectedElement.key})`;
    } else {
        info.textContent = 'Click on an element to select it';
    }
}

// Handle click on hit region with Alt+Click cycling support
function handleHitRegionClick(event, key, bbox) {
    event.stopPropagation();
    event.preventDefault();  // Prevent browser default Alt+Click behavior

    const element = { key, ...bbox };
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
        for (const [key, info] of Object.entries(colorMap)) {
            if (info.rgb[0] === r && info.rgb[1] === g && info.rgb[2] === b) {
                console.log(`Found element via hitmap: ${key} (${info.type})`);
                return { key, ...info };
            }
        }
        console.log('No matching element in colorMap for this color');
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

// Select an element
function selectElement(element) {
    selectedElement = element;

    // Update info display
    const info = document.getElementById('selected-info');
    info.textContent = `Selected: ${element.type} (${element.label || element.key})`;

    // Draw selection overlay
    drawSelection(element.key);

    // Sync properties panel to show relevant section
    syncPropertiesToElement(element);
}

// Sync properties panel to selected element
function syncPropertiesToElement(element) {
    // Map element types to section IDs
    const sectionMap = {
        'axes': 'section-dimensions',
        'line': 'section-lines',
        'scatter': 'section-lines',
        'bar': 'section-lines',
        'fill': 'section-lines',
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
}

// Clear selection
function clearSelection() {
    selectedElement = null;
    document.getElementById('selected-info').textContent = 'Click on an element to select it';
    clearSelectionOverlay();

    // Clear section and field highlights
    document.querySelectorAll('.section-highlighted').forEach(s => s.classList.remove('section-highlighted'));
    document.querySelectorAll('.field-highlighted').forEach(f => f.classList.remove('field-highlighted'));
}

// Draw selection rectangle
function drawSelection(key) {
    const overlay = document.getElementById('selection-overlay');
    overlay.innerHTML = '';

    const bbox = currentBboxes[key];
    if (!bbox) return;

    // Get preview image dimensions and position
    const img = document.getElementById('preview-image');
    const imgRect = img.getBoundingClientRect();
    const wrapperRect = img.parentElement.getBoundingClientRect();

    // Scale bbox to display coordinates
    const scaleX = imgRect.width / img.naturalWidth;
    const scaleY = imgRect.height / img.naturalHeight;

    const x = (imgRect.left - wrapperRect.left) + bbox.x * scaleX;
    const y = (imgRect.top - wrapperRect.top) + bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('class', 'selection-rect');

    overlay.appendChild(rect);
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
"""

__all__ = ["SCRIPTS"]
