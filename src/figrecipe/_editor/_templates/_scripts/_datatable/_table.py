#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable table rendering JavaScript with smart cell truncation."""

JS_DATATABLE_TABLE = """
// ============================================================================
// Render Datatable (with span-wrapped cells for smart truncation)
// ============================================================================
function renderDatatable() {
    const content = document.getElementById('datatable-content');
    if (!content || !datatableData) return;

    const { columns, rows } = datatableData;

    // Build table HTML with span-wrapped content (vis_app pattern)
    let html = '<table class="datatable-table" tabindex="0">';

    // Header row
    html += '<thead><tr>';
    html += '<th class="row-num">#</th>';
    columns.forEach((col, idx) => {
        const isSelected = datatableSelectedColumns.has(idx);
        html += `<th class="${isSelected ? 'selected' : ''}" data-col="${idx}">
            <div class="datatable-col-header">
                <input type="checkbox"
                       data-col-idx="${idx}"
                       ${isSelected ? 'checked' : ''}
                       onchange="toggleColumnSelection(${idx})">
                <span class="col-name" title="${col.name}">${col.name}</span>
                <span class="col-type">${col.type === 'numeric' ? 'N' : 'S'}</span>
            </div>
        </th>`;
    });
    html += '</tr></thead>';

    // Data rows (limit to first 100 for performance)
    html += '<tbody>';
    const maxRows = Math.min(rows.length, 100);
    for (let i = 0; i < maxRows; i++) {
        html += `<tr data-row-idx="${i}">`;
        html += `<td class="row-num">${i + 1}</td>`;
        columns.forEach((col, colIdx) => {
            const value = rows[i][colIdx];
            const displayValue = value === null || value === undefined ? '' : value;
            // Wrap in span for smart truncation without interfering with editing
            html += `<td data-row="${i}" data-col="${colIdx}" tabindex="0" title="${displayValue}">
                <span class="cell-text">${displayValue}</span>
            </td>`;
        });
        html += '</tr>';
    }
    html += '</tbody></table>';

    content.innerHTML = html;

    // Attach cell event listeners for selection/editing/clipboard
    if (typeof attachCellEventListeners === 'function') {
        attachCellEventListeners();
    }

    // Update selection info
    updateSelectionInfo();

    // Hide dropzone, show content
    const dropzone = document.getElementById('datatable-dropzone');
    if (dropzone) dropzone.style.display = 'none';
    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'flex';
}

// ============================================================================
// Column Selection (for backward compatibility)
// ============================================================================
function toggleColumnSelection(colIdx) {
    if (datatableSelectedColumns.has(colIdx)) {
        datatableSelectedColumns.delete(colIdx);
    } else {
        datatableSelectedColumns.add(colIdx);
    }

    const isSelected = datatableSelectedColumns.has(colIdx);

    // Update header styling
    const th = document.querySelector(`th:has(input[data-col-idx="${colIdx}"])`);
    if (th) {
        th.classList.toggle('selected', isSelected);
    }

    // Update entire column cells highlighting
    document.querySelectorAll(`td[data-col="${colIdx}"]`).forEach(td => {
        td.classList.toggle('col-selected', isSelected);
    });

    updateSelectionInfo();
}

function updateSelectionInfo() {
    const info = document.getElementById('datatable-selection-info');

    if (info) {
        // Count assigned variables
        const assignedCount = Object.keys(datatableVarAssignments).length;
        if (assignedCount > 0) {
            info.innerHTML = `<span class="selected-count">${assignedCount}</span> variable${assignedCount !== 1 ? 's' : ''} assigned`;
        } else {
            info.innerHTML = `<span class="selected-count">0</span> variables assigned`;
        }
    }
}

// ============================================================================
// Canvas-Datatable Linking: Highlight columns for selected canvas element
// ============================================================================
let datatableLinkedCallId = null;

function highlightDatatableForElement(callId) {
    datatableLinkedCallId = callId;

    // Clear previous highlights (headers and data cells)
    document.querySelectorAll('.datatable-table .canvas-linked').forEach(el => {
        el.classList.remove('canvas-linked');
    });

    if (!callId || !datatableData) return;

    const columns = datatableData.columns || [];
    const matchedIndices = [];

    // Strategy 1: Match columns by prefix pattern (e.g., scatter_x, scatter_y)
    columns.forEach((col, idx) => {
        if (col.name.startsWith(callId + '_') || col.name === callId) {
            matchedIndices.push(idx);
            // Highlight header
            const th = document.querySelector(`.datatable-table th:nth-child(${idx + 2})`);
            if (th) th.classList.add('canvas-linked');
        }
    });

    // Highlight data cells in matched columns
    matchedIndices.forEach(idx => {
        document.querySelectorAll(`.datatable-table tr td:nth-child(${idx + 2})`).forEach(td => {
            td.classList.add('canvas-linked');
        });
    });

    let hasMatch = matchedIndices.length > 0;

    // Strategy 2: If in a matching tab, highlight ALL columns in that tab
    // (handles shared x-data case for line plots where x column isn't prefixed)
    if (typeof datatableTabs !== 'undefined' && typeof activeTabId !== 'undefined') {
        const activeTab = datatableTabs[activeTabId];
        if (activeTab && (activeTab.callId === callId || activeTab.name === callId)) {
            columns.forEach((col, idx) => {
                // Highlight header
                const th = document.querySelector(`.datatable-table th:nth-child(${idx + 2})`);
                if (th) {
                    th.classList.add('canvas-linked');
                    hasMatch = true;
                }
                // Highlight data cells
                document.querySelectorAll(`.datatable-table tr td:nth-child(${idx + 2})`).forEach(td => {
                    td.classList.add('canvas-linked');
                });
            });
        }
    }

    // Expand datatable panel if collapsed and has linked columns
    const panel = document.getElementById('datatable-panel');
    if (hasMatch && panel && !panel.classList.contains('expanded')) {
        panel.classList.add('expanded');
    }
}

function clearDatatableHighlight() {
    datatableLinkedCallId = null;
    document.querySelectorAll('.datatable-table .canvas-linked').forEach(el => {
        el.classList.remove('canvas-linked');
    });
}

// Full sync: highlight columns + auto-select plot type + set target panel
function syncDatatableToElement(element) {
    if (!element) {
        clearDatatableHighlight();
        return;
    }

    // Skip highlighting for panel/axes selections - they don't have data columns
    const elemType = element.type || '';
    if (elemType === 'axes' || elemType === 'panel' || (element.label && element.label.startsWith('Panel '))) {
        console.log('[Highlight] Skipping panel/axes element');
        return;
    }

    const callId = element.call_id || element.label;

    // 1. Highlight matching columns
    highlightDatatableForElement(callId);

    // 2. Auto-select plot type if element has a function type
    if (element.function) {
        const plotSelect = document.getElementById('datatable-plot-type');
        if (plotSelect) {
            // Find matching option
            const options = plotSelect.querySelectorAll('option');
            for (const opt of options) {
                if (opt.value === element.function) {
                    plotSelect.value = element.function;
                    datatablePlotType = element.function;
                    if (typeof updateVarAssignSlots === 'function') updateVarAssignSlots();
                    break;
                }
            }
        }
    }

    // 3. Set target panel to the element's axis
    if (element.ax_index !== undefined) {
        const targetSelect = document.getElementById('datatable-target-panel');
        if (targetSelect) {
            targetSelect.value = element.ax_index;
            datatableTargetAxis = element.ax_index;
        }
    }

    // 4. Switch to matching datatable tab
    if (typeof datatableTabs !== 'undefined') {
        // Try multiple matching strategies
        const elemKey = element.key || '';
        const elemType = element.type || '';

        for (const [tabId, tabState] of Object.entries(datatableTabs)) {
            const tabName = (tabState.callId || tabState.name || '').toLowerCase();
            // Match: exact callId, name match, or element key contains tab name
            const matches = (callId && (tabState.callId === callId || tabState.name === callId)) ||
                           (elemKey && elemKey.toLowerCase().includes(tabName)) ||
                           (elemType && tabName.includes(elemType.toLowerCase()));
            if (matches) {
                if (activeTabId !== tabId && typeof selectTab === 'function') {
                    // Use internal flag to prevent sync loop
                    window._syncingFromCanvasToData = true;
                    selectTab(tabId);
                    window._syncingFromCanvasToData = false;
                    console.log('[Datatable] Canvas->Data: Switched to tab', tabName);
                }
                break;
            }
        }
    }
}
"""

__all__ = ["JS_DATATABLE_TABLE"]

# EOF
