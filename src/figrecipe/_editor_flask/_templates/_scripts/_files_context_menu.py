#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Files tree right-click context menu JavaScript."""

JS_FILES_CONTEXT_MENU = """
// ============================================================================
// Files Tree Context Menu (Right-Click Menu)
// ============================================================================
let filesContextMenu = null;
let filesContextTarget = null;  // Track which file was right-clicked

function createFilesContextMenu() {
    if (filesContextMenu) return;

    filesContextMenu = document.createElement('div');
    filesContextMenu.className = 'files-context-menu';
    filesContextMenu.style.display = 'none';
    filesContextMenu.innerHTML = `
        <div class="context-menu-item" data-action="open">
            Open
        </div>
        <div class="context-menu-item" data-action="rename">
            Rename
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="duplicate">
            Duplicate
        </div>
        <div class="context-menu-item" data-action="download">
            Download
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item context-menu-danger" data-action="delete">
            Delete
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="new-file">
            New figure
        </div>
        <div class="context-menu-item" data-action="refresh">
            Refresh list
        </div>
    `;
    document.body.appendChild(filesContextMenu);
    setupFilesContextMenuListeners();
}

function setupFilesContextMenuListeners() {
    if (!filesContextMenu) return;

    // Click on menu items
    filesContextMenu.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = item.dataset.action;
            handleFilesContextMenuAction(action);
            hideFilesContextMenu();
        });
    });

    // Hide on click outside
    document.addEventListener('click', hideFilesContextMenu);
    document.addEventListener('scroll', hideFilesContextMenu, true);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hideFilesContextMenu();
    });
}

function handleFilesContextMenuAction(action) {
    switch (action) {
        case 'open':
            if (filesContextTarget) {
                loadFile(filesContextTarget);
            }
            break;
        case 'rename':
            if (filesContextTarget) {
                const newName = prompt('Enter new name:', filesContextTarget.split('/').pop());
                if (newName && newName !== filesContextTarget.split('/').pop()) {
                    renameFile(filesContextTarget, newName);
                }
            }
            break;
        case 'duplicate':
            if (filesContextTarget) {
                duplicateFile(filesContextTarget);
            }
            break;
        case 'download':
            if (filesContextTarget) {
                downloadFile(filesContextTarget);
            }
            break;
        case 'delete':
            if (filesContextTarget) {
                if (confirm(`Delete "${filesContextTarget.split('/').pop()}"?`)) {
                    deleteFile(filesContextTarget);
                }
            }
            break;
        case 'new-file':
            document.getElementById('btn-new-file')?.click();
            break;
        case 'refresh':
            document.getElementById('btn-refresh-files')?.click();
            break;
    }
    filesContextTarget = null;
}

async function renameFile(filePath, newName) {
    try {
        const response = await fetch('/api/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath, new_name: newName })
        });
        const result = await response.json();
        if (result.success) {
            refreshFileList();
            showToast('File renamed');
        } else {
            showToast(result.error || 'Failed to rename', 'error');
        }
    } catch (err) {
        console.error('Rename error:', err);
        showToast('Failed to rename', 'error');
    }
}

async function duplicateFile(filePath) {
    try {
        const response = await fetch('/api/duplicate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });
        const result = await response.json();
        if (result.success) {
            refreshFileList();
            showToast('File duplicated');
        } else {
            showToast(result.error || 'Failed to duplicate', 'error');
        }
    } catch (err) {
        console.error('Duplicate error:', err);
        showToast('Failed to duplicate', 'error');
    }
}

function downloadFile(filePath) {
    window.location.href = `/api/download?path=${encodeURIComponent(filePath)}`;
}

async function deleteFile(filePath) {
    try {
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });
        const result = await response.json();
        if (result.success) {
            refreshFileList();
            showToast('File deleted');
        } else {
            showToast(result.error || 'Failed to delete', 'error');
        }
    } catch (err) {
        console.error('Delete error:', err);
        showToast('Failed to delete', 'error');
    }
}

function showFilesContextMenu(e, filePath) {
    if (!filesContextMenu) createFilesContextMenu();

    e.preventDefault();
    e.stopPropagation();

    filesContextTarget = filePath;

    const x = e.clientX;
    const y = e.clientY;

    // Position off-screen to measure
    filesContextMenu.style.left = '-9999px';
    filesContextMenu.style.top = '-9999px';
    filesContextMenu.style.display = 'block';

    const menuWidth = filesContextMenu.offsetWidth;
    const menuHeight = filesContextMenu.offsetHeight;

    // Adjust position to fit in viewport
    let left = x;
    let top = y;
    if (x + menuWidth > window.innerWidth - 10) {
        left = x - menuWidth;
    }
    if (y + menuHeight > window.innerHeight - 10) {
        top = y - menuHeight;
    }

    filesContextMenu.style.left = `${Math.max(10, left)}px`;
    filesContextMenu.style.top = `${Math.max(10, top)}px`;

    // Update menu based on context
    const isFile = filePath && !filePath.endsWith('/');
    filesContextMenu.querySelectorAll('[data-action="open"], [data-action="rename"], [data-action="duplicate"], [data-action="download"], [data-action="delete"]').forEach(item => {
        item.style.display = isFile ? 'flex' : 'none';
    });
}

function hideFilesContextMenu() {
    if (filesContextMenu) {
        filesContextMenu.style.display = 'none';
    }
}

// Initialize files context menu
function initializeFilesContextMenu() {
    const fileTree = document.getElementById('file-tree');
    if (fileTree) {
        fileTree.addEventListener('contextmenu', (e) => {
            const fileEntry = e.target.closest('.file-tree-entry');
            if (fileEntry) {
                const filePath = fileEntry.dataset.path;
                showFilesContextMenu(e, filePath);
            } else {
                // Right-click on empty area
                showFilesContextMenu(e, null);
            }
        });
    }
}
"""

__all__ = ["JS_FILES_CONTEXT_MENU"]

# EOF
