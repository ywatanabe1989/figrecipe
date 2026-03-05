#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modal dialogs JavaScript for the figure editor.

This module contains the JavaScript code for:
- Theme modal (view, download, copy theme)
- Shortcuts modal
- Theme switching
"""

SCRIPTS_MODALS = """
// ===== MODAL DIALOGS =====

// Initialize theme modal handlers
function initializeThemeModal() {
    const modal = document.getElementById('theme-modal');
    const themeSelector = document.getElementById('theme-selector');
    const btnView = document.getElementById('btn-view-theme');
    const btnDownload = document.getElementById('btn-download-theme');
    const btnCopy = document.getElementById('btn-copy-theme');
    const modalClose = document.getElementById('theme-modal-close');
    const modalDownload = document.getElementById('theme-modal-download');
    const modalCopy = document.getElementById('theme-modal-copy');

    // Theme selector change handler
    if (themeSelector) {
        loadCurrentTheme();
        themeSelector.addEventListener('change', function() {
            switchTheme(this.value);
        });
    }

    // View button opens modal
    if (btnView) btnView.addEventListener('click', showThemeModal);

    // Download and copy buttons
    if (btnDownload) btnDownload.addEventListener('click', downloadTheme);
    if (btnCopy) btnCopy.addEventListener('click', copyTheme);

    // Modal close
    if (modalClose) modalClose.addEventListener('click', hideThemeModal);

    // Modal buttons
    if (modalDownload) modalDownload.addEventListener('click', downloadTheme);
    if (modalCopy) modalCopy.addEventListener('click', copyTheme);

    // Close modal on outside click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) hideThemeModal();
        });
    }
}

// Show theme modal
async function showThemeModal() {
    const modal = document.getElementById('theme-modal');
    const themeContent = document.getElementById('theme-content');
    const themeModalName = document.getElementById('theme-modal-name');
    const themeSelector = document.getElementById('theme-selector');

    try {
        const response = await fetch('/theme');
        const data = await response.json();

        const themeName = themeSelector ? themeSelector.value : data.name;
        if (themeModalName) themeModalName.textContent = themeName;
        if (themeContent) themeContent.textContent = data.content;
        if (modal) modal.style.display = 'flex';
    } catch (error) {
        console.error('Failed to load theme:', error);
    }
}

// Hide theme modal
function hideThemeModal() {
    const modal = document.getElementById('theme-modal');
    if (modal) modal.style.display = 'none';
}

// Initialize shortcuts modal handlers
function initializeShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    const btnShortcuts = document.getElementById('btn-shortcuts');
    const modalClose = document.getElementById('shortcuts-modal-close');

    if (btnShortcuts) btnShortcuts.addEventListener('click', showShortcutsModal);
    if (modalClose) modalClose.addEventListener('click', hideShortcutsModal);

    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) hideShortcutsModal();
        });
    }
}

// Show/hide shortcuts modal
function showShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) modal.style.display = 'flex';
}

function hideShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) modal.style.display = 'none';
}

// Download theme as YAML
async function downloadTheme() {
    try {
        const response = await fetch('/theme');
        const data = await response.json();

        const blob = new Blob([data.content], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.name + '.yaml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Failed to download theme:', error);
    }
}

// Copy theme to clipboard
async function copyTheme() {
    try {
        const response = await fetch('/theme');
        const data = await response.json();

        await navigator.clipboard.writeText(data.content);

        const btn = document.getElementById('btn-copy-theme');
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = originalText; }, 1500);
    } catch (error) {
        console.error('Failed to copy theme:', error);
    }
}

// Load current theme and set selector
async function loadCurrentTheme() {
    try {
        const response = await fetch('/list_themes');
        const data = await response.json();

        const selector = document.getElementById('theme-selector');
        if (selector && data.current) {
            selector.value = data.current;
        }
        console.log('Current theme:', data.current);
    } catch (error) {
        console.error('Failed to load current theme:', error);
    }
}

// Switch to a different theme preset
async function switchTheme(themeName) {
    console.log('Switching theme to:', themeName);
    document.body.classList.add('loading');

    try {
        const response = await fetch('/switch_theme', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: themeName })
        });

        const result = await response.json();

        if (result.success) {
            const previewImg = document.getElementById('preview-image');
            previewImg.src = 'data:image/png;base64,' + result.image;

            if (result.img_size) {
                currentImgWidth = result.img_size.width;
                currentImgHeight = result.img_size.height;
            }

            // Update form values from new theme
            if (result.values) {
                for (const [key, value] of Object.entries(result.values)) {
                    const element = document.getElementById(key);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = Boolean(value);
                        } else {
                            element.value = value;
                        }
                        if (element.placeholder !== undefined) {
                            element.placeholder = value;
                        }
                    }
                }
                Object.assign(themeDefaults, result.values);
                updateAllModifiedStates();
            }

            if (result.bboxes) {
                currentBboxes = result.bboxes;
                previewImg.onload = () => {
                    updateHitRegions();
                    loadHitmap();
                };
            }
            console.log('Theme switched to:', themeName);
        } else {
            console.error('Theme switch failed:', result.error);
            loadCurrentTheme();
        }
    } catch (error) {
        console.error('Failed to switch theme:', error);
        loadCurrentTheme();
    } finally {
        document.body.classList.remove('loading');
    }
}
"""

__all__ = ["SCRIPTS_MODALS"]

# EOF
