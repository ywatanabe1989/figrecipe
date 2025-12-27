#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel drag snapshot functionality with server-side isolated rendering.

This module provides clean panel snapshots rendered in isolation (no overlap)
by fetching from the server, with async caching for smooth UX.
"""

SCRIPTS_PANEL_DRAG_SNAPSHOT = """
// ===== PANEL DRAG SNAPSHOT (server-side isolated render) =====

let panelDragSnapshot = null;  // Current snapshot being dragged
let snapshotCache = {};        // { panelIndex: { imgSrc, timestamp } }
let lastPreviewSrc = null;     // Track image changes for cache invalidation

// Invalidate cache when preview image changes
function setupSnapshotCacheInvalidation() {
    const img = document.getElementById('preview-image');
    if (!img) return;

    lastPreviewSrc = img.src;

    // Watch for src changes
    const observer = new MutationObserver(() => {
        if (img.src !== lastPreviewSrc) {
            console.log('[Snapshot] Preview changed, invalidating cache');
            snapshotCache = {};
            lastPreviewSrc = img.src;
            // Pre-fetch snapshots for all panels (async)
            prefetchAllSnapshots();
        }
    });
    observer.observe(img, { attributes: true, attributeFilter: ['src'] });
}

// Prefetch snapshots for all panels during idle time
function prefetchAllSnapshots() {
    if (typeof panelPositions === 'undefined') return;

    const panelCount = Object.keys(panelPositions).length;
    let i = 0;

    function fetchNext() {
        if (i < panelCount) {
            const idx = i++;
            if (!snapshotCache[idx]) {
                fetchPanelSnapshot(idx).then(() => {
                    if (typeof requestIdleCallback !== 'undefined') {
                        requestIdleCallback(fetchNext);
                    } else {
                        setTimeout(fetchNext, 50);
                    }
                });
            } else {
                if (typeof requestIdleCallback !== 'undefined') {
                    requestIdleCallback(fetchNext);
                } else {
                    setTimeout(fetchNext, 10);
                }
            }
        }
    }

    // Start after a delay to not block initial load
    // Use 5 seconds to avoid triggering during short test windows
    setTimeout(() => {
        if (typeof requestIdleCallback !== 'undefined') {
            requestIdleCallback(fetchNext);
        } else {
            fetchNext();
        }
    }, 5000);
}

// Fetch a single panel snapshot from server
async function fetchPanelSnapshot(panelIndex) {
    try {
        const response = await fetch(`/get_panel_snapshot/${panelIndex}`);
        const data = await response.json();

        if (data.success) {
            snapshotCache[panelIndex] = {
                imgSrc: 'data:image/png;base64,' + data.image,
                timestamp: Date.now()
            };
            console.log('[Snapshot] Cached panel', panelIndex);
            return snapshotCache[panelIndex];
        }
    } catch (error) {
        console.warn('[Snapshot] Failed to fetch panel', panelIndex, error);
    }
    return null;
}

// Get snapshot for a panel (from cache or fetch)
async function getPanelSnapshot(panelIndex) {
    // Check cache first
    if (snapshotCache[panelIndex]) {
        return snapshotCache[panelIndex];
    }
    // Fetch from server
    return await fetchPanelSnapshot(panelIndex);
}

// Create snapshot element for drag preview
function createSnapshotElement(imgSrc, panelIndex) {
    const snapshot = document.createElement('img');
    snapshot.src = imgSrc;
    snapshot.id = 'panel-drag-snapshot';
    snapshot.style.cssText = `
        position: absolute;
        pointer-events: none;
        opacity: 0.7;
        z-index: 1001;
        display: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-radius: 4px;
    `;
    snapshot.dataset.panelIndex = panelIndex;

    const zoomContainer = document.getElementById('zoom-container');
    if (zoomContainer) {
        zoomContainer.appendChild(snapshot);
    }

    return snapshot;
}

// Show the snapshot at the current drag position
function showPanelSnapshot(pos, imgRect) {
    if (!panelDragSnapshot || !figSize.width_mm) return;

    // Convert mm to screen pixels
    const scaleX = imgRect.width / figSize.width_mm;
    const scaleY = imgRect.height / figSize.height_mm;

    // Position at panel location
    const left = pos.left * scaleX;
    const top = pos.top * scaleY;

    // Scale snapshot to match panel size
    const displayWidth = pos.width * scaleX;
    const displayHeight = pos.height * scaleY;

    panelDragSnapshot.style.left = `${left}px`;
    panelDragSnapshot.style.top = `${top}px`;
    panelDragSnapshot.style.width = `${displayWidth}px`;
    panelDragSnapshot.style.height = `${displayHeight}px`;
    panelDragSnapshot.style.display = 'block';
}

// Hide and cleanup the snapshot
function hidePanelSnapshot() {
    if (panelDragSnapshot) {
        panelDragSnapshot.remove();
        panelDragSnapshot = null;
    }
}

// Start snapshot drag - get cached or fetch snapshot
async function startSnapshotDrag(panelIndex, imgRect) {
    // Cleanup any existing snapshot
    hidePanelSnapshot();

    // Get snapshot (from cache or server)
    const cached = await getPanelSnapshot(panelIndex);

    if (cached) {
        panelDragSnapshot = createSnapshotElement(cached.imgSrc, panelIndex);
    }
}

// Update snapshot position during drag
function updateSnapshotPosition(pos, imgRect) {
    showPanelSnapshot(pos, imgRect);
}

// End snapshot drag - cleanup
function endSnapshotDrag() {
    hidePanelSnapshot();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupSnapshotCacheInvalidation();
    // Prefetch after initial load
    setTimeout(prefetchAllSnapshots, 5000);
});

// Also prefetch when panel positions are loaded
if (typeof window !== 'undefined') {
    const originalLoadPanelPositions = window.loadPanelPositions;
    if (originalLoadPanelPositions) {
        window.loadPanelPositions = async function() {
            const result = await originalLoadPanelPositions.apply(this, arguments);
            prefetchAllSnapshots();
            return result;
        };
    }
}
"""

__all__ = ["SCRIPTS_PANEL_DRAG_SNAPSHOT"]

# EOF
