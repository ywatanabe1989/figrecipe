#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug snapshot functionality for the figure editor.

Captures screenshots and console logs with Ctrl+Alt+I shortcut.
"""

SCRIPTS_DEBUG_SNAPSHOT = """
// ==================== DEBUG SNAPSHOT ====================
console.log('[DEBUG] Debug snapshot module loaded');

// Console log collection for debug snapshots
const debugSnapshotLogs = [];
const maxDebugLogs = 500;
const _origConsole = {
    log: console.log.bind(console),
    warn: console.warn.bind(console),
    error: console.error.bind(console),
    info: console.info.bind(console),
    debug: console.debug.bind(console)
};

// Wrap console methods to capture logs (non-destructive - chains with existing)
['log', 'warn', 'error', 'info', 'debug'].forEach(method => {
    const prev = console[method];
    console[method] = function(...args) {
        debugSnapshotLogs.push({
            type: method,
            timestamp: new Date().toISOString(),
            args: args.map(arg => {
                if (arg === null) return 'null';
                if (arg === undefined) return 'undefined';
                if (typeof arg === 'string') return arg;
                if (arg instanceof Error) return `${arg.name}: ${arg.message}`;
                try { return JSON.stringify(arg); } catch (e) { return String(arg); }
            })
        });
        if (debugSnapshotLogs.length > maxDebugLogs) debugSnapshotLogs.shift();
        return prev.apply(console, args);
    };
});

// Get formatted console logs
function getConsoleLogs() {
    if (debugSnapshotLogs.length === 0) return 'No console logs captured.';
    return debugSnapshotLogs.map(entry => {
        const icon = { error: '❌', warn: '⚠️', info: 'ℹ️', debug: '🔍', log: '📝' }[entry.type] || '📝';
        return `${icon} [${entry.type.toUpperCase()}] ${entry.args.join(' ')}`;
    }).join('\\n');
}

// Show camera flash effect
function showCameraFlash() {
    const flash = document.createElement('div');
    flash.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: white; opacity: 0.8; z-index: 99999;
        animation: flashFade 0.3s ease-out forwards;
    `;
    const style = document.createElement('style');
    style.textContent = '@keyframes flashFade { to { opacity: 0; } }';
    document.head.appendChild(style);
    document.body.appendChild(flash);
    setTimeout(() => { flash.remove(); style.remove(); }, 300);
}

// Capture FULL PAGE screenshot using html2canvas (no dialog required)
async function captureScreenshot() {
    console.log('[DebugSnapshot] === Starting screenshot capture ===');

    // Check html2canvas availability
    if (typeof html2canvas === 'undefined') {
        console.error('[DebugSnapshot] html2canvas NOT LOADED!');
        return await captureFigureOnly();
    }

    console.log('[DebugSnapshot] html2canvas version:', html2canvas.toString().slice(0, 50));

    try {
        // Small delay to ensure DOM is stable
        await new Promise(r => setTimeout(r, 100));

        // Get the editor container
        const container = document.querySelector('.editor-container');
        if (!container) {
            console.error('[DebugSnapshot] .editor-container not found!');
            return await captureFigureOnly();
        }

        const rect = container.getBoundingClientRect();
        console.log('[DebugSnapshot] Container size:', rect.width, 'x', rect.height);

        // Capture with explicit dimensions
        console.log('[DebugSnapshot] Starting html2canvas...');
        const canvas = await html2canvas(container, {
            backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-color') || '#1e1e1e',
            width: Math.ceil(rect.width),
            height: Math.ceil(rect.height),
            scale: 1,
            useCORS: true,
            allowTaint: true,
            logging: true,  // Enable for debugging
            onclone: (clonedDoc) => {
                console.log('[DebugSnapshot] DOM cloned for rendering');
            }
        });

        console.log('[DebugSnapshot] Canvas result:', canvas.width, 'x', canvas.height);

        // Validate result - full page should be wider than just the figure
        if (canvas.width > 500 && canvas.height > 300) {
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
            console.log('[DebugSnapshot] FULL PAGE SUCCESS! Blob size:', blob?.size);
            return blob;
        }

        console.warn('[DebugSnapshot] Canvas too small, using figure fallback');
    } catch (err) {
        console.error('[DebugSnapshot] html2canvas ERROR:', err.name, err.message);
        console.error(err.stack);
    }

    return await captureFigureOnly();
}

// Fallback: capture just the figure image
async function captureFigureOnly() {
    console.log('[DebugSnapshot] Using figure-only fallback...');
    try {
        const img = document.getElementById('preview-image');
        if (img && img.src && img.src.startsWith('data:')) {
            const response = await fetch(img.src);
            const blob = await response.blob();
            console.log('[DebugSnapshot] Figure captured, size:', blob.size);
            return blob;
        }
    } catch (err) {
        console.error('[DebugSnapshot] Figure fallback failed:', err);
    }
    return null;
}

// Capture debug snapshot (screenshot + console logs)
async function captureDebugSnapshot() {
    showCameraFlash();
    showToast('📷 Capturing...', 'info');

    const screenshotBlob = await captureScreenshot();
    const logsText = getConsoleLogs();

    if (!screenshotBlob && logsText === 'No console logs captured.') {
        showToast('✗ Capture failed', 'error');
        return;
    }

    // Copy screenshot first
    if (screenshotBlob) {
        try {
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': screenshotBlob })
            ]);
            showToast('📷 Screenshot copied! Paste now, then logs copy in 3s...', 'success');
        } catch (e) {
            console.error('[DebugSnapshot] Clipboard failed:', e);
            showToast('✗ Clipboard failed', 'error');
            return;
        }
    }

    // Copy logs after delay
    if (logsText !== 'No console logs captured.') {
        const delay = screenshotBlob ? 3000 : 0;
        await new Promise(r => setTimeout(r, delay));
        try {
            await navigator.clipboard.writeText(logsText);
            showToast('📋 Console logs copied!', 'success');
        } catch (e) {
            console.error('[DebugSnapshot] Logs clipboard failed:', e);
        }
    }
}

// ==================== END DEBUG SNAPSHOT ====================
"""

__all__ = ["SCRIPTS_DEBUG_SNAPSHOT"]
