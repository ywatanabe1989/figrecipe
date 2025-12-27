#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Element highlighting for demo recordings.

Highlights elements with colored overlays to draw attention
during demo recordings. Based on scitex browser debugging patterns.
"""

# JavaScript for highlighting element
HIGHLIGHT_JS = """
async (args) => {
    const { selector, duration = 1000, color = '#FF4444' } = args;

    // Find element
    const element = document.querySelector(selector);
    if (!element) {
        console.warn('Element not found:', selector);
        return false;
    }

    // Scroll into view
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Wait for scroll
    await new Promise(r => setTimeout(r, 300));

    // Get position after scroll
    const rect = element.getBoundingClientRect();

    // Create highlight overlay
    const overlay = document.createElement('div');
    overlay.className = 'demo-highlight';
    overlay.style.cssText = `
        position: fixed;
        top: ${rect.top - 4}px;
        left: ${rect.left - 4}px;
        width: ${rect.width + 8}px;
        height: ${rect.height + 8}px;
        border: 4px solid ${color};
        border-radius: 4px;
        background: ${color}20;
        pointer-events: none;
        z-index: 2147483644;
        box-shadow: 0 0 20px ${color}80;
        animation: demo-highlight-pulse 0.5s ease-in-out infinite alternate;
    `;

    // Add animation style if not exists
    if (!document.getElementById('demo-highlight-style')) {
        const style = document.createElement('style');
        style.id = 'demo-highlight-style';
        style.textContent = `
            @keyframes demo-highlight-pulse {
                0% { box-shadow: 0 0 10px ${color}40; }
                100% { box-shadow: 0 0 25px ${color}80; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(overlay);

    // Remove after duration
    setTimeout(() => {
        overlay.style.transition = 'opacity 0.3s';
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
    }, duration);

    return true;
}
"""


async def highlight_element(
    page,
    selector: str,
    duration_ms: int = 1000,
    color: str = "#FF4444",
) -> bool:
    """Highlight an element with colored overlay.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    selector : str
        CSS selector for element to highlight.
    duration_ms : int, optional
        Duration to show highlight in milliseconds (default: 1000).
    color : str, optional
        Highlight color in hex format (default: "#FF4444").

    Returns
    -------
    bool
        True if element was found and highlighted.
    """
    args = {"selector": selector, "duration": duration_ms, "color": color}
    return await page.evaluate(HIGHLIGHT_JS, args)


__all__ = ["highlight_element"]

# EOF
