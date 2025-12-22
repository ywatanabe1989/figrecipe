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
const UPDATE_DEBOUNCE = 500;  // ms

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeValues();
    initializeEventListeners();
    loadHitmap();
});

// Initialize form values from server data
function initializeValues() {
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
                element.value = value;
            }
        }
    }
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

        input.addEventListener('change', scheduleUpdate);
        if (input.type === 'number' || input.type === 'text') {
            input.addEventListener('input', scheduleUpdate);
        }

        // Range slider value display
        if (input.type === 'range') {
            input.addEventListener('input', function() {
                const valueSpan = document.getElementById(this.id + '_value');
                if (valueSpan) valueSpan.textContent = this.value;
            });
        }
    });

    // Buttons
    document.getElementById('btn-refresh').addEventListener('click', updatePreview);
    document.getElementById('btn-reset').addEventListener('click', resetValues);
    document.getElementById('btn-save').addEventListener('click', saveOverrides);
    document.getElementById('btn-restore').addEventListener('click', restoreOriginal);

    // Download buttons
    document.getElementById('btn-download-png').addEventListener('click', () => downloadFigure('png'));
    document.getElementById('btn-download-svg').addEventListener('click', () => downloadFigure('svg'));
    document.getElementById('btn-download-pdf').addEventListener('click', () => downloadFigure('pdf'));

    // Check initial override status
    checkOverrideStatus();
}

// Load hitmap for element detection
async function loadHitmap() {
    try {
        const response = await fetch('/hitmap');
        const data = await response.json();

        colorMap = data.color_map;

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
        };
        hitmapImg.src = 'data:image/png;base64,' + data.image;
    } catch (error) {
        console.error('Failed to load hitmap:', error);
    }
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
    if (!hitmapLoaded) return null;

    // Scale to hitmap coordinates
    const scaleX = hitmapImg.width / imgWidth;
    const scaleY = hitmapImg.height / imgHeight;
    const hitmapX = Math.floor(imgX * scaleX);
    const hitmapY = Math.floor(imgY * scaleY);

    // Get pixel color
    try {
        const pixel = hitmapCtx.getImageData(hitmapX, hitmapY, 1, 1).data;
        const [r, g, b, a] = pixel;

        // Skip transparent or background
        if (a < 128) return null;
        if (r === 26 && g === 26 && b === 26) return null;  // Background
        if (r === 64 && g === 64 && b === 64) return null;  // Axes

        // Find element by RGB color
        for (const [key, info] of Object.entries(colorMap)) {
            if (info.rgb[0] === r && info.rgb[1] === g && info.rgb[2] === b) {
                return { key, ...info };
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

// Select an element
function selectElement(element) {
    selectedElement = element;

    // Update info display
    const info = document.getElementById('selected-info');
    info.textContent = `Selected: ${element.type} (${element.label || element.key})`;

    // Draw selection overlay
    drawSelection(element.key);
}

// Clear selection
function clearSelection() {
    selectedElement = null;
    document.getElementById('selected-info').textContent = 'Click on an element to select it';
    clearSelectionOverlay();
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

__all__ = ['SCRIPTS']
