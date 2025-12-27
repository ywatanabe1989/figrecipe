#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Click effect visualization for demo recordings.

Shows ripple/pulse animation at click locations to make
mouse clicks visible in recordings.
"""

# JavaScript to inject click effect handler
CLICK_EFFECT_JS = """
() => {
    // Add CSS animation if not exists
    if (!document.getElementById('demo-click-style')) {
        const style = document.createElement('style');
        style.id = 'demo-click-style';
        style.textContent = `
            @keyframes demo-click-ripple {
                0% {
                    transform: translate(-50%, -50%) scale(0);
                    opacity: 1;
                }
                100% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 0;
                }
            }
            .demo-click-ripple {
                position: fixed;
                width: 60px;
                height: 60px;
                border: 4px solid #FF4444;
                border-radius: 50%;
                pointer-events: none;
                z-index: 2147483646;
                animation: demo-click-ripple 0.6s ease-out forwards;
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize click sound audio element
    if (!window._demoClickAudio) {
        window._demoClickAudio = new Audio('/static/click.mp3');
        window._demoClickAudio.volume = 0.15;
    }

    // Function to play click sound
    window._playClickSound = () => {
        if (window._demoClickAudio) {
            window._demoClickAudio.currentTime = 0;
            window._demoClickAudio.play().catch(() => {});
        }
    };

    // Remove existing handler if any
    if (window._demoClickHandler) {
        document.removeEventListener('mousedown', window._demoClickHandler);
    }

    // Add click handler
    window._demoClickHandler = (e) => {
        // Play click sound
        if (window._playClickSound) window._playClickSound();

        const ripple = document.createElement('div');
        ripple.className = 'demo-click-ripple';
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        document.body.appendChild(ripple);

        // Also pulse the cursor if it exists
        const cursor = document.getElementById('demo-cursor');
        if (cursor) {
            cursor.style.transform = 'translate(-50%, -50%) scale(1.3)';
            setTimeout(() => {
                cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            }, 150);
        }

        // Remove ripple after animation
        setTimeout(() => ripple.remove(), 600);
    };
    document.addEventListener('mousedown', window._demoClickHandler);

    return true;
}
"""

REMOVE_CLICK_EFFECT_JS = """
() => {
    // Remove handler
    if (window._demoClickHandler) {
        document.removeEventListener('mousedown', window._demoClickHandler);
        delete window._demoClickHandler;
    }
    // Remove audio element
    if (window._demoClickAudio) {
        window._demoClickAudio.pause();
        delete window._demoClickAudio;
    }
    delete window._playClickSound;
    // Remove style
    const style = document.getElementById('demo-click-style');
    if (style) style.remove();
    // Remove any remaining ripples
    document.querySelectorAll('.demo-click-ripple').forEach(el => el.remove());
    return true;
}
"""


async def inject_click_effect(page) -> bool:
    """Inject click ripple effect handler into page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(CLICK_EFFECT_JS)


async def remove_click_effect(page) -> bool:
    """Remove click effect handler from page.

    Parameters
    ----------
    page : playwright.async_api.Page
        Playwright page object.

    Returns
    -------
    bool
        True if successful.
    """
    return await page.evaluate(REMOVE_CLICK_EFFECT_JS)


__all__ = ["inject_click_effect", "remove_click_effect"]

# EOF
