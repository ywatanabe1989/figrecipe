#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Element selection and group functions for hitmap."""

SCRIPTS_HITMAP_SELECTION = """
// ===== ELEMENT SELECTION =====

// Find all elements belonging to the same logical group
function findGroupElements(callId) {
    if (!callId || !colorMap) return [];

    const groupElements = [];
    for (const [key, info] of Object.entries(colorMap)) {
        if (info.call_id === callId) {
            groupElements.push({ key, ...info });
        }
    }
    return groupElements;
}

// Get representative color for a call_id group
function getGroupRepresentativeColor(callId, fallbackColor) {
    if (!callId || !colorMap) return fallbackColor;
    const groupElements = findGroupElements(callId);
    return groupElements.length > 0 && groupElements[0].original_color ? groupElements[0].original_color : fallbackColor;
}

// Try to find a parent diagram box for a text/box element
// Returns the diagram_box element from colorMap if the text is inside one, else null
function findParentDiagramBox(element) {
    if (!colorMap) return null;
    const axIdx = element.ax_index;
    if (axIdx === undefined) return null;

    // Check if this axes has any diagram elements
    const diagramEntries = Object.entries(colorMap).filter(
        ([k, info]) => info.ax_index === axIdx && info.type === 'diagram_box'
    );
    if (diagramEntries.length === 0) return null;

    // Strategy 1: Match by label — text label often equals diagram box title
    if (element.label) {
        const textLabel = element.label.trim().toLowerCase();
        for (const [key, info] of diagramEntries) {
            if (info.label && info.label.trim().toLowerCase() === textLabel) {
                return { key, ...info };
            }
        }
    }

    // Strategy 2: Spatial containment using bboxes
    if (currentBboxes) {
        const elemBbox = currentBboxes[element.key];
        if (elemBbox) {
            const elemCx = elemBbox.x + elemBbox.width / 2;
            const elemCy = elemBbox.y + elemBbox.height / 2;

            let best = null, bestDist = Infinity;
            for (const [key, info] of diagramEntries) {
                const boxBbox = currentBboxes[key];
                if (!boxBbox) continue;
                // Check containment first
                if (elemCx >= boxBbox.x && elemCx <= boxBbox.x + boxBbox.width &&
                    elemCy >= boxBbox.y && elemCy <= boxBbox.y + boxBbox.height) {
                    return { key, ...info };
                }
                // Otherwise, track closest
                const dx = elemCx - (boxBbox.x + boxBbox.width / 2);
                const dy = elemCy - (boxBbox.y + boxBbox.height / 2);
                const dist = dx * dx + dy * dy;
                if (dist < bestDist) { bestDist = dist; best = { key, ...info }; }
            }
            if (best) return best;
        }
    }

    // Strategy 3: Fallback to first diagram box at same axes
    const [key, info] = diagramEntries[0];
    return { key, ...info };
}

// Select an element (and its logical group if applicable)
function selectElement(element) {
    // If text/box clicked inside a diagram, redirect to the parent diagram box
    // so the diagram editor (with title field) shows instead of generic text info
    if ((element.type === 'text' || element.type === 'box') && !element.diagram_element) {
        const parentBox = findParentDiagramBox(element);
        if (parentBox) {
            console.log('[selectElement] Redirecting text to parent diagram box:', parentBox.key);
            element = parentBox;
        }
    }

    selectedElement = element;
    const callId = element.call_id || element.label;
    const groupElements = findGroupElements(callId);
    selectedElement.groupElements = groupElements.length > 1 ? groupElements : null;

    drawSelection(element.key);
    autoSwitchTab(element.type);
    updateTabHints();
    syncPropertiesToElement(element);
    if (element && typeof syncDatatableToElement === 'function') syncDatatableToElement(element);

    // Always sync panel position for any element that belongs to a panel
    const axIndex = element.ax_index !== undefined ? element.ax_index : getPanelIndexFromKey(element.key);
    if (axIndex !== null && typeof selectPanelByIndex === 'function') {
        selectPanelByIndex(axIndex, element.type === 'axes');
    }
}
"""

__all__ = ["SCRIPTS_HITMAP_SELECTION"]

# EOF
