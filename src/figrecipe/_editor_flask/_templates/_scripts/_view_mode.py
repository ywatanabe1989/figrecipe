#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""View mode JavaScript for the figure editor.

This module contains the JavaScript code for:
- View mode management (all/selected)
- Property filtering by element type
- Section visibility control
"""

SCRIPTS_VIEW_MODE = """
// ===== VIEW MODE MANAGEMENT =====
// Note: viewMode variable is declared in _core.py

// Set view mode (all or selected)
function setViewMode(mode) {
    viewMode = mode;

    // Update toggle buttons (legacy)
    const btnAll = document.getElementById('btn-show-all');
    const btnSelected = document.getElementById('btn-show-selected');
    if (btnAll) btnAll.classList.toggle('active', mode === 'all');
    if (btnSelected) btnSelected.classList.toggle('active', mode === 'selected');

    // Update controls sections class
    const controlsSections = document.querySelector('.controls-sections');
    controlsSections.classList.toggle('filter-mode', mode === 'selected');

    // Update selection hint
    const hint = document.getElementById('selection-hint');
    if (mode === 'selected') {
        if (selectedElement) {
            hint.textContent = `Showing: ${selectedElement.type}`;
            hint.style.color = 'var(--accent-color)';
            // Hide all style sections - only show call properties
            hideAllStyleSections();
        } else {
            hint.textContent = '';
            hint.style.color = '';
            // Show all when no selection in filter mode
            showAllProperties();
        }
    } else {
        hint.textContent = '';
        showAllProperties();
    }
}

// Hide all style sections (for Selected mode - only show call properties)
function hideAllStyleSections() {
    const sections = document.querySelectorAll('.section[data-element-types]');
    sections.forEach(section => {
        section.classList.add('section-hidden');
        section.classList.remove('section-visible');
    });
}

// Filter properties by element type
function filterPropertiesByElementType(elementType) {
    const sections = document.querySelectorAll('.section[data-element-types]');

    sections.forEach(section => {
        const types = section.getAttribute('data-element-types').split(',');
        const isGlobal = types.includes('global');
        const matches = isGlobal || types.includes(elementType);

        section.classList.toggle('section-hidden', !matches);
        section.classList.toggle('section-visible', matches);

        // If section matches, filter individual form-rows within it
        if (matches && !isGlobal) {
            const formRows = section.querySelectorAll('.form-row[data-element-types]');
            formRows.forEach(row => {
                const rowTypes = row.getAttribute('data-element-types').split(',');
                const rowMatches = rowTypes.includes(elementType);
                row.classList.toggle('field-hidden', !rowMatches);
            });

            // Open matching sections
            section.setAttribute('open', '');
        }
    });

    // Update hint
    const hint = document.getElementById('selection-hint');
    hint.textContent = `Showing: ${elementType}`;
    hint.style.color = 'var(--accent-color)';
}

// Show all properties (remove filtering)
function showAllProperties() {
    const sections = document.querySelectorAll('.section[data-element-types]');

    sections.forEach(section => {
        section.classList.remove('section-hidden', 'section-visible');

        const formRows = section.querySelectorAll('.form-row[data-element-types]');
        formRows.forEach(row => {
            row.classList.remove('field-hidden');
        });
    });
}
"""

__all__ = ["SCRIPTS_VIEW_MODE"]

# EOF
