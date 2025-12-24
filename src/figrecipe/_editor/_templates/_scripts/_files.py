#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File switcher JavaScript for switching between recipe files."""

SCRIPTS_FILES = """
// ==================== FILE SWITCHER ====================
// Allows switching between recipe files without restarting the server

let currentFilePath = null;

async function loadFileList() {
    const selector = document.getElementById('file-selector');
    if (!selector) return;

    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            selector.innerHTML = '<option value="">No files found</option>';
            return;
        }

        const data = await response.json();
        const files = data.files || [];
        currentFilePath = data.current_file;

        if (files.length === 0) {
            selector.innerHTML = '<option value="">(No recipe files in directory)</option>';
            return;
        }

        // Build options
        let optionsHtml = '';
        if (!currentFilePath) {
            optionsHtml += '<option value="" selected>(Unsaved figure)</option>';
        }

        files.forEach(file => {
            const isCurrent = file.is_current;
            const icon = file.has_image ? '📊 ' : '📄 ';
            const selected = isCurrent ? ' selected' : '';
            optionsHtml += `<option value="${file.path}"${selected}>${icon}${file.name}</option>`;
        });

        selector.innerHTML = optionsHtml;

        console.log('[FileSwitcher] Loaded', files.length, 'files');

    } catch (error) {
        console.error('[FileSwitcher] Error loading files:', error);
        selector.innerHTML = '<option value="">Error loading files</option>';
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
        clearElementHighlights();
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

function initFileSwitcher() {
    const selector = document.getElementById('file-selector');
    const newBtn = document.getElementById('btn-new-figure');

    if (selector) {
        selector.addEventListener('change', (e) => {
            const filePath = e.target.value;
            if (filePath) {
                switchToFile(filePath);
            }
        });
    }

    if (newBtn) {
        newBtn.addEventListener('click', () => {
            showToast('New figure: Use fr.edit() to create a new figure', 'info');
            // Future: could implement creating a new blank figure via API
        });
    }

    // Load file list on init
    loadFileList();
}

// Initialize file switcher after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFileSwitcher);
} else {
    initFileSwitcher();
}

console.log('[FileSwitcher] Loaded - Use dropdown to switch figures');
"""

__all__ = ["SCRIPTS_FILES"]
