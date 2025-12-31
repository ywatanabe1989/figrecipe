#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable editable table JavaScript - create and edit tables manually."""

JS_DATATABLE_EDITABLE = """
// ============================================================================
// Create New CSV (Empty Editable Table)
// ============================================================================
const DEFAULT_ROWS = 100;  // Large table by default (vis_app uses 1000)
const DEFAULT_COLS = 5;
const ROWS_PER_BATCH = 100;  // Rows to load per scroll batch
const COLS_PER_BATCH = 20;   // Columns to load per scroll batch
let datatableRenderedRows = 0;  // Track how many rows are currently rendered
let datatableRenderedCols = 0;  // Track how many columns are currently rendered
let datatableIsLoadingMore = false;  // Prevent multiple concurrent loads

function createNewCSV() {
    // Create default structure with more columns and rows for real data entry
    const columns = [];
    for (let i = 0; i < DEFAULT_COLS; i++) {
        // Default to 'string' type so users can type anything (change to N if needed)
        columns.push({ name: `col${i + 1}`, type: 'string', index: i });
    }

    const rows = [];
    for (let i = 0; i < DEFAULT_ROWS; i++) {
        rows.push(new Array(DEFAULT_COLS).fill(''));
    }

    const defaultData = { columns, rows };

    // Set as current data
    datatableData = defaultData;
    datatableSelectedColumns = new Set();
    datatableVarAssignments = {};

    // Render editable table
    renderEditableTable();

    // Show toolbar, hide entire import section
    const importSection = document.getElementById('datatable-import-section');
    if (importSection) importSection.style.display = 'none';

    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'flex';

    updateVarAssignSlots();
}

// ============================================================================
// Render Editable Table (vis_app pattern: span cells, no inline inputs)
// Uses event delegation for cell selection, editing, and clipboard
// ============================================================================
function renderEditableTable() {
    const content = document.getElementById('datatable-content');
    if (!content || !datatableData) return;

    const { columns, rows } = datatableData;

    // Initial render: show first batch of columns
    const initialCols = Math.min(columns.length, COLS_PER_BATCH);
    datatableRenderedCols = initialCols;

    let html = '<div class="editable-table-wrapper">';

    // Build editable table with scroll container
    html += '<div class="editable-table-scroll">';
    html += '<table class="datatable-table editable" tabindex="0">';

    // Header row with editable column names and selection checkboxes
    html += '<thead><tr id="datatable-thead-row">';
    html += '<th class="row-num">#</th>';
    const elemColor = getCurrentTabElementColor();
    for (let idx = 0; idx < initialCols; idx++) {
        html += renderColumnHeader(idx, columns[idx], elemColor);
    }
    html += '</tr></thead>';

    // Data rows with span-wrapped cells (vis_app pattern)
    // Uses event delegation - no per-cell handlers
    html += '<tbody id="datatable-tbody">';
    // Initial render: show first batch of rows and columns
    const initialRows = Math.min(rows.length, ROWS_PER_BATCH);
    datatableRenderedRows = initialRows;
    const colsToRender = columns.slice(0, initialCols);
    for (let rowIdx = 0; rowIdx < initialRows; rowIdx++) {
        html += renderTableRow(rowIdx, colsToRender, rows[rowIdx]);
    }
    html += '</tbody></table>';
    html += '</div>';  // Close scroll container

    html += '</div>';  // Close wrapper

    content.innerHTML = html;

    // Attach event delegation listeners for selection/editing/clipboard
    if (typeof attachCellEventListeners === 'function') {
        attachCellEventListeners();
    }

    // Attach scroll listener for infinite scroll (both vertical and horizontal)
    attachScrollListener();

    updateSelectionInfo();

    // Restore cell selection display if any
    if (typeof updateCellSelectionDisplay === 'function') {
        updateCellSelectionDisplay();
    }
}

// Helper function to render a column header (with optional element color)
function renderColumnHeader(idx, col, elementColor = null) {
    const isSelected = datatableSelectedColumns && datatableSelectedColumns.has(idx);
    // Apply element color as left border if available
    const colorStyle = elementColor ? `style="border-left: 3px solid ${elementColor};"` : '';
    const colorClass = elementColor ? 'has-element-color' : '';
    return `<th class="${isSelected ? 'selected' : ''} ${colorClass}" data-col="${idx}" ${colorStyle}>
        <div class="datatable-col-header editable-header">
            <input type="checkbox"
                   data-col-idx="${idx}"
                   ${isSelected ? 'checked' : ''}
                   onchange="toggleColumnSelection(${idx}); renderEditableTable();">
            <input type="text" class="col-name-input" value="${col.name}"
                   onchange="updateColumnName(${idx}, this.value)"
                   onclick="event.stopPropagation()">
            <select class="col-type-select" onchange="updateColumnType(${idx}, this.value)"
                    title="${col.type === 'numeric' ? 'Numerical Column' : 'String Column'}">
                <option value="numeric" ${col.type === 'numeric' ? 'selected' : ''} title="Numerical Column">Num</option>
                <option value="string" ${col.type === 'string' ? 'selected' : ''} title="String Column">Str</option>
            </select>
        </div>
    </th>`;
}

// Get element color for current tab
function getCurrentTabElementColor() {
    if (!activeTabId || !datatableTabs[activeTabId]) return null;
    return datatableTabs[activeTabId].elementColor || null;
}

// Helper function to render a single row (renders all provided columns)
function renderTableRow(rowIdx, columns, rowData) {
    let html = `<tr data-row-idx="${rowIdx}">`;
    html += `<td class="row-num">${rowIdx + 1}</td>`;
    // Render all columns passed (caller controls which columns via slice)
    for (let colIdx = 0; colIdx < columns.length; colIdx++) {
        const col = columns[colIdx];
        const rawValue = rowData[colIdx];
        const value = rawValue !== null && rawValue !== undefined ? rawValue : '';
        const displayValue = formatCellValue(value, col.type);
        const isColSelected = datatableSelectedColumns && datatableSelectedColumns.has(colIdx);
        // title shows full precision on hover
        html += `<td data-row="${rowIdx}" data-col="${colIdx}" tabindex="0"
                    class="${isColSelected ? 'col-selected' : ''}" title="${value}" data-raw="${value}">
            <span class="cell-text">${displayValue}</span>
        </td>`;
    }
    html += '</tr>';
    return html;
}

// Smart cell value formatting (like Excel)
function formatCellValue(value, colType) {
    if (value === null || value === undefined || value === '') return '';

    // For numeric columns, apply smart precision
    if (colType === 'numeric' || typeof value === 'number') {
        const num = parseFloat(value);
        if (isNaN(num)) return String(value);

        // Integer check - show without decimals
        if (Number.isInteger(num)) return num.toString();

        // Scientific notation for very large/small numbers
        if (Math.abs(num) >= 1e10 || (Math.abs(num) < 1e-4 && num !== 0)) {
            return num.toExponential(3);
        }

        // Smart decimal places: show up to 4 significant decimal places
        // but remove trailing zeros
        const fixed = num.toFixed(6);
        // Remove trailing zeros after decimal point
        return parseFloat(fixed).toString();
    }

    // String values - truncate if too long
    const str = String(value);
    if (str.length > 30) {
        return str.substring(0, 27) + '...';
    }
    return str;
}

// Attach scroll listener for infinite scroll / lazy loading
function attachScrollListener() {
    const scrollContainer = document.querySelector('.editable-table-scroll');
    if (!scrollContainer) return;

    scrollContainer.addEventListener('scroll', handleTableScroll);
}

// Handle scroll event - load more rows/columns when near edges
function handleTableScroll(e) {
    if (datatableIsLoadingMore || !datatableData) return;

    const container = e.target;
    const { scrollTop, scrollHeight, clientHeight, scrollLeft, scrollWidth, clientWidth } = container;

    // Load more rows when within 100px of bottom
    if (scrollHeight - scrollTop - clientHeight < 100) {
        loadMoreRows();
    }

    // Load more columns when within 100px of right edge
    if (scrollWidth - scrollLeft - clientWidth < 100) {
        loadMoreColumns();
    }
}

// Check if the current table is an editable/new table (not plotted data)
function isEditableTable() {
    const table = document.querySelector('.datatable-table.editable');
    return table !== null;
}

// Load next batch of rows (or auto-expand for editable tables)
function loadMoreRows() {
    if (!datatableData || datatableIsLoadingMore) return;

    const { columns, rows } = datatableData;

    // For editable tables: auto-expand by adding new empty rows when at bottom
    if (datatableRenderedRows >= rows.length && isEditableTable()) {
        autoExpandRows();
        return;
    }

    if (datatableRenderedRows >= rows.length) return;  // All rows loaded (non-editable)

    datatableIsLoadingMore = true;

    const tbody = document.getElementById('datatable-tbody');
    if (!tbody) {
        datatableIsLoadingMore = false;
        return;
    }

    // Calculate next batch
    const startIdx = datatableRenderedRows;
    const endIdx = Math.min(startIdx + ROWS_PER_BATCH, rows.length);

    // Append new rows (only render columns up to datatableRenderedCols)
    let newRowsHtml = '';
    const colsToRender = columns.slice(0, datatableRenderedCols);
    for (let rowIdx = startIdx; rowIdx < endIdx; rowIdx++) {
        newRowsHtml += renderTableRow(rowIdx, colsToRender, rows[rowIdx]);
    }

    // Use insertAdjacentHTML for performance (doesn't re-parse existing DOM)
    tbody.insertAdjacentHTML('beforeend', newRowsHtml);

    datatableRenderedRows = endIdx;
    datatableIsLoadingMore = false;
}

// Auto-expand: add new empty rows to editable table when scrolling to bottom
function autoExpandRows() {
    if (!datatableData || datatableIsLoadingMore) return;

    datatableIsLoadingMore = true;

    const { columns, rows } = datatableData;
    const tbody = document.getElementById('datatable-tbody');
    if (!tbody) {
        datatableIsLoadingMore = false;
        return;
    }

    // Add ROWS_PER_BATCH new empty rows to data
    const startIdx = rows.length;
    for (let i = 0; i < ROWS_PER_BATCH; i++) {
        rows.push(new Array(columns.length).fill(''));
    }

    // Render the new rows
    let newRowsHtml = '';
    const colsToRender = columns.slice(0, datatableRenderedCols);
    for (let rowIdx = startIdx; rowIdx < rows.length; rowIdx++) {
        newRowsHtml += renderTableRow(rowIdx, colsToRender, rows[rowIdx]);
    }

    tbody.insertAdjacentHTML('beforeend', newRowsHtml);
    datatableRenderedRows = rows.length;
    datatableIsLoadingMore = false;
}

// Load next batch of columns (or auto-expand for editable tables)
function loadMoreColumns() {
    if (!datatableData || datatableIsLoadingMore) return;

    const { columns, rows } = datatableData;

    // For editable tables: auto-expand by adding new columns when at right edge
    if (datatableRenderedCols >= columns.length && isEditableTable()) {
        autoExpandColumns();
        return;
    }

    if (datatableRenderedCols >= columns.length) return;  // All columns loaded (non-editable)

    datatableIsLoadingMore = true;

    const theadRow = document.getElementById('datatable-thead-row');
    const tbody = document.getElementById('datatable-tbody');
    if (!theadRow || !tbody) {
        datatableIsLoadingMore = false;
        return;
    }

    // Calculate next batch of columns
    const startCol = datatableRenderedCols;
    const endCol = Math.min(startCol + COLS_PER_BATCH, columns.length);

    // Add new column headers
    let newHeadersHtml = '';
    const elemColor = getCurrentTabElementColor();
    for (let colIdx = startCol; colIdx < endCol; colIdx++) {
        newHeadersHtml += renderColumnHeader(colIdx, columns[colIdx], elemColor);
    }
    theadRow.insertAdjacentHTML('beforeend', newHeadersHtml);

    // Add cells to each existing row (use data-row-idx for actual row index)
    const existingRows = tbody.querySelectorAll('tr');
    existingRows.forEach((tr) => {
        const rowIdx = parseInt(tr.dataset.rowIdx);
        const rowData = rows[rowIdx];
        if (!rowData) return;  // Skip if row doesn't exist
        let newCellsHtml = '';
        for (let colIdx = startCol; colIdx < endCol; colIdx++) {
            const col = columns[colIdx];
            const rawValue = rowData[colIdx];
            const value = rawValue !== null && rawValue !== undefined ? rawValue : '';
            const displayValue = formatCellValue(value, col.type);
            const isColSelected = datatableSelectedColumns && datatableSelectedColumns.has(colIdx);
            newCellsHtml += `<td data-row="${rowIdx}" data-col="${colIdx}" tabindex="0"
                        class="${isColSelected ? 'col-selected' : ''}" title="${value}" data-raw="${value}">
                <span class="cell-text">${displayValue}</span>
            </td>`;
        }
        tr.insertAdjacentHTML('beforeend', newCellsHtml);
    });

    datatableRenderedCols = endCol;
    datatableIsLoadingMore = false;
}

// Auto-expand: add new empty columns to editable table when scrolling to right edge
function autoExpandColumns() {
    if (!datatableData || datatableIsLoadingMore) return;

    datatableIsLoadingMore = true;

    const { columns, rows } = datatableData;
    const theadRow = document.getElementById('datatable-thead-row');
    const tbody = document.getElementById('datatable-tbody');
    if (!theadRow || !tbody) {
        datatableIsLoadingMore = false;
        return;
    }

    // Add COLS_PER_BATCH new columns to data
    const startCol = columns.length;
    for (let i = 0; i < COLS_PER_BATCH; i++) {
        const newColIdx = columns.length;
        columns.push({
            name: `col${newColIdx + 1}`,
            type: 'string',
            index: newColIdx
        });
        // Add empty cell to all existing rows
        rows.forEach(row => row.push(''));
    }

    // Add new column headers
    let newHeadersHtml = '';
    const elemColor = getCurrentTabElementColor();
    for (let colIdx = startCol; colIdx < columns.length; colIdx++) {
        newHeadersHtml += renderColumnHeader(colIdx, columns[colIdx], elemColor);
    }
    theadRow.insertAdjacentHTML('beforeend', newHeadersHtml);

    // Add cells to each existing row
    const existingRows = tbody.querySelectorAll('tr');
    existingRows.forEach((tr) => {
        const rowIdx = parseInt(tr.dataset.rowIdx);
        const rowData = rows[rowIdx];
        if (!rowData) return;
        let newCellsHtml = '';
        for (let colIdx = startCol; colIdx < columns.length; colIdx++) {
            const col = columns[colIdx];
            newCellsHtml += `<td data-row="${rowIdx}" data-col="${colIdx}" tabindex="0" title="" data-raw="">
                <span class="cell-text"></span>
            </td>`;
        }
        tr.insertAdjacentHTML('beforeend', newCellsHtml);
    });

    datatableRenderedCols = columns.length;
    datatableIsLoadingMore = false;

    // Update var assignment slots to include new columns
    if (typeof updateVarAssignSlots === 'function') {
        updateVarAssignSlots();
    }
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
