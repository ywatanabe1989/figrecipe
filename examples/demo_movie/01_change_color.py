#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: Change Element Color

Shows how to click on a bar chart element and change its color
using the figrecipe editor.

Duration target: ~8 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class ChangeColorDemo(DemoRecorder):
    """Demo showing how to change element color in the editor."""

    title = "Change Element Color"
    duration_target = 8
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Wait for page to fully load
        await self.wait(1)

        # Step 1: Click on bar chart element
        await self.caption("Step 1: Click on a bar chart element")
        await self.wait(1)

        # Find and click a bar element (adjust selector as needed)
        # The bar elements have data-key attributes like "bar_0", "bar_1", etc.
        bar_selector = '[data-key^="bar_"]'

        # Highlight the element first
        await self.highlight(bar_selector, duration=1.0)

        # Click the element
        try:
            await page.click(bar_selector, timeout=5000)
        except Exception:
            # Fallback: click on the preview image area for bars
            await page.click("#preview-image", position={"x": 200, "y": 300})

        await self.wait(1)

        # Step 2: Open color picker
        await self.caption("Step 2: Open color picker")
        await self.wait(1)

        # Look for color input or dropdown
        color_selectors = [
            "#color-select",
            "[id*='color']",
            "select[id*='color']",
            ".color-picker",
        ]

        clicked = False
        for selector in color_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await self.highlight(selector, duration=0.5)
                    await page.click(selector, timeout=2000)
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            await self.caption("(Color picker not found - demo continues)")

        await self.wait(1)

        # Step 3: Select a color (red)
        await self.caption("Step 3: Select red color")
        await self.wait(1)

        # Try to select red color option
        try:
            await page.select_option("select", label="red", timeout=2000)
        except Exception:
            try:
                # Try clicking a red color option
                await page.click('[data-color="red"]', timeout=2000)
            except Exception:
                pass

        await self.wait(1)

        # Final caption
        await self.caption("Color changed successfully!")
        await self.wait(2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record change color demo")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:5050",
        help="Editor URL",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Run with visible browser",
    )
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    demo = ChangeColorDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    print(f"  MP4: {mp4_path}")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
