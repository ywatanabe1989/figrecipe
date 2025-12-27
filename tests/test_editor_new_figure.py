#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for creating new figures via the /api/new endpoint."""

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


class TestNewFigureAPI:
    """Test the /api/new endpoint for creating new blank figures."""

    def test_routes_core_has_new_endpoint(self):
        """Test that _routes_core contains /api/new route registration."""
        from figrecipe._editor._routes_core import register_core_routes

        # Create mock app to capture routes
        routes = []
        mock_app = MagicMock()

        def capture_route(rule, **kwargs):
            def decorator(func):
                routes.append((rule, kwargs.get("methods", ["GET"]), func.__name__))
                return func

            return decorator

        mock_app.route = capture_route

        # Create mock editor
        mock_editor = MagicMock()
        mock_editor.fig = MagicMock()
        mock_editor._color_map = {}
        mock_editor.dark_mode = False
        mock_editor._hitmap_generated = False

        # Register routes
        register_core_routes(mock_app, mock_editor)

        # Find /api/new route
        new_routes = [r for r in routes if r[0] == "/api/new"]
        assert len(new_routes) == 1, "Expected /api/new route to be registered"
        assert "POST" in new_routes[0][1], "Expected /api/new to accept POST method"
        assert (
            new_routes[0][2] == "new_figure"
        ), "Expected handler name to be 'new_figure'"

    def test_create_new_figure_function_exists(self):
        """Test that createNewFigure JavaScript function is defined."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "async function createNewFigure()" in SCRIPTS_FILES
        assert "fetch('/api/new'" in SCRIPTS_FILES
        assert "method: 'POST'" in SCRIPTS_FILES

    def test_new_button_calls_create_function(self):
        """Test that + button click handler calls createNewFigure."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        assert "newBtn.addEventListener('click', createNewFigure)" in SCRIPTS_FILES

    def test_keyboard_shortcut_ctrl_n(self):
        """Test that Ctrl+N keyboard shortcut is defined."""
        from figrecipe._editor._templates._scripts._core import SCRIPTS_CORE

        assert "event.ctrlKey && event.key === 'n'" in SCRIPTS_CORE
        assert "createNewFigure()" in SCRIPTS_CORE

    def test_new_figure_updates_ui(self):
        """Test that createNewFigure updates UI elements."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        # Check that the function updates preview image
        assert "img.src = 'data:image/png;base64,' + data.image" in SCRIPTS_FILES

        # Check that it updates bboxes
        assert "window.currentBboxes = data.bboxes" in SCRIPTS_FILES

        # Check that it shows success toast with filename
        assert "Created:" in SCRIPTS_FILES
        assert ".yaml" in SCRIPTS_FILES

        # Check that it reloads file list
        assert "loadFileList()" in SCRIPTS_FILES


class TestResolveSourceNone:
    """Test that _resolve_source handles None input correctly."""

    def test_resolve_source_none_creates_blank_figure(self):
        """Test that passing None to _resolve_source creates a blank figure."""
        from figrecipe._editor import _resolve_source

        fig, recipe_path = _resolve_source(None)

        assert fig is not None
        assert recipe_path is None

        # Check it's a RecordingFigure
        from figrecipe._wrappers import RecordingFigure

        assert isinstance(fig, RecordingFigure)

        # Check it has a title
        ax = fig.fig.axes[0] if hasattr(fig, "fig") else fig.axes[0]
        assert ax.get_title() == "New Figure"


class TestFileSwitcherUI:
    """Test file switcher UI elements."""

    def test_html_has_new_button(self):
        """Test that HTML template includes the + button in file browser panel."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="test",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
        )

        # New button is now in file browser panel
        assert 'id="btn-new-file"' in html
        assert 'class="btn-new-file"' in html
        assert "+" in html  # The button text

    def test_html_has_file_browser(self):
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

        # File browser panel with file tree
        assert 'id="file-browser-panel"' in html
        assert 'id="file-tree"' in html


class TestFileSwitcherClearSelection:
    """Test that file switcher uses correct clearSelection function."""

    def test_uses_clear_selection_not_clear_element_highlights(self):
        """Test that code uses clearSelection instead of clearElementHighlights."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        # Should use clearSelection (the correct function name)
        assert "clearSelection()" in SCRIPTS_FILES

        # Should NOT use clearElementHighlights (non-existent function)
        assert "clearElementHighlights()" not in SCRIPTS_FILES

    def test_create_new_figure_clears_selection(self):
        """Test that createNewFigure calls clearSelection."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        # Check that clearSelection is called (with typeof check for safety)
        assert "typeof clearSelection === 'function'" in SCRIPTS_FILES

    def test_switch_to_file_clears_selection(self):
        """Test that switchToFile calls clearSelection."""
        from figrecipe._editor._templates._scripts._files import SCRIPTS_FILES

        # The function should have clearSelection call in switchToFile
        # Check that it's called after "Update current file path"
        assert "// Clear selection" in SCRIPTS_FILES
        assert "clearSelection();" in SCRIPTS_FILES


class TestDebugSnapshot:
    """Test debug snapshot functionality."""

    def test_capture_screenshot_no_dialog(self):
        """Test that captureScreenshot doesn't call getDisplayMedia (no dialog)."""
        from figrecipe._editor._templates._scripts._debug_snapshot import (
            SCRIPTS_DEBUG_SNAPSHOT,
        )

        # Should NOT call getDisplayMedia as it shows a dialog
        # It's OK to mention it in comments, but not call it
        assert (
            "await navigator.mediaDevices.getDisplayMedia" not in SCRIPTS_DEBUG_SNAPSHOT
        )
        assert ".getDisplayMedia(" not in SCRIPTS_DEBUG_SNAPSHOT

    def test_capture_screenshot_uses_html2canvas_for_full_page(self):
        """Test that captureScreenshot uses html2canvas for full page capture."""
        from figrecipe._editor._templates._scripts._debug_snapshot import (
            SCRIPTS_DEBUG_SNAPSHOT,
        )

        # Should use html2canvas for full page capture
        assert "html2canvas" in SCRIPTS_DEBUG_SNAPSHOT
        assert "document.body" in SCRIPTS_DEBUG_SNAPSHOT
        assert "full page" in SCRIPTS_DEBUG_SNAPSHOT.lower()

    def test_capture_screenshot_has_figure_fallback(self):
        """Test that captureScreenshot falls back to figure image if html2canvas fails."""
        from figrecipe._editor._templates._scripts._debug_snapshot import (
            SCRIPTS_DEBUG_SNAPSHOT,
        )

        # Should have fallback to figure image
        assert "preview-image" in SCRIPTS_DEBUG_SNAPSHOT
        assert "figure image" in SCRIPTS_DEBUG_SNAPSHOT.lower()

    def test_capture_debug_snapshot_defined(self):
        """Test that captureDebugSnapshot function is defined."""
        from figrecipe._editor._templates._scripts._debug_snapshot import (
            SCRIPTS_DEBUG_SNAPSHOT,
        )

        assert "async function captureDebugSnapshot()" in SCRIPTS_DEBUG_SNAPSHOT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
