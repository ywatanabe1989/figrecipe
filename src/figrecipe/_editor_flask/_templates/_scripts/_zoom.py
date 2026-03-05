#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zoom and pan JavaScript for the figure editor."""

SCRIPTS_ZOOM = """
// ==================== ZOOM/PAN FUNCTIONS ====================

function initializeZoomPan() {
    const wrapper = document.getElementById('preview-wrapper');
    const container = document.getElementById('zoom-container');

    if (!wrapper || !container) return;

    // Zoom dropdown
    const zoomSelect = document.getElementById('zoom-select');
    zoomSelect?.addEventListener('change', (e) => {
        setZoom(parseInt(e.target.value) / 100);
    });

    // Fit button
    document.getElementById('btn-zoom-fit')?.addEventListener('click', zoomToFit);

    // Mouse wheel zoom
    wrapper.addEventListener('wheel', (e) => {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
            setZoom(zoomLevel + delta);
        }
    }, { passive: false });

    // Pan with middle mouse, alt+drag, or left-click on empty area when zoomed
    wrapper.addEventListener('mousedown', (e) => {
        // Middle mouse or Alt+drag always pans
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            e.preventDefault();
            startPan(e);
            return;
        }
        // Left-click when zoomed > 100% and clicking on background (not on elements)
        if (e.button === 0 && zoomLevel > 1.0) {
            const target = e.target;
            // Only pan if clicking on wrapper/container background, not on canvas elements
            if (target.id === 'preview-wrapper' || target.classList.contains('zoom-container') ||
                target.tagName === 'svg' || target.id === 'preview-image') {
                // Don't pan if clicking on hitmap regions (they have data attributes)
                const hitRegion = document.elementFromPoint(e.clientX, e.clientY);
                if (!hitRegion || !hitRegion.closest('.hit-region')) {
                    e.preventDefault();
                    startPan(e);
                }
            }
        }
    });

    wrapper.addEventListener('mousemove', (e) => {
        if (isPanning) {
            doPan(e);
        }
    });

    wrapper.addEventListener('mouseup', endPan);
    wrapper.addEventListener('mouseleave', endPan);

    // Keyboard shortcuts for zoom
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === '+' || e.key === '=') {
            e.preventDefault();
            setZoom(zoomLevel + ZOOM_STEP);
        } else if (e.key === '-' || e.key === '_') {
            e.preventDefault();
            setZoom(zoomLevel - ZOOM_STEP);
        } else if (e.key === '0') {
            e.preventDefault();
            setZoom(1.0);
        } else if (e.key === 'f' || e.key === 'F') {
            e.preventDefault();
            zoomToFit();
        }
    });

    // Initialize fit to view
    setTimeout(zoomToFit, 200);
}

function setZoom(newLevel) {
    zoomLevel = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, newLevel));

    const container = document.getElementById('zoom-container');
    const wrapper = document.getElementById('preview-wrapper');
    const img = document.getElementById('preview-image');

    if (container && wrapper) {
        container.style.transform = `scale(${zoomLevel})`;

        // Update container size to enable proper scrolling
        // Transform scale doesn't change layout size, so we set explicit dimensions
        if (img) {
            // Use rendered dimensions if naturalWidth not available
            const imgWidth = img.naturalWidth || img.width || img.clientWidth;
            const imgHeight = img.naturalHeight || img.height || img.clientHeight;

            if (imgWidth && imgHeight) {
                const scaledWidth = imgWidth * zoomLevel;
                const scaledHeight = imgHeight * zoomLevel;

                // Set container dimensions for scroll area calculation
                container.style.width = `${imgWidth}px`;
                container.style.height = `${imgHeight}px`;
                container.style.minWidth = `${scaledWidth}px`;
                container.style.minHeight = `${scaledHeight}px`;
            }
        }

        // Update wrapper class for cursor hint
        if (zoomLevel > 1.0) {
            wrapper.classList.add('zoomed-in');
        } else {
            wrapper.classList.remove('zoomed-in');
            // Reset scroll position when not zoomed
            wrapper.scrollLeft = 0;
            wrapper.scrollTop = 0;
        }
    }

    // Update zoom dropdown to nearest value
    const zoomSelect = document.getElementById('zoom-select');
    if (zoomSelect) {
        const percent = Math.round(zoomLevel * 100);
        // Find closest option
        const options = Array.from(zoomSelect.options).map(o => parseInt(o.value));
        const closest = options.reduce((prev, curr) =>
            Math.abs(curr - percent) < Math.abs(prev - percent) ? curr : prev
        );
        zoomSelect.value = closest;
    }
}

function zoomToFit() {
    const wrapper = document.getElementById('preview-wrapper');
    const img = document.getElementById('preview-image');

    if (!wrapper || !img || !img.naturalWidth) return;

    const wrapperRect = wrapper.getBoundingClientRect();
    const padding = 40;

    const scaleX = (wrapperRect.width - padding) / img.naturalWidth;
    const scaleY = (wrapperRect.height - padding) / img.naturalHeight;

    setZoom(Math.min(scaleX, scaleY, 1.0));
}

// Find nearest scrollable parent element
function findScrollableParent(element) {
    while (element && element !== document.body) {
        const style = window.getComputedStyle(element);
        const overflowY = style.overflowY;
        const overflowX = style.overflowX;
        const isScrollable = (overflowY === 'auto' || overflowY === 'scroll' ||
                             overflowX === 'auto' || overflowX === 'scroll');
        const canScroll = element.scrollHeight > element.clientHeight ||
                         element.scrollWidth > element.clientWidth;
        if (isScrollable && canScroll) {
            return element;
        }
        element = element.parentElement;
    }
    return null;
}

function startPan(e) {
    // Find scrollable container under mouse
    panTarget = findScrollableParent(e.target);
    if (!panTarget) {
        // Fallback to preview-wrapper for canvas
        panTarget = document.getElementById('preview-wrapper');
    }
    if (!panTarget) return;

    isPanning = true;
    panStartX = e.clientX;
    panStartY = e.clientY;
    scrollStartX = panTarget.scrollLeft;
    scrollStartY = panTarget.scrollTop;
    panTarget.classList.add('panning');
}

function doPan(e) {
    if (!isPanning || !panTarget) return;

    const dx = e.clientX - panStartX;
    const dy = e.clientY - panStartY;

    panTarget.scrollLeft = scrollStartX - dx;
    panTarget.scrollTop = scrollStartY - dy;
}

function endPan() {
    if (isPanning && panTarget) {
        panTarget.classList.remove('panning');
        isPanning = false;
        panTarget = null;
    }
}

// ==================== END ZOOM/PAN ====================
"""

__all__ = ["SCRIPTS_ZOOM"]
