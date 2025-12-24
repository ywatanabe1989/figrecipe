#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color handling JavaScript for the figure editor.

This module contains the JavaScript code for:
- Color presets (SCITEX, matplotlib, CSS)
- Color conversion utilities
- Color input widget creation
"""

SCRIPTS_COLORS = """
// ===== COLOR HANDLING =====

// Color presets from SCITEX theme (priority 1 - highest)
const COLOR_PRESETS = {
    'blue':      { hex: '#0080c0', rgb: [0, 128, 192] },
    'red':       { hex: '#ff4632', rgb: [255, 70, 50] },
    'green':     { hex: '#14b414', rgb: [20, 180, 20] },
    'yellow':    { hex: '#e6a014', rgb: [230, 160, 20] },
    'purple':    { hex: '#c832ff', rgb: [200, 50, 255] },
    'lightblue': { hex: '#14c8c8', rgb: [20, 200, 200] },
    'orange':    { hex: '#e45e32', rgb: [228, 94, 50] },
    'pink':      { hex: '#ff96c8', rgb: [255, 150, 200] },
    'black':     { hex: '#000000', rgb: [0, 0, 0] },
    'white':     { hex: '#ffffff', rgb: [255, 255, 255] },
    'gray':      { hex: '#808080', rgb: [128, 128, 128] }
};

// Matplotlib single-letter colors (priority 2)
const MATPLOTLIB_SINGLE = {
    'b': { hex: '#1f77b4', rgb: [31, 119, 180] },
    'g': { hex: '#2ca02c', rgb: [44, 160, 44] },
    'r': { hex: '#d62728', rgb: [214, 39, 40] },
    'c': { hex: '#17becf', rgb: [23, 190, 207] },
    'm': { hex: '#9467bd', rgb: [148, 103, 189] },
    'y': { hex: '#bcbd22', rgb: [188, 189, 34] },
    'k': { hex: '#000000', rgb: [0, 0, 0] },
    'w': { hex: '#ffffff', rgb: [255, 255, 255] }
};

// Common matplotlib/CSS named colors (priority 3)
const MATPLOTLIB_NAMED = {
    'aqua': '#00ffff', 'coral': '#ff7f50', 'crimson': '#dc143c',
    'cyan': '#00ffff', 'gold': '#ffd700', 'indigo': '#4b0082',
    'lime': '#00ff00', 'magenta': '#ff00ff', 'maroon': '#800000',
    'navy': '#000080', 'olive': '#808000', 'salmon': '#fa8072',
    'silver': '#c0c0c0', 'teal': '#008080', 'tomato': '#ff6347',
    'turquoise': '#40e0d0', 'violet': '#ee82ee'
};

// Check if a field is a color field
function isColorField(key, sigInfo) {
    const colorKeywords = ['color', 'facecolor', 'edgecolor', 'markerfacecolor', 'markeredgecolor', 'c'];
    if (colorKeywords.includes(key.toLowerCase())) return true;
    if (sigInfo?.type && sigInfo.type.toLowerCase().includes('color')) return true;
    return false;
}

// Convert color to RGB string for display
function colorToRGB(color) {
    if (!color) return '';
    if (typeof color === 'string' && color.match(/^rgb/i)) return color;
    if (typeof color === 'string' && color.startsWith('#')) {
        const hex = color.slice(1);
        if (hex.length === 3) {
            const r = parseInt(hex[0] + hex[0], 16);
            const g = parseInt(hex[1] + hex[1], 16);
            const b = parseInt(hex[2] + hex[2], 16);
            return `rgb(${r}, ${g}, ${b})`;
        } else if (hex.length === 6) {
            const r = parseInt(hex.slice(0, 2), 16);
            const g = parseInt(hex.slice(2, 4), 16);
            const b = parseInt(hex.slice(4, 6), 16);
            return `rgb(${r}, ${g}, ${b})`;
        }
    }
    return color;
}

// Convert color to hex for color picker
function colorToHex(color) {
    return resolveColorToHex(color);
}

// Find preset color matching input (name, hex, or RGB)
function findPresetColor(input) {
    if (!input) return null;
    const inputLower = typeof input === 'string' ? input.toLowerCase().trim() : '';

    if (COLOR_PRESETS[inputLower]) return { name: inputLower, ...COLOR_PRESETS[inputLower] };
    if (MATPLOTLIB_SINGLE[inputLower]) return { name: inputLower, ...MATPLOTLIB_SINGLE[inputLower] };

    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        if (preset.hex.toLowerCase() === inputLower) return { name, ...preset };
    }
    return null;
}

// Find preset by hex value
function findPresetByHex(hexValue) {
    if (!hexValue) return null;
    const hex = hexValue.toLowerCase();

    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        if (preset.hex.toLowerCase() === hex) return { name, ...preset };
    }
    for (const [name, preset] of Object.entries(MATPLOTLIB_SINGLE)) {
        if (preset.hex.toLowerCase() === hex) return { name, ...preset };
    }
    return null;
}

// Resolve color to hex using priority: theme > matplotlib > CSS
function resolveColorToHex(input) {
    if (!input) return '#000000';

    if (typeof input === 'string' && input.startsWith('#')) {
        return input.length === 4 ?
            '#' + input[1] + input[1] + input[2] + input[2] + input[3] + input[3] :
            input;
    }

    if (typeof input === 'string' && input.startsWith('(')) {
        const match = input.match(/\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)/);
        if (match) {
            const r = Math.round(parseFloat(match[1]) * 255);
            const g = Math.round(parseFloat(match[2]) * 255);
            const b = Math.round(parseFloat(match[3]) * 255);
            return '#' + [r, g, b].map(c => c.toString(16).padStart(2, '0')).join('');
        }
    }

    const inputLower = input.toLowerCase().trim();
    if (COLOR_PRESETS[inputLower]) return COLOR_PRESETS[inputLower].hex;
    if (MATPLOTLIB_SINGLE[inputLower]) return MATPLOTLIB_SINGLE[inputLower].hex;
    if (MATPLOTLIB_NAMED[inputLower]) return MATPLOTLIB_NAMED[inputLower];

    return '#000000';
}

// Format color for display
function formatColorDisplay(value) {
    if (!value) return '';
    const preset = findPresetColor(value);
    if (preset) return preset.name;
    return value;
}

// Convert hex to RGB tuple string
function hexToRGBTuple(hex) {
    if (!hex || !hex.startsWith('#')) return null;
    const h = hex.slice(1);
    if (h.length !== 6) return null;
    const r = parseInt(h.slice(0, 2), 16) / 255;
    const g = parseInt(h.slice(2, 4), 16) / 255;
    const b = parseInt(h.slice(4, 6), 16) / 255;
    return `(${r.toFixed(3)}, ${g.toFixed(3)}, ${b.toFixed(3)})`;
}

// Create color input with preset dropdown and picker
function createColorInput(callId, key, value) {
    const wrapper = document.createElement('div');
    wrapper.className = 'color-input-wrapper';

    const swatch = document.createElement('div');
    swatch.className = 'color-swatch';

    const select = document.createElement('select');
    select.className = 'color-select';

    for (const [name, preset] of Object.entries(COLOR_PRESETS)) {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
    }

    const separator = document.createElement('option');
    separator.disabled = true;
    separator.textContent = '───────────';
    select.appendChild(separator);

    const customOpt = document.createElement('option');
    customOpt.value = '__custom__';
    customOpt.textContent = 'Custom...';
    select.appendChild(customOpt);

    const customInput = document.createElement('input');
    customInput.type = 'text';
    customInput.className = 'color-custom-input';
    customInput.placeholder = '#rrggbb or name';
    customInput.style.display = 'none';

    const rgbDisplay = document.createElement('span');
    rgbDisplay.className = 'color-rgb';

    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.className = 'color-picker-hidden';

    function updateDisplay(colorValue) {
        const hex = resolveColorToHex(colorValue);
        swatch.style.backgroundColor = hex;
        colorPicker.value = hex;
        rgbDisplay.textContent = colorToRGB(hex);
    }

    const initialPreset = findPresetColor(value);
    if (initialPreset) {
        select.value = initialPreset.name;
    } else if (value) {
        const currentOpt = document.createElement('option');
        currentOpt.value = value;
        currentOpt.textContent = formatColorDisplay(value);
        select.insertBefore(currentOpt, separator);
        select.value = value;
    }
    updateDisplay(value || 'blue');

    select.addEventListener('change', function() {
        if (this.value === '__custom__') {
            customInput.style.display = '';
            customInput.focus();
            swatch.style.display = 'none';
            rgbDisplay.style.display = 'none';
        } else {
            customInput.style.display = 'none';
            swatch.style.display = '';
            rgbDisplay.style.display = '';
            updateDisplay(this.value);
            handleDynamicParamChange(callId, key, { value: this.value });
        }
    });

    customInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const inputValue = this.value.trim();
            if (inputValue) {
                swatch.style.display = '';
                rgbDisplay.style.display = '';
                const preset = findPresetColor(inputValue);
                if (preset) {
                    select.value = preset.name;
                } else {
                    let existingOpt = Array.from(select.options).find(o => o.value === inputValue);
                    if (!existingOpt) {
                        const newOpt = document.createElement('option');
                        newOpt.value = inputValue;
                        newOpt.textContent = inputValue;
                        select.insertBefore(newOpt, separator);
                    }
                    select.value = inputValue;
                }
                customInput.style.display = 'none';
                updateDisplay(inputValue);
                handleDynamicParamChange(callId, key, { value: inputValue });
            }
        } else if (e.key === 'Escape') {
            customInput.style.display = 'none';
            if (select.value === '__custom__') select.selectedIndex = 0;
        }
    });

    swatch.addEventListener('click', () => colorPicker.click());

    colorPicker.addEventListener('change', function() {
        const pickedColor = this.value;
        const preset = findPresetColor(pickedColor);
        if (preset) {
            select.value = preset.name;
        } else {
            const rgbTuple = hexToRGBTuple(pickedColor);
            let existingOpt = Array.from(select.options).find(o => o.value === pickedColor || o.value === rgbTuple);
            if (!existingOpt) {
                const newOpt = document.createElement('option');
                newOpt.value = rgbTuple || pickedColor;
                newOpt.textContent = rgbTuple || pickedColor;
                select.insertBefore(newOpt, separator);
            }
            select.value = rgbTuple || pickedColor;
        }
        swatch.style.display = '';
        rgbDisplay.style.display = '';
        customInput.style.display = 'none';
        updateDisplay(select.value);
        handleDynamicParamChange(callId, key, { value: select.value });
    });

    wrapper.appendChild(swatch);
    wrapper.appendChild(select);
    wrapper.appendChild(customInput);
    wrapper.appendChild(rgbDisplay);
    wrapper.appendChild(colorPicker);

    return wrapper;
}
"""

__all__ = ["SCRIPTS_COLORS"]

# EOF
