#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mouse cursor visualization for demo recordings.

Injects a visible cursor element that follows mouse movements,
making demos more intuitive when the system cursor isn't captured.
"""

# JavaScript to inject cursor visualization
CURSOR_JS = """
() => {
    // Remove existing cursor if any
    const existing = document.getElementById('demo-cursor');
    if (existing) existing.remove();

    // Create cursor element
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 24px;
        height: 24px;
        border: 3px solid #FF4444;
        border-radius: 50%;
        pointer-events: none;
        z-index: 2147483647;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
        transform: translate(-50%, -50%);
        transition: transform 0.05s ease-out;
    `;
    document.body.appendChild(cursor);

    // Create inner dot
    const dot = document.createElement('div');
    dot.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        width: 6px;
        height: 6px;
        background: #FF4444;
        border-radius: 50%;
        transform: translate(-50%, -50%);
    `;
    cursor.appendChild(dot);

    // Track mouse movement
    window._demoCursorHandler = (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    };
    document.addEventListener('mousemove', window._demoCursorHandler);

    // Initial position at center
    cursor.style.left = window.innerWidth / 2 + 'px';
    cursor.style.top = window.innerHeight / 2 + 'px';

    return true;
}
"""

REMOVE_CURSOR_JS = """
() => {
    const cursor = document.getElementById('demo-cursor');
    if (cursor) cursor.remove();
    if (window._demoCursorHandler) {
        document.removeEventListener('mousemove', window._demoCursorHandler);
        delete window._demoCursorHandler;
    }
    return true;
}
"""


async def inject_cursor(page) -> bool:
    """Inject visible cursor element into page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(CURSOR_JS)


async def remove_cursor(page) -> bool:
    """Remove cursor visualization from page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(REMOVE_CURSOR_JS)


__all__ = ["inject_cursor", "remove_cursor"]

# EOF
