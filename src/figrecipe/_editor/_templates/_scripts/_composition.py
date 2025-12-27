#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaScript for composition features (alignment, visibility, import)."""

SCRIPTS_COMPOSITION = """
// ============================================================
// Composition: Panel Visibility, Alignment, Distribution
// ============================================================

// Spinner helper functions (CSS-based using body.loading class)
function showSpinner(message) {
    const textEl = document.querySelector('.spinner-text');
    if (textEl && message) textEl.textContent = message;
    document.body.classList.add('loading');
}

function hideSpinner() {
    document.body.classList.remove('loading');
}

// Update preview image with new base64 data
function updatePreviewImage(imageBase64) {
    const img = document.getElementById('preview-image');
    if (img && imageBase64) {
        img.src = 'data:image/png;base64,' + imageBase64;
    }
}

// Update bounding boxes (refresh hit regions)
function updateBboxes(newBboxes) {
    if (typeof bboxes !== 'undefined' && newBboxes) {
        Object.assign(bboxes, newBboxes);
        if (typeof updateHitRegions === 'function') {
            updateHitRegions();
        }
    }
}

// Track panel visibility states
let panelVisibility = {};

// Initialize panel visibility from server
async function initPanelVisibility() {
    try {
        const response = await fetch('/api/panel-info');
        const data = await response.json();
        if (data.panels) {
            data.panels.forEach(panel => {
                const key = `${panel.position[0]}_${panel.position[1]}`;
                panelVisibility[key] = panel.visible;
            });
        }
    } catch (e) {
        console.error('Failed to init panel visibility:', e);
    }
}

// Toggle panel visibility
async function togglePanelVisibility(row, col) {
    const key = `${row}_${col}`;
    const currentVisible = panelVisibility[key] !== false;
    const newVisible = !currentVisible;

    showSpinner('Updating visibility...');
    try {
        const response = await fetch('/api/panel-visibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                position: [row, col],
                visible: newVisible
            })
        });
        const data = await response.json();
        if (data.success) {
            panelVisibility[key] = newVisible;
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
            console.log(`Panel (${row},${col}) visibility: ${newVisible}`);
        } else {
            console.error('Toggle visibility failed:', data.error);
        }
    } catch (e) {
        console.error('Toggle visibility error:', e);
    } finally {
        hideSpinner();
    }
}

// Hide panel
async function hidePanel(row, col) {
    showSpinner('Hiding panel...');
    try {
        const response = await fetch('/api/panel-visibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                position: [row, col],
                visible: false
            })
        });
        const data = await response.json();
        if (data.success) {
            panelVisibility[`${row}_${col}`] = false;
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
        }
    } catch (e) {
        console.error('Hide panel error:', e);
    } finally {
        hideSpinner();
    }
}

// Show panel
async function showPanel(row, col) {
    showSpinner('Showing panel...');
    try {
        const response = await fetch('/api/panel-visibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                position: [row, col],
                visible: true
            })
        });
        const data = await response.json();
        if (data.success) {
            panelVisibility[`${row}_${col}`] = true;
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
        }
    } catch (e) {
        console.error('Show panel error:', e);
    } finally {
        hideSpinner();
    }
}

// Align selected panels
async function alignPanels(mode) {
    const panels = getSelectedPanelPositions();
    if (panels.length < 2) {
        console.log('Need at least 2 panels selected for alignment');
        return;
    }

    showSpinner(`Aligning ${mode}...`);
    try {
        const response = await fetch('/api/align-panels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                panels: panels,
                mode: mode
            })
        });
        const data = await response.json();
        if (data.success) {
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
            console.log(`Aligned ${panels.length} panels: ${mode}`);
        } else {
            console.error('Align panels failed:', data.error);
        }
    } catch (e) {
        console.error('Align panels error:', e);
    } finally {
        hideSpinner();
    }
}

// Distribute panels evenly
async function distributePanels(direction) {
    const panels = getSelectedPanelPositions();
    if (panels.length < 2) {
        console.log('Need at least 2 panels selected for distribution');
        return;
    }

    showSpinner(`Distributing ${direction}...`);
    try {
        const response = await fetch('/api/distribute-panels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                panels: panels,
                direction: direction
            })
        });
        const data = await response.json();
        if (data.success) {
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
            console.log(`Distributed ${panels.length} panels: ${direction}`);
        } else {
            console.error('Distribute panels failed:', data.error);
        }
    } catch (e) {
        console.error('Distribute panels error:', e);
    } finally {
        hideSpinner();
    }
}

// Smart align all panels
async function smartAlign() {
    showSpinner('Smart aligning...');
    try {
        const response = await fetch('/api/smart-align', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        if (data.success) {
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
            console.log('Smart align complete');
        } else {
            console.error('Smart align failed:', data.error);
        }
    } catch (e) {
        console.error('Smart align error:', e);
    } finally {
        hideSpinner();
    }
}

// Import axes from another recipe
async function importPanel(sourcePath, sourceAxes, targetRow, targetCol) {
    showSpinner('Importing panel...');
    try {
        const response = await fetch('/api/import-panel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: sourcePath,
                source_axes: sourceAxes || 'ax_0_0',
                target_position: [targetRow, targetCol]
            })
        });
        const data = await response.json();
        if (data.success) {
            updatePreviewImage(data.image);
            updateBboxes(data.bboxes);
            console.log(`Imported ${sourceAxes} from ${sourcePath} to (${targetRow},${targetCol})`);
        } else {
            console.error('Import panel failed:', data.error);
        }
    } catch (e) {
        console.error('Import panel error:', e);
    } finally {
        hideSpinner();
    }
}

// Get positions of selected panels (from bboxes with 'axes_' prefix)
function getSelectedPanelPositions() {
    const positions = [];
    // Get all panel bboxes (axes_X_Y format)
    if (typeof bboxes !== 'undefined') {
        for (const key in bboxes) {
            if (key.startsWith('axes_')) {
                const parts = key.split('_');
                if (parts.length >= 3) {
                    const row = parseInt(parts[1]);
                    const col = parseInt(parts[2]);
                    positions.push([row, col]);
                }
            }
        }
    }
    return positions;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initPanelVisibility();
});
"""

__all__ = ["SCRIPTS_COMPOSITION"]
