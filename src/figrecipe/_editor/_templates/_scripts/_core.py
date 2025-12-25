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
let hitmapVisible = false;         // Hitmap overlay visibility (hover-only by default)
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

    // Draw hit regions - handle both already-loaded and loading images
    function initHitRegions() {
        if (previewImg.complete && previewImg.naturalWidth > 0) {
            console.log('Image already loaded, drawing hit regions');
            drawHitRegions();
        } else {
            console.log('Image not loaded yet, waiting...');
            setTimeout(initHitRegions, 100);
        }
    }
    setTimeout(initHitRegions, 50);

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

// ==================== EVENT LISTENERS ====================

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
    // Exclude panel position inputs - they have their own Apply button
    const panelPositionInputIds = ['panel_left', 'panel_top', 'panel_width', 'panel_height', 'panel_selector'];
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.id === 'dark-mode-toggle') return;
        if (panelPositionInputIds.includes(input.id)) return;  // Skip panel position inputs

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

    // Ctrl+Alt+I: Debug snapshot (screenshot + console logs)
    if (event.ctrlKey && event.altKey && (event.key === 'i' || event.key === 'I')) {
        event.preventDefault();
        event.stopPropagation();
        console.log('[DEBUG] Ctrl+Alt+I pressed, calling captureDebugSnapshot');
        if (typeof captureDebugSnapshot === 'function') {
            captureDebugSnapshot();
        } else {
            console.error('[DEBUG] captureDebugSnapshot is not defined!');
            showToast('Debug snapshot not available', 'error');
        }
        return;
    }

    // Ctrl+S: Save overrides
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        saveOverrides();
        showToast('Saved!', 'success');
        return;
    }

    // Ctrl+N: New blank figure
    if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        if (typeof createNewFigure === 'function') {
            createNewFigure();
        }
        return;
    }

    // Ctrl+Z: Undo
    if (event.ctrlKey && !event.shiftKey && event.key === 'z') {
        event.preventDefault();
        if (typeof undo === 'function') {
            undo();
        }
        return;
    }

    // Ctrl+Shift+Z or Ctrl+Y: Redo
    if ((event.ctrlKey && event.shiftKey && event.key === 'Z') ||
        (event.ctrlKey && event.key === 'y')) {
        event.preventDefault();
        if (typeof redo === 'function') {
            redo();
        }
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

// Note: scheduleUpdate() is defined in _api.py to avoid duplication
// It calls updatePreview() with debounce, which properly includes dark_mode

// ==================== END CORE ====================
"""

__all__ = ["SCRIPTS_CORE"]
