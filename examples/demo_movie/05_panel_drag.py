#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: Panel Drag

Shows how to drag panels to rearrange figure layout.
Now supports contourf, specgram, quiver, and other filled plot types.

Duration target: ~12 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class PanelDragDemo(DemoRecorder):
    """Demo showing panel drag functionality."""

    title = "Panel Drag Rearrangement"
    demo_id = "05"
    duration_target = 12
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        from figrecipe._dev.browser._cursor import move_cursor_to

        # Show intro
        await self.caption("Drag panels to rearrange figure layout")
        await self.wait(1.5)

        # Find a panel to drag (imshow panel at index 4)
        preview = page.locator("#preview-image")
        box = await preview.bounding_box()

        if box:
            # Calculate position for panel at row 1, col 1 (imshow)
            panel_x = box["x"] + box["width"] * 0.5
            panel_y = box["y"] + box["height"] * 0.5

            await self.caption("Click and drag any panel")

            # Move visual cursor AND actual mouse together
            await move_cursor_to(page, panel_x, panel_y, 600)
            await page.mouse.move(panel_x, panel_y)
            await self.wait(0.5)

            # Mouse down to start drag
            await page.mouse.down()
            await self.wait(0.3)

            # Drag to new position - animate both cursor and mouse
            new_x = panel_x + 100
            new_y = panel_y + 60
            steps = 20
            for i in range(steps + 1):
                progress = i / steps
                curr_x = panel_x + (new_x - panel_x) * progress
                curr_y = panel_y + (new_y - panel_y) * progress
                await page.mouse.move(curr_x, curr_y)
                await move_cursor_to(page, curr_x, curr_y, 30)

            await self.wait(0.3)
            await self.caption("Panels snap to grid and edges")
            await self.wait(1.0)

            await page.mouse.up()
            await self.wait(0.5)

        # Explain supported types
        await self.caption("Works with imshow, contourf, specgram, quiver...")
        await self.wait(2.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record panel drag demo")
    parser.add_argument("--url", default="http://127.0.0.1:5050", help="Editor URL")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    demo = PanelDragDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
