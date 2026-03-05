#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable cell selection JavaScript - multi-cell selection and highlights."""

JS_DATATABLE_SELECTION = """
// ============================================================================
// Cell Selection State
// ============================================================================
let datatableCurrentCell = null;  // { row, col } - active cell for input
let datatableSelectedCells = null;  // { startRow, startCol, endRow, endCol } - range
let datatableIsSelecting = false;  // Mouse drag selection in progress
let datatableEditMode = false;  // Cell is being edited

// ============================================================================
// Cell Event Listeners (Event Delegation Pattern - vis_app)
// ============================================================================
let datatableListenersAttached = false;

function attachCellEventListeners() {
    const table = document.querySelector('.datatable-table');
    if (!table || datatableListenersAttached) return;

    // Use event delegation - attach once to table, handle all cells
    // This is efficient for large tables (100+ rows)

    // Click to select cell (delegated)
    table.addEventListener('click', handleCellClick);

    // Double-click to edit (delegated)
    table.addEventListener('dblclick', handleCellDoubleClick);

    // Mouse drag for range selection (delegated)
    table.addEventListener('mousedown', handleMouseDown);

    // These need document-level for drag outside table
    if (!datatableListenersAttached) {
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    // Keyboard navigation and editing (delegated)
    table.addEventListener('keydown', handleCellKeydown);

    // Clipboard events (delegated)
    table.addEventListener('copy', handleCopy);
    table.addEventListener('paste', handlePaste);
    table.addEventListener('cut', handleCut);

    // Context menu (right-click)
    if (typeof attachContextMenuListener === 'function') {
        attachContextMenuListener();
    }

    datatableListenersAttached = true;
}

function handleCellClick(e) {
    const cell = e.target.closest('td[data-row][data-col]');
    if (!cell || datatableEditMode) return;

    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);

    if (e.shiftKey && datatableCurrentCell) {
        // Shift+click: extend selection
        datatableSelectedCells = {
            startRow: datatableCurrentCell.row,
            startCol: datatableCurrentCell.col,
            endRow: row,
            endCol: col
        };
    } else {
        // Regular click: single cell selection
        datatableCurrentCell = { row, col };
        datatableSelectedCells = {
            startRow: row, startCol: col, endRow: row, endCol: col
        };
    }

    updateCellSelectionDisplay();
    cell.focus();
}

function handleCellDoubleClick(e) {
    const cell = e.target.closest('td[data-row][data-col]');
    if (!cell) return;
    enterCellEditMode(cell);
}

function handleMouseDown(e) {
    const cell = e.target.closest('td[data-row][data-col]');
    if (!cell || datatableEditMode) return;

    datatableIsSelecting = true;
    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);
    datatableCurrentCell = { row, col };
    datatableSelectedCells = {
        startRow: row, startCol: col, endRow: row, endCol: col
    };
    updateCellSelectionDisplay();
}

function handleMouseMove(e) {
    if (!datatableIsSelecting) return;

    const elem = document.elementFromPoint(e.clientX, e.clientY);
    const cell = elem?.closest('td[data-row][data-col]');
    if (!cell) return;

    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);
    datatableSelectedCells.endRow = row;
    datatableSelectedCells.endCol = col;
    updateCellSelectionDisplay();
}

function handleMouseUp() {
    datatableIsSelecting = false;
}

// ============================================================================
// Cell Selection Display
// ============================================================================
function updateCellSelectionDisplay() {
    // Clear previous selection
    document.querySelectorAll('.datatable-table td.cell-selected').forEach(td => {
        td.classList.remove('cell-selected', 'cell-current');
    });

    if (!datatableSelectedCells) return;

    const { startRow, startCol, endRow, endCol } = datatableSelectedCells;
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);

    // Highlight selected range
    for (let r = minRow; r <= maxRow; r++) {
        for (let c = minCol; c <= maxCol; c++) {
            const cell = document.querySelector(
                `td[data-row="${r}"][data-col="${c}"]`
            );
            if (cell) cell.classList.add('cell-selected');
        }
    }

    // Mark current cell
    if (datatableCurrentCell) {
        const current = document.querySelector(
            `td[data-row="${datatableCurrentCell.row}"][data-col="${datatableCurrentCell.col}"]`
        );
        if (current) current.classList.add('cell-current');
    }
}

function moveToNextCell(deltaRow, deltaCol) {
    if (!datatableCurrentCell || !datatableData) return;

    let newRow = datatableCurrentCell.row + deltaRow;
    let newCol = datatableCurrentCell.col + deltaCol;

    // Wrap around columns
    if (newCol >= datatableData.columns.length) {
        newCol = 0;
        newRow++;
    } else if (newCol < 0) {
        newCol = datatableData.columns.length - 1;
        newRow--;
    }

    // Clamp rows
    const maxRows = Math.min(datatableData.rows.length, 100);
    newRow = Math.max(0, Math.min(newRow, maxRows - 1));

    datatableCurrentCell = { row: newRow, col: newCol };
    datatableSelectedCells = {
        startRow: newRow, startCol: newCol, endRow: newRow, endCol: newCol
    };
    updateCellSelectionDisplay();

    const nextCell = document.querySelector(
        `td[data-row="${newRow}"][data-col="${newCol}"]`
    );
    if (nextCell) nextCell.focus();
}

// Calculate next cell position (shared by both functions)
function calculateNextPosition(mode, reverse) {
    if (!datatableCurrentCell || !datatableData) return null;

    const maxRows = Math.min(datatableData.rows.length, datatableRenderedRows || 100) - 1;
    const maxCols = datatableData.columns.length - 1;

    // Get selection bounds (or just current cell if no selection)
    let minRow = 0, minCol = 0, selMaxRow = maxRows, selMaxCol = maxCols;
    const hasRangeSelection = datatableSelectedCells &&
        (datatableSelectedCells.startRow !== datatableSelectedCells.endRow ||
         datatableSelectedCells.startCol !== datatableSelectedCells.endCol);

    if (hasRangeSelection) {
        minRow = Math.min(datatableSelectedCells.startRow, datatableSelectedCells.endRow);
        selMaxRow = Math.max(datatableSelectedCells.startRow, datatableSelectedCells.endRow);
        minCol = Math.min(datatableSelectedCells.startCol, datatableSelectedCells.endCol);
        selMaxCol = Math.max(datatableSelectedCells.startCol, datatableSelectedCells.endCol);
    }

    let { row, col } = datatableCurrentCell;

    if (mode === 'tab') {
        // Tab: horizontal movement (left-to-right, wrap to next row)
        if (!reverse) {
            if (col < selMaxCol) {
                col++;
            } else {
                col = minCol;
                row = row < selMaxRow ? row + 1 : minRow;
            }
        } else {
            if (col > minCol) {
                col--;
            } else {
                col = selMaxCol;
                row = row > minRow ? row - 1 : selMaxRow;
            }
        }
    } else {
        // Enter: vertical movement (top-to-bottom, wrap to next column)
        if (!reverse) {
            if (row < selMaxRow) {
                row++;
            } else {
                row = minRow;
                col = col < selMaxCol ? col + 1 : minCol;
            }
        } else {
            if (row > minRow) {
                row--;
            } else {
                row = selMaxRow;
                col = col > minCol ? col - 1 : selMaxCol;
            }
        }
    }

    return { row, col, hasRangeSelection };
}

// Smart Tab/Enter navigation (vis_app pattern) - selection mode only (no edit)
// Tab: horizontal (left-to-right, wrap to next row)
// Enter: vertical (top-to-bottom, wrap to next column)
function navigateWithTabEnter(mode, reverse) {
    const result = calculateNextPosition(mode, reverse);
    if (!result) return;

    const { row, col, hasRangeSelection } = result;

    datatableCurrentCell = { row, col };

    // If we have a range selection, keep it; otherwise move selection too
    if (!hasRangeSelection) {
        datatableSelectedCells = {
            startRow: row, startCol: col, endRow: row, endCol: col
        };
    }

    updateCellSelectionDisplay();

    const nextCell = document.querySelector(`td[data-row="${row}"][data-col="${col}"]`);
    if (nextCell) nextCell.focus();
}

// Smart Tab/Enter navigation AND enter edit mode (scitex-cloud pattern)
// Used when exiting edit mode with Tab/Enter to continue editing in next cell
function navigateWithTabEnterAndEdit(mode, reverse) {
    const result = calculateNextPosition(mode, reverse);
    if (!result) return;

    const { row, col, hasRangeSelection } = result;

    datatableCurrentCell = { row, col };

    // If we have a range selection, keep it; otherwise move selection too
    if (!hasRangeSelection) {
        datatableSelectedCells = {
            startRow: row, startCol: col, endRow: row, endCol: col
        };
    }

    updateCellSelectionDisplay();

    const nextCell = document.querySelector(`td[data-row="${row}"][data-col="${col}"]`);
    if (nextCell) {
        // Enter edit mode on the next cell (scitex-cloud behavior)
        enterCellEditMode(nextCell);
    }
}

// ============================================================================
// Keyboard Navigation
// ============================================================================
function handleCellKeydown(e) {
    if (datatableEditMode) return;

    const cell = e.target.closest('td[data-row][data-col]');
    if (!cell) return;

    switch (e.key) {
        case 'ArrowUp':
            e.preventDefault();
            moveToNextCell(-1, 0);
            break;
        case 'ArrowDown':
            e.preventDefault();
            moveToNextCell(1, 0);
            break;
        case 'ArrowLeft':
            e.preventDefault();
            moveToNextCell(0, -1);
            break;
        case 'ArrowRight':
            e.preventDefault();
            moveToNextCell(0, 1);
            break;
        case 'Tab':
            e.preventDefault();
            navigateWithTabEnter('tab', e.shiftKey);
            break;
        case 'Enter':
            e.preventDefault();
            navigateWithTabEnter('enter', e.shiftKey);
            break;
        case 'F2':
            e.preventDefault();
            enterCellEditMode(cell);
            break;
        case 'Delete':
        case 'Backspace':
            e.preventDefault();
            clearSelectedCells();
            break;
        default:
            // Type to start editing
            if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
                enterCellEditMode(cell);
            }
    }
}

function clearSelectedCells() {
    if (!datatableSelectedCells || !datatableData) return;

    const { startRow, startCol, endRow, endCol } = datatableSelectedCells;
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

    renderDatatable();
    updateCellSelectionDisplay();
}

// ============================================================================
// Shortcuts Info Popup
// ============================================================================
let shortcutsPopup = null;

function showShortcutsPopup() {
    if (!shortcutsPopup) {
        shortcutsPopup = document.createElement('div');
        shortcutsPopup.className = 'shortcuts-popup';
        shortcutsPopup.innerHTML = `
            <div class="shortcuts-header">
                <h4>Keyboard Shortcuts</h4>
                <button class="btn-close" onclick="hideShortcutsPopup()">&times;</button>
            </div>
            <div class="shortcuts-content">
                <div class="shortcut-group">
                    <div class="shortcut-row"><kbd>Tab</kbd> Move right (wrap to next row)</div>
                    <div class="shortcut-row"><kbd>Shift+Tab</kbd> Move left</div>
                    <div class="shortcut-row"><kbd>Enter</kbd> Move down (wrap to next col)</div>
                    <div class="shortcut-row"><kbd>Shift+Enter</kbd> Move up</div>
                </div>
                <div class="shortcut-group">
                    <div class="shortcut-row"><kbd>F2</kbd> Edit cell</div>
                    <div class="shortcut-row"><kbd>Esc</kbd> Cancel edit</div>
                    <div class="shortcut-row"><kbd>Delete</kbd> Clear selected cells</div>
                </div>
                <div class="shortcut-group">
                    <div class="shortcut-row"><kbd>Ctrl+C</kbd> Copy</div>
                    <div class="shortcut-row"><kbd>Ctrl+X</kbd> Cut</div>
                    <div class="shortcut-row"><kbd>Ctrl+V</kbd> Paste</div>
                </div>
                <div class="shortcut-group">
                    <div class="shortcut-row"><kbd>Click</kbd> Select cell</div>
                    <div class="shortcut-row"><kbd>Shift+Click</kbd> Extend selection</div>
                    <div class="shortcut-row"><kbd>Drag</kbd> Range selection</div>
                    <div class="shortcut-row"><kbd>Right-click</kbd> Context menu</div>
                </div>
            </div>
        `;
        document.body.appendChild(shortcutsPopup);
    }
    shortcutsPopup.style.display = 'block';
}

function hideShortcutsPopup() {
    if (shortcutsPopup) {
        shortcutsPopup.style.display = 'none';
    }
}

// Attach shortcuts button listener
function initShortcutsButton() {
    const btn = document.getElementById('btn-shortcuts-info');
    if (btn) {
        btn.addEventListener('click', showShortcutsPopup);
    }
}

// Initialize on load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', initShortcutsButton);
}
"""

__all__ = ["JS_DATATABLE_SELECTION"]

# EOF
