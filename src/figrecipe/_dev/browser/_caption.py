#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caption overlay for demo recordings.

Shows text captions/banners during demo recordings to explain
what is happening in the demo.
"""

# JavaScript template for showing caption
SHOW_CAPTION_JS = """
(text) => {
    // Remove existing caption if any
    const existing = document.getElementById('demo-caption');
    if (existing) existing.remove();

    // Add CSS if not exists
    if (!document.getElementById('demo-caption-style')) {
        const style = document.createElement('style');
        style.id = 'demo-caption-style';
        style.textContent = `
            @keyframes demo-caption-fade-in {
                0% { opacity: 0; transform: translateY(20px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            @keyframes demo-caption-fade-out {
                0% { opacity: 1; transform: translateY(0); }
                100% { opacity: 0; transform: translateY(-20px); }
            }
        `;
        document.head.appendChild(style);
    }

    // Create caption element
    const caption = document.createElement('div');
    caption.id = 'demo-caption';
    caption.textContent = text;
    caption.style.cssText = `
        position: fixed;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.85);
        color: white;
        padding: 16px 32px;
        border-radius: 8px;
        font-size: 18px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        z-index: 2147483645;
        pointer-events: none;
        animation: demo-caption-fade-in 0.3s ease-out forwards;
        max-width: 80%;
        text-align: center;
    `;
    document.body.appendChild(caption);

    return true;
}
"""

HIDE_CAPTION_JS = """
() => {
    const caption = document.getElementById('demo-caption');
    if (caption) {
        caption.style.animation = 'demo-caption-fade-out 0.3s ease-out forwards';
        setTimeout(() => caption.remove(), 300);
    }
    return true;
}
"""


async def show_caption(page, text: str) -> bool:
    """Show caption text overlay on page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    text : str
        Caption text to display.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(SHOW_CAPTION_JS, text)


async def hide_caption(page) -> bool:
    """Hide caption overlay from page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(HIDE_CAPTION_JS)


__all__ = ["show_caption", "hide_caption"]

# EOF
