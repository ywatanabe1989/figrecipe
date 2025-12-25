#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DemoRecorder base class for creating demo videos.

Provides a framework for recording browser demos with:
- Video recording via Playwright
- Cursor and click visualization
- Caption overlays
- Audio narration (via TTS)
- GIF conversion
"""

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ._caption import hide_caption, show_caption
from ._click_effect import inject_click_effect, remove_click_effect
from ._cursor import inject_cursor, remove_cursor
from ._highlight import highlight_element
from ._utils import convert_to_gif


class DemoRecorder(ABC):
    """Base class for creating demo recordings.

    Subclass this and implement the `run` method to define
    your demo actions.

    Attributes
    ----------
    title : str
        Demo title (used for captions and filenames).
    duration_target : int
        Target duration in seconds.
    url : str
        URL to navigate to (default: http://127.0.0.1:5050).
    output_dir : Path
        Directory for output files.

    Example
    -------
    ```python
    class ChangeColorDemo(DemoRecorder):
        title = "Change Element Color"
        duration_target = 8

        async def run(self, page):
            await self.caption("Click on bar chart element")
            await page.click('[data-key="bar_0"]')
            await self.wait(1)
            await self.caption("Select red color")
            await page.click('#color-select')
    ```
    """

    title: str = "Demo"
    duration_target: int = 10
    url: str = "http://127.0.0.1:5050"
    output_dir: Path = Path("examples/demo_movie/outputs")

    def __init__(
        self,
        url: Optional[str] = None,
        output_dir: Optional[Path] = None,
        headless: bool = True,
    ):
        """Initialize DemoRecorder.

        Parameters
        ----------
        url : str, optional
            Override default URL.
        output_dir : Path, optional
            Override default output directory.
        headless : bool, optional
            Run browser in headless mode (default: True).
        """
        if url:
            self.url = url
        if output_dir:
            self.output_dir = Path(output_dir)
        self.headless = headless
        self._page = None

    @abstractmethod
    async def run(self, page) -> None:
        """Define demo actions.

        Override this method to define the demo sequence.

        Parameters
        ----------
        page : playwright.async_api.Page
            Playwright page object.
        """
        pass

    async def caption(self, text: str, duration: float = 2.0) -> None:
        """Show caption overlay.

        Parameters
        ----------
        text : str
            Caption text to display.
        duration : float, optional
            Duration to show caption in seconds (default: 2.0).
        """
        if self._page:
            await show_caption(self._page, text)
            if duration > 0:
                await asyncio.sleep(duration)

    async def hide_caption_now(self) -> None:
        """Hide current caption immediately."""
        if self._page:
            await hide_caption(self._page)

    async def highlight(
        self,
        selector: str,
        duration: float = 1.0,
        color: str = "#FF4444",
    ) -> None:
        """Highlight an element.

        Parameters
        ----------
        selector : str
            CSS selector for element.
        duration : float, optional
            Duration to highlight in seconds (default: 1.0).
        color : str, optional
            Highlight color (default: "#FF4444").
        """
        if self._page:
            await highlight_element(self._page, selector, int(duration * 1000), color)

    async def wait(self, seconds: float) -> None:
        """Wait for specified duration.

        Parameters
        ----------
        seconds : float
            Time to wait in seconds.
        """
        await asyncio.sleep(seconds)

    async def speak(self, text: str) -> None:
        """Speak text using TTS (non-blocking).

        Parameters
        ----------
        text : str
            Text to speak.
        """
        # TTS is handled externally via MCP - this is a placeholder
        # In practice, call mcp__scitex-audio__speak from the demo script
        print(f"[TTS] {text}")

    def _get_output_paths(self) -> tuple:
        """Get output file paths.

        Returns
        -------
        tuple
            (mp4_path, gif_path)
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self.title.lower().replace(" ", "_").replace("-", "_")
        mp4_path = self.output_dir / f"{safe_name}.mp4"
        gif_path = self.output_dir / f"{safe_name}.gif"
        return mp4_path, gif_path

    async def _setup_page(self, page) -> None:
        """Setup page with visual effects.

        Parameters
        ----------
        page : playwright.async_api.Page
            Playwright page object.
        """
        self._page = page
        await inject_cursor(page)
        await inject_click_effect(page)

    async def _cleanup_page(self, page) -> None:
        """Cleanup visual effects from page.

        Parameters
        ----------
        page : playwright.async_api.Page
            Playwright page object.
        """
        await remove_cursor(page)
        await remove_click_effect(page)
        await hide_caption(page)
        self._page = None

    async def record(self) -> Path:
        """Record the demo and save video.

        Returns
        -------
        Path
            Path to output MP4 file.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError(
                "Playwright not installed. Install with: pip install playwright && playwright install chromium"
            )

        mp4_path, gif_path = self._get_output_paths()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": 1280, "height": 720},
            )
            page = await context.new_page()

            try:
                # Navigate to URL
                await page.goto(self.url, wait_until="networkidle")
                await asyncio.sleep(1)  # Wait for page to stabilize

                # Setup visual effects
                await self._setup_page(page)

                # Show title
                await self.caption(f"Demo: {self.title}", duration=2.0)

                # Run demo actions
                await self.run(page)

                # Cleanup
                await self._cleanup_page(page)
                await asyncio.sleep(0.5)

            finally:
                await context.close()
                await browser.close()

            # Get recorded video path and rename
            video_path = await page.video.path()
            if video_path and Path(video_path).exists():
                Path(video_path).rename(mp4_path)

        print(f"Recorded: {mp4_path}")
        return mp4_path

    async def record_and_convert(self) -> tuple:
        """Record demo and convert to GIF.

        Returns
        -------
        tuple
            (mp4_path, gif_path)
        """
        mp4_path = await self.record()
        _, gif_path = self._get_output_paths()

        try:
            convert_to_gif(mp4_path, gif_path)
            print(f"Converted: {gif_path}")
        except Exception as e:
            print(f"GIF conversion failed: {e}")
            gif_path = None

        return mp4_path, gif_path

    def execute(self) -> tuple:
        """Execute recording (synchronous wrapper).

        Returns
        -------
        tuple
            (mp4_path, gif_path)
        """
        return asyncio.run(self.record_and_convert())


__all__ = ["DemoRecorder"]

# EOF
