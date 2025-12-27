#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the file browser panel feature."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


class TestFileBrowserHTML:
    """Test file browser panel HTML structure."""

    def test_html_has_file_browser_panel(self):
        """Test that HTML template includes file browser panel."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="test",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
        )

        assert 'id="file-browser-panel"' in html
        assert 'class="file-browser-panel"' in html

    def test_html_has_file_tree_container(self):
        """Test that HTML template includes file tree container."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="test",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
        )

        assert 'id="file-tree-container"' in html
        assert 'id="file-tree"' in html

    def test_html_has_file_browser_actions(self):
        """Test that HTML template includes file browser action buttons."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="test",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
        )

        assert 'id="btn-new-file"' in html
        assert 'id="btn-refresh-files"' in html
        assert 'id="btn-collapse-browser"' in html


class TestFileBrowserCSS:
    """Test file browser panel CSS styles."""

    def test_file_browser_styles_exist(self):
        """Test that file browser CSS styles are defined."""
        from figrecipe._editor._templates._styles import STYLES_FILE_BROWSER

        assert ".file-browser-panel" in STYLES_FILE_BROWSER
        assert ".file-tree-container" in STYLES_FILE_BROWSER
        assert ".file-tree-entry" in STYLES_FILE_BROWSER

    def test_file_browser_collapsed_style(self):
        """Test that collapsed state style is defined."""
        from figrecipe._editor._templates._styles import STYLES_FILE_BROWSER

        assert ".file-browser-panel.collapsed" in STYLES_FILE_BROWSER

    def test_file_browser_styles_in_combined(self):
        """Test that file browser styles are included in combined STYLES."""
        from figrecipe._editor._templates._styles import STYLES

        assert ".file-browser-panel" in STYLES


class TestFileBrowserJavaScript:
    """Test file browser JavaScript functionality."""

    def test_load_file_list_function_exists(self):
        """Test that loadFileList function is defined."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "async function loadFileList()" in SCRIPTS_FILES

    def test_load_file_list_uses_file_tree(self):
        """Test that loadFileList populates file tree."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "getElementById('file-tree')" in SCRIPTS_FILES
        assert "file-tree-entry" in SCRIPTS_FILES
        assert "file-tree-item" in SCRIPTS_FILES

    def test_toggle_file_browser_function(self):
        """Test that toggleFileBrowser function is defined."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "function toggleFileBrowser()" in SCRIPTS_FILES
        assert "file-browser-panel" in SCRIPTS_FILES
        assert "fileBrowserCollapsed" in SCRIPTS_FILES

    def test_init_file_browser_function(self):
        """Test that initFileBrowser function is defined."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "function initFileBrowser()" in SCRIPTS_FILES
        assert "getElementById('btn-new-file')" in SCRIPTS_FILES
        assert "getElementById('btn-refresh-files')" in SCRIPTS_FILES
        assert "getElementById('btn-collapse-browser')" in SCRIPTS_FILES

    def test_file_tree_click_handler(self):
        """Test that file tree entries have click handlers."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "addEventListener('click'" in SCRIPTS_FILES
        assert "switchToFile(path)" in SCRIPTS_FILES

    def test_file_tree_shows_png_badge(self):
        """Test that files with PNG show badge."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "has_image" in SCRIPTS_FILES
        assert "file-tree-badge" in SCRIPTS_FILES
        assert "PNG" in SCRIPTS_FILES


class TestFileBrowserAPI:
    """Test file browser API routes."""

    def test_api_files_route_registered(self):
        """Test that /api/files route is registered."""
        from figrecipe._editor._routes_core import register_core_routes

        routes = []
        mock_app = MagicMock()

        def capture_route(rule, **kwargs):
            def decorator(func):
                routes.append((rule, kwargs.get("methods", ["GET"]), func.__name__))
                return func

            return decorator

        mock_app.route = capture_route

        mock_editor = MagicMock()
        mock_editor.fig = MagicMock()
        mock_editor._color_map = {}
        mock_editor.dark_mode = False
        mock_editor._hitmap_generated = False

        register_core_routes(mock_app, mock_editor)

        files_routes = [r for r in routes if r[0] == "/api/files"]
        assert len(files_routes) == 1, "Expected /api/files route"

    def test_api_switch_route_registered(self):
        """Test that /api/switch route is registered."""
        from figrecipe._editor._routes_core import register_core_routes

        routes = []
        mock_app = MagicMock()

        def capture_route(rule, **kwargs):
            def decorator(func):
                routes.append((rule, kwargs.get("methods", ["GET"]), func.__name__))
                return func

            return decorator

        mock_app.route = capture_route

        mock_editor = MagicMock()
        mock_editor.fig = MagicMock()
        mock_editor._color_map = {}
        mock_editor.dark_mode = False
        mock_editor._hitmap_generated = False

        register_core_routes(mock_app, mock_editor)

        switch_routes = [r for r in routes if r[0] == "/api/switch"]
        assert len(switch_routes) == 1, "Expected /api/switch route"
        assert "POST" in switch_routes[0][1], "Expected POST method"


class TestFileBrowserIntegration:
    """Test file browser integration with editor."""

    def test_file_browser_in_template_output(self):
        """Test that file browser appears before preview panel."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="test",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
        )

        file_browser_pos = html.find('id="file-browser-panel"')
        preview_panel_pos = html.find('class="preview-panel"')

        assert file_browser_pos > 0, "File browser panel not found"
        assert preview_panel_pos > 0, "Preview panel not found"
        assert (
            file_browser_pos < preview_panel_pos
        ), "File browser should be before preview"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
