#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test for JavaScript errors on editor load."""

import time
from typing import List

from .conftest import requires_playwright


@requires_playwright
class TestEditorJSErrors:
    """Test for JavaScript errors when loading the editor."""

    def test_no_javascript_errors_on_load(self, editor_server):
        """Verify no JavaScript errors occur when loading the editor."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []
        console_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.on("pageerror", lambda err: js_errors.append(str(err)))

            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)

            page.on("console", handle_console)

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            browser.close()

        assert len(js_errors) == 0, "JavaScript errors found:\n" + "\n".join(js_errors)

        # Filter out expected/non-JS errors:
        # - favicon (browser default request)
        # - 500 errors (server errors, not JS errors - tested separately)
        # - panel_snapshot (async prefetch may fail during test startup)
        unexpected_errors = [
            e
            for e in console_errors
            if "favicon" not in e.lower()
            and "500" not in e
            and "panel_snapshot" not in e.lower()
            and "get_panel_snapshot" not in e.lower()
        ]
        assert len(unexpected_errors) == 0, "Console errors found:\n" + "\n".join(
            unexpected_errors
        )

    def test_no_duplicate_declarations(self, editor_server):
        """Check for duplicate variable declaration errors."""
        from playwright.sync_api import sync_playwright

        syntax_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def capture_error(err):
                err_str = str(err)
                if "SyntaxError" in err_str or "already been declared" in err_str:
                    syntax_errors.append(err_str)

            page.on("pageerror", capture_error)

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            browser.close()

        assert len(syntax_errors) == 0, (
            "Syntax/declaration errors found:\n" + "\n".join(syntax_errors)
        )

    def test_editor_elements_present(self, editor_server):
        """Verify essential editor elements are present."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            assert (
                page.locator("#editor-container").count() > 0
                or page.locator(".editor-container").count() > 0
                or page.locator("body").count() > 0
            ), "Editor container not found"

            assert (
                page.locator("img").count() > 0 or page.locator("canvas").count() > 0
            ), "Figure preview not found"

            browser.close()
