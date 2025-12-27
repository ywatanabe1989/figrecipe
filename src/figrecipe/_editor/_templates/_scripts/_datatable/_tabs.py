#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable tab management JavaScript."""

JS_DATATABLE_TABS = """
// ============================================================================
// Multi-Tab Datatable State
// ============================================================================
let datatableTabs = {};  // Maps tabId -> {data, selectedColumns, varAssignments, plotType, targetAxis}
let activeTabId = null;
let tabCounter = 0;

// ============================================================================
// Tab Management
// ============================================================================
function initDatatableTabs() {
    const newTabBtn = document.getElementById('btn-new-tab');
    if (newTabBtn) {
        newTabBtn.addEventListener('click', createNewTab);
    }

    // Load tabs from figure data
    loadTabsFromFigure();
}

function loadTabsFromFigure() {
    // Fetch existing plot data and calls to get axis info
    Promise.all([
        fetch('/datatable/data').then(r => r.json()),
        fetch('/calls').then(r => r.json())
    ]).then(([data, calls]) => {
        if (data.columns && data.columns.length > 0) {
            // Build a map of call_id -> axis index from calls
            // calls is an object: {call_id: {function, ax_key, ...}, ...}
            const callToAxis = {};
            const callToFunction = {};
            Object.entries(calls).forEach(([callId, call]) => {
                // Extract axis index from ax_key (e.g., "ax_0_1" -> row=0, col=1 -> panel index)
                let axIndex = 0;
                if (call.ax_key) {
                    const match = call.ax_key.match(/ax_(\\d+)_(\\d+)/);
                    if (match) {
                        const row = parseInt(match[1]);
                        const col = parseInt(match[2]);
                        // For now, use simple linear indexing (works for 1xN grids)
                        // TODO: get actual ncols from axes_positions for proper MxN support
                        axIndex = col > 0 ? col : row;
                    }
                }
                callToAxis[callId] = axIndex;
                callToFunction[callId] = call.function || 'plot';
            });

            // Group columns by call_id (e.g., plot_000_x, plot_000_y -> plot_000)
            // First pass: identify which columns belong to each group
            const groups = {};
            const colIndexMap = {};  // Maps callId -> [column indices]
            data.columns.forEach((col, idx) => {
                // Extract call_id from column name (e.g., "plot_000_x" -> "plot_000")
                const match = col.name.match(/^(.+?)_[xy]$/);
                const callId = match ? match[1] : col.name;
                if (!groups[callId]) {
                    groups[callId] = {
                        columns: [],
                        axIndex: callToAxis[callId] !== undefined ? callToAxis[callId] : 0,
                        plotType: callToFunction[callId] || 'plot'
                    };
                    colIndexMap[callId] = [];
                }
                // Store column with new index for this group
                groups[callId].columns.push({
                    ...col,
                    index: groups[callId].columns.length
                });
                colIndexMap[callId].push(idx);
            });

            // Second pass: extract rows for each group (only relevant columns)
            Object.keys(groups).forEach(callId => {
                const indices = colIndexMap[callId];
                groups[callId].rows = data.rows.map(row =>
                    indices.map(idx => row[idx])
                );
            });

            // Create a tab for each group with element colors
            Object.entries(groups).forEach(([callId, groupData]) => {
                // Get element color from colorMap (populated by hitmap)
                const elemColor = typeof getGroupRepresentativeColor === 'function'
                    ? getGroupRepresentativeColor(callId, null)
                    : null;
                createTab(callId, groupData, false, groupData.axIndex, groupData.plotType, elemColor);
            });

            // Select first tab
            const firstTabId = Object.keys(datatableTabs)[0];
            if (firstTabId) {
                selectTab(firstTabId);
            }

            // Retry color update after hitmap loads (may not be ready yet)
            setTimeout(() => { if (typeof updateTabColors === 'function') updateTabColors(); }, 500);
        }
    }).catch(err => {
        console.error('Failed to load tabs from figure:', err);
    });
}

function createTab(name, data = null, select = true, axIndex = null, plotType = 'plot', elementColor = null) {
    const tabId = `tab_${tabCounter++}`;
    const tabList = document.getElementById('datatable-tab-list');

    // Create tab element with axis badge
    const tab = document.createElement('button');
    tab.className = 'datatable-tab';
    tab.dataset.tabId = tabId;
    const axBadge = axIndex !== null ? `<span class="tab-axis" title="Axis ${axIndex}">P${axIndex + 1}</span>` : '';
    tab.innerHTML = `
        ${axBadge}
        <span class="tab-name" title="${name}">${name}</span>
        <span class="tab-close" onclick="event.stopPropagation(); closeTab('${tabId}')">&times;</span>
    `;
    tab.onclick = () => selectTab(tabId);

    // Apply element color if available
    if (elementColor) {
        tab.style.setProperty('--element-color', elementColor);
    }

    tabList.appendChild(tab);

    // Initialize tab state with axis association
    datatableTabs[tabId] = {
        name: name,
        data: data,
        selectedColumns: new Set(),
        varAssignments: {},
        varColors: {},
        plotType: plotType,
        targetAxis: axIndex,  // Associated axis
        callId: name,  // Original call_id for linking
        elementColor: elementColor  // Element's original color
    };

    if (select) {
        selectTab(tabId);
    }

    return tabId;
}

function createNewTab() {
    const name = `Data ${tabCounter + 1}`;
    // Auto-create empty editable table data
    const defaultData = {
        columns: [
            { name: 'col1', type: 'numeric', index: 0 },
            { name: 'col2', type: 'numeric', index: 1 },
            { name: 'col3', type: 'string', index: 2 }
        ],
        rows: [
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            ['', '', '']
        ]
    };
    createTab(name, defaultData, true);
}

function selectTab(tabId) {
    if (!datatableTabs[tabId]) return;

    // Save current tab state
    saveCurrentTabState();

    // Update active tab
    activeTabId = tabId;

    // Update tab UI
    document.querySelectorAll('.datatable-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tabId === tabId);
    });

    // Restore tab state
    restoreTabState(tabId);
}

function closeTab(tabId) {
    const tab = document.querySelector(`.datatable-tab[data-tab-id="${tabId}"]`);
    if (tab) {
        tab.remove();
    }

    delete datatableTabs[tabId];

    // If closing active tab, select another
    if (activeTabId === tabId) {
        const remainingTabs = Object.keys(datatableTabs);
        if (remainingTabs.length > 0) {
            selectTab(remainingTabs[0]);
        } else {
            activeTabId = null;
            clearDatatableDisplay();
        }
    }
}

function saveCurrentTabState() {
    if (!activeTabId || !datatableTabs[activeTabId]) return;

    datatableTabs[activeTabId].data = datatableData;
    datatableTabs[activeTabId].selectedColumns = new Set(datatableSelectedColumns);
    datatableTabs[activeTabId].varAssignments = {...datatableVarAssignments};
    datatableTabs[activeTabId].varColors = {...datatableVarColors};
    datatableTabs[activeTabId].plotType = datatablePlotType;
    datatableTabs[activeTabId].targetAxis = datatableTargetAxis;
}

function restoreTabState(tabId) {
    const state = datatableTabs[tabId];
    if (!state) return;

    // Restore global state
    datatableData = state.data;
    datatableSelectedColumns = new Set(state.selectedColumns);
    datatableVarAssignments = {...state.varAssignments};
    datatableVarColors = state.varColors ? {...state.varColors} : {};
    datatablePlotType = state.plotType || 'plot';
    datatableTargetAxis = state.targetAxis;

    // Update UI
    if (datatableData) {
        renderDatatable();

        // Show toolbar
        const dropzone = document.getElementById('datatable-dropzone');
        if (dropzone) dropzone.style.display = 'none';
        const toolbar = document.querySelector('.datatable-toolbar');
        if (toolbar) toolbar.style.display = 'flex';

        // Restore plot type selection
        const plotTypeSelect = document.getElementById('datatable-plot-type');
        if (plotTypeSelect) plotTypeSelect.value = datatablePlotType;

        // Restore target panel selection
        const targetPanelSelect = document.getElementById('datatable-target-panel');
        if (targetPanelSelect && datatableTargetAxis !== null) {
            targetPanelSelect.value = datatableTargetAxis;
        }

        // Update variable assignment UI
        updateVarAssignSlots();
    } else {
        clearDatatableDisplay();
    }
}

function clearDatatableDisplay() {
    const content = document.getElementById('datatable-content');
    if (content) content.innerHTML = '';

    const dropzone = document.getElementById('datatable-dropzone');
    if (dropzone) dropzone.style.display = 'block';

    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'none';

    const varAssign = document.getElementById('datatable-var-assign');
    if (varAssign) varAssign.style.display = 'none';

    updateSelectionInfo();
}

// Override loadExistingData to use tabs
function loadExistingData() {
    // This is now handled by loadTabsFromFigure
    // But we still call initDatatableTabs
    initDatatableTabs();
}

// Override handleParsedData to work with tabs
const originalHandleParsedData = typeof handleParsedData === 'function' ? handleParsedData : null;

function handleParsedDataWithTabs(parsedData) {
    if (!activeTabId) {
        // Create a new tab for imported data
        createNewTab();
    }

    // Store in current tab
    datatableTabs[activeTabId].data = parsedData;
    datatableData = parsedData;

    renderDatatable();

    // Show toolbar
    const dropzone = document.getElementById('datatable-dropzone');
    if (dropzone) dropzone.style.display = 'none';
    const toolbar = document.querySelector('.datatable-toolbar');
    if (toolbar) toolbar.style.display = 'flex';

    updateVarAssignSlots();
}

// Hook into handleParsedData
if (typeof window !== 'undefined') {
    window.handleParsedData = handleParsedDataWithTabs;
}

// Update tab colors after colorMap is loaded
function updateTabColors() {
    if (typeof colorMap === 'undefined' || !colorMap) return;
    if (typeof getGroupRepresentativeColor !== 'function') return;

    Object.entries(datatableTabs).forEach(([tabId, tabState]) => {
        if (tabState.callId && !tabState.elementColor) {
            const elemColor = getGroupRepresentativeColor(tabState.callId, null);
            if (elemColor) {
                tabState.elementColor = elemColor;
                const tabEl = document.querySelector(`.datatable-tab[data-tab-id="${tabId}"]`);
                if (tabEl) {
                    tabEl.style.setProperty('--element-color', elemColor);
                }
            }
        }
    });
}

// Export for hitmap to call after colorMap is loaded
if (typeof window !== 'undefined') {
    window.updateTabColors = updateTabColors;
}

"""

__all__ = ["JS_DATATABLE_TABS"]

# EOF
