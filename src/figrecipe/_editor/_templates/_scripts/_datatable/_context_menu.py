#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable right-click context menu JavaScript."""

JS_DATATABLE_CONTEXT_MENU = """
// ============================================================================
// Context Menu (Right-Click Menu)
// ============================================================================
let datatableContextMenu = null;

function createContextMenu() {
    if (datatableContextMenu) return;

    datatableContextMenu = document.createElement('div');
    datatableContextMenu.className = 'datatable-context-menu';
    datatableContextMenu.style.display = 'none';
    datatableContextMenu.innerHTML = `
        <div class="context-menu-item" data-action="cut">
            Cut<span class="shortcut">Ctrl+X</span>
        </div>
        <div class="context-menu-item" data-action="copy">
            Copy<span class="shortcut">Ctrl+C</span>
        </div>
        <div class="context-menu-item" data-action="paste">
            Paste<span class="shortcut">Ctrl+V</span>
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="clear">
            Clear cells<span class="shortcut">Del</span>
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="insert-row">
            Insert row below
        </div>
        <div class="context-menu-item" data-action="insert-col">
            Insert column right
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="delete-row">
            Delete row
        </div>
        <div class="context-menu-item" data-action="delete-col">
            Delete column
        </div>
    `;
    document.body.appendChild(datatableContextMenu);
    setupContextMenuListeners();
}

function setupContextMenuListeners() {
    if (!datatableContextMenu) return;

    // Click on menu items
    datatableContextMenu.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = item.dataset.action;
            handleContextMenuAction(action);
            hideContextMenu();
        });
    });

    // Hide on click outside
    document.addEventListener('click', hideContextMenu);
    document.addEventListener('scroll', hideContextMenu, true);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hideContextMenu();
    });
}

function handleContextMenuAction(action) {
    if (!datatableData) return;

    switch (action) {
        case 'cut':
            // Simulate Ctrl+X
            document.execCommand('cut');
            break;
        case 'copy':
            // Copy selected cells as TSV
            const copyText = getSelectedCellsAsTSV();
            navigator.clipboard.writeText(copyText).catch(console.error);
            break;
        case 'paste':
            // Paste from clipboard
            navigator.clipboard.readText().then(text => {
                if (!text || !datatableCurrentCell) return;
                const rows = text.split('\\n').map(line => line.split('\\t'));
                const startRow = datatableCurrentCell.row;
                const startCol = datatableCurrentCell.col;
                rows.forEach((rowData, rOffset) => {
                    const targetRow = startRow + rOffset;
                    if (targetRow >= datatableData.rows.length) return;
                    rowData.forEach((value, cOffset) => {
                        const targetCol = startCol + cOffset;
                        if (targetCol >= datatableData.columns.length) return;
                        datatableData.rows[targetRow][targetCol] = value;
                    });
                });
                renderDatatable();
            }).catch(console.error);
            break;
        case 'clear':
            clearSelectedCells();
            break;
        case 'insert-row':
            insertRowBelow();
            break;
        case 'insert-col':
            insertColumnRight();
            break;
        case 'delete-row':
            deleteCurrentRow();
            break;
        case 'delete-col':
            deleteCurrentColumn();
            break;
    }
}

function insertRowBelow() {
    if (!datatableData || !datatableCurrentCell) return;
    const row = datatableCurrentCell.row;
    const newRow = datatableData.columns.map(() => '');
    datatableData.rows.splice(row + 1, 0, newRow);
    renderDatatable();
}

function insertColumnRight() {
    if (!datatableData || !datatableCurrentCell) return;
    const col = datatableCurrentCell.col;
    const newColIdx = datatableData.columns.length;
    datatableData.columns.splice(col + 1, 0, {
        name: `col${newColIdx + 1}`,
        type: 'numeric',
        index: col + 1
    });
    // Reindex columns
    datatableData.columns.forEach((c, i) => c.index = i);
    // Add cell to all rows
    datatableData.rows.forEach(row => row.splice(col + 1, 0, ''));
    renderDatatable();
    updateVarAssignSlots();
}

function deleteCurrentRow() {
    if (!datatableData || !datatableCurrentCell) return;
    if (datatableData.rows.length <= 1) return;  // Keep at least 1 row
    const row = datatableCurrentCell.row;
    datatableData.rows.splice(row, 1);
    if (datatableCurrentCell.row >= datatableData.rows.length) {
        datatableCurrentCell.row = datatableData.rows.length - 1;
    }
    renderDatatable();
}

function deleteCurrentColumn() {
    if (!datatableData || !datatableCurrentCell) return;
    if (datatableData.columns.length <= 1) return;  // Keep at least 1 col
    const col = datatableCurrentCell.col;
    datatableData.columns.splice(col, 1);
    // Reindex columns
    datatableData.columns.forEach((c, i) => c.index = i);
    // Remove cell from all rows
    datatableData.rows.forEach(row => row.splice(col, 1));
    if (datatableCurrentCell.col >= datatableData.columns.length) {
        datatableCurrentCell.col = datatableData.columns.length - 1;
    }
    renderDatatable();
    updateVarAssignSlots();
}

function showContextMenu(e) {
    if (!datatableContextMenu) createContextMenu();

    e.preventDefault();
    e.stopPropagation();

    const x = e.clientX;
    const y = e.clientY;

    // Position off-screen to measure
    datatableContextMenu.style.left = '-9999px';
    datatableContextMenu.style.top = '-9999px';
    datatableContextMenu.style.display = 'block';

    const menuWidth = datatableContextMenu.offsetWidth;
    const menuHeight = datatableContextMenu.offsetHeight;

    // Adjust position to fit in viewport
    let left = x;
    let top = y;
    if (x + menuWidth > window.innerWidth - 10) {
        left = x - menuWidth;
    }
    if (y + menuHeight > window.innerHeight - 10) {
        top = y - menuHeight;
    }

    datatableContextMenu.style.left = `${Math.max(10, left)}px`;
    datatableContextMenu.style.top = `${Math.max(10, top)}px`;
}

function hideContextMenu() {
    if (datatableContextMenu) {
        datatableContextMenu.style.display = 'none';
    }
}

// Attach context menu to table
function attachContextMenuListener() {
    const table = document.querySelector('.datatable-table');
    if (table) {
        table.addEventListener('contextmenu', showContextMenu);
    }
}
"""

__all__ = ["JS_DATATABLE_CONTEXT_MENU"]

# EOF
