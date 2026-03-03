#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Element inspector and debug capture JavaScript."""

SCRIPTS_INSPECTOR = """
// ==================== ELEMENT INSPECTOR ====================
// Visual debugging tool for DOM elements (Alt+I to toggle)
let elementInspectorActive = false;
let elementInspectorOverlay = null;
const inspectorColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
];

function toggleElementInspector() {
    if (elementInspectorActive) {
        deactivateElementInspector();
    } else {
        activateElementInspector();
    }
}

function activateElementInspector() {
    console.log('[ElementInspector] Activating...');
    elementInspectorActive = true;

    // Create overlay container
    elementInspectorOverlay = document.createElement('div');
    elementInspectorOverlay.id = 'element-inspector-overlay';
    elementInspectorOverlay.className = 'element-inspector-overlay';
    document.body.appendChild(elementInspectorOverlay);

    // Scan and visualize elements
    scanInspectorElements();

    console.log('[ElementInspector] Active - Press Alt+I to deactivate');
}

function deactivateElementInspector() {
    console.log('[ElementInspector] Deactivating...');
    elementInspectorActive = false;

    if (elementInspectorOverlay) {
        elementInspectorOverlay.remove();
        elementInspectorOverlay = null;
    }
}

function scanInspectorElements() {
    if (!elementInspectorOverlay) return;

    // Clear existing overlays
    elementInspectorOverlay.innerHTML = '';

    // Get all visible elements
    const allElements = document.querySelectorAll('*');
    let colorIndex = 0;

    allElements.forEach(element => {
        // Skip non-visible, overlay, and script/style elements
        if (element.tagName === 'SCRIPT' || element.tagName === 'STYLE' ||
            element.tagName === 'HEAD' || element.tagName === 'META' ||
            element.tagName === 'LINK' || element.tagName === 'TITLE' ||
            element.id === 'element-inspector-overlay' ||
            element.closest('#element-inspector-overlay')) {
            return;
        }

        const rect = element.getBoundingClientRect();

        // Skip invisible or zero-size elements
        if (rect.width < 5 || rect.height < 5 ||
            rect.bottom < 0 || rect.right < 0 ||
            rect.top > window.innerHeight || rect.left > window.innerWidth) {
            return;
        }

        // Create element box
        const box = document.createElement('div');
        box.className = 'element-inspector-box';
        const color = inspectorColors[colorIndex % inspectorColors.length];
        box.style.cssText = `
            left: ${rect.left + window.scrollX}px;
            top: ${rect.top + window.scrollY}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            border-color: ${color};
        `;

        // Create label
        const label = document.createElement('div');
        label.className = 'element-inspector-label';
        label.style.backgroundColor = color;

        // Build element identifier
        let identifier = element.tagName.toLowerCase();
        if (element.id) identifier += '#' + element.id;
        if (element.className && typeof element.className === 'string') {
            const classes = element.className.split(' ').filter(c => c && !c.startsWith('element-inspector')).slice(0, 2);
            if (classes.length) identifier += '.' + classes.join('.');
        }

        label.textContent = identifier;
        box.appendChild(label);

        // Add click handler to show element info
        box.addEventListener('click', (e) => {
            e.stopPropagation();
            showInspectorElementInfo(element, color);
        });

        // Right-click to copy element path
        box.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            e.stopPropagation();
            copyInspectorElementPath(element);
        });

        elementInspectorOverlay.appendChild(box);
        colorIndex++;
    });

    console.log('[ElementInspector] Scanned ' + colorIndex + ' elements');
}

function showInspectorElementInfo(element, color) {
    // Log element info to console
    console.group('%cElement Info', 'color: ' + color + '; font-weight: bold;');
    console.log('Tag:', element.tagName);
    console.log('ID:', element.id || '(none)');
    console.log('Classes:', element.className || '(none)');
    console.log('Size:', element.offsetWidth + 'x' + element.offsetHeight);
    console.log('Position:', element.getBoundingClientRect());
    console.log('Element:', element);
    console.groupEnd();
}

function copyInspectorElementPath(element) {
    // Build CSS selector path
    const path = [];
    let current = element;

    while (current && current !== document.body) {
        let selector = current.tagName.toLowerCase();
        if (current.id) {
            selector = '#' + current.id;
            path.unshift(selector);
            break;
        } else if (current.className && typeof current.className === 'string') {
            const classes = current.className.split(' ').filter(c => c).slice(0, 2);
            if (classes.length) selector += '.' + classes.join('.');
        }
        path.unshift(selector);
        current = current.parentElement;
    }

    const selectorPath = path.join(' > ');
    navigator.clipboard.writeText(selectorPath).then(() => {
        console.log('[ElementInspector] Copied selector:', selectorPath);
        showToast('Copied: ' + selectorPath, 'success');
    });
}

// Shutter effect for screenshot feedback
function showShutterEffect() {
    const shutter = document.createElement('div');
    shutter.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: white;
        opacity: 0.8;
        z-index: 99999;
        pointer-events: none;
        animation: shutterFlash 0.3s ease-out forwards;
    `;

    // Add keyframes if not exists
    if (!document.getElementById('shutter-keyframes')) {
        const style = document.createElement('style');
        style.id = 'shutter-keyframes';
        style.textContent = `
            @keyframes shutterFlash {
                0% { opacity: 0.8; }
                100% { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(shutter);
    setTimeout(() => shutter.remove(), 300);
}

// Capture debug info: full-page screenshot first, then console logs after delay
async function captureDebugInfo() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Show shutter effect
    showShutterEffect();

    // Step 1: Capture full page screenshot using html2canvas, fallback to figure only
    try {
        let blob = null;

        // Try html2canvas for full page capture
        if (typeof html2canvas !== 'undefined') {
            try {
                console.log('[DebugCapture] Attempting full-page capture with html2canvas...');
                const canvas = await html2canvas(document.body, {
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    backgroundColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#1e1e1e' : '#ffffff',
                    ignoreElements: (element) => {
                        // Skip script and noscript elements
                        return element.tagName === 'SCRIPT' || element.tagName === 'NOSCRIPT';
                    }
                });
                blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
                console.log('[DebugCapture] Full-page capture successful');
            } catch (html2canvasErr) {
                console.warn('[DebugCapture] html2canvas failed, falling back to figure only:', html2canvasErr.message);
            }
        }

        // Fallback: copy just the figure image
        if (!blob) {
            const img = document.getElementById('preview-image');
            if (img && img.src) {
                const response = await fetch(img.src);
                blob = await response.blob();
                console.log('[DebugCapture] Fallback: copied figure image only');
            }
        }

        if (blob) {
            await navigator.clipboard.write([
                new ClipboardItem({ [blob.type]: blob })
            ]);
            showToast('Screenshot copied! Paste now. Text in 2s...', 'success');
            console.log('[DebugCapture] Image copied to clipboard');
        } else {
            showToast('No image captured, copying text only...', 'warning');
        }
    } catch (err) {
        console.error('[DebugCapture] Image copy failed:', err);
        showToast('Image copy failed, copying text...', 'warning');
    }

    // Step 2: Wait 2 seconds, then copy debug text
    setTimeout(async () => {
        let debugInfo = `=== Debug Capture: ${timestamp} ===\\n\\n`;

        // Collect console logs
        debugInfo += '=== Console Logs ===\\n';
        if (window.consoleLogs && window.consoleLogs.length > 0) {
            window.consoleLogs.forEach(log => {
                debugInfo += `[${log.type}] ${log.message}\\n`;
            });
        } else {
            debugInfo += '(No logs captured)\\n';
        }

        // Add current state info
        debugInfo += '\\n=== Current State ===\\n';
        debugInfo += `URL: ${window.location.href}\\n`;
        debugInfo += `Selected Element: ${selectedElement ? selectedElement.key : 'None'}\\n`;
        debugInfo += `Zoom Level: ${Math.round(zoomLevel * 100)}%\\n`;
        debugInfo += `Theme: ${document.documentElement.getAttribute('data-theme') || 'light'}\\n`;

        try {
            await navigator.clipboard.writeText(debugInfo);
            showToast('Debug text copied! Paste now.', 'success');
            console.log('[DebugCapture] Text copied:', debugInfo);
        } catch (err) {
            console.error('[DebugCapture] Text copy failed:', err);
            showToast('Text copy failed: ' + err.message, 'error');
        }
    }, 2000);
}

// Console log interceptor (captures logs for debug export)
window.consoleLogs = [];
const originalConsole = {
    log: console.log,
    warn: console.warn,
    error: console.error
};

console.log = function(...args) {
    window.consoleLogs.push({ type: 'LOG', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.log.apply(console, args);
};

console.warn = function(...args) {
    window.consoleLogs.push({ type: 'WARN', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.warn.apply(console, args);
};

console.error = function(...args) {
    window.consoleLogs.push({ type: 'ERROR', message: args.join(' '), time: new Date() });
    if (window.consoleLogs.length > 100) window.consoleLogs.shift();
    originalConsole.error.apply(console, args);
};

console.log('[ElementInspector] Loaded - Press Alt+I to toggle');
console.log('[DebugCapture] Loaded - Press Alt+Shift+I for screenshot + logs');
"""

__all__ = ["SCRIPTS_INSPECTOR"]
