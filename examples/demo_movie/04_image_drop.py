#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: Image Drop

Shows how to drag external images onto the canvas to add as panels.

Duration target: ~12 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class ImageDropDemo(DemoRecorder):
    """Demo showing image drop functionality."""

    title = "Image Drop Support"
    demo_id = "04"
    duration_target = 12
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Show intro
        await self.caption("Drag & Drop external images onto the canvas")
        await self.wait(1.5)

        # Point to canvas area
        preview = page.locator("#preview-image")
        await self.move_to(preview, duration=0.6)
        await self.wait(0.5)

        # Explain the feature
        await self.caption("PNG, JPG, GIF images become imshow panels")
        await self.wait(2.0)

        # Show where panels appear
        await self.caption("Images are added as new draggable panels")
        await self.wait(2.0)

        # Explain YAML recipes
        await self.caption("Drop YAML recipes to switch figures")
        await self.wait(2.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record image drop demo")
    parser.add_argument("--url", default="http://127.0.0.1:5050", help="Editor URL")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    demo = ImageDropDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
