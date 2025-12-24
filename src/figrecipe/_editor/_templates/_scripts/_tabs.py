#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tab navigation JavaScript for the figure editor.

This module contains the JavaScript code for:
- Tab switching (Figure/Axis/Element)
- Auto-switching based on selected element
- Tab hints management
"""

SCRIPTS_TABS = """
// ===== TAB NAVIGATION =====

// Current active tab
let currentTab = 'figure';

// Element type to tab mapping
const AXIS_TYPES = ['title', 'xlabel', 'ylabel', 'suptitle', 'supxlabel', 'supylabel', 'legend'];
const ELEMENT_TYPES = ['line', 'scatter', 'bar', 'hist', 'fill', 'boxplot', 'violin', 'image', 'linecollection', 'quiver', 'pie', 'contour', 'specgram'];

// Switch between Figure/Axis/Element tabs
function switchTab(tabName) {
    currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id === `tab-${tabName}`);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-content-${tabName}`);
    });

    // Update hints based on selection state
    updateTabHints();
}

// Get appropriate tab for element type
function getTabForElementType(elementType) {
    if (!elementType) return 'figure';
    if (AXIS_TYPES.includes(elementType)) return 'axis';
    if (ELEMENT_TYPES.includes(elementType)) return 'element';
    return 'figure';
}

// Auto-switch to appropriate tab based on selected element
function autoSwitchTab(elementType) {
    const targetTab = getTabForElementType(elementType);
    if (targetTab !== currentTab) {
        switchTab(targetTab);
    }
}

// Update tab hints based on current state
function updateTabHints() {
    const axisHint = document.getElementById('axis-tab-hint');
    const elementHint = document.getElementById('element-tab-hint');
    const elementPanel = document.getElementById('selected-element-panel');
    const dynamicProps = document.getElementById('dynamic-call-properties');

    if (currentTab === 'axis') {
        if (selectedElement && AXIS_TYPES.includes(selectedElement.type)) {
            if (axisHint) axisHint.style.display = 'none';
        } else {
            if (axisHint) axisHint.style.display = 'block';
        }
    }

    if (currentTab === 'element') {
        if (selectedElement && ELEMENT_TYPES.includes(selectedElement.type)) {
            if (elementHint) elementHint.style.display = 'none';
            if (elementPanel) {
                elementPanel.style.display = 'block';
                document.getElementById('element-type-badge').textContent = selectedElement.type;
                document.getElementById('element-name').textContent = selectedElement.label || selectedElement.key;
            }
        } else {
            if (elementHint) elementHint.style.display = 'block';
            if (elementPanel) elementPanel.style.display = 'none';
            if (dynamicProps) dynamicProps.style.display = 'none';
        }
    }
}
"""

__all__ = ["SCRIPTS_TABS"]

# EOF
