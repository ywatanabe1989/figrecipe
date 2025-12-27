#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Datatable import JavaScript: drag-drop, file parsing."""

JS_DATATABLE_IMPORT = """
// ============================================================================
// Drag and Drop Import
// ============================================================================
function initDatatableDropzone() {
    const dropzone = document.getElementById('datatable-dropzone');
    const fileInput = document.getElementById('datatable-file-input');

    if (!dropzone || !fileInput) return;

    // Click to select file
    dropzone.addEventListener('click', () => fileInput.click());

    // File selected
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleDataFile(e.target.files[0]);
        }
    });

    // Drag events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            handleDataFile(e.dataTransfer.files[0]);
        }
    });
}

function handleDataFile(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        const content = e.target.result;
        const ext = file.name.split('.').pop().toLowerCase();

        if (ext === 'csv') {
            parseCSV(content);
        } else if (ext === 'tsv' || ext === 'txt') {
            parseTSV(content);
        } else if (ext === 'json') {
            parseJSON(content);
        } else {
            // Try CSV by default
            parseCSV(content);
        }
    };

    reader.readAsText(file);
}

// ============================================================================
// Data Parsing
// ============================================================================
function parseCSV(content, delimiter = ',') {
    const lines = content.trim().split('\\n');
    if (lines.length === 0) return;

    // Parse header
    const headers = lines[0].split(delimiter).map(h => h.trim().replace(/^["']|["']$/g, ''));

    // Parse rows
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const values = line.split(delimiter).map(v => {
            v = v.trim().replace(/^["']|["']$/g, '');
            const num = parseFloat(v);
            return isNaN(num) ? v : num;
        });
        rows.push(values);
    }

    // Determine column types
    const columns = headers.map((name, idx) => {
        const values = rows.map(r => r[idx]).filter(v => v !== '' && v !== null && v !== undefined);
        const isNumeric = values.every(v => typeof v === 'number');
        return {
            name: name,
            type: isNumeric ? 'numeric' : 'string',
            index: idx
        };
    });

    datatableData = { columns, rows };
    renderDatatable();
    updateVarAssignSlots();
}

function parseTSV(content) {
    parseCSV(content, '\\t');
}

function parseJSON(content) {
    try {
        const data = JSON.parse(content);

        if (Array.isArray(data)) {
            // Array of objects
            if (data.length === 0) return;

            const headers = Object.keys(data[0]);
            const rows = data.map(obj => headers.map(h => obj[h]));

            const columns = headers.map((name, idx) => {
                const values = rows.map(r => r[idx]).filter(v => v !== '' && v !== null && v !== undefined);
                const isNumeric = values.every(v => typeof v === 'number');
                return { name, type: isNumeric ? 'numeric' : 'string', index: idx };
            });

            datatableData = { columns, rows };
            renderDatatable();
            updateVarAssignSlots();
        } else if (typeof data === 'object') {
            // Object with column arrays
            const headers = Object.keys(data);
            const maxLen = Math.max(...headers.map(h => Array.isArray(data[h]) ? data[h].length : 0));

            const rows = [];
            for (let i = 0; i < maxLen; i++) {
                rows.push(headers.map(h => Array.isArray(data[h]) ? data[h][i] : data[h]));
            }

            const columns = headers.map((name, idx) => {
                const values = rows.map(r => r[idx]).filter(v => v !== '' && v !== null && v !== undefined);
                const isNumeric = values.every(v => typeof v === 'number');
                return { name, type: isNumeric ? 'numeric' : 'string', index: idx };
            });

            datatableData = { columns, rows };
            renderDatatable();
            updateVarAssignSlots();
        }
    } catch (err) {
        console.error('Failed to parse JSON:', err);
    }
}

// loadExistingData is defined in _tabs.py to use multi-tab system
"""

__all__ = ["JS_DATATABLE_IMPORT"]

# EOF
