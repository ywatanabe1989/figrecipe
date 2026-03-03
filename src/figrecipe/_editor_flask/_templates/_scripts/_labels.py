#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Label and axis controls JavaScript for the figure editor.

This module contains the JavaScript code for:
- Label input handlers (title, xlabel, ylabel, suptitle)
- Axis type toggles (numerical/categorical)
- Legend position controls
"""

SCRIPTS_LABELS = """
// ===== LABEL AND AXIS CONTROLS =====

// Load current axis labels from server
async function loadLabels() {
    try {
        const response = await fetch('/get_labels');
        const labels = await response.json();

        const titleInput = document.getElementById('label_title');
        const xlabelInput = document.getElementById('label_xlabel');
        const ylabelInput = document.getElementById('label_ylabel');
        const suptitleInput = document.getElementById('label_suptitle');

        if (titleInput) titleInput.value = labels.title || '';
        if (xlabelInput) xlabelInput.value = labels.xlabel || '';
        if (ylabelInput) ylabelInput.value = labels.ylabel || '';
        if (suptitleInput) suptitleInput.value = labels.suptitle || '';

        console.log('Loaded labels:', labels);
    } catch (error) {
        console.error('Failed to load labels:', error);
    }
}

// Update axis label on server
async function updateLabel(labelType, text) {
    console.log(`Updating ${labelType} to: "${text}"`);
    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_label', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label_type: labelType, text: text })
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
            updateHitRegions();
            console.log('Label updated successfully');
        } else {
            console.error('Label update failed:', data.error);
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        console.error('Label update failed:', error);
        alert('Update failed: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Initialize label input event handlers
function initializeLabelInputs() {
    const labelMap = {
        'label_title': 'title',
        'label_xlabel': 'xlabel',
        'label_ylabel': 'ylabel',
        'label_suptitle': 'suptitle'
    };

    for (const [inputId, labelType] of Object.entries(labelMap)) {
        const input = document.getElementById(inputId);
        if (input) {
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    updateLabel(labelType, this.value);
                }, UPDATE_DEBOUNCE);
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    clearTimeout(timeout);
                    updateLabel(labelType, this.value);
                }
            });

            input.addEventListener('blur', function() {
                clearTimeout(timeout);
                updateLabel(labelType, this.value);
            });
        }
    }

    initializeAxisTypeToggles();
    initializeLegendPosition();
}

// Initialize axis type toggle buttons
function initializeAxisTypeToggles() {
    const xNumerical = document.getElementById('xaxis-numerical');
    const xCategorical = document.getElementById('xaxis-categorical');
    const yNumerical = document.getElementById('yaxis-numerical');
    const yCategorical = document.getElementById('yaxis-categorical');
    const xLabelsRow = document.getElementById('xaxis-labels-row');
    const yLabelsRow = document.getElementById('yaxis-labels-row');
    const xLabelsInput = document.getElementById('xaxis_labels');
    const yLabelsInput = document.getElementById('yaxis_labels');

    if (xNumerical) {
        xNumerical.addEventListener('click', () => {
            xNumerical.classList.add('active');
            xCategorical.classList.remove('active');
            xLabelsRow.style.display = 'none';
            updateAxisType('x', 'numerical');
        });
    }

    if (xCategorical) {
        xCategorical.addEventListener('click', () => {
            xCategorical.classList.add('active');
            xNumerical.classList.remove('active');
            xLabelsRow.style.display = 'flex';
        });
    }

    if (yNumerical) {
        yNumerical.addEventListener('click', () => {
            yNumerical.classList.add('active');
            yCategorical.classList.remove('active');
            yLabelsRow.style.display = 'none';
            updateAxisType('y', 'numerical');
        });
    }

    if (yCategorical) {
        yCategorical.addEventListener('click', () => {
            yCategorical.classList.add('active');
            yNumerical.classList.remove('active');
            yLabelsRow.style.display = 'flex';
        });
    }

    // Labels input handlers
    [xLabelsInput, yLabelsInput].forEach((input, idx) => {
        const axis = idx === 0 ? 'x' : 'y';
        if (input) {
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                    if (labels.length > 0) updateAxisType(axis, 'categorical', labels);
                }, UPDATE_DEBOUNCE);
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    clearTimeout(timeout);
                    const labels = this.value.split(',').map(l => l.trim()).filter(l => l);
                    if (labels.length > 0) updateAxisType(axis, 'categorical', labels);
                }
            });
        }
    });

    loadAxisInfo();
}

// Load current axis type info
async function loadAxisInfo() {
    try {
        const response = await fetch('/get_axis_info');
        const info = await response.json();

        if (info.x_type === 'categorical') {
            document.getElementById('xaxis-categorical')?.classList.add('active');
            document.getElementById('xaxis-numerical')?.classList.remove('active');
            const xLabelsRow = document.getElementById('xaxis-labels-row');
            if (xLabelsRow) xLabelsRow.style.display = 'flex';
            if (info.x_labels?.length > 0) {
                const input = document.getElementById('xaxis_labels');
                if (input) input.value = info.x_labels.join(', ');
            }
        }

        if (info.y_type === 'categorical') {
            document.getElementById('yaxis-categorical')?.classList.add('active');
            document.getElementById('yaxis-numerical')?.classList.remove('active');
            const yLabelsRow = document.getElementById('yaxis-labels-row');
            if (yLabelsRow) yLabelsRow.style.display = 'flex';
            if (info.y_labels?.length > 0) {
                const input = document.getElementById('yaxis_labels');
                if (input) input.value = info.y_labels.join(', ');
            }
        }

        console.log('Loaded axis info:', info);
    } catch (error) {
        console.error('Failed to load axis info:', error);
    }
}

// Update axis type on server
async function updateAxisType(axis, type, labels = []) {
    console.log(`Updating ${axis} axis to ${type}`, labels);
    document.body.classList.add('loading');

    try {
        const response = await fetch('/update_axis_type', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ axis, type, labels })
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
            updateHitRegions();
            console.log('Axis type updated successfully');
        } else {
            console.error('Axis type update failed:', data.error);
            alert('Update failed: ' + data.error);
        }
    } catch (error) {
        console.error('Axis type update failed:', error);
        alert('Update failed: ' + error.message);
    }

    document.body.classList.remove('loading');
}

// Initialize legend position controls
function initializeLegendPosition() {
    const locSelect = document.getElementById('legend_loc');
    const customPosDiv = document.getElementById('legend-custom-pos');
    const xInput = document.getElementById('legend_x');
    const yInput = document.getElementById('legend_y');
    const visibleCheckbox = document.getElementById('legend_visible');

    if (!locSelect) return;

    if (visibleCheckbox) {
        visibleCheckbox.addEventListener('change', function() {
            updateLegendVisibility(this.checked);
        });
    }

    locSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customPosDiv.style.display = 'block';
        } else {
            customPosDiv.style.display = 'none';
            updateLegendPosition(this.value);
        }
    });

    if (xInput && yInput) {
        let timeout;
        const updateCustomPos = () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const x = parseFloat(xInput.value);
                const y = parseFloat(yInput.value);
                if (!isNaN(x) && !isNaN(y)) updateLegendPosition('custom', x, y);
            }, UPDATE_DEBOUNCE);
        };

        xInput.addEventListener('input', updateCustomPos);
        yInput.addEventListener('input', updateCustomPos);

        [xInput, yInput].forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(timeout);
                    const x = parseFloat(xInput.value);
                    const y = parseFloat(yInput.value);
                    if (!isNaN(x) && !isNaN(y)) updateLegendPosition('custom', x, y);
                }
            });
        });
    }

    loadLegendInfo();
}

// Load current legend position info
async function loadLegendInfo() {
    try {
        const response = await fetch('/get_legend_info');
        const info = await response.json();

        if (!info.has_legend) {
            console.log('No legend found');
            return;
        }

        const locSelect = document.getElementById('legend_loc');
        const customPosDiv = document.getElementById('legend-custom-pos');
        const xInput = document.getElementById('legend_x');
        const yInput = document.getElementById('legend_y');
        const visibleCheckbox = document.getElementById('legend_visible');

        if (visibleCheckbox) visibleCheckbox.checked = info.visible !== false;
        if (locSelect) locSelect.value = info.loc;

        if (info.loc === 'custom' && customPosDiv) {
            customPosDiv.style.display = 'block';
            if (xInput && info.x !== null) xInput.value = info.x;
            if (yInput && info.y !== null) yInput.value = info.y;
        }

        console.log('Loaded legend info:', info);
    } catch (error) {
        console.error('Failed to load legend info:', error);
    }
}

// Update legend visibility
async function updateLegendVisibility(visible) {
    console.log('Updating legend visibility:', visible);

    try {
        const response = await fetch('/update_legend_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ visible })
        });

        const result = await response.json();

        if (result.success) {
            const previewImg = document.getElementById('preview-image');
            previewImg.src = 'data:image/png;base64,' + result.image;

            if (result.img_size) {
                currentImgWidth = result.img_size.width;
                currentImgHeight = result.img_size.height;
            }

            if (result.bboxes) {
                currentBboxes = result.bboxes;
                previewImg.onload = () => {
                    updateHitRegions();
                    loadHitmap();
                };
            }
        } else {
            console.error('Legend visibility update failed:', result.error);
        }
    } catch (error) {
        console.error('Failed to update legend visibility:', error);
    }
}

// Update legend position on server
async function updateLegendPosition(loc, x = null, y = null) {
    console.log(`Updating legend position: loc=${loc}, x=${x}, y=${y}`);
    document.body.classList.add('loading');

    try {
        const body = { loc };
        if (loc === 'custom' && x !== null && y !== null) {
            body.x = x;
            body.y = y;
        }

        const response = await fetch('/update_legend_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
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
            updateHitRegions();
            console.log('Legend position updated successfully');
        } else {
            console.error('Legend position update failed:', data.error);
            if (!data.error.includes('No legend')) {
                alert('Update failed: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Legend position update failed:', error);
    }

    document.body.classList.remove('loading');
}

// Initialize download dropdown
function initializeDownloadDropdown() {
    const mainBtn = document.getElementById('btn-download-main');
    const toggleBtn = document.getElementById('btn-download-toggle');
    const menu = document.getElementById('download-menu');

    // Download dropdown state
    let currentDownloadFormat = 'png';

    mainBtn?.addEventListener('click', () => downloadFigure(currentDownloadFormat));

    toggleBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('open');
    });

    document.querySelectorAll('.download-option').forEach(option => {
        option.addEventListener('click', () => {
            const format = option.dataset.format;
            currentDownloadFormat = format;
            mainBtn.textContent = 'Download ' + format.toUpperCase();

            document.querySelectorAll('.download-option').forEach(opt => {
                opt.classList.toggle('active', opt.dataset.format === format);
            });

            menu.classList.remove('open');
            downloadFigure(format);
        });
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.download-dropdown')) {
            menu?.classList.remove('open');
        }
    });
}
"""

__all__ = ["SCRIPTS_LABELS"]

# EOF
