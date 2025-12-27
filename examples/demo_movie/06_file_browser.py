#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: File Browser

Shows how to use the file browser panel to manage recipe files.

Duration target: ~12 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class FileBrowserDemo(DemoRecorder):
    """Demo showing file browser functionality."""

    title = "Recipe File Management"
    demo_id = "06"
    duration_target = 12
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Show intro
        await self.caption("File Browser: Manage your recipe files")
        await self.wait(1.5)

        # Look for file browser panel (correct class name)
        file_browser = page.locator(".file-browser-panel")
        await self.move_to(file_browser, duration=0.5)
        await self.wait(0.5)

        # Explain features
        await self.caption("Browse, create, rename, and delete recipes")
        await self.wait(2.0)

        # Show file list area
        await self.caption("Click any recipe to load it into the editor")
        await self.wait(2.0)

        # Explain save
        await self.caption("Changes are saved automatically to YAML")
        await self.wait(2.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record file browser demo")
    parser.add_argument("--url", default="http://127.0.0.1:5050", help="Editor URL")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    demo = FileBrowserDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
