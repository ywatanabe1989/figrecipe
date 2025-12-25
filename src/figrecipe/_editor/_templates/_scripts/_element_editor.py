#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Element editor JavaScript for the figure editor.

This module contains the JavaScript code for:
- Dynamic form field creation
- Call properties display
- Parameter change handling
"""

SCRIPTS_ELEMENT_EDITOR = """
// ===== ELEMENT EDITOR =====

// Create a dynamic form field for call parameter
function createDynamicField(callId, key, value, sigInfo, isUnused = false) {
    const container = document.createElement('div');
    container.className = 'dynamic-field-container' + (isUnused ? ' unused' : '');

    const row = document.createElement('div');
    row.className = 'form-row dynamic-field';

    const label = document.createElement('label');
    label.textContent = key;

    let input;

    // Handle color list fields (e.g., pie chart colors array)
    if (isColorListField(key, value)) {
        input = createColorListInput(callId, key, value);
        row.appendChild(label);
        row.appendChild(input);
        container.appendChild(row);
        return container;
    }

    if (isColorField(key, sigInfo)) {
        input = createColorInput(callId, key, value);
        row.appendChild(label);
        row.appendChild(input);
        container.appendChild(row);
        return container;
    }

    if (typeof value === 'boolean' || value === true || value === false) {
        input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = value === true;
    } else if (typeof value === 'number') {
        input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.value = value;
    } else if (value === null || value === undefined) {
        input = document.createElement('input');
        input.type = 'text';
        input.value = '';
        input.placeholder = 'null';
    } else {
        input = document.createElement('input');
        input.type = 'text';
        input.value = String(value);
    }

    input.dataset.callId = callId;
    input.dataset.param = key;
    input.className = 'dynamic-input';

    input.addEventListener('change', function() {
        handleDynamicParamChange(callId, key, this);
    });

    row.appendChild(label);
    row.appendChild(input);
    container.appendChild(row);

    if (sigInfo?.type) {
        const typeHint = document.createElement('div');
        typeHint.className = 'type-hint';
        let typeText = sigInfo.type
            .replace(/:mpltype:`([^`]+)`/g, '$1')
            .replace(/`~[^`]+`/g, '')
            .replace(/`([^`]+)`/g, '$1');
        typeHint.textContent = typeText;
        container.appendChild(typeHint);
    }

    return container;
}

// Show dynamic call properties for selected element
function showDynamicCallProperties(element) {
    const container = document.getElementById('dynamic-call-properties');
    if (!container) return;

    container.innerHTML = '';

    // Get call_id - try element directly, then colorMap, then label
    let callId = element.call_id;
    if (!callId && element.key && typeof colorMap !== 'undefined') {
        // Look up call_id from colorMap (hitmap has this info)
        const colorInfo = colorMap[element.key];
        if (colorInfo && colorInfo.call_id) {
            callId = colorInfo.call_id;
        }
    }
    if (!callId) {
        callId = element.label;
    }

    // If no call data found, show basic element info instead
    if (!callId || !callsData[callId]) {
        container.style.display = 'block';

        // Create header with element type
        const header = document.createElement('div');
        header.className = 'dynamic-props-header';
        const elemType = element.type || 'element';
        const elemLabel = element.label || callId || 'unknown';
        header.innerHTML = `<strong>${elemType}</strong> <span class="call-id">${elemLabel}</span>`;
        container.appendChild(header);

        // Show basic info section
        const infoSection = document.createElement('div');
        infoSection.className = 'dynamic-props-section';
        infoSection.innerHTML = '<div class="dynamic-props-label">Element Info:</div>';

        // Show type
        const typeRow = document.createElement('div');
        typeRow.className = 'form-row dynamic-field';
        typeRow.innerHTML = `<label>Type</label><span class="arg-value">${elemType}</span>`;
        infoSection.appendChild(typeRow);

        // Show color if available
        if (element.original_color) {
            const colorRow = document.createElement('div');
            colorRow.className = 'form-row dynamic-field';
            colorRow.innerHTML = `<label>Color</label><span class="arg-value" style="color:${element.original_color}">${element.original_color}</span>`;
            infoSection.appendChild(colorRow);
        }

        // Show axes index
        if (element.ax_index !== undefined) {
            const axRow = document.createElement('div');
            axRow.className = 'form-row dynamic-field';
            axRow.innerHTML = `<label>Axes</label><span class="arg-value">ax_${element.ax_index}</span>`;
            infoSection.appendChild(axRow);
        }

        container.appendChild(infoSection);

        // Add note about no recorded call
        const noteDiv = document.createElement('div');
        noteDiv.className = 'dynamic-props-note';
        noteDiv.style.cssText = 'font-size: 11px; color: var(--text-secondary); margin-top: 8px; font-style: italic;';
        noteDiv.textContent = 'No recorded call data available for this element.';
        container.appendChild(noteDiv);

        return;
    }

    const callData = callsData[callId];
    container.style.display = 'block';

    // Create header
    const header = document.createElement('div');
    header.className = 'dynamic-props-header';
    header.innerHTML = `<strong>${callData.function}()</strong> <span class="call-id">${callId}</span>`;
    container.appendChild(header);

    const usedArgs = callData.args || [];
    const usedKwargs = { ...callData.kwargs } || {};
    const sigArgs = callData.signature?.args || [];
    const sigKwargs = callData.signature?.kwargs || {};

    // Get representative color if not set
    if (!usedKwargs.color && !usedKwargs.c) {
        if ('color' in sigKwargs || 'c' in sigKwargs) {
            const hitmapCallId = element.call_id;
            const groupColor = getGroupRepresentativeColor(hitmapCallId, element.original_color) ||
                               element.original_color;
            if (groupColor) {
                usedKwargs.color = groupColor;
            }
        }
    }

    // Show args (read-only)
    if (usedArgs.length > 0) {
        const argsSection = document.createElement('div');
        argsSection.className = 'dynamic-props-section';
        argsSection.innerHTML = '<div class="dynamic-props-label">Arguments:</div>';

        for (let i = 0; i < usedArgs.length; i++) {
            const arg = usedArgs[i];
            const sigArg = sigArgs[i] || {};
            const row = document.createElement('div');
            row.className = 'form-row dynamic-field arg-field';

            const label = document.createElement('label');
            label.textContent = arg.name;
            if (sigArg.type) label.title = `Type: ${sigArg.type}`;
            if (sigArg.optional) label.textContent += ' (opt)';

            const valueSpan = document.createElement('span');
            valueSpan.className = 'arg-value';
            if (arg.data && Array.isArray(arg.data)) {
                valueSpan.textContent = `[${arg.data.length} items]`;
            } else if (arg.data === '__FILE__') {
                valueSpan.textContent = '[external file]';
            } else {
                valueSpan.textContent = String(arg.data).substring(0, 30);
            }

            row.appendChild(label);
            row.appendChild(valueSpan);
            argsSection.appendChild(row);
        }
        container.appendChild(argsSection);
    }

    // Show used kwargs (editable)
    if (Object.keys(usedKwargs).length > 0) {
        const usedSection = document.createElement('div');
        usedSection.className = 'dynamic-props-section';
        usedSection.innerHTML = '<div class="dynamic-props-label">Used Parameters:</div>';

        for (const [key, value] of Object.entries(usedKwargs)) {
            const field = createDynamicField(callId, key, value, sigKwargs[key]);
            usedSection.appendChild(field);
        }
        container.appendChild(usedSection);
    }

    // Show available (unused) params
    const availableParams = Object.keys(sigKwargs).filter(k => !(k in usedKwargs));
    if (availableParams.length > 0) {
        const availSection = document.createElement('details');
        availSection.className = 'dynamic-props-available';
        availSection.setAttribute('open', '');
        availSection.innerHTML = `<summary>Available Parameters (${availableParams.length})</summary>`;

        const availContent = document.createElement('div');
        availContent.className = 'dynamic-props-section';
        for (const key of availableParams) {
            const sigInfo = sigKwargs[key];
            const field = createDynamicField(callId, key, sigInfo?.default, sigInfo, true);
            availContent.appendChild(field);
        }
        availSection.appendChild(availContent);
        container.appendChild(availSection);
    }
}

// Handle change to dynamic call parameter
async function handleDynamicParamChange(callId, param, input) {
    let value;
    if (input.type === 'checkbox') {
        value = input.checked;
    } else if (input.type === 'number') {
        value = parseFloat(input.value);
        if (isNaN(value)) value = null;
    } else {
        value = input.value || null;
        if (value === 'null') value = null;
    }

    // Resolve color to hex
    const colorParams = ['color', 'facecolor', 'edgecolor', 'markerfacecolor', 'markeredgecolor', 'c'];
    if (value && typeof value === 'string' && colorParams.includes(param.toLowerCase())) {
        value = resolveColorToHex(value);
    }

    console.log(`Dynamic param change: ${callId}.${param} = ${value}`);

    document.body.classList.add('loading');
    if (input.disabled !== undefined) input.disabled = true;

    try {
        const response = await fetch('/update_call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ call_id: callId, param: param, value: value })
        });

        const data = await response.json();

        if (data.success) {
            const img = document.getElementById('preview-image');
            img.src = 'data:image/png;base64,' + data.image;

            if (data.img_size) {
                currentImgWidth = data.img_size.width;
                currentImgHeight = data.img_size.height;
            }

            currentBboxes = data.bboxes;
            loadHitmap();
            updateHitRegions();

            // Sync callsData from server response (source of truth)
            if (callsData[callId] && data.updated_call) {
                callsData[callId].kwargs = data.updated_call.kwargs;
            } else if (callsData[callId]) {
                // Fallback: manual update
                if (value === null) {
                    delete callsData[callId].kwargs[param];
                } else {
                    callsData[callId].kwargs[param] = value;
                }
            }
        } else {
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        alert('Update failed: ' + error.message);
    }

    if (input.disabled !== undefined) input.disabled = false;
    document.body.classList.remove('loading');
}
"""

__all__ = ["SCRIPTS_ELEMENT_EDITOR"]

# EOF
