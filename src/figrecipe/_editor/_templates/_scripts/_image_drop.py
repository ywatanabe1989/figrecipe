#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""External image drop JavaScript for the figure editor.

This module contains the JavaScript code for:
- Handling drag & drop of external images onto the editor
- Creating imshow panels from dropped images
- Handling recipe file drops
"""

SCRIPTS_IMAGE_DROP = """
// ===== EXTERNAL IMAGE/FILE DROP =====

let dropOverlay = null;

// Initialize drop zone functionality
function initImageDrop() {
    console.log('[ImageDrop] initImageDrop called');
    const zoomContainer = document.getElementById('zoom-container');
    const previewContainer = document.getElementById('preview-wrapper');

    if (!previewContainer) {
        console.error('[ImageDrop] preview-wrapper not found!');
        return;
    }

    // Create drop overlay
    dropOverlay = document.createElement('div');
    dropOverlay.id = 'drop-overlay';
    dropOverlay.innerHTML = `
        <div class="drop-message">
            <div class="drop-icon">📷</div>
            <div class="drop-text">Drop image to add as panel</div>
            <div class="drop-subtext">Supports PNG, JPG, GIF, YAML recipe files</div>
        </div>
    `;
    dropOverlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(37, 99, 235, 0.9);
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 2000;
        pointer-events: none;
    `;
    previewContainer.style.position = 'relative';
    previewContainer.appendChild(dropOverlay);

    // Style the drop message
    const style = document.createElement('style');
    style.textContent = `
        .drop-message {
            text-align: center;
            color: white;
        }
        .drop-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        .drop-text {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .drop-subtext {
            font-size: 14px;
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);

    // Add drag & drop event listeners
    previewContainer.addEventListener('dragenter', handleDragEnter);
    previewContainer.addEventListener('dragover', handleDragOver);
    previewContainer.addEventListener('dragleave', handleDragLeave);
    previewContainer.addEventListener('drop', handleDrop);

    console.log('[ImageDrop] Drop zone initialized');
}

// Handle drag enter
function handleDragEnter(event) {
    event.preventDefault();
    event.stopPropagation();

    // Always show overlay if dragging files - browser restricts type info until drop
    if (hasAnyFiles(event)) {
        showDropOverlay();
    }
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();

    // Must call preventDefault to allow drop
    if (hasAnyFiles(event)) {
        event.dataTransfer.dropEffect = 'copy';
    }
}

// Check if event has any files (permissive check for dragenter/dragover)
function hasAnyFiles(event) {
    // Check dataTransfer.types for 'Files' - most reliable cross-browser
    if (event.dataTransfer.types) {
        for (const type of event.dataTransfer.types) {
            if (type === 'Files' || type === 'application/x-moz-file') {
                return true;
            }
        }
    }
    // Fallback: check items
    const items = event.dataTransfer.items;
    if (items && items.length > 0) {
        for (const item of items) {
            if (item.kind === 'file') {
                return true;
            }
        }
    }
    return false;
}

// Handle drag leave
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();

    // Only hide if leaving the container entirely
    const rect = event.currentTarget.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right ||
        event.clientY < rect.top || event.clientY > rect.bottom) {
        hideDropOverlay();
    }
}

// Handle drop
async function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    hideDropOverlay();

    const files = event.dataTransfer.files;
    if (files.length === 0) {
        // Try to get image from URL (dragged from browser)
        const imageUrl = event.dataTransfer.getData('text/uri-list') ||
                        event.dataTransfer.getData('text/plain');
        if (imageUrl && isImageUrl(imageUrl)) {
            await handleImageUrl(imageUrl, event);
            return;
        }
        console.log('[ImageDrop] No files dropped');
        return;
    }

    for (const file of files) {
        if (isImageFile(file)) {
            await handleImageFile(file, event);
        } else if (isRecipeFile(file)) {
            await handleRecipeFile(file);
        } else {
            console.log('[ImageDrop] Unsupported file type:', file.type);
        }
    }
}

// Check if event has valid files
function hasValidFiles(event) {
    const items = event.dataTransfer.items;
    if (!items) return false;

    for (const item of items) {
        if (item.kind === 'file') {
            const type = item.type;
            // Accept known image/yaml types
            if (type.startsWith('image/') ||
                type === 'application/x-yaml' ||
                type === 'text/yaml') {
                return true;
            }
            // When dragging from file system, type may be empty
            // Accept any file and filter by extension in handleDrop
            if (type === '' || type === 'application/octet-stream') {
                return true;
            }
        }
        // Also accept URLs (images dragged from browser)
        if (item.kind === 'string' && item.type === 'text/uri-list') {
            return true;
        }
    }
    return false;
}

// Check if file is an image
function isImageFile(file) {
    if (file.type.startsWith('image/')) {
        return true;
    }
    // Fallback to extension check when type is empty (Windows file drag)
    const ext = file.name.toLowerCase().split('.').pop();
    return ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'].includes(ext);
}

// Check if file is a recipe file
function isRecipeFile(file) {
    return file.name.endsWith('.yaml') ||
           file.name.endsWith('.yml') ||
           file.type === 'application/x-yaml' ||
           file.type === 'text/yaml';
}

// Check if URL points to an image
function isImageUrl(url) {
    const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'];
    const lowerUrl = url.toLowerCase();
    return imageExtensions.some(ext => lowerUrl.includes(ext));
}

// Handle dropped image file
async function handleImageFile(file, event) {
    console.log('[ImageDrop] Processing image file:', file.name);
    document.body.classList.add('loading');

    try {
        // Get drop position relative to image
        const img = document.getElementById('preview-image');
        let dropX = 0.5, dropY = 0.5;  // Default to center

        if (img && figSize.width_mm && figSize.height_mm) {
            const rect = img.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            dropX = Math.max(0, Math.min(1, x / rect.width));
            dropY = Math.max(0, Math.min(1, y / rect.height));
        }

        // Read file as base64
        const base64 = await fileToBase64(file);

        // Send to server
        const response = await fetch('/add_image_panel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_data: base64,
                filename: file.name,
                drop_x: dropX,
                drop_y: dropY
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview
            const previewImg = document.getElementById('preview-image');
            if (previewImg) {
                await new Promise((resolve) => {
                    previewImg.onload = resolve;
                    previewImg.src = 'data:image/png;base64,' + data.image;
                });
            }

            // Update state
            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }
            if (data.bboxes) {
                currentBboxes = data.bboxes;
                loadHitmap();
                updateHitRegions();
            }
            await loadPanelPositions();

            console.log('[ImageDrop] Image panel added successfully');
        } else {
            console.error('[ImageDrop] Failed to add image:', data.error);
            alert('Failed to add image: ' + data.error);
        }
    } catch (error) {
        console.error('[ImageDrop] Error processing image:', error);
        alert('Error processing image: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Handle image URL (dragged from browser)
async function handleImageUrl(url, event) {
    console.log('[ImageDrop] Processing image URL:', url);
    document.body.classList.add('loading');

    try {
        // Get drop position
        const img = document.getElementById('preview-image');
        let dropX = 0.5, dropY = 0.5;

        if (img && figSize.width_mm && figSize.height_mm) {
            const rect = img.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            dropX = Math.max(0, Math.min(1, x / rect.width));
            dropY = Math.max(0, Math.min(1, y / rect.height));
        }

        // Send URL to server
        const response = await fetch('/add_image_from_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                drop_x: dropX,
                drop_y: dropY
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview
            const previewImg = document.getElementById('preview-image');
            if (previewImg) {
                await new Promise((resolve) => {
                    previewImg.onload = resolve;
                    previewImg.src = 'data:image/png;base64,' + data.image;
                });
            }

            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }
            if (data.bboxes) {
                currentBboxes = data.bboxes;
                loadHitmap();
                updateHitRegions();
            }
            await loadPanelPositions();

            console.log('[ImageDrop] Image from URL added successfully');
        } else {
            console.error('[ImageDrop] Failed to add image from URL:', data.error);
            alert('Failed to add image: ' + data.error);
        }
    } catch (error) {
        console.error('[ImageDrop] Error processing URL:', error);
        alert('Error processing image URL: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Handle dropped recipe file
async function handleRecipeFile(file) {
    console.log('[ImageDrop] Processing recipe file:', file.name);
    document.body.classList.add('loading');

    try {
        const content = await file.text();

        const response = await fetch('/load_recipe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipe_content: content,
                filename: file.name
            })
        });

        const data = await response.json();

        if (data.success) {
            // Reload the editor with new figure
            window.location.reload();
        } else {
            console.error('[ImageDrop] Failed to load recipe:', data.error);
            alert('Failed to load recipe: ' + data.error);
        }
    } catch (error) {
        console.error('[ImageDrop] Error processing recipe:', error);
        alert('Error processing recipe: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // Remove data URL prefix (e.g., "data:image/png;base64,")
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Show drop overlay
function showDropOverlay() {
    if (dropOverlay) {
        dropOverlay.style.display = 'flex';
    }
}

// Hide drop overlay
function hideDropOverlay() {
    if (dropOverlay) {
        dropOverlay.style.display = 'none';
    }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initImageDrop);
"""

__all__ = ["SCRIPTS_IMAGE_DROP"]

# EOF
