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
        bottom: 50px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.85);
        color: white;
        padding: 18px 40px;
        border-radius: 10px;
        font-size: 24px;
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

# JavaScript for title screen with blur overlay
TITLE_SCREEN_JS = """
async (args) => {
    const { title, subtitle = '', timestamp = '', duration = 2000 } = args;

    // Add CSS animations if not exists
    if (!document.getElementById('demo-title-style')) {
        const style = document.createElement('style');
        style.id = 'demo-title-style';
        style.textContent = `
            @keyframes demo-title-fade-in {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            @keyframes demo-title-fade-out {
                0% { opacity: 1; }
                100% { opacity: 0; }
            }
            @keyframes demo-title-text-in {
                0% { opacity: 0; transform: scale(0.9); }
                100% { opacity: 1; transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
    }

    // Create blur overlay
    const overlay = document.createElement('div');
    overlay.id = 'demo-title-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 2147483646;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: demo-title-fade-in 0.5s ease-out forwards;
    `;

    // Create title text
    const titleEl = document.createElement('div');
    titleEl.style.cssText = `
        color: white;
        font-size: 48px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
        text-align: center;
        animation: demo-title-text-in 0.6s ease-out 0.2s both;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    `;
    titleEl.textContent = title;
    overlay.appendChild(titleEl);

    // Create subtitle if provided
    if (subtitle) {
        const subtitleEl = document.createElement('div');
        subtitleEl.style.cssText = `
            color: rgba(255, 255, 255, 0.8);
            font-size: 24px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-weight: 400;
            margin-top: 16px;
            text-align: center;
            animation: demo-title-text-in 0.6s ease-out 0.4s both;
        `;
        subtitleEl.textContent = subtitle;
        overlay.appendChild(subtitleEl);
    }

    // Create timestamp if provided
    if (timestamp) {
        const timestampEl = document.createElement('div');
        timestampEl.style.cssText = `
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            font-family: monospace;
            margin-top: 24px;
            text-align: center;
            animation: demo-title-text-in 0.6s ease-out 0.5s both;
        `;
        timestampEl.textContent = timestamp;
        overlay.appendChild(timestampEl);
    }

    document.body.appendChild(overlay);

    // Wait and fade out
    await new Promise(r => setTimeout(r, duration));

    overlay.style.animation = 'demo-title-fade-out 0.5s ease-out forwards';
    await new Promise(r => setTimeout(r, 500));
    overlay.remove();

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


async def show_title_screen(
    page,
    title: str,
    subtitle: str = "",
    timestamp: str = "",
    duration_ms: int = 2000,
) -> bool:
    """Show title screen with blur overlay and fade effect.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    title : str
        Main title text.
    subtitle : str, optional
        Subtitle text (default: "").
    timestamp : str, optional
        Timestamp to display (default: "").
    duration_ms : int, optional
        Duration to show title in milliseconds (default: 2000).

    Returns
    -------
    bool
        True if successful.
    """
    args = {
        "title": title,
        "subtitle": subtitle,
        "timestamp": timestamp,
        "duration": duration_ms,
    }
    return await page.evaluate(TITLE_SCREEN_JS, args)


# JavaScript for closing branding screen
CLOSING_SCREEN_JS = """
async (args) => {
    const { duration = 2500 } = args;

    // Add CSS animations
    if (!document.getElementById('demo-closing-style')) {
        const style = document.createElement('style');
        style.id = 'demo-closing-style';
        style.textContent = `
            @keyframes demo-closing-fade-in {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            @keyframes demo-closing-fade-out {
                0% { opacity: 1; }
                100% { opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'demo-closing-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        z-index: 2147483646;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: demo-closing-fade-in 0.5s ease-out forwards;
    `;

    // FigRecipe title
    const title = document.createElement('div');
    title.style.cssText = `
        color: white;
        font-size: 56px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
        margin-bottom: 16px;
    `;
    title.textContent = 'FigRecipe';
    overlay.appendChild(title);

    // Part of SciTeX
    const scitex = document.createElement('div');
    scitex.style.cssText = `
        color: rgba(255, 255, 255, 0.7);
        font-size: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin-bottom: 24px;
    `;
    scitex.innerHTML = 'Part of SciTeX&trade;';
    overlay.appendChild(scitex);

    // URL
    const url = document.createElement('div');
    url.style.cssText = `
        color: #4da6ff;
        font-size: 18px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    url.textContent = 'https://scitex.ai';
    overlay.appendChild(url);

    document.body.appendChild(overlay);

    // Wait and fade out
    await new Promise(r => setTimeout(r, duration));

    overlay.style.animation = 'demo-closing-fade-out 0.5s ease-out forwards';
    await new Promise(r => setTimeout(r, 500));
    overlay.remove();

    return true;
}
"""


async def show_closing_screen(page, duration_ms: int = 2500) -> bool:
    """Show closing branding screen with FigRecipe and SciTeX.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    duration_ms : int, optional
        Duration to show screen in milliseconds (default: 2500).

    Returns
    -------
    bool
        True if successful.
    """
    args = {"duration": duration_ms}
    return await page.evaluate(CLOSING_SCREEN_JS, args)


__all__ = ["show_caption", "hide_caption", "show_title_screen", "show_closing_screen"]

# EOF
