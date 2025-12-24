#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selection drawing and property synchronization JavaScript.

This module contains the JavaScript code for:
- Drawing selection overlays (polylines, circles, rectangles)
- Clearing selection state
- Syncing properties panel to selected element
- Updating element property highlights
"""

SCRIPTS_SELECTION = """
// ===== SELECTION AND PROPERTY SYNC =====

// Clear current selection
function clearSelection() {
    selectedElement = null;
    clearSelectionOverlay();

    // Clear section and field highlights
    document.querySelectorAll('.section-highlighted').forEach(s => s.classList.remove('section-highlighted'));
    document.querySelectorAll('.field-highlighted').forEach(f => f.classList.remove('field-highlighted'));

    // Switch back to Figure tab when nothing selected
    switchTab('figure');

    // Update hint and show all if in filter mode
    const hint = document.getElementById('selection-hint');
    if (hint && viewMode === 'selected') {
        hint.textContent = '';
        hint.style.color = '';
        showAllProperties();
    }
}

// Draw selection shape(s) - handles lines, scatter, and rectangles
function drawSelection(key) {
    const overlay = document.getElementById('selection-overlay');
    overlay.innerHTML = '';

    const img = document.getElementById('preview-image');
    if (!img.naturalWidth || !img.naturalHeight) return;

    // Set SVG viewBox to match natural image size
    overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
    overlay.style.width = `${img.naturalWidth}px`;
    overlay.style.height = `${img.naturalHeight}px`;

    const scaleX = 1.0;
    const scaleY = 1.0;
    const offsetX = 0;
    const offsetY = 0;

    // Determine which elements to highlight
    let elementsToHighlight = [key];
    if (selectedElement && selectedElement.groupElements) {
        elementsToHighlight = selectedElement.groupElements.map(e => e.key);
    }

    // Draw selection for each element
    for (const elemKey of elementsToHighlight) {
        const bbox = currentBboxes[elemKey];
        if (!bbox) continue;

        const elementColor = bbox.original_color || '#2563eb';
        const isPrimary = elemKey === key;

        if (bbox.type === 'line' && bbox.points && bbox.points.length > 1) {
            _drawLineSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY);
        } else if (bbox.type === 'scatter' && bbox.points && bbox.points.length > 0) {
            _drawScatterSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY);
        } else {
            _drawRectSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY);
        }
    }
}

// Helper: Draw line selection (polyline)
function _drawLineSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY) {
    const points = bbox.points.map(pt => {
        const x = offsetX + pt[0] * scaleX;
        const y = offsetY + pt[1] * scaleY;
        return `${x},${y}`;
    }).join(' ');

    const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    polyline.setAttribute('points', points);
    polyline.setAttribute('class', 'selection-polyline');
    polyline.style.setProperty('--element-color', elementColor);
    if (isPrimary) {
        polyline.style.strokeWidth = '10';
        polyline.style.strokeOpacity = '0.6';
    }
    overlay.appendChild(polyline);
}

// Helper: Draw scatter selection (circles)
function _drawScatterSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY) {
    bbox.points.forEach(pt => {
        const cx = offsetX + pt[0] * scaleX;
        const cy = offsetY + pt[1] * scaleY;

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', isPrimary ? 4 : 3);
        circle.setAttribute('class', 'selection-circle-subtle');
        circle.style.setProperty('--element-color', elementColor);
        overlay.appendChild(circle);
    });
}

// Helper: Draw rectangle selection
function _drawRectSelection(overlay, bbox, elementColor, isPrimary, offsetX, offsetY, scaleX, scaleY) {
    const x = offsetX + bbox.x * scaleX;
    const y = offsetY + bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', Math.max(width, 2));
    rect.setAttribute('height', Math.max(height, 2));
    rect.setAttribute('class', 'selection-rect');
    rect.style.setProperty('--element-color', elementColor);

    if (isPrimary) {
        rect.classList.add('selection-primary');
    }

    overlay.appendChild(rect);
}

// Clear selection overlay
function clearSelectionOverlay() {
    document.getElementById('selection-overlay').innerHTML = '';
}

// Sync properties panel to selected element
function syncPropertiesToElement(element) {
    // Always show dynamic call properties for the selected element
    showDynamicCallProperties(element);

    // In 'selected' mode, only show call properties (no section highlighting)
    if (viewMode === 'selected') {
        return;
    }

    // Map element types to section IDs (for 'all' mode)
    const sectionMap = {
        'axes': 'section-dimensions',
        'line': 'section-lines',
        'scatter': 'section-markers',
        'bar': 'section-lines',
        'fill': 'section-lines',
        'boxplot': 'section-boxplot',
        'violin': 'section-violin',
        'title': 'section-fonts',
        'xlabel': 'section-fonts',
        'ylabel': 'section-fonts',
        'xticks': 'section-ticks',
        'yticks': 'section-ticks',
        'legend': 'section-legend',
        'spine': 'section-dimensions',
        'contour': 'section-dimensions',
        'image': 'section-dimensions',
        'pie': 'section-dimensions',
        'hist': 'section-lines',
        'quiver': 'section-lines',
    };

    const sectionId = sectionMap[element.type] || 'section-dimensions';

    // Close all sections and remove highlights (accordion behavior)
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('section-highlighted');
        if (section.id && section.id !== 'section-download') {
            section.removeAttribute('open');
        }
    });

    // Find and highlight the relevant section
    const section = document.getElementById(sectionId);
    if (section) {
        section.setAttribute('open', '');
        section.classList.add('section-highlighted');
        setTimeout(() => {
            section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 50);
    }

    updateElementProperties(element);
}

// Update property values for selected element
function updateElementProperties(element) {
    // Clear previous field highlights
    document.querySelectorAll('.form-row').forEach(row => {
        row.classList.remove('field-highlighted');
    });

    // Map element types to relevant form field IDs
    const fieldMap = {
        'line': ['lines_trace_mm', 'lines_errorbar_mm', 'lines_errorbar_cap_mm'],
        'scatter': ['markers_size_mm', 'markers_scatter_mm', 'markers_edge_width_mm'],
        'bar': ['lines_trace_mm'],
        'fill': ['lines_trace_mm'],
        'boxplot': ['lines_trace_mm', 'markers_flier_mm', 'boxplot_median_color'],
        'violin': ['lines_trace_mm'],
        'title': ['fonts_title_pt', 'fonts_family'],
        'xlabel': ['fonts_axis_label_pt', 'fonts_family'],
        'ylabel': ['fonts_axis_label_pt', 'fonts_family'],
        'xticks': ['fonts_tick_label_pt', 'ticks_length_mm', 'ticks_direction'],
        'yticks': ['fonts_tick_label_pt', 'ticks_length_mm', 'ticks_direction'],
        'legend': ['fonts_legend_pt', 'legend_frameon', 'legend_loc'],
        'spine': ['axes_thickness_mm'],
    };

    const relevantFields = fieldMap[element.type] || [];

    // Highlight relevant form rows
    relevantFields.forEach(fieldId => {
        const row = document.querySelector(`[data-field="${fieldId}"]`);
        if (row) {
            row.classList.add('field-highlighted');
        }
    });

    // Show dynamic call properties for this element
    showDynamicCallProperties(element);
}
"""

__all__ = ["SCRIPTS_SELECTION"]

# EOF
