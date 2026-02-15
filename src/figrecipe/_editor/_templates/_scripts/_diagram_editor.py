#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram element editor JavaScript for the figure editor.

This module contains the JavaScript code for editing diagram-specific
elements (boxes, containers, arrows) via the YAML override system.
Diagram overrides use dotted param paths like "boxes.a.fill_color"
that are deep-merged into diagram_data by _apply_diagram_override().
"""

SCRIPTS_DIAGRAM_EDITOR = """
// ===== DIAGRAM ELEMENT EDITOR =====

// Show property editor for diagram elements (boxes, containers, arrows)
function showDiagramElementProperties(element, callId) {
    const container = document.getElementById('dynamic-call-properties');
    if (!container) return;

    container.style.display = 'block';

    // Parse diagram_element: "box:a", "container:group1", "arrow:0"
    const colonIdx = element.diagram_element.indexOf(':');
    const elemCategory = element.diagram_element.substring(0, colonIdx);
    const elemId = element.diagram_element.substring(colonIdx + 1);

    // Map category to collection name for override paths
    const collectionMap = { 'box': 'boxes', 'container': 'containers', 'arrow': 'arrows' };
    const collection = collectionMap[elemCategory] || elemCategory;

    // Header
    const header = document.createElement('div');
    header.className = 'dynamic-props-header';
    const typeLabel = elemCategory === 'arrow' ? 'Arrow' :
                      elemCategory === 'container' ? 'Container' : 'Box';
    header.innerHTML = `<strong>Diagram ${typeLabel}</strong> <span class="call-id">${element.label}</span>`;
    container.appendChild(header);

    // Find element data from callsData
    let elemData = {};
    const callData = callsData[callId];
    if (callData && callData.kwargs) {
        const diagramData = callData.kwargs.diagram_data || callData.kwargs.schematic_data;
        if (diagramData) {
            const items = diagramData[collection] || [];
            if (elemCategory === 'arrow') {
                const idx = parseInt(elemId, 10);
                if (idx >= 0 && idx < items.length) {
                    elemData = items[idx];
                }
            } else {
                elemData = items.find(item => item.id === elemId) || {};
            }
        }
    }

    // Define editable properties per element type
    let editableProps;
    if (elemCategory === 'arrow') {
        editableProps = [
            { key: 'color', label: 'Color', type: 'color' },
            { key: 'style', label: 'Style', type: 'select', options: ['solid', 'dashed', 'dotted'] },
            { key: 'linewidth_mm', label: 'Line Width (mm)', type: 'number', step: 0.1 },
            { key: 'label', label: 'Label', type: 'text' },
        ];
    } else {
        editableProps = [
            { key: 'fill_color', label: 'Fill Color', type: 'color' },
            { key: 'border_color', label: 'Border Color', type: 'color' },
            { key: 'title_color', label: 'Title Color', type: 'color' },
            { key: 'title', label: 'Title', type: 'text' },
            { key: 'emphasis', label: 'Emphasis', type: 'select',
              options: ['normal', 'bold', 'muted'] },
        ];
    }

    // Create form fields
    const section = document.createElement('div');
    section.className = 'dynamic-props-section';
    section.innerHTML = '<div class="dynamic-props-label">Properties:</div>';

    for (const prop of editableProps) {
        const row = document.createElement('div');
        row.className = 'form-row dynamic-field';

        const label = document.createElement('label');
        label.textContent = prop.label;

        let input;
        let currentValue = elemData[prop.key];
        // For fill_color, use element's rendered color from hitmap as fallback
        if (!currentValue && prop.key === 'fill_color' && element.original_color) {
            currentValue = element.original_color;
        }

        if (prop.type === 'color') {
            input = _createDiagramColorInput(
                callId, collection, elemId, prop.key, currentValue || '#cccccc'
            );
        } else if (prop.type === 'select') {
            input = document.createElement('select');
            input.className = 'dynamic-input';
            for (const opt of prop.options) {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                if (currentValue === opt) option.selected = true;
                input.appendChild(option);
            }
            input.addEventListener('change', function() {
                _handleDiagramParamChange(
                    callId, collection, elemId, prop.key, this.value
                );
            });
        } else if (prop.type === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.step = prop.step || 'any';
            input.value = currentValue != null ? currentValue : '';
            input.className = 'dynamic-input';
            input.addEventListener('change', function() {
                _handleDiagramParamChange(
                    callId, collection, elemId, prop.key, parseFloat(this.value)
                );
            });
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.value = currentValue != null ? String(currentValue) : '';
            input.className = 'dynamic-input';
            input.addEventListener('change', function() {
                _handleDiagramParamChange(
                    callId, collection, elemId, prop.key, this.value
                );
            });
        }

        row.appendChild(label);
        row.appendChild(input);
        section.appendChild(row);
    }

    container.appendChild(section);
}

// Create color input with swatch for diagram elements
function _createDiagramColorInput(callId, collection, elemId, propKey, color) {
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'display: flex; align-items: center; gap: 6px;';

    const swatch = document.createElement('span');
    swatch.style.cssText = `
        display: inline-block; width: 20px; height: 20px;
        border-radius: 3px; border: 1px solid var(--border-color, #444);
        background-color: ${color}; cursor: pointer;
    `;

    const picker = document.createElement('input');
    picker.type = 'color';
    picker.value = color;
    picker.style.cssText = (
        'width: 0; height: 0; padding: 0; border: 0; '
        + 'opacity: 0; position: absolute;'
    );

    const hexLabel = document.createElement('span');
    hexLabel.className = 'arg-value';
    hexLabel.style.fontFamily = 'monospace';
    hexLabel.textContent = color;

    swatch.addEventListener('click', () => picker.click());

    picker.addEventListener('change', function() {
        swatch.style.backgroundColor = this.value;
        hexLabel.textContent = this.value;
        _handleDiagramParamChange(callId, collection, elemId, propKey, this.value);
    });

    wrapper.appendChild(swatch);
    wrapper.appendChild(picker);
    wrapper.appendChild(hexLabel);
    return wrapper;
}

// Send diagram element property change to server via /update_call
async function _handleDiagramParamChange(callId, collection, elemId, propKey, value) {
    const param = `${collection}.${elemId}.${propKey}`;
    console.log(`Diagram param change: ${callId}.${param} = ${value}`);

    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ call_id: callId, param: param, value: value })
        });

        const data = await response.json();

        if (data.success) {
            const img = document.getElementById('preview-image');
            if (img) {
                await new Promise((resolve) => {
                    img.onload = resolve;
                    img.src = 'data:image/png;base64,' + data.image;
                });
            }

            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Sync callsData from server response
            if (callsData[callId] && data.updated_call) {
                callsData[callId].kwargs = data.updated_call.kwargs;
            }

            showToast('Updated', 'success');
        } else {
            showToast('Update failed: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Update failed: ' + error.message, 'error');
    }

    document.body.classList.remove('loading');
}
"""

__all__ = ["SCRIPTS_DIAGRAM_EDITOR"]

# EOF
