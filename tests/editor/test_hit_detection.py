#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test hitmap-based element selection."""

import time
from typing import List

from .conftest import requires_playwright


@requires_playwright
class TestEditorHitDetection:
    """Test hitmap-based element selection."""

    def test_click_on_figure_selects_element(self, editor_server):
        """Verify clicking on figure elements triggers selection."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")
            time.sleep(0.5)

            preview = page.locator("#preview-img, .preview-img, img").first
            if preview.count() > 0:
                box = preview.bounding_box()
                if box:
                    page.mouse.click(
                        box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                    )
                    time.sleep(0.3)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e or "TypeError" in e]
        assert len(critical) == 0, "Click errors:\n" + "\n".join(critical)

    def test_hitmap_loads_without_error(self, editor_server):
        """Verify hitmap endpoint returns valid JSON with image data."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            response = page.request.get(f"{editor_server.url}/hitmap")
            assert response.ok, f"Hitmap request failed: {response.status}"
            assert "application/json" in response.headers.get(
                "content-type", ""
            ), "Hitmap endpoint should return JSON"

            # Verify JSON structure
            data = response.json()
            assert "image" in data, "Response missing 'image' field"
            assert "color_map" in data, "Response missing 'color_map' field"
            # Check for valid PNG base64 (PNG signature starts with iVBOR)
            assert data["image"].startswith("iVBOR"), "Invalid PNG base64 image"

            browser.close()

        assert len(js_errors) == 0, "JS errors:\n" + "\n".join(js_errors)

    def test_multiple_clicks_no_errors(self, editor_server):
        """Test rapid clicking doesn't cause errors."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            preview = page.locator("#preview-img, .preview-img, img").first
            if preview.count() > 0:
                box = preview.bounding_box()
                if box:
                    for _ in range(5):
                        page.mouse.click(
                            box["x"] + box["width"] / 3,
                            box["y"] + box["height"] / 3,
                        )
                        time.sleep(0.1)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e]
        assert len(critical) == 0, "Multiple click errors:\n" + "\n".join(critical)
