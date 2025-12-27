#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable plotting JavaScript: hints, variable assignment, plotting."""

from ...._plot_types_registry import generate_js_hints


def get_js_datatable_plot() -> str:
    """Generate JavaScript for plot type hints and variable assignment."""
    js_hints = generate_js_hints()

    return f"""
// ============================================================================
// Plot Type Hints (Generated from matplotlib signatures)
// ============================================================================
{js_hints}

function initPlotTypeButtons() {{
    const selector = document.getElementById('datatable-plot-type');
    if (!selector) return;

    selector.addEventListener('change', (e) => {{
        datatablePlotType = e.target.value;
        updateVarAssignSlots();
        updatePlotButtonState();
    }});
}}

// ============================================================================
// Variable Assignment UI with Color-Coded Linking
// ============================================================================
let datatableVarColors = {{}};  // Maps varName -> colorIndex

function updateVarAssignSlots() {{
    const container = document.getElementById('var-assign-slots');
    const varAssignDiv = document.getElementById('datatable-var-assign');
    if (!container || !varAssignDiv) return;

    const info = PLOT_TYPE_HINTS[datatablePlotType];
    if (!info || !datatableData) {{
        varAssignDiv.style.display = 'none';
        return;
    }}

    // Parse variables from hint to preserve signature order
    const hintMatch = info.hint.match(/\\((.*)\\)/);
    const argsStr = hintMatch ? hintMatch[1] : '';

    // Parse each arg, preserving order and optional status
    const allVars = [];
    argsStr.split(',').forEach(arg => {{
        arg = arg.trim();
        if (!arg || arg === 'data') return;
        const isOptional = arg.startsWith('[') && arg.endsWith(']');
        const varName = arg.replace(/[\\[\\]]/g, '');
        allVars.push({{ name: varName, optional: isOptional }});
    }});

    // Reset assignments and colors
    datatableVarAssignments = {{}};
    datatableVarColors = {{}};

    // Assign colors to each variable (0-5 cycle)
    allVars.forEach((v, idx) => {{
        datatableVarColors[v.name] = idx % 6;
    }});

    // Build column options
    const columns = datatableData.columns || [];
    let colOptions = '<option value="">--</option>';
    columns.forEach((col, idx) => {{
        colOptions += `<option value="${{idx}}">${{col.name}}</option>`;
    }});

    // Build slots HTML in signature order with color classes
    let html = '';
    let requiredIdx = 0;

    allVars.forEach((v, idx) => {{
        const isOptional = v.optional;
        const varName = v.name;
        const colorClass = `var-color-${{idx % 6}}`;

        if (isOptional) {{
            html += `
            <div class="var-assign-slot optional ${{colorClass}}" data-var="${{varName}}">
                <span class="var-name">[${{varName}}]:</span>
                <select onchange="assignVariable('${{varName}}', this.value, false)">
                    ${{colOptions}}
                </select>
            </div>`;
        }} else {{
            const autoAssign = requiredIdx < columns.length ? requiredIdx : '';
            if (autoAssign !== '') {{
                datatableVarAssignments[varName] = autoAssign;
            }}
            const selectedOpt = autoAssign !== '' ? colOptions.replace(`value="${{autoAssign}}"`, `value="${{autoAssign}}" selected`) : colOptions;
            html += `
            <div class="var-assign-slot required ${{colorClass}}${{autoAssign !== '' ? ' assigned' : ''}}" data-var="${{varName}}">
                <span class="var-name">${{varName}}:</span>
                <select onchange="assignVariable('${{varName}}', this.value, true)">
                    ${{selectedOpt}}
                </select>
            </div>`;
            requiredIdx++;
        }}
    }});

    container.innerHTML = html;
    varAssignDiv.style.display = html ? 'block' : 'none';

    updatePlotButtonState();
    updateSelectionInfo();
    updateColumnHighlights();
}}

function updateColumnHighlights() {{
    // Remove all existing highlights
    document.querySelectorAll('.datatable-table th').forEach(th => {{
        th.classList.remove('var-linked', 'var-color-0', 'var-color-1', 'var-color-2', 'var-color-3', 'var-color-4', 'var-color-5');
    }});

    // Add highlights based on current assignments
    Object.entries(datatableVarAssignments).forEach(([varName, colIdx]) => {{
        const colorIdx = datatableVarColors[varName];
        if (colorIdx === undefined) return;

        // Find the column header (colIdx + 1 because of row number column)
        const th = document.querySelector(`.datatable-table th:nth-child(${{colIdx + 2}})`);
        if (th) {{
            th.classList.add('var-linked', `var-color-${{colorIdx}}`);
        }}
    }});
}}

function assignVariable(varName, colIdx, isRequired) {{
    const slot = event.target.closest('.var-assign-slot');

    if (colIdx === '' || colIdx === null) {{
        delete datatableVarAssignments[varName];
        if (slot) slot.classList.remove('assigned');
    }} else {{
        datatableVarAssignments[varName] = parseInt(colIdx);
        if (slot) slot.classList.add('assigned');
    }}

    updatePlotButtonState();
    updateSelectionInfo();
    updateColumnHighlights();
}}

function updatePlotButtonState() {{
    const plotBtn = document.getElementById('btn-datatable-plot');
    if (!plotBtn) return;

    const info = PLOT_TYPE_HINTS[datatablePlotType];
    if (!info) {{
        plotBtn.disabled = true;
        return;
    }}

    // Check if all required variables are assigned
    const requiredVars = info.required.split(',').map(s => s.trim()).filter(s => s && s !== 'data');
    const allAssigned = requiredVars.length === 0 || requiredVars.every(v => datatableVarAssignments[v] !== undefined);

    plotBtn.disabled = !allAssigned || !datatableData;
}}

// ============================================================================
// Plot from Variable Assignments
// ============================================================================
async function plotFromVarAssignments() {{
    if (!datatableData || Object.keys(datatableVarAssignments).length === 0) return;

    // Build data and columns from variable assignments
    const plotData = {{}};
    const columns = [];

    // Order matters: required vars first, then optional
    const info = PLOT_TYPE_HINTS[datatablePlotType];
    const requiredVars = info.required.split(',').map(s => s.trim()).filter(s => s && s !== 'data');
    const optionalVars = info.optional.split(',').map(s => s.replace(/[\\[\\]]/g, '').trim()).filter(s => s);

    [...requiredVars, ...optionalVars].forEach(varName => {{
        const colIdx = datatableVarAssignments[varName];
        if (colIdx !== undefined) {{
            const col = datatableData.columns[colIdx];
            plotData[col.name] = datatableData.rows.map(row => row[colIdx]);
            columns.push(col.name);
        }}
    }});

    if (columns.length === 0) return;

    // Send to backend for plotting
    if (typeof showSpinner === 'function') showSpinner();

    try {{
        const response = await fetch('/datatable/plot', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                data: plotData,
                columns: columns,
                plot_type: datatablePlotType,
                target_axis: datatableTargetAxis
            }})
        }});

        const result = await response.json();

        if (result.success) {{
            // Update preview
            const previewImg = document.getElementById('preview-image');
            if (previewImg && result.image) {{
                previewImg.src = 'data:image/png;base64,' + result.image;
            }}

            // Update bboxes
            if (result.bboxes && typeof currentBboxes !== 'undefined') {{
                currentBboxes = result.bboxes;
            }}

            // Reload hitmap
            if (typeof loadHitmap === 'function') loadHitmap();

            // Refresh panel selector (in case new panel was added)
            if (typeof updatePanelSelector === 'function') updatePanelSelector();

            // Clear selection
            if (typeof clearSelection === 'function') clearSelection();
        }} else {{
            console.error('Plot failed:', result.error);
            alert('Failed to create plot: ' + (result.error || 'Unknown error'));
        }}
    }} catch (err) {{
        console.error('Plot request failed:', err);
        alert('Failed to create plot: ' + err.message);
    }} finally {{
        if (typeof hideSpinner === 'function') hideSpinner();
    }}
}}
"""


# For backward compatibility
JS_DATATABLE_PLOT = get_js_datatable_plot()

__all__ = ["JS_DATATABLE_PLOT", "get_js_datatable_plot"]

# EOF
