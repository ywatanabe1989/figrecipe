#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable clipboard operations JavaScript - copy, paste, cut."""

JS_DATATABLE_CLIPBOARD = """
// ============================================================================
// Clipboard Operations (Copy, Paste, Cut)
// ============================================================================
let datatableCopiedRange = null;  // Track copied cell range for marching ants
let datatableIsCutOperation = false;  // Track if it was cut (not copy)

function handleCopy(e) {
    if (!datatableSelectedCells || datatableEditMode) return;

    e.preventDefault();
    const text = getSelectedCellsAsTSV();
    e.clipboardData.setData('text/plain', text);

    // Store copied range and show marching ants
    datatableCopiedRange = { ...datatableSelectedCells };
    datatableIsCutOperation = false;
    showMarchingAnts();
}

function handleCut(e) {
    if (!datatableSelectedCells || datatableEditMode) return;

    e.preventDefault();
    const text = getSelectedCellsAsTSV();
    e.clipboardData.setData('text/plain', text);

    // Store cut range and show marching ants with faded cells
    datatableCopiedRange = { ...datatableSelectedCells };
    datatableIsCutOperation = true;
    showMarchingAnts();
}

// Show Excel-style marching ants border around copied/cut cells
function showMarchingAnts() {
    clearMarchingAnts();  // Clear any existing marching ants
    if (!datatableCopiedRange) return;

    const { startRow, startCol, endRow, endCol } = datatableCopiedRange;
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);

    for (let r = minRow; r <= maxRow; r++) {
        for (let c = minCol; c <= maxCol; c++) {
            const cell = document.querySelector(`td[data-row="${r}"][data-col="${c}"]`);
            if (!cell) continue;

            // Add border classes based on position in selection
            if (r === minRow) cell.classList.add('copy-border-top');
            if (r === maxRow) cell.classList.add('copy-border-bottom');
            if (c === minCol) cell.classList.add('copy-border-left');
            if (c === maxCol) cell.classList.add('copy-border-right');

            // Add faded effect for cut operation
            if (datatableIsCutOperation) {
                cell.classList.add('cut-pending');
            }
        }
    }
}

// Clear marching ants border
function clearMarchingAnts() {
    document.querySelectorAll('.copy-border-top, .copy-border-bottom, .copy-border-left, .copy-border-right, .cut-pending').forEach(cell => {
        cell.classList.remove('copy-border-top', 'copy-border-bottom', 'copy-border-left', 'copy-border-right', 'cut-pending');
    });
}

function handlePaste(e) {
    if (!datatableCurrentCell || datatableEditMode || !datatableData) return;

    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    if (!text) return;

    // If this was a cut operation, clear the source cells
    if (datatableIsCutOperation && datatableCopiedRange) {
        const { startRow, startCol, endRow, endCol } = datatableCopiedRange;
        const minRow = Math.min(startRow, endRow);
        const maxRow = Math.max(startRow, endRow);
        const minCol = Math.min(startCol, endCol);
        const maxCol = Math.max(startCol, endCol);

        for (let r = minRow; r <= maxRow; r++) {
            for (let c = minCol; c <= maxCol; c++) {
                if (datatableData.rows[r]) {
                    datatableData.rows[r][c] = '';
                }
            }
        }
    }

    const rows = text.split('\\n').map(line => line.split('\\t'));
    const startRow = datatableCurrentCell.row;
    const startCol = datatableCurrentCell.col;

    rows.forEach((rowData, rOffset) => {
        const targetRow = startRow + rOffset;
        if (targetRow >= datatableData.rows.length) return;

        rowData.forEach((value, cOffset) => {
            const targetCol = startCol + cOffset;
            if (targetCol >= datatableData.columns.length) return;

            // Preserve empty strings as empty (not convert to 0)
            if (value === '' || value === null || value === undefined) {
                datatableData.rows[targetRow][targetCol] = '';
            } else {
                const colType = datatableData.columns[targetCol]?.type;
                if (colType === 'numeric') {
                    const num = parseFloat(value);
                    datatableData.rows[targetRow][targetCol] = isNaN(num) ? value : num;
                } else {
                    datatableData.rows[targetRow][targetCol] = value;
                }
            }
        });
    });

    // Clear marching ants and reset cut state
    clearMarchingAnts();
    datatableCopiedRange = null;
    datatableIsCutOperation = false;

    renderDatatable();
    updateCellSelectionDisplay();
}

function getSelectedCellsAsTSV() {
    if (!datatableSelectedCells || !datatableData) return '';

    const { startRow, startCol, endRow, endCol } = datatableSelectedCells;
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);

    const lines = [];
    for (let r = minRow; r <= maxRow; r++) {
        const cells = [];
        for (let c = minCol; c <= maxCol; c++) {
            const value = datatableData.rows[r]?.[c];
            // Preserve None as "None" string for copy
            if (value === null || value === undefined) {
                cells.push('');
            } else {
                cells.push(String(value));
            }
        }
        lines.push(cells.join('\\t'));
    }
    return lines.join('\\n');
}
"""

__all__ = ["JS_DATATABLE_CLIPBOARD"]

# EOF
