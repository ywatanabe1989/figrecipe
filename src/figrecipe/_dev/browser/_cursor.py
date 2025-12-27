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

# JavaScript to animate cursor to a position
MOVE_CURSOR_JS = """
async (args) => {
    const { x, y, duration = 500 } = args;
    const cursor = document.getElementById('demo-cursor');
    if (!cursor) return false;

    // Get current position
    const startX = parseFloat(cursor.style.left) || window.innerWidth / 2;
    const startY = parseFloat(cursor.style.top) || window.innerHeight / 2;

    // Animate to target
    const startTime = performance.now();

    return new Promise((resolve) => {
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease-out cubic for natural motion
            const eased = 1 - Math.pow(1 - progress, 3);

            const currentX = startX + (x - startX) * eased;
            const currentY = startY + (y - startY) * eased;

            cursor.style.left = currentX + 'px';
            cursor.style.top = currentY + 'px';

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                resolve(true);
            }
        }
        requestAnimationFrame(animate);
    });
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


async def move_cursor_to(page, x: float, y: float, duration_ms: int = 500) -> bool:
    """Animate cursor to a specific position.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    x : float
        Target X coordinate.
    y : float
        Target Y coordinate.
    duration_ms : int, optional
        Animation duration in milliseconds (default: 500).

    Returns
    -------
    bool
        True if successful.
    """
    args = {"x": x, "y": y, "duration": duration_ms}
    return await page.evaluate(MOVE_CURSOR_JS, args)


async def move_cursor_to_element(page, locator, duration_ms: int = 500) -> bool:
    """Animate cursor to an element's center.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    locator : playwright.async_api.Locator
        Playwright locator for target element.
    duration_ms : int, optional
        Animation duration in milliseconds (default: 500).

    Returns
    -------
    bool
        True if successful.
    """
    box = await locator.bounding_box()
    if not box:
        return False
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    return await move_cursor_to(page, x, y, duration_ms)


__all__ = ["inject_cursor", "remove_cursor", "move_cursor_to", "move_cursor_to_element"]

# EOF
