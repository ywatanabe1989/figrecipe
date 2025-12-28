#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation drag-to-move JavaScript for the figure editor.

This module contains the JavaScript code for:
- Detecting mousedown on annotation elements (panel labels, text, arrows)
- Handling drag movement with visual feedback
- Updating annotation position on drop

Annotation coordinates are in axes-relative units (0-1 range).
"""

SCRIPTS_ANNOTATION_DRAG = """
// ===== ANNOTATION DRAG-TO-MOVE =====

let isDraggingAnnotation = false;
let annotationDragStartPos = null;
let annotationDragStartBbox = null;
let annotationDragOverlay = null;
let annotationDragLabel = null;
let annotationKey = null;
let annotationAxIndex = 0;
let annotationDragOffset = null;  // Offset from click to bbox corner for precise cursor following
let annotationOriginalRelPos = null;  // Original axes-relative position (anchor point)
let annotationLastSnappedBbox = null;  // Last snapped bbox position (used on mouse up)

// Track annotation positions for undo support (axes-relative 0-1 coordinates)
// Key format: "ax{axIndex}_text{textIndex}" or "ax{axIndex}_panel_label0"
let annotationPositions = {};  // {ax0_text0: {x, y}, ...}

// Initialize annotation positions from current bboxes
function initAnnotationPositions() {
    if (typeof currentBboxes === 'undefined') return;

    annotationPositions = {};
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (isAnnotationElement(key) && bbox.rel_x !== undefined && bbox.rel_y !== undefined) {
            annotationPositions[key] = {
                x: bbox.rel_x,
                y: bbox.rel_y,
                type: bbox.type || 'text'
            };
        }
    }
    console.log('[AnnotationDrag] Initialized annotation positions:', Object.keys(annotationPositions).length);
}

// Snap configuration for annotations (uses same visual system as panel snap)
const ANNOTATION_SNAP = {
    enabled: true,
    threshold: 5,       // mm - same as panel snap threshold
    magneticZone: 10,   // mm - distance where magnetic attraction starts
    snapToEdges: true,
    snapToOtherLabels: true  // Snap to other panel labels
};

// Initialize annotation drag functionality
function initAnnotationDrag() {
    console.log('[AnnotationDrag] initAnnotationDrag called');
    const zoomContainer = document.getElementById('zoom-container');
    if (!zoomContainer) {
        console.error('[AnnotationDrag] zoom-container not found!');
        return;
    }

    // Create annotation drag overlay element (bounding box)
    annotationDragOverlay = document.createElement('div');
    annotationDragOverlay.id = 'annotation-drag-overlay';
    annotationDragOverlay.style.cssText = `
        position: absolute;
        border: 2px dashed #8b5cf6;
        background: rgba(139, 92, 246, 0.15);
        pointer-events: none;
        display: none;
        z-index: 1001;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
        transition: box-shadow 0.1s ease;
    `;
    zoomContainer.appendChild(annotationDragOverlay);

    // Create label showing text content during drag
    annotationDragLabel = document.createElement('div');
    annotationDragLabel.id = 'annotation-drag-label';
    annotationDragLabel.style.cssText = `
        position: absolute;
        background: #8b5cf6;
        color: white;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: bold;
        pointer-events: none;
        display: none;
        z-index: 1002;
        white-space: nowrap;
    `;
    zoomContainer.appendChild(annotationDragLabel);

    console.log('[AnnotationDrag] Overlay and label created');
    // Note: Snap guides are shared with panel snap (created in initPanelSnap)

    // Initialize positions after a short delay to ensure bboxes are loaded
    setTimeout(initAnnotationPositions, 500);
}

// Check if an element is an annotation (panel_label, text, arrow)
function isAnnotationElement(key) {
    if (!key) return false;
    return key.includes('_panel_label') ||
           key.includes('_text_') ||
           key.includes('_arrow_');
}

// Handle annotation drag start (called from hitmap click handler)
function startAnnotationDrag(event, elemKey) {
    console.log('[AnnotationDrag] startAnnotationDrag called for:', elemKey);

    const img = document.getElementById('preview-image');
    if (!img) return false;

    const bbox = currentBboxes[elemKey];
    if (!bbox) return false;

    event.preventDefault();
    event.stopPropagation();

    // Capture state before drag for undo
    if (typeof pushToHistory === 'function') {
        pushToHistory();
    }

    isDraggingAnnotation = true;
    annotationKey = elemKey;
    annotationDragStartPos = { x: event.clientX, y: event.clientY };
    annotationDragStartBbox = { ...bbox };

    // Store the original axes-relative position (anchor point, not bbox corner)
    // This is the actual text position used by matplotlib
    annotationOriginalRelPos = {
        x: bbox.rel_x !== undefined ? bbox.rel_x : 0,
        y: bbox.rel_y !== undefined ? bbox.rel_y : 0
    };
    console.log('[AnnotationDrag] Original anchor position (rel):', annotationOriginalRelPos.x.toFixed(3), annotationOriginalRelPos.y.toFixed(3));

    // Calculate offset from click position to bbox corner for precise cursor following
    // This ensures the overlay follows the cursor at exactly the click point
    const rect = img.getBoundingClientRect();
    const scaleX = rect.width / img.naturalWidth;
    const scaleY = rect.height / img.naturalHeight;
    const bboxScreenX = bbox.x * scaleX;
    const bboxScreenY = bbox.y * scaleY;
    // Offset is the distance from bbox corner to click point (in screen pixels)
    annotationDragOffset = {
        x: event.clientX - rect.left - bboxScreenX,
        y: event.clientY - rect.top - bboxScreenY
    };
    console.log('[AnnotationDrag] Click offset from bbox corner:', annotationDragOffset.x.toFixed(1), annotationDragOffset.y.toFixed(1));

    // Extract axis index from key (e.g., "ax0_panel_label" -> 0)
    const match = elemKey.match(/ax(\\d+)_/);
    annotationAxIndex = match ? parseInt(match[1], 10) : 0;

    // Show drag overlay
    if (annotationDragOverlay) {
        updateAnnotationDragOverlay(bbox);
        annotationDragOverlay.style.display = 'block';
        // Add glow effect when dragging starts
        annotationDragOverlay.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.5)';
    }

    // Show label with text content
    if (annotationDragLabel && bbox.text) {
        annotationDragLabel.textContent = bbox.text;
        annotationDragLabel.style.display = 'block';
    }

    // Add temporary event listeners
    document.addEventListener('mousemove', handleAnnotationDragMove);
    document.addEventListener('mouseup', handleAnnotationDragEnd);

    document.body.style.cursor = 'move';
    console.log('[AnnotationDrag] Started dragging annotation:', bbox.text || elemKey);
    return true;
}

// Handle mouse move during annotation drag
function handleAnnotationDragMove(event) {
    if (!isDraggingAnnotation) return;

    event.preventDefault();

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();

    // Calculate new bbox position directly from cursor position minus offset
    // This ensures the overlay follows the cursor precisely at the click point
    const screenToImgX = img.naturalWidth / rect.width;
    const screenToImgY = img.naturalHeight / rect.height;

    // Convert current mouse position to image coordinates, accounting for the click offset
    const cursorScreenX = event.clientX - rect.left - annotationDragOffset.x;
    const cursorScreenY = event.clientY - rect.top - annotationDragOffset.y;

    let newBbox = {
        x: cursorScreenX * screenToImgX,
        y: cursorScreenY * screenToImgY,
        width: annotationDragStartBbox.width,
        height: annotationDragStartBbox.height
    };

    // Apply snap and update visual overlay
    const snapResult = applyAnnotationSnap(newBbox, annotationAxIndex);
    updateAnnotationDragOverlay(snapResult.bbox, snapResult.snapped);

    // Store snapped position for use on mouse up
    annotationLastSnappedBbox = snapResult.bbox;
}

// Update the annotation drag overlay position
function updateAnnotationDragOverlay(bbox, isSnapped = false) {
    if (!annotationDragOverlay) return;

    const img = document.getElementById('preview-image');
    if (!img) return;

    const rect = img.getBoundingClientRect();
    const scaleX = rect.width / img.naturalWidth;
    const scaleY = rect.height / img.naturalHeight;

    const left = bbox.x * scaleX;
    const top = bbox.y * scaleY;
    const width = bbox.width * scaleX;
    const height = bbox.height * scaleY;

    annotationDragOverlay.style.left = `${left}px`;
    annotationDragOverlay.style.top = `${top}px`;
    annotationDragOverlay.style.width = `${width}px`;
    annotationDragOverlay.style.height = `${height}px`;

    // Visual feedback for snap
    if (isSnapped) {
        annotationDragOverlay.style.borderColor = '#22c55e';  // Green when snapped
        annotationDragOverlay.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.5)';
    } else {
        annotationDragOverlay.style.borderColor = '#8b5cf6';  // Purple when not snapped
        annotationDragOverlay.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.5)';
    }

    // Update label position (above the overlay)
    if (annotationDragLabel && annotationDragLabel.style.display !== 'none') {
        annotationDragLabel.style.left = `${left}px`;
        annotationDragLabel.style.top = `${top - 20}px`;
    }
}

// Get snap targets from other panel labels (for alignment)
function getAnnotationSnapTargets(excludeKey) {
    const targets = { h: [], v: [] };
    if (typeof currentBboxes === 'undefined' || !figSize.width_mm) return targets;
    const img = document.getElementById('preview-image');
    if (!img) return targets;
    const pxToMmX = figSize.width_mm / img.naturalWidth;
    const pxToMmY = figSize.height_mm / img.naturalHeight;
    for (const [key, bbox] of Object.entries(currentBboxes)) {
        if (key === excludeKey || !key.includes('_panel_label')) continue;
        const cx = (bbox.x + bbox.width / 2) * pxToMmX;
        const cy = (bbox.y + bbox.height / 2) * pxToMmY;
        targets.v.push({ pos: cx, type: 'label-center' });
        targets.h.push({ pos: cy, type: 'label-center' });
    }
    return targets;
}

// Apply snap using CENTER-TO-CENTER alignment for labels
// Always snaps to the CLOSEST target within threshold (not the first match)
function applyAnnotationSnap(newBbox, axIndex) {
    const img = document.getElementById('preview-image');
    const rect = img ? img.getBoundingClientRect() : null;
    if (!ANNOTATION_SNAP.enabled || !img || !figSize.width_mm) {
        if (typeof hideSnapGuides === 'function') hideSnapGuides();
        return { bbox: newBbox, snapped: false, guides: [] };
    }
    const pxToMmX = figSize.width_mm / img.naturalWidth;
    const pxToMmY = figSize.height_mm / img.naturalHeight;
    const threshold = ANNOTATION_SNAP.threshold;
    let snapped = false, snapX = newBbox.x, snapY = newBbox.y;
    const guides = [];
    // Dragged label's CENTER (in mm)
    const cx = (newBbox.x + newBbox.width / 2) * pxToMmX;
    const cy = (newBbox.y + newBbox.height / 2) * pxToMmY;
    const hw = newBbox.width / 2, hh = newBbox.height / 2;

    // Snap to CLOSEST panel label center (center-to-center alignment)
    if (ANNOTATION_SNAP.snapToOtherLabels && annotationKey) {
        const targets = getAnnotationSnapTargets(annotationKey);
        // Find closest vertical target (X alignment)
        let bestV = null, bestVDist = threshold;
        for (const t of targets.v) {
            const dist = Math.abs(cx - t.pos);
            if (dist < bestVDist) { bestVDist = dist; bestV = t; }
        }
        if (bestV) {
            snapX = bestV.pos / pxToMmX - hw;
            snapped = true;
            guides.push({type:'vertical',pos:bestV.pos,targetType:'label-center',strength:1});
            console.log('[AnnotationSnap] X snap to', bestV.pos.toFixed(1), 'mm (dist:', bestVDist.toFixed(2), 'mm)');
        }
        // Find closest horizontal target (Y alignment)
        let bestH = null, bestHDist = threshold;
        for (const t of targets.h) {
            const dist = Math.abs(cy - t.pos);
            if (dist < bestHDist) { bestHDist = dist; bestH = t; }
        }
        if (bestH) {
            snapY = bestH.pos / pxToMmY - hh;
            snapped = true;
            guides.push({type:'horizontal',pos:bestH.pos,targetType:'label-center',strength:1});
            console.log('[AnnotationSnap] Y snap to', bestH.pos.toFixed(1), 'mm (dist:', bestHDist.toFixed(2), 'mm)');
        }
    }
    // Show/hide snap guides
    if (guides.length > 0 && typeof showSnapGuides === 'function' && rect) showSnapGuides(guides, rect);
    else if (typeof hideSnapGuides === 'function') hideSnapGuides();
    return { bbox: {...newBbox, x: snapX, y: snapY}, snapped: snapped, guides: guides };
}

// Handle mouse up - complete the annotation drag
async function handleAnnotationDragEnd(event) {
    console.log('[AnnotationDrag] handleAnnotationDragEnd called');
    if (!isDraggingAnnotation) return;

    // Remove temporary event listeners
    document.removeEventListener('mousemove', handleAnnotationDragMove);
    document.removeEventListener('mouseup', handleAnnotationDragEnd);

    // Hide overlay, label, and snap guides
    if (annotationDragOverlay) {
        annotationDragOverlay.style.display = 'none';
        annotationDragOverlay.style.borderColor = '#8b5cf6';  // Reset color
    }
    if (annotationDragLabel) {
        annotationDragLabel.style.display = 'none';
    }
    if (typeof hideSnapGuides === 'function') hideSnapGuides();
    document.body.style.cursor = '';

    const img = document.getElementById('preview-image');
    if (!img) {
        isDraggingAnnotation = false;
        return;
    }

    const rect = img.getBoundingClientRect();

    // Calculate delta in pixels (for threshold check only)
    const deltaX = event.clientX - annotationDragStartPos.x;
    const deltaY = event.clientY - annotationDragStartPos.y;

    // Only update if moved significantly (5px threshold)
    if (Math.abs(deltaX) < 5 && Math.abs(deltaY) < 5) {
        console.log('[AnnotationDrag] Movement below threshold, not updating');
        isDraggingAnnotation = false;
        return;
    }

    const axKey = Object.keys(panelPositions).sort()[annotationAxIndex];
    const axPos = panelPositions[axKey];
    if (!axPos || !figSize.width_mm || !figSize.height_mm) {
        console.error('[AnnotationDrag] Cannot calculate axes-relative position');
        isDraggingAnnotation = false;
        return;
    }

    // Calculate position using DELTA from original to snapped/current position
    // This ensures coordinates stay valid even when snapping to labels from other axes
    const pxToMmX = figSize.width_mm / img.naturalWidth;
    const pxToMmY = figSize.height_mm / img.naturalHeight;

    // Original bbox center in mm
    const origCenterX_mm = (annotationDragStartBbox.x + annotationDragStartBbox.width / 2) * pxToMmX;
    const origCenterY_mm = (annotationDragStartBbox.y + annotationDragStartBbox.height / 2) * pxToMmY;

    let relX, relY;

    if (annotationLastSnappedBbox) {
        // Calculate delta from original to snapped position (in mm)
        const snappedCenterX_mm = (annotationLastSnappedBbox.x + annotationLastSnappedBbox.width / 2) * pxToMmX;
        const snappedCenterY_mm = (annotationLastSnappedBbox.y + annotationLastSnappedBbox.height / 2) * pxToMmY;
        const deltaX_mm = snappedCenterX_mm - origCenterX_mm;
        const deltaY_mm = snappedCenterY_mm - origCenterY_mm;

        // Convert mm delta to axes-relative delta
        const relDeltaX = deltaX_mm / axPos.width;
        const relDeltaY = -deltaY_mm / axPos.height;  // Y flipped (figure Y increases down, axes Y increases up)

        // Apply delta to original axes-relative position
        relX = annotationOriginalRelPos.x + relDeltaX;
        relY = annotationOriginalRelPos.y + relDeltaY;

        console.log('[AnnotationDrag] Using SNAPPED delta | Delta mm:', deltaX_mm.toFixed(2), deltaY_mm.toFixed(2),
                    '| Delta rel:', relDeltaX.toFixed(3), relDeltaY.toFixed(3), '| New pos:', relX.toFixed(3), relY.toFixed(3));
    } else {
        // Fallback: Calculate from cursor delta
        const screenToImgScale = img.naturalWidth / rect.width;
        const screenDeltaX = event.clientX - annotationDragStartPos.x;
        const screenDeltaY = event.clientY - annotationDragStartPos.y;
        const mmDeltaX = screenDeltaX * screenToImgScale * pxToMmX;
        const mmDeltaY = screenDeltaY * screenToImgScale * pxToMmY;
        const relDeltaX = mmDeltaX / axPos.width;
        const relDeltaY = -mmDeltaY / axPos.height;  // Y flipped

        relX = annotationOriginalRelPos.x + relDeltaX;
        relY = annotationOriginalRelPos.y + relDeltaY;
        console.log('[AnnotationDrag] Using CURSOR delta | Delta:', relDeltaX.toFixed(3), relDeltaY.toFixed(3),
                    '| New pos:', relX.toFixed(3), relY.toFixed(3));
    }

    // Get annotation type and index from key
    const bboxInfo = annotationDragStartBbox;
    const annotationType = bboxInfo.type || 'text';
    const textIndex = bboxInfo.text_index !== undefined ? bboxInfo.text_index : 0;

    // Apply the new position
    await applyAnnotationPosition(annotationAxIndex, annotationType, textIndex, relX, relY);

    // Update annotationPositions for undo support
    if (annotationKey) {
        annotationPositions[annotationKey] = {
            x: relX,
            y: relY,
            type: annotationType
        };
        console.log('[AnnotationDrag] Updated position:', annotationKey, relX.toFixed(3), relY.toFixed(3));
    }

    // Reset state
    isDraggingAnnotation = false;
    annotationDragStartPos = null;
    annotationDragStartBbox = null;
    annotationDragOffset = null;
    annotationOriginalRelPos = null;
    annotationLastSnappedBbox = null;
    annotationKey = null;
    console.log('[AnnotationDrag] Drag state reset');
}

// Apply the dragged annotation position to the server
async function applyAnnotationPosition(axIndex, annotationType, textIndex, x, y) {
    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_annotation_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ax_index: axIndex,
                annotation_type: annotationType,
                text_index: textIndex,
                x: x,
                y: y
            })
        });

        const data = await response.json();

        if (data.success) {
            // Update preview image
            const img = document.getElementById('preview-image');
            if (img) {
                await new Promise((resolve) => {
                    img.onload = resolve;
                    img.src = 'data:image/png;base64,' + data.image;
                });
            }

            // Update bboxes and hitmap
            if (data.bboxes) {
                currentBboxes = data.bboxes;
                loadHitmap();
                updateHitRegions();
                // Reinitialize annotation positions from new bboxes
                initAnnotationPositions();
            }

            console.log('[AnnotationDrag] Annotation position updated successfully');
        } else {
            console.error('[AnnotationDrag] Failed to update annotation:', data.error);
        }
    } catch (error) {
        console.error('[AnnotationDrag] Failed to update annotation:', error);
    }

    document.body.classList.remove('loading');
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initAnnotationDrag);
"""

__all__ = ["SCRIPTS_ANNOTATION_DRAG"]

# EOF
