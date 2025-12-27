#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable table rendering JavaScript."""

JS_DATATABLE_TABLE = """
// ============================================================================
// Render Datatable
// ============================================================================
function renderDatatable() {
    const content = document.getElementById('datatable-content');
    if (!content || !datatableData) return;

    const { columns, rows } = datatableData;

    // Build table HTML
    let html = '<table class="datatable-table">';

    // Header row
    html += '<thead><tr>';
    html += '<th class="row-num">#</th>';
    columns.forEach((col, idx) => {
        const isSelected = datatableSelectedColumns.has(idx);
        html += `<th class="${isSelected ? 'selected' : ''}">
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
        html += '<tr>';
        html += `<td class="row-num">${i + 1}</td>`;
        columns.forEach((col, idx) => {
            const value = rows[i][idx];
            const displayValue = value === null || value === undefined ? '' : value;
            html += `<td title="${displayValue}">${displayValue}</td>`;
        });
        html += '</tr>';
    }
    html += '</tbody></table>';

    // Add row count info if truncated
    if (rows.length > 100) {
        html += `<div class="datatable-truncated">Showing 100 of ${rows.length} rows</div>`;
    }

    content.innerHTML = html;

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

    // Update header styling
    const th = document.querySelector(`th:has(input[data-col-idx="${colIdx}"])`);
    if (th) {
        th.classList.toggle('selected', datatableSelectedColumns.has(colIdx));
    }

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

    // Clear previous highlights
    document.querySelectorAll('.datatable-table th.canvas-linked').forEach(th => {
        th.classList.remove('canvas-linked');
    });

    if (!callId || !datatableData) return;

    // Find columns that match this call_id (column names like "callId_x", "callId_y")
    const columns = datatableData.columns || [];
    columns.forEach((col, idx) => {
        // Match if column name starts with callId or contains callId
        if (col.name.startsWith(callId + '_') || col.name === callId) {
            // Highlight column header (idx + 2 because of row-num column)
            const th = document.querySelector(`.datatable-table th:nth-child(${idx + 2})`);
            if (th) {
                th.classList.add('canvas-linked');
            }
        }
    });

    // Expand datatable panel if collapsed and has linked columns
    const panel = document.getElementById('datatable-panel');
    const hasLinked = document.querySelector('.datatable-table th.canvas-linked');
    if (hasLinked && panel && !panel.classList.contains('expanded')) {
        panel.classList.add('expanded');
    }
}

function clearDatatableHighlight() {
    datatableLinkedCallId = null;
    document.querySelectorAll('.datatable-table th.canvas-linked').forEach(th => {
        th.classList.remove('canvas-linked');
    });
}

// Full sync: highlight columns + auto-select plot type + set target panel
function syncDatatableToElement(element) {
    if (!element) {
        clearDatatableHighlight();
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
    if (typeof datatableTabs !== 'undefined' && callId) {
        for (const [tabId, tabState] of Object.entries(datatableTabs)) {
            if (tabState.callId === callId || tabState.name === callId) {
                if (activeTabId !== tabId && typeof selectTab === 'function') {
                    selectTab(tabId);
                }
                break;
            }
        }
    }
}
"""

__all__ = ["JS_DATATABLE_TABLE"]

# EOF
