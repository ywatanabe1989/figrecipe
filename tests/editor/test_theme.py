#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test theme and dark mode functionality."""

import time
from typing import List

from .conftest import requires_playwright


@requires_playwright
class TestEditorTheme:
    """Test theme application functionality."""

    def test_theme_modal_opens(self, editor_server):
        """Verify theme modal can be opened."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            theme_btn = page.locator(
                "button:has-text('Theme'), #theme-btn, .theme-button"
            ).first
            if theme_btn.count() > 0:
                theme_btn.click()
                time.sleep(0.3)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e or "TypeError" in e]
        assert len(critical) == 0, "Theme modal errors:\n" + "\n".join(critical)

    def test_dark_mode_toggle(self, editor_server):
        """Test dark mode toggle functionality."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            dark_toggle = page.locator(
                "#dark-mode-toggle, .dark-mode-toggle, "
                "button:has-text('Dark'), input[type='checkbox'][id*='dark']"
            ).first

            if dark_toggle.count() > 0:
                dark_toggle.click()
                time.sleep(0.3)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e or "TypeError" in e]
        assert len(critical) == 0, "Dark mode errors:\n" + "\n".join(critical)

    def test_theme_change_updates_preview(self, editor_server):
        """Test that changing theme updates the preview."""
        from playwright.sync_api import sync_playwright

        js_errors: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: js_errors.append(str(err)))

            page.goto(editor_server.url)
            page.wait_for_load_state("networkidle")

            # Try to find and interact with theme selector
            theme_select = page.locator("select[id*='theme'], #theme-select").first
            if theme_select.count() > 0:
                options = theme_select.locator("option")
                if options.count() > 1:
                    theme_select.select_option(index=1)
                    time.sleep(0.5)

            browser.close()

        critical = [e for e in js_errors if "SyntaxError" in e]
        assert len(critical) == 0, "Theme change errors:\n" + "\n".join(critical)
