#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

    title = "Change Element Color"
    duration_target = 10
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Wait for page to fully load
        await self.wait(1.0)

        # Step 1: Click on bar chart element
        await self.caption("Click on a bar chart element")
        await self.wait(1.0)

        # Move cursor naturally (trajectory) to bar element, then click
        bar_locator = page.locator("g").filter(has_text="bar: bar").first
        await self.move_to(bar_locator, duration=0.6)
        await self.wait(0.3)
        await bar_locator.click(timeout=5000)
        await self.wait(1.0)

        # Step 2: Find and click color dropdown
        await self.caption("Select red color from dropdown")
        await self.wait(1.0)

        # Move cursor to dropdown (trajectory animation), then select
        color_dropdown = page.get_by_role("combobox").nth(2)
        await self.move_to(color_dropdown, duration=0.5)
        await self.wait(0.3)
        await color_dropdown.select_option("red", timeout=5000)
        await self.wait(1.5)

        # Final caption
        await self.caption("Color changed to red!")
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
