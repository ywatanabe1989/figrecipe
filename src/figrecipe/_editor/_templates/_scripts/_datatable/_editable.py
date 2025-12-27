#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable editable table JavaScript - create and edit tables manually."""

JS_DATATABLE_EDITABLE = """
// ============================================================================
// Create New CSV (Empty Editable Table)
// ============================================================================
function createNewCSV() {
    // Create default structure with 3 columns and 5 rows (empty cells)
    const defaultData = {
        columns: [
            { name: 'col1', type: 'numeric', index: 0 },
            { name: 'col2', type: 'numeric', index: 1 },
            { name: 'col3', type: 'string', index: 2 }
        ],
        rows: [
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            ['', '', '']
        ]
    };

    // Set as current data
    datatableData = defaultData;
    datatableSelectedColumns = new Set();
    datatableVarAssignments = {};

    // Render editable table
    renderEditableTable();

    // Show toolbar
    const dropzone = document.getElementById('datatable-dropzone');
    const createNew = document.querySelector('.datatable-create-new');
    if (dropzone) dropzone.style.display = 'none';
    if (createNew) createNew.style.display = 'none';

    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'flex';

    updateVarAssignSlots();
}

// ============================================================================
// Render Editable Table
// ============================================================================
function renderEditableTable() {
    const content = document.getElementById('datatable-content');
    if (!content || !datatableData) return;

    const { columns, rows } = datatableData;

    let html = '<div class="editable-table-wrapper">';

    // Add column/row buttons
    html += '<div class="editable-table-actions">';
    html += '<button class="btn-small" onclick="addColumn()" title="Add column">+ Col</button>';
    html += '<button class="btn-small" onclick="addRow()" title="Add row">+ Row</button>';
    html += '<button class="btn-small btn-danger" onclick="removeLastColumn()" title="Remove last column">- Col</button>';
    html += '<button class="btn-small btn-danger" onclick="removeLastRow()" title="Remove last row">- Row</button>';
    html += '</div>';

    // Build editable table with scroll container for large tables
    html += '<div class="editable-table-scroll">';
    html += '<table class="datatable-table editable">';

    // Header row with editable column names
    html += '<thead><tr>';
    html += '<th class="row-num">#</th>';
    columns.forEach((col, idx) => {
        html += `<th>
            <div class="datatable-col-header editable-header">
                <input type="text" class="col-name-input" value="${col.name}"
                       onchange="updateColumnName(${idx}, this.value)"
                       onclick="event.stopPropagation()">
                <select class="col-type-select" onchange="updateColumnType(${idx}, this.value)">
                    <option value="numeric" ${col.type === 'numeric' ? 'selected' : ''}>N</option>
                    <option value="string" ${col.type === 'string' ? 'selected' : ''}>S</option>
                </select>
            </div>
        </th>`;
    });
    html += '</tr></thead>';

    // Data rows with editable cells
    html += '<tbody>';
    rows.forEach((row, rowIdx) => {
        html += '<tr>';
        html += `<td class="row-num">${rowIdx + 1}</td>`;
        columns.forEach((col, colIdx) => {
            const value = row[colIdx] !== null && row[colIdx] !== undefined ? row[colIdx] : '';
            const inputType = col.type === 'numeric' ? 'number' : 'text';
            html += `<td class="editable-cell">
                <input type="${inputType}" value="${value}"
                       onchange="updateCellValue(${rowIdx}, ${colIdx}, this.value)"
                       step="any">
            </td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    html += '</div>';  // Close scroll container

    html += '</div>';  // Close wrapper

    content.innerHTML = html;
    updateSelectionInfo();
}

// ============================================================================
// Table Editing Functions
// ============================================================================
function updateColumnName(colIdx, newName) {
    if (!datatableData || !datatableData.columns[colIdx]) return;
    datatableData.columns[colIdx].name = newName;
}

function updateColumnType(colIdx, newType) {
    if (!datatableData || !datatableData.columns[colIdx]) return;
    datatableData.columns[colIdx].type = newType;

    // Convert existing values if changing type
    datatableData.rows.forEach(row => {
        if (newType === 'numeric') {
            const val = parseFloat(row[colIdx]);
            row[colIdx] = isNaN(val) ? 0 : val;
        } else {
            row[colIdx] = String(row[colIdx] || '');
        }
    });

    renderEditableTable();
    updateVarAssignSlots();
}

function updateCellValue(rowIdx, colIdx, value) {
    if (!datatableData || !datatableData.rows[rowIdx]) return;

    const col = datatableData.columns[colIdx];
    if (col.type === 'numeric') {
        datatableData.rows[rowIdx][colIdx] = parseFloat(value) || 0;
    } else {
        datatableData.rows[rowIdx][colIdx] = value;
    }
}

function addColumn() {
    if (!datatableData) return;

    const newColIdx = datatableData.columns.length;
    const newColName = `col${newColIdx + 1}`;

    datatableData.columns.push({
        name: newColName,
        type: 'numeric',
        index: newColIdx
    });

    // Add empty value to all rows
    datatableData.rows.forEach(row => {
        row.push('');
    });

    renderEditableTable();
    updateVarAssignSlots();
}

function addRow() {
    if (!datatableData) return;

    // All cells start empty
    const newRow = datatableData.columns.map(() => '');
    datatableData.rows.push(newRow);

    renderEditableTable();
}

function removeLastColumn() {
    if (!datatableData || datatableData.columns.length <= 1) return;

    datatableData.columns.pop();
    datatableData.rows.forEach(row => row.pop());

    // Update column indices
    datatableData.columns.forEach((col, idx) => {
        col.index = idx;
    });

    renderEditableTable();
    updateVarAssignSlots();
}

function removeLastRow() {
    if (!datatableData || datatableData.rows.length <= 1) return;

    datatableData.rows.pop();
    renderEditableTable();
}
"""

__all__ = ["JS_DATATABLE_EDITABLE"]

# EOF
