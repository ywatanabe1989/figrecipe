#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: Toggle Dark Mode

Shows how to enable dark mode in the figrecipe editor.
This is shown first as users may be surprised by the bright interface.

Duration target: ~8 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class DarkModeDemo(DemoRecorder):
    """Demo showing how to toggle dark mode in the editor."""

    title = "Enable Dark Mode"
    duration_target = 8
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Wait for page to fully load
        await self.wait(1.0)

        # Show caption
        await self.caption("Toggle Dark Mode for comfortable viewing")
        await self.wait(1.0)

        # Find and move to dark mode toggle
        dark_toggle = page.locator("#dark-mode-toggle")
        await self.move_to(dark_toggle, duration=0.6)
        await self.wait(0.3)

        # Click to enable dark mode
        await dark_toggle.click(timeout=5000)
        await self.wait(1.5)

        # Show result
        await self.caption("Dark mode enabled!")
        await self.wait(2.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record dark mode demo")
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

    demo = DarkModeDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
