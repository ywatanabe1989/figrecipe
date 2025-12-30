#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable inline cell editing JavaScript."""

JS_DATATABLE_CELL_EDIT = """
// ============================================================================
// Cell Editing (Inline Edit Mode)
// ============================================================================
let datatableEditingCell = null;  // Track which cell is being edited
let datatableSkipBlur = false;    // Flag to skip blur during Tab/Enter navigation

function enterCellEditMode(cell) {
    if (datatableEditMode) return;

    datatableEditMode = true;
    datatableEditingCell = cell;
    cell.classList.add('cell-editing');

    const span = cell.querySelector('.cell-text');
    const originalValue = span ? span.textContent : '';

    // Replace span with input
    cell.innerHTML = `<input type="text" class="cell-edit-input" value="${originalValue}">`;
    const input = cell.querySelector('input');
    input.focus();
    input.select();

    // Handle input events
    input.addEventListener('blur', (e) => {
        // Skip if Tab/Enter is handling navigation, or if this isn't the editing cell
        if (datatableSkipBlur || datatableEditingCell !== cell) {
            return;
        }
        if (datatableEditMode && datatableEditingCell === cell) {
            exitCellEditMode(cell, input.value, false);
        }
    });
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            datatableSkipBlur = true;  // Prevent blur from interfering
            exitCellEditMode(cell, input.value, true);
            navigateWithTabEnterAndEdit('enter', e.shiftKey);
            datatableSkipBlur = false;
        } else if (e.key === 'Escape') {
            e.preventDefault();
            exitCellEditMode(cell, originalValue, false);
        } else if (e.key === 'Tab') {
            e.preventDefault();
            datatableSkipBlur = true;  // Prevent blur from interfering
            exitCellEditMode(cell, input.value, true);
            navigateWithTabEnterAndEdit('tab', e.shiftKey);
            datatableSkipBlur = false;
        }
    });
}

function exitCellEditMode(cell, value, continueEditing = false) {
    if (!datatableEditMode) return;

    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);

    // Update data - preserve empty values as empty (not 0)
    if (datatableData && datatableData.rows[row]) {
        if (value === '' || value === null || value === undefined) {
            datatableData.rows[row][col] = '';
        } else {
            const colType = datatableData.columns[col]?.type;
            if (colType === 'numeric') {
                const num = parseFloat(value);
                datatableData.rows[row][col] = isNaN(num) ? value : num;
            } else {
                datatableData.rows[row][col] = value;
            }
        }
    }

    // Restore cell display with span wrapper
    const displayValue = value === null || value === undefined ? '' : value;
    cell.innerHTML = `<span class="cell-text">${displayValue}</span>`;
    cell.classList.remove('cell-editing');
    cell.setAttribute('title', displayValue);

    datatableEditMode = false;
    datatableEditingCell = null;  // Clear editing cell reference

    // Only focus this cell if we're NOT continuing to next cell
    if (!continueEditing) {
        cell.focus();
    }
}
"""

__all__ = ["JS_DATATABLE_CELL_EDIT"]

# EOF
