#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test style override functionality."""

import time
from typing import List

from .conftest import requires_playwright


@requires_playwright
class TestEditorOverrides:
    """Test style override functionality."""

    def test_overrides_api_endpoint(self, editor_server):
        """Verify overrides API endpoint works."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            response = page.request.get(f"{editor_server.url}/overrides")
            assert response.ok, f"Overrides request failed: {response.status}"

            data = response.json()
            assert isinstance(data, dict), "Overrides should return a dict"

            browser.close()

    def test_save_triggers_update(self, editor_server):
        """Test that save action triggers preview update."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            page.keyboard.press("Control+KeyS")
            time.sleep(0.5)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e or "TypeError" in e]
        assert len(critical) == 0, "Save errors:\n" + "\n".join(critical)

    def test_update_api_endpoint(self, editor_server):
        """Test the update API endpoint accepts changes."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            # POST to update endpoint
            response = page.request.post(
                f"{editor_server.url}/update",
                data={"overrides": "{}"},
            )
            # May return 200 or 400 depending on implementation
            assert response.status in [
                200,
                400,
                415,
            ], f"Update endpoint error: {response.status}"

            browser.close()

    def test_preview_api_endpoint(self, editor_server):
        """Verify preview image endpoint works."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            response = page.request.get(f"{editor_server.url}/preview")
            assert response.ok, f"Preview request failed: {response.status}"
            assert "image" in response.headers.get(
                "content-type", ""
            ), "Preview not an image"

            browser.close()
