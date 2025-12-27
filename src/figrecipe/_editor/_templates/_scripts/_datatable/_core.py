#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core datatable JavaScript: state, panel toggle, initialization."""

JS_DATATABLE_CORE = """
// ============================================================================
// Datatable Panel State
// ============================================================================
let datatableData = null;  // Parsed data: {columns: [...], rows: [...]}
let datatableSelectedColumns = new Set();  // Selected column indices
let datatablePlotType = 'plot';  // Default plot type
let datatableTargetAxis = null;  // null = new figure, 0+ = existing axis index
let datatableVarAssignments = {};  // Variable name -> column index mapping

// ============================================================================
// Panel Toggle
// ============================================================================
function toggleDatatablePanel() {
    const panel = document.getElementById('datatable-panel');
    if (panel) {
        panel.classList.toggle('expanded');
        localStorage.setItem('figrecipe_datatable_expanded', panel.classList.contains('expanded'));
    }
}

function initDatatablePanel() {
    const panel = document.getElementById('datatable-panel');
    const toggleBtn = document.getElementById('datatable-toggle');
    const closeBtn = document.getElementById('btn-close-datatable');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleDatatablePanel);
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', toggleDatatablePanel);
    }

    // Restore expanded state from localStorage
    const wasExpanded = localStorage.getItem('figrecipe_datatable_expanded');
    if (wasExpanded === 'true' && panel) {
        panel.classList.add('expanded');
    }

    // Initialize sub-modules
    initDatatableDropzone();
    initPlotTypeButtons();

    // Initialize plot button (New = create new panel)
    const plotBtn = document.getElementById('btn-datatable-plot');
    if (plotBtn) {
        plotBtn.addEventListener('click', () => {
            datatableTargetAxis = null;  // New panel
            plotFromVarAssignments();
        });
    }

    // Initialize split button dropdown
    initPlotDropdown();

    // Load existing data if available from figure
    loadExistingData();

    // Hook into canvas selection to sync with datatable
    hookCanvasSelection();
}

function hookCanvasSelection() {
    // Wrap the selectElement function to add datatable sync
    if (typeof window.selectElement === 'function') {
        const originalSelectElement = window.selectElement;
        window.selectElement = function(element) {
            originalSelectElement(element);
            if (typeof syncDatatableToElement === 'function') {
                syncDatatableToElement(element);
            }
        };
    }

    // Also hook clearSelection
    if (typeof window.clearSelection === 'function') {
        const originalClearSelection = window.clearSelection;
        window.clearSelection = function() {
            originalClearSelection();
            if (typeof clearDatatableHighlight === 'function') {
                clearDatatableHighlight();
            }
        };
    }
}

function initPlotDropdown() {
    const dropdownBtn = document.getElementById('btn-plot-dropdown');
    const dropdownMenu = document.getElementById('plot-dropdown-menu');
    if (!dropdownBtn || !dropdownMenu) return;

    // Toggle dropdown
    dropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
        if (dropdownMenu.classList.contains('show')) {
            populatePlotDropdown();
        }
    });

    // Close on outside click
    document.addEventListener('click', () => {
        dropdownMenu.classList.remove('show');
    });
}

function populatePlotDropdown() {
    const menu = document.getElementById('plot-dropdown-menu');
    if (!menu) return;

    fetch('/get_axes_positions').then(r => r.json()).then(data => {
        const axes = Object.keys(data)
            .filter(k => k.startsWith('ax_'))
            .sort((a, b) => {
                const matchA = a.match(/ax_(\\d+)_(\\d+)/);
                const matchB = b.match(/ax_(\\d+)_(\\d+)/);
                if (matchA && matchB) {
                    return parseInt(matchA[2]) - parseInt(matchB[2]) || parseInt(matchA[1]) - parseInt(matchB[1]);
                }
                return 0;
            });

        let html = '';
        axes.forEach((key, i) => {
            html += `<button class="dropdown-item" onclick="addToPanel(${i})">Add to P${i + 1}</button>`;
        });
        menu.innerHTML = html || '<div class="dropdown-item" style="color:var(--text-secondary)">No panels</div>';
    }).catch(() => {
        menu.innerHTML = '<div class="dropdown-item" style="color:var(--text-secondary)">No panels</div>';
    });
}

function addToPanel(axisIndex) {
    datatableTargetAxis = axisIndex;
    document.getElementById('plot-dropdown-menu').classList.remove('show');
    plotFromVarAssignments();
}

// ============================================================================
// Clear Data
// ============================================================================
function clearDatatableData() {
    datatableData = null;
    datatableSelectedColumns.clear();
    datatableVarAssignments = {};

    const content = document.getElementById('datatable-content');
    if (content) {
        content.innerHTML = '';
    }

    // Show dropzone again
    const dropzone = document.getElementById('datatable-dropzone');
    if (dropzone) dropzone.style.display = 'block';

    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'none';

    const varAssign = document.getElementById('datatable-var-assign');
    if (varAssign) varAssign.style.display = 'none';

    updateSelectionInfo();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDatatablePanel);
"""

__all__ = ["JS_DATATABLE_CORE"]

# EOF
