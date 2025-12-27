#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo: Datatable Import and Plot Creation

Shows how to import CSV data and create plots from the datatable panel.

Duration target: ~15 seconds
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import DemoRecorder


class DatatableDemo(DemoRecorder):
    """Demo showing datatable import and plot creation."""

    title = "Data Import and Plot Creation"
    demo_id = "03"
    duration_target = 15
    url = "http://127.0.0.1:5050"

    async def run(self, page):
        """Execute demo actions."""
        # Show intro caption
        await self.caption("Open Datatable Panel to import data")
        await self.wait(1.0)

        # Click datatable toggle button
        datatable_toggle = page.locator("#datatable-toggle")
        await self.move_to(datatable_toggle, duration=0.5)
        await datatable_toggle.click()
        await self.wait(1.0)

        # Show dropzone
        await self.caption("Drop CSV/TSV/JSON files to import data")
        await self.wait(1.5)

        # Point to dropzone area
        dropzone = page.locator("#datatable-dropzone")
        await self.move_to(dropzone, duration=0.5)
        await self.wait(1.0)

        # Show plot type selector
        await self.caption("Select plot type and assign columns")
        plot_select = page.locator("#datatable-plot-type")
        await self.move_to(plot_select, duration=0.5)
        await self.wait(1.0)

        # Point to plot button
        await self.caption("Click 'New' to create a new panel")
        plot_btn = page.locator("#btn-datatable-plot")
        await self.move_to(plot_btn, duration=0.5)
        await self.wait(1.5)

        # Close panel
        close_btn = page.locator("#btn-close-datatable")
        await close_btn.click()
        await self.wait(0.5)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record datatable demo")
    parser.add_argument("--url", default="http://127.0.0.1:5050", help="Editor URL")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    demo = DatatableDemo(url=args.url, headless=args.headless)
    mp4_path, gif_path = demo.execute()

    print("\nOutput files:")
    if gif_path:
        print(f"  GIF: {gif_path}")

# EOF
