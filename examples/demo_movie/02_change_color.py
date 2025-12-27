#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-27 20:53:04 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_movie/02_change_color.py


"""Demo: Change Element Color

Shows how to click on a bar chart element and change its color
using the figrecipe editor.

Duration target: ~10 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class ChangeColorDemo(DemoRecorder):
    """Demo showing how to change element color in the editor."""

    title = "Element Color Editing"
    demo_id = "02"
    duration_target = 10
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        import asyncio

        # Restore to clean state first
        restore_btn = page.locator("button:has-text('Restore')")
        if await restore_btn.count() > 0:
            page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            await restore_btn.click()
            await self.wait(1.0)

        # Step 1: Click on bar chart element
        await self.caption("Click on a bar chart element")
        await self.wait(0.8)

        # Move cursor to bar element, then click
        bar_locator = page.locator("g").filter(has_text="bar: bar").first
        await self.move_to(bar_locator, duration=0.6)
        await self.wait(0.3)
        await bar_locator.click(timeout=5000)
        await self.wait(1.0)

        # Step 2: Show element selected
        await self.caption("Properties panel shows element settings")
        await self.wait(1.5)

        # Step 3: Click on color dropdown to open it visually
        await self.caption("Click color dropdown to change color")
        await self.wait(0.5)

        color_dropdown = page.locator(".color-select").first
        await self.move_to(color_dropdown, duration=0.5)
        await self.wait(0.3)
        await color_dropdown.click()
        await self.wait(0.8)

        # Step 4: Move cursor to red option and click it
        await self.caption("Select a new color")
        from figrecipe._dev.browser._cursor import move_cursor_to

        # Get dropdown bounding box and move down to "red" option (2nd item)
        dropdown_box = await color_dropdown.bounding_box()
        if dropdown_box:
            # Move cursor down to hover over "red" option
            red_y = dropdown_box["y"] + dropdown_box["height"] + 25  # ~2nd option
            await move_cursor_to(page, dropdown_box["x"] + 50, red_y, 400)
            await self.wait(0.3)

        # Select option - this closes the native dropdown automatically
        await color_dropdown.select_option("red")
        await self.wait(2.0)

        # Final caption - show the result
        await self.caption("Color changes instantly!")
        await self.wait(1.5)


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
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
