#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File browser JavaScript for the file tree panel."""

SCRIPTS_FILES = """
// ==================== FILE BROWSER ====================
// File tree panel for browsing and switching between recipe files

let currentFilePath = null;
let fileBrowserCollapsed = false;
let expandedFolders = new Set();

// Load expanded state from localStorage
function loadExpandedState() {
    try {
        const saved = localStorage.getItem('figrecipe-expanded-folders');
        if (saved) {
            expandedFolders = new Set(JSON.parse(saved));
        }
    } catch (e) {
        console.warn('[FileBrowser] Failed to load expanded state:', e);
    }
}

// Save expanded state to localStorage
function saveExpandedState() {
    try {
        localStorage.setItem('figrecipe-expanded-folders', JSON.stringify([...expandedFolders]));
    } catch (e) {
        console.warn('[FileBrowser] Failed to save expanded state:', e);
    }
}

// Toggle folder expand/collapse
function toggleFolder(folderPath) {
    if (expandedFolders.has(folderPath)) {
        expandedFolders.delete(folderPath);
    } else {
        expandedFolders.add(folderPath);
    }
    saveExpandedState();

    // Update DOM
    const folderEl = document.querySelector(`.file-tree-folder[data-path="${folderPath}"]`);
    if (folderEl) {
        folderEl.classList.toggle('expanded', expandedFolders.has(folderPath));
    }
}

// Render a tree item (file or folder)
function renderTreeItem(item, level = 0) {
    const indent = level * 16; // 16px per level

    if (item.type === 'directory') {
        const isExpanded = expandedFolders.has(item.path);
        const expandedClass = isExpanded ? ' expanded' : '';

        let childrenHtml = '';
        if (item.children && item.children.length > 0) {
            childrenHtml = item.children.map(child => renderTreeItem(child, level + 1)).join('');
        }

        return `<li class="file-tree-folder${expandedClass}" data-path="${item.path}">
            <div class="file-tree-entry" data-path="${item.path}" data-type="folder" style="padding-left: ${12 + indent}px;">
                <span class="file-tree-icon">📁</span>
                <span class="file-tree-name">${item.name}</span>
                <span class="file-tree-badge folder-badge">${item.children ? item.children.length : 0}</span>
            </div>
            <ul class="file-tree-children">
                ${childrenHtml}
            </ul>
        </li>`;
    } else {
        // File item
        const isCurrent = item.is_current;
        const currentClass = isCurrent ? ' current' : '';
        const hasImageClass = item.has_image ? ' has-image' : '';
        const icon = item.has_image ? '📊' : '📄';
        const badge = item.has_image ? '<span class="file-tree-badge">PNG</span>' : '';

        return `<li class="file-tree-item">
            <div class="file-tree-entry${currentClass}${hasImageClass}" data-path="${item.path}" data-type="file" style="padding-left: ${12 + indent}px;">
                <span class="file-tree-icon">${icon}</span>
                <span class="file-tree-name">${item.name}</span>
                ${badge}
                <span class="file-tree-actions">
                    <button class="file-action-btn btn-rename" data-path="${item.path}" title="Rename">✏️</button>
                    <button class="file-action-btn btn-delete" data-path="${item.path}" title="Delete">🗑️</button>
                </span>
            </div>
        </li>`;
    }
}

async function loadFileList() {
    const fileTree = document.getElementById('file-tree');
    if (!fileTree) return;

    // Load saved expanded state
    loadExpandedState();

    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            fileTree.innerHTML = '<li class="file-tree-empty"><p>No files found</p></li>';
            return;
        }

        const data = await response.json();
        const tree = data.tree || [];
        const files = data.files || [];
        currentFilePath = data.current_file;

        // Build file tree HTML
        let treeHtml = '';

        // Show unsaved figure entry when no current file path (new/unsaved figure)
        if (!currentFilePath) {
            treeHtml += `<li class="file-tree-item">
                <div class="file-tree-entry current" data-path="" data-type="file">
                    <span class="file-tree-icon">✨</span>
                    <span class="file-tree-name">(Unsaved figure)</span>
                </div>
            </li>`;
        }

        // Show empty state only if no unsaved figure AND no files
        if (tree.length === 0 && files.length === 0 && currentFilePath !== null) {
            fileTree.innerHTML = '<li class="file-tree-empty"><p>No recipe files</p><p>Create one with figrecipe.subplots()</p></li>';
            return;
        }

        // Render tree structure
        tree.forEach(item => {
            treeHtml += renderTreeItem(item, 0);
        });

        fileTree.innerHTML = treeHtml;

        // Add click handlers for folder entries (expand/collapse)
        fileTree.querySelectorAll('.file-tree-folder > .file-tree-entry').forEach(entry => {
            entry.addEventListener('click', (e) => {
                const folderPath = entry.dataset.path;
                if (folderPath !== undefined) {
                    toggleFolder(folderPath);
                }
            });
        });

        // Add click handlers for file entries
        fileTree.querySelectorAll('.file-tree-entry[data-type="file"]').forEach(entry => {
            entry.addEventListener('click', (e) => {
                // Don't switch if clicking action buttons
                if (e.target.closest('.file-action-btn')) return;
                const path = entry.dataset.path;
                if (path) {
                    switchToFile(path);
                }
            });
        });

        // Add click handlers for rename buttons
        fileTree.querySelectorAll('.btn-rename').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                renameFile(btn.dataset.path);
            });
        });

        // Add click handlers for delete buttons
        fileTree.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteFile(btn.dataset.path);
            });
        });

        console.log('[FileBrowser] Loaded', files.length, 'files in', tree.length, 'root items');

    } catch (error) {
        console.error('[FileBrowser] Error loading files:', error);
        fileTree.innerHTML = '<li class="file-tree-empty"><p>Error loading files</p></li>';
    }
}

async function switchToFile(filePath) {
    if (!filePath || filePath === currentFilePath) return;

    showToast('Loading figure...', 'info');

    try {
        const response = await fetch('/api/switch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to switch file');
        }

        const data = await response.json();

        // Update preview image
        const img = document.getElementById('preview-image');
        if (img && data.image) {
            img.src = 'data:image/png;base64,' + data.image;
        }

        // Update bboxes
        if (data.bboxes) {
            window.currentBboxes = data.bboxes;
        }

        // Update color map for hitmap
        if (data.color_map) {
            window.currentColorMap = data.color_map;
        }

        // Update current file path
        currentFilePath = filePath;

        // Clear selection
        clearSelection();
        document.getElementById('selected-element-panel')?.style.setProperty('display', 'none');

        showToast('Loaded: ' + filePath, 'success');
        console.log('[FileSwitcher] Switched to:', filePath);

        // Reload file list to update selection state
        loadFileList();

    } catch (error) {
        console.error('[FileSwitcher] Error switching file:', error);
        showToast('Error: ' + error.message, 'error');
        // Revert selector
        loadFileList();
    }
}

async function createNewFigure() {
    showToast('Creating new figure...', 'info');

    try {
        const response = await fetch('/api/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create new figure');
        }

        const data = await response.json();

        // Update preview image
        const img = document.getElementById('preview-image');
        if (img && data.image) {
            img.src = 'data:image/png;base64,' + data.image;
        }

        // Update bboxes
        if (data.bboxes) {
            window.currentBboxes = data.bboxes;
        }

        // Update color map for hitmap
        if (data.color_map) {
            window.currentColorMap = data.color_map;
        }

        // Update current file path to the new file
        currentFilePath = data.file || null;

        // Clear selection
        if (typeof clearSelection === 'function') {
            clearSelection();
        }
        const selectedPanel = document.getElementById('selected-element-panel');
        if (selectedPanel) selectedPanel.style.display = 'none';

        const fileName = data.file_name || 'new_figure';
        showToast(`Created: ${fileName}.yaml`, 'success');
        console.log('[FileSwitcher] Created new figure:', data.file);

        // Reload file list to show (Unsaved figure)
        loadFileList();

    } catch (error) {
        console.error('[FileSwitcher] Error creating new figure:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

function toggleFileBrowser() {
    const panel = document.getElementById('file-browser-panel');
    const collapseBtn = document.getElementById('btn-collapse-browser');
    if (!panel) return;

    fileBrowserCollapsed = !fileBrowserCollapsed;
    panel.classList.toggle('collapsed', fileBrowserCollapsed);
    if (collapseBtn) {
        collapseBtn.innerHTML = fileBrowserCollapsed ? '&#x276F;' : '&#x276E;';
        collapseBtn.title = fileBrowserCollapsed ? 'Expand panel' : 'Collapse panel';
    }
}

function initFileBrowser() {
    const newBtn = document.getElementById('btn-new-file');
    const refreshBtn = document.getElementById('btn-refresh-files');
    const collapseBtn = document.getElementById('btn-collapse-browser');

    if (newBtn) {
        newBtn.addEventListener('click', createNewFigure);
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadFileList);
    }

    if (collapseBtn) {
        collapseBtn.addEventListener('click', toggleFileBrowser);
    }

    // Load file list on init
    loadFileList();
}

// Initialize file browser after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFileBrowser);
} else {
    initFileBrowser();
}

async function deleteFile(filePath) {
    if (!filePath) return;

    const fileName = filePath.split('/').pop().replace('.yaml', '');
    if (!confirm(`Delete "${fileName}" and its associated files (.yaml, .png)?`)) {
        return;
    }

    showToast('Deleting...', 'info');

    try {
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete');
        }

        showToast(`Deleted: ${data.deleted.join(', ')}`, 'success');
        console.log('[FileBrowser] Deleted:', data.deleted);

        // If we deleted the current file, switch to another or create new
        if (data.was_current) {
            if (data.switch_to) {
                // Switch to another existing file
                console.log('[FileBrowser] Switching to:', data.switch_to);
                await switchToFile(data.switch_to);
            } else {
                // No other files, create a new one
                console.log('[FileBrowser] No files left, creating new figure');
                await createNewFigure();
            }
        } else {
            // Just reload file list
            loadFileList();
        }

    } catch (error) {
        console.error('[FileBrowser] Delete error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function renameFile(filePath) {
    if (!filePath) return;

    const oldName = filePath.split('/').pop().replace('.yaml', '');
    const newName = prompt(`Rename "${oldName}" to:`, oldName);

    if (!newName || newName === oldName) return;

    showToast('Renaming...', 'info');

    try {
        const response = await fetch('/api/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath, new_name: newName })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to rename');
        }

        showToast(`Renamed to: ${data.new_name}`, 'success');
        console.log('[FileBrowser] Renamed:', data.renamed);

        // Update current file path if it was the renamed file
        if (currentFilePath === filePath) {
            currentFilePath = data.new_name + '.yaml';
        }

        // Reload file list
        loadFileList();

    } catch (error) {
        console.error('[FileBrowser] Rename error:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

console.log('[FileBrowser] Loaded - Use file tree to switch figures');
"""

__all__ = ["SCRIPTS_FILES"]
