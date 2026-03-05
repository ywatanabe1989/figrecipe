#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canvas right-click context menu JavaScript."""

JS_CANVAS_CONTEXT_MENU = """
// ============================================================================
// Canvas Context Menu (Right-Click Menu)
// ============================================================================
let canvasContextMenu = null;

function createCanvasContextMenu() {
    if (canvasContextMenu) return;

    canvasContextMenu = document.createElement('div');
    canvasContextMenu.className = 'canvas-context-menu';
    canvasContextMenu.style.display = 'none';
    canvasContextMenu.innerHTML = `
        <div class="context-menu-item" data-action="copy-image">
            Copy image<span class="shortcut">Ctrl+C</span>
        </div>
        <div class="context-menu-item" data-action="download-png">
            Download PNG
        </div>
        <div class="context-menu-item" data-action="download-svg">
            Download SVG
        </div>
        <div class="context-menu-item" data-action="download-pdf">
            Download PDF
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="zoom-fit">
            Fit to view<span class="shortcut">F</span>
        </div>
        <div class="context-menu-item" data-action="zoom-100">
            Zoom 100%<span class="shortcut">0</span>
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" data-action="render">
            Re-render<span class="shortcut">R</span>
        </div>
        <div class="context-menu-item" data-action="toggle-grid">
            Toggle grid<span class="shortcut">G</span>
        </div>
    `;
    document.body.appendChild(canvasContextMenu);
    setupCanvasContextMenuListeners();
}

function setupCanvasContextMenuListeners() {
    if (!canvasContextMenu) return;

    // Click on menu items
    canvasContextMenu.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = item.dataset.action;
            handleCanvasContextMenuAction(action);
            hideCanvasContextMenu();
        });
    });

    // Hide on click outside
    document.addEventListener('click', hideCanvasContextMenu);
    document.addEventListener('scroll', hideCanvasContextMenu, true);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hideCanvasContextMenu();
    });
}

function handleCanvasContextMenuAction(action) {
    switch (action) {
        case 'copy-image':
            copyCanvasImage();
            break;
        case 'download-png':
            document.getElementById('btn-download-png-menu')?.click();
            break;
        case 'download-svg':
            document.getElementById('btn-download-svg-menu')?.click();
            break;
        case 'download-pdf':
            document.getElementById('btn-download-pdf-menu')?.click();
            break;
        case 'zoom-fit':
            zoomToFit();
            break;
        case 'zoom-100':
            setZoom(1.0);
            break;
        case 'render':
            document.getElementById('btn-refresh')?.click();
            break;
        case 'toggle-grid':
            document.getElementById('btn-ruler-grid')?.click();
            break;
    }
}

async function copyCanvasImage() {
    const img = document.getElementById('preview-image');
    if (!img) return;

    try {
        // Fetch the image and convert to blob
        const response = await fetch(img.src);
        const blob = await response.blob();
        await navigator.clipboard.write([
            new ClipboardItem({ 'image/png': blob })
        ]);
        showToast('Image copied to clipboard');
    } catch (err) {
        console.error('Failed to copy image:', err);
        showToast('Failed to copy image', 'error');
    }
}

function showCanvasContextMenu(e) {
    if (!canvasContextMenu) createCanvasContextMenu();

    e.preventDefault();
    e.stopPropagation();

    const x = e.clientX;
    const y = e.clientY;

    // Position off-screen to measure
    canvasContextMenu.style.left = '-9999px';
    canvasContextMenu.style.top = '-9999px';
    canvasContextMenu.style.display = 'block';

    const menuWidth = canvasContextMenu.offsetWidth;
    const menuHeight = canvasContextMenu.offsetHeight;

    // Adjust position to fit in viewport
    let left = x;
    let top = y;
    if (x + menuWidth > window.innerWidth - 10) {
        left = x - menuWidth;
    }
    if (y + menuHeight > window.innerHeight - 10) {
        top = y - menuHeight;
    }

    canvasContextMenu.style.left = `${Math.max(10, left)}px`;
    canvasContextMenu.style.top = `${Math.max(10, top)}px`;
}

function hideCanvasContextMenu() {
    if (canvasContextMenu) {
        canvasContextMenu.style.display = 'none';
    }
}

// Simple toast notification
function showToast(message, type = 'success') {
    let toast = document.getElementById('toast-notification');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        toast.className = 'toast-notification';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `toast-notification ${type}`;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 2000);
}

// Initialize canvas context menu
function initializeCanvasContextMenu() {
    const wrapper = document.getElementById('preview-wrapper');
    if (wrapper) {
        wrapper.addEventListener('contextmenu', showCanvasContextMenu);
    }
}
"""

__all__ = ["JS_CANVAS_CONTEXT_MENU"]

# EOF
