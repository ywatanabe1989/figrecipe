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
        # Show intro
        await self.caption("Drag panels to rearrange figure layout")
        await self.wait(1.5)

        # Find a panel to drag (imshow panel at index 4)
        preview = page.locator("#preview-image")
        box = await preview.bounding_box()

        if box:
            # Calculate position for panel at row 1, col 1 (imshow)
            # Grid is 3x3, so panel 4 is at (1,1)
            panel_x = box["x"] + box["width"] * 0.5  # center column
            panel_y = box["y"] + box["height"] * 0.5  # center row

            await self.caption("Click and drag any panel")
            await page.mouse.move(panel_x, panel_y)
            await self.wait(0.5)

            # Simulate drag motion
            await page.mouse.down()
            await self.wait(0.3)

            # Drag to new position
            new_x = panel_x + 50
            new_y = panel_y + 30
            await page.mouse.move(new_x, new_y, steps=10)
            await self.wait(0.5)

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
