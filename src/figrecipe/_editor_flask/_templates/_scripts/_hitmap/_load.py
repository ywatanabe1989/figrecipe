#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hitmap loading JavaScript for the figure editor."""

SCRIPTS_HITMAP_LOAD = """
// ===== HITMAP LOADING =====

// Load hitmap data from server
async function loadHitmap() {
    try {
        // Load hitmap and calls data in parallel
        const [hitmapResponse, callsResponse] = await Promise.all([
            fetch('/hitmap'),
            fetch('/calls')
        ]);
        const data = await hitmapResponse.json();
        callsData = await callsResponse.json();

        colorMap = data.color_map;
        console.log('Loaded colorMap:', Object.keys(colorMap));
        console.log('Loaded callsData:', Object.keys(callsData), callsData);

        // Create canvas for hitmap
        const canvas = document.getElementById('hitmap-canvas');
        hitmapCtx = canvas.getContext('2d', { willReadFrequently: true });

        // Load hitmap image
        hitmapImg = new Image();
        hitmapImg.onload = function() {
            canvas.width = hitmapImg.width;
            canvas.height = hitmapImg.height;
            hitmapCtx.drawImage(hitmapImg, 0, 0);
            hitmapLoaded = true;
            console.log('Hitmap loaded:', hitmapImg.width, 'x', hitmapImg.height);

            // Update overlay image source
            const overlay = document.getElementById('hitmap-overlay');
            if (overlay) {
                overlay.src = hitmapImg.src;
            }

            // Sync datatable tab colors now that colorMap is loaded
            if (typeof updateTabColors === 'function') {
                updateTabColors();
            }
        };
        hitmapImg.src = 'data:image/png;base64,' + data.image;
    } catch (error) {
        console.error('Failed to load hitmap:', error);
    }
}

// Toggle hit regions overlay visibility mode
function toggleHitmapOverlay() {
    hitmapVisible = !hitmapVisible;
    const overlay = document.getElementById('hitregion-overlay');
    const btn = document.getElementById('btn-show-hitmap');

    if (hitmapVisible) {
        // Show all hit regions
        overlay.classList.add('visible');
        overlay.classList.remove('hover-mode');
        btn.classList.add('active');
        btn.textContent = 'Hide Hit Regions';
    } else {
        // Hover-only mode: hit regions visible only on hover
        overlay.classList.remove('visible');
        overlay.classList.add('hover-mode');
        btn.classList.remove('active');
        btn.textContent = 'Show Hit Regions';
    }
    // Always draw hit regions for hover detection
    drawHitRegions();
}
"""

__all__ = ["SCRIPTS_HITMAP_LOAD"]

# EOF
