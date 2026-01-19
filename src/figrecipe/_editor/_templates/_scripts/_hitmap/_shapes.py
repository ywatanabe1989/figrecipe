#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shape creation helper functions for hit regions."""

SCRIPTS_HITMAP_SHAPES = """
// ===== SHAPE CREATION HELPERS =====

// Helper: Create polyline shape for lines
function _createPolylineShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    const points = bbox.points.map(pt => {
        const x = offsetX + pt[0] * scaleX;
        const y = offsetY + pt[1] * scaleY;
        return `${x},${y}`;
    }).join(' ');

    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    shape.setAttribute('points', points);
    shape.setAttribute('class', 'hitregion-polyline');
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }
    return shape;
}

// Helper: Create scatter circles group
function _createScatterShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    shape.setAttribute('class', 'scatter-group');
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }

    const hitRadius = 8;  // Larger radius for easier click targeting
    const allCircles = [];

    bbox.points.forEach((pt, idx) => {
        const cx = offsetX + pt[0] * scaleX;
        const cy = offsetY + pt[1] * scaleY;

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', hitRadius);
        circle.setAttribute('class', 'hitregion-circle');
        circle.setAttribute('data-key', key);
        circle.setAttribute('data-point-index', idx);

        allCircles.push(circle);
        shape.appendChild(circle);
    });

    // Add event handlers to scatter group
    shape.addEventListener('mouseenter', () => {
        handleHitRegionHover(key, bbox);
        allCircles.forEach(c => c.classList.add('hovered'));
        shape.classList.add('hovered');
    });
    shape.addEventListener('mouseleave', () => {
        handleHitRegionLeave();
        allCircles.forEach(c => c.classList.remove('hovered'));
        shape.classList.remove('hovered');
    });
    shape.addEventListener('click', (e) => handleHitRegionClick(e, key, bbox));

    return shape;
}

// Helper: Create rectangle shape for other elements
function _createRectShape(bbox, key, originalColor, offsetX, offsetY, scaleX, scaleY) {
    let regionClass = 'hitregion-rect';
    if (bbox.type === 'axes') {
        regionClass += ' axes-region';  // Special class for axes - lower z-order
    } else if (bbox.type === 'line' || bbox.type === 'scatter') {
        regionClass += ' line-region';
    } else if (['title', 'xlabel', 'ylabel', 'suptitle', 'supxlabel', 'supylabel'].includes(bbox.type)) {
        regionClass += ' text-region';
    } else if (bbox.type === 'legend') {
        regionClass += ' legend-region';
    } else if (bbox.type === 'xticks' || bbox.type === 'yticks') {
        regionClass += ' tick-region';
    }

    const x = offsetX + bbox.x * scaleX;
    const y = offsetY + bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    const shape = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    shape.setAttribute('x', x);
    shape.setAttribute('y', y);
    shape.setAttribute('width', Math.max(width, 5));
    shape.setAttribute('height', Math.max(height, 5));
    shape.setAttribute('class', regionClass);
    shape.setAttribute('data-key', key);
    if (originalColor) {
        shape.style.setProperty('--element-color', originalColor);
    }

    return { shape, labelX: x + 2, labelY: y - 3 };
}
"""

__all__ = ["SCRIPTS_HITMAP_SHAPES"]

# EOF
