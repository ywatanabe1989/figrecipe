#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zoom and pan JavaScript for the figure editor."""

SCRIPTS_ZOOM = """
// ==================== ZOOM/PAN FUNCTIONS ====================

function initializeZoomPan() {
    const wrapper = document.getElementById('preview-wrapper');
    const container = document.getElementById('zoom-container');

    if (!wrapper || !container) return;

    // Zoom buttons
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => setZoom(zoomLevel + ZOOM_STEP));
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => setZoom(zoomLevel - ZOOM_STEP));
    document.getElementById('btn-zoom-reset')?.addEventListener('click', () => setZoom(1.0));
    document.getElementById('btn-zoom-fit')?.addEventListener('click', zoomToFit);

    // Mouse wheel zoom
    wrapper.addEventListener('wheel', (e) => {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
            setZoom(zoomLevel + delta);
        }
    }, { passive: false });

    // Pan with middle mouse or space+drag
    wrapper.addEventListener('mousedown', (e) => {
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            e.preventDefault();
            startPan(e);
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
    if (container) {
        container.style.transform = `scale(${zoomLevel})`;
    }

    // Update zoom level display
    const levelDisplay = document.getElementById('zoom-level');
    if (levelDisplay) {
        levelDisplay.textContent = Math.round(zoomLevel * 100) + '%';
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

function startPan(e) {
    const wrapper = document.getElementById('preview-wrapper');
    isPanning = true;
    panStartX = e.clientX;
    panStartY = e.clientY;
    scrollStartX = wrapper.scrollLeft;
    scrollStartY = wrapper.scrollTop;
    wrapper.classList.add('panning');
}

function doPan(e) {
    if (!isPanning) return;

    const wrapper = document.getElementById('preview-wrapper');
    const dx = e.clientX - panStartX;
    const dy = e.clientY - panStartY;

    wrapper.scrollLeft = scrollStartX - dx;
    wrapper.scrollTop = scrollStartY - dy;
}

function endPan() {
    if (isPanning) {
        const wrapper = document.getElementById('preview-wrapper');
        wrapper.classList.remove('panning');
        isPanning = false;
    }
}

// ==================== END ZOOM/PAN ====================
"""

__all__ = ["SCRIPTS_ZOOM"]
