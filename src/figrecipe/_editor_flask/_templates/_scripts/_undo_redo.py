#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Undo/Redo functionality for the figure editor.

This module provides a history stack for tracking changes and
enabling undo/redo operations with Ctrl+Z and Ctrl+Shift+Z.
"""

SCRIPTS_UNDO_REDO = """
// ==================== UNDO/REDO HISTORY ====================

// History state
const historyStack = [];
const redoStack = [];
const MAX_HISTORY = 50;  // Maximum number of undo steps
let isUndoRedoInProgress = false;  // Prevent recursive history recording

// Capture current state as a snapshot
function captureState() {
    const state = {
        overrides: collectOverrides(),
        panelPositions: typeof panelPositions !== 'undefined' ? JSON.parse(JSON.stringify(panelPositions)) : {},
        annotationPositions: typeof annotationPositions !== 'undefined' ? JSON.parse(JSON.stringify(annotationPositions)) : {},
        timestamp: Date.now()
    };
    return state;
}

// Compare two states for equality
function statesEqual(a, b) {
    return JSON.stringify(a.overrides) === JSON.stringify(b.overrides) &&
           JSON.stringify(a.panelPositions) === JSON.stringify(b.panelPositions) &&
           JSON.stringify(a.annotationPositions) === JSON.stringify(b.annotationPositions);
}

// Push current state to history (call before making changes)
function pushToHistory() {
    if (isUndoRedoInProgress) return;

    const state = captureState();

    // Don't push if identical to last state
    if (historyStack.length > 0) {
        const lastState = historyStack[historyStack.length - 1];
        if (statesEqual(lastState, state)) {
            return;
        }
    }

    historyStack.push(state);

    // Clear redo stack when new action is performed
    redoStack.length = 0;

    // Trim history if too long
    while (historyStack.length > MAX_HISTORY) {
        historyStack.shift();
    }

    updateUndoRedoButtons();
    console.log('[History] Pushed state, stack size:', historyStack.length);
}

// Apply a state snapshot to the form
async function applyState(state) {
    isUndoRedoInProgress = true;

    try {
        const overrides = state.overrides;

        for (const [key, value] of Object.entries(overrides)) {
            const element = document.getElementById(key);
            if (!element) continue;

            if (element.type === 'checkbox') {
                element.checked = Boolean(value);
            } else if (element.type === 'range') {
                element.value = value;
                const valueSpan = document.getElementById(key + '_value');
                if (valueSpan) valueSpan.textContent = value;
            } else if (element.type === 'color') {
                element.value = value;
            } else if (element.tagName === 'SELECT') {
                element.value = value;
            } else {
                element.value = value;
            }
        }

        // Restore panel positions if they differ
        if (state.panelPositions && typeof panelPositions !== 'undefined') {
            const axKeys = Object.keys(state.panelPositions).sort();
            for (let i = 0; i < axKeys.length; i++) {
                const axKey = axKeys[i];
                const savedPos = state.panelPositions[axKey];
                const currentPos = panelPositions[axKey];

                // Check if position changed
                if (currentPos && savedPos &&
                    (Math.abs(savedPos.left - currentPos.left) > 0.1 ||
                     Math.abs(savedPos.top - currentPos.top) > 0.1)) {
                    // Restore panel position via API
                    try {
                        await fetch('/update_axes_position', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                ax_index: i,
                                left: savedPos.left,
                                top: savedPos.top,
                                width: savedPos.width,
                                height: savedPos.height
                            })
                        });
                        // Update local panelPositions to match restored state
                        panelPositions[axKey] = { ...savedPos };
                    } catch (e) {
                        console.error('[History] Failed to restore panel position:', e);
                    }
                }
            }
        }

        // Restore annotation positions if they differ
        if (state.annotationPositions && typeof annotationPositions !== 'undefined') {
            let needsRefresh = false;
            for (const [key, savedPos] of Object.entries(state.annotationPositions)) {
                const currentPos = annotationPositions[key];

                // Check if position changed
                if (!currentPos ||
                    Math.abs(savedPos.x - (currentPos?.x || 0)) > 0.001 ||
                    Math.abs(savedPos.y - (currentPos?.y || 0)) > 0.001) {

                    // Parse key formats:
                    // "ax0_panel_label" -> axIndex=0, type=panel_label, textIndex=0
                    // "ax0_text_0" -> axIndex=0, type=text, textIndex=0
                    let axIndex, annotationType, textIndex;

                    if (key.includes('_panel_label')) {
                        const match = key.match(/ax(\\d+)_panel_label/);
                        if (match) {
                            axIndex = parseInt(match[1], 10);
                            annotationType = 'panel_label';
                            textIndex = 0;
                        }
                    } else if (key.includes('_text_')) {
                        const match = key.match(/ax(\\d+)_text_(\\d+)/);
                        if (match) {
                            axIndex = parseInt(match[1], 10);
                            annotationType = 'text';
                            textIndex = parseInt(match[2], 10);
                        }
                    }

                    if (axIndex !== undefined) {
                        try {
                            const response = await fetch('/update_annotation_position', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    ax_index: axIndex,
                                    annotation_type: annotationType,
                                    text_index: textIndex,
                                    x: savedPos.x,
                                    y: savedPos.y
                                })
                            });
                            const data = await response.json();

                            if (data.success && data.image) {
                                // Update preview image
                                const img = document.getElementById('preview-image');
                                if (img) {
                                    img.src = 'data:image/png;base64,' + data.image;
                                }
                                // Update bboxes
                                if (data.bboxes && typeof currentBboxes !== 'undefined') {
                                    currentBboxes = data.bboxes;
                                }
                                needsRefresh = true;
                            }

                            // Update local annotationPositions to match restored state
                            annotationPositions[key] = { ...savedPos };
                            console.log('[History] Restored annotation position:', key);
                        } catch (e) {
                            console.error('[History] Failed to restore annotation position:', e);
                        }
                    }
                }
            }

            // Refresh hitmap if positions were restored
            if (needsRefresh && typeof loadHitmap === 'function') {
                loadHitmap();
                if (typeof updateHitRegions === 'function') {
                    updateHitRegions();
                }
                if (typeof initAnnotationPositions === 'function') {
                    initAnnotationPositions();
                }
            }
        }

        // Update preview with the restored state
        updatePreview();

    } finally {
        isUndoRedoInProgress = false;
    }
}

// Undo last action
async function undo() {
    if (historyStack.length === 0) {
        showToast('Nothing to undo', 'info');
        return;
    }

    // Save current state to redo stack
    const currentState = captureState();
    redoStack.push(currentState);

    // Pop and apply previous state
    const previousState = historyStack.pop();
    await applyState(previousState);

    updateUndoRedoButtons();
    showToast('Undo', 'info');
    console.log('[History] Undo, remaining:', historyStack.length);
}

// Redo last undone action
async function redo() {
    if (redoStack.length === 0) {
        showToast('Nothing to redo', 'info');
        return;
    }

    // Save current state to history
    const currentState = captureState();
    historyStack.push(currentState);

    // Pop and apply redo state
    const redoState = redoStack.pop();
    await applyState(redoState);

    updateUndoRedoButtons();
    showToast('Redo', 'info');
    console.log('[History] Redo, remaining redo:', redoStack.length);
}

// Update undo/redo button states
function updateUndoRedoButtons() {
    const undoBtn = document.getElementById('btn-undo');
    const redoBtn = document.getElementById('btn-redo');

    if (undoBtn) {
        undoBtn.disabled = historyStack.length === 0;
        undoBtn.title = historyStack.length > 0
            ? `Undo (${historyStack.length} steps available)`
            : 'Nothing to undo';
    }

    if (redoBtn) {
        redoBtn.disabled = redoStack.length === 0;
        redoBtn.title = redoStack.length > 0
            ? `Redo (${redoStack.length} steps available)`
            : 'Nothing to redo';
    }
}

// Clear all history (e.g., when switching files)
function clearHistory() {
    historyStack.length = 0;
    redoStack.length = 0;
    updateUndoRedoButtons();
    console.log('[History] Cleared');
}

// Hook into form changes to record history
function initUndoRedo() {
    // Capture initial state
    pushToHistory();

    // Add change listeners to all form inputs
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.id === 'dark-mode-toggle') return;
        if (!input.id) return;

        // Capture state before change
        input.addEventListener('focus', () => {
            pushToHistory();
        });

        // For inputs without focus events (like range sliders)
        if (input.type === 'range') {
            let rangeStartValue = null;
            input.addEventListener('mousedown', () => {
                rangeStartValue = input.value;
                pushToHistory();
            });
        }

        // For select elements
        if (input.tagName === 'SELECT') {
            input.addEventListener('mousedown', () => {
                pushToHistory();
            });
        }
    });

    // Initialize button states
    updateUndoRedoButtons();

    console.log('[History] Undo/Redo initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUndoRedo);
} else {
    // Small delay to ensure other scripts have initialized
    setTimeout(initUndoRedo, 100);
}

// Add button click handlers after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const undoBtn = document.getElementById('btn-undo');
    const redoBtn = document.getElementById('btn-redo');

    if (undoBtn) {
        undoBtn.addEventListener('click', undo);
    }

    if (redoBtn) {
        redoBtn.addEventListener('click', redo);
    }
});

console.log('[UndoRedo] Module loaded - Ctrl+Z to undo, Ctrl+Shift+Z to redo');
"""

__all__ = ["SCRIPTS_UNDO_REDO"]

# EOF
