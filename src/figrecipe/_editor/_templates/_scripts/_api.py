#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API calls JavaScript for the figure editor.

This module contains the JavaScript code for:
- Preview update and refresh
- Form data collection
- Save/reset/restore operations
- Override status management
- Download functionality
"""

SCRIPTS_API = """
// ===== API CALLS AND SERVER COMMUNICATION =====

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

        // Reload hitmap and redraw hit regions
        loadHitmap();
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
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

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

            clearSelection();
            hideOverrideStatus();
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

    if (statusEl) statusEl.style.display = 'flex';

    if (timestampEl && timestamp) {
        const date = new Date(timestamp);
        timestampEl.textContent = 'Last modified: ' + date.toLocaleString();
    }
}

// Hide override status indicator
function hideOverrideStatus() {
    const statusEl = document.getElementById('override-status');
    if (statusEl) statusEl.style.display = 'none';
}

// Update override status after save
async function updateOverrideStatusAfterSave(data) {
    if (data.has_overrides) {
        showOverrideStatus(data.timestamp);
    }
}
"""

__all__ = ["SCRIPTS_API"]

# EOF
