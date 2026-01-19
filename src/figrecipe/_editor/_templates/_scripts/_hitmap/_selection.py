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

// Select an element (and its logical group if applicable)
function selectElement(element) {
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
