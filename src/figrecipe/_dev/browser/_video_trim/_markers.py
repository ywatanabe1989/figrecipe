#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Marker injection for video trimming.

Injects visual markers with OCR-readable metadata text.
Uses same async pattern as title_screen which is known to work.
"""

# Marker identifiers
MARKER_START_ID = "TRIM_START"
MARKER_END_ID = "TRIM_END"

# JavaScript to create marker overlay with metadata text
# Uses async function pattern matching show_title_screen
MARKER_OVERLAY_JS = """
async (args) => {
    const { marker_id, version, timestamp, duration } = args;

    const overlay = document.createElement('div');
    overlay.id = 'trim-marker-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: #000000;
        z-index: 2147483647;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-family: 'Courier New', monospace;
        color: #FFFFFF;
    `;

    // Marker ID (top) - OCR-friendly format
    const idText = document.createElement('div');
    idText.textContent = '== ' + marker_id + ' ==';
    idText.style.cssText = `
        font-size: 72px;
        font-weight: bold;
        letter-spacing: 8px;
        margin-bottom: 60px;
    `;
    overlay.appendChild(idText);

    // Version (center)
    const verText = document.createElement('div');
    verText.textContent = version;
    verText.style.cssText = `
        font-size: 48px;
        margin-bottom: 40px;
    `;
    overlay.appendChild(verText);

    // Timestamp (bottom)
    const tsText = document.createElement('div');
    tsText.textContent = timestamp;
    tsText.style.cssText = `
        font-size: 36px;
        opacity: 0.9;
    `;
    overlay.appendChild(tsText);

    document.body.appendChild(overlay);

    // Wait for duration
    await new Promise(r => setTimeout(r, duration));

    overlay.remove();
    return true;
}
"""


async def inject_start_marker(
    page,
    version: str = "",
    timestamp: str = "",
    duration_ms: int = 500,
) -> None:
    """Inject start marker with metadata.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    version : str
        Version string to display.
    timestamp : str
        Timestamp string to display.
    duration_ms : int
        Duration to show marker in milliseconds (default: 500).
    """
    args = {
        "marker_id": MARKER_START_ID,
        "version": version,
        "timestamp": timestamp,
        "duration": duration_ms,
    }
    await page.evaluate(MARKER_OVERLAY_JS, args)


async def inject_end_marker(
    page,
    version: str = "",
    timestamp: str = "",
    duration_ms: int = 500,
) -> None:
    """Inject end marker with metadata.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.
    version : str
        Version string to display.
    timestamp : str
        Timestamp string to display.
    duration_ms : int
        Duration to show marker in milliseconds (default: 500).
    """
    args = {
        "marker_id": MARKER_END_ID,
        "version": version,
        "timestamp": timestamp,
        "duration": duration_ms,
    }
    await page.evaluate(MARKER_OVERLAY_JS, args)


__all__ = [
    "MARKER_START_ID",
    "MARKER_END_ID",
    "inject_start_marker",
    "inject_end_marker",
]

# EOF
