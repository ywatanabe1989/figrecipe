#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core state, initialization, and utility JavaScript for the figure editor."""

SCRIPTS_CORE = """
// ==================== CORE STATE & INITIALIZATION ====================

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

// ==================== UTILITY FUNCTIONS ====================

// Show toast notification
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

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Schedule update with debounce
function scheduleUpdate() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(async () => {
        const overrides = collectOverrides();
        try {
            const response = await fetch('/api/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(overrides)
            });

            if (response.ok) {
                const data = await response.json();
                // Update preview image
                const previewImg = document.getElementById('preview-image');
                previewImg.src = 'data:image/png;base64,' + data.image;

                // Update bboxes and hitmap
                currentBboxes = data.bboxes;
                colorMap = data.color_map;

                // Update image dimensions for hit detection
                currentImgWidth = data.img_width;
                currentImgHeight = data.img_height;

                // Update hit regions
                drawHitRegions();
                updateAllModifiedStates();
            }
        } catch (error) {
            console.error('Update failed:', error);
        }
    }, UPDATE_DEBOUNCE);
}

// ==================== END CORE ====================
"""

__all__ = ["SCRIPTS_CORE"]
