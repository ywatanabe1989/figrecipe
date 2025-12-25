#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for figrecipe.edit() function variants."""

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


class TestEditFunctionVariants:
    """Test the different ways to call figrecipe.edit()."""

    def test_edit_with_recording_figure(self):
        """Test edit(fig) with RecordingFigure."""
        from figrecipe import subplots
        from figrecipe._editor import _resolve_source
        from figrecipe._wrappers import RecordingFigure

        fig, ax = subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        resolved_fig, recipe_path = _resolve_source(fig)

        assert isinstance(resolved_fig, RecordingFigure)
        assert recipe_path is None

    def test_edit_with_none_creates_blank(self):
        """Test edit() or edit(None) creates blank figure."""
        from figrecipe._editor import _resolve_source
        from figrecipe._wrappers import RecordingFigure

        fig, recipe_path = _resolve_source(None)

        assert isinstance(fig, RecordingFigure)
        assert recipe_path is None

        # Check it has placeholder content
        mpl_fig = fig.fig if hasattr(fig, "fig") else fig
        ax = mpl_fig.axes[0]
        assert ax.get_title() == "New Figure"

    def test_edit_with_yaml_path(self, tmp_path):
        """Test edit('/path/to/fig.yaml') loads recipe."""
        from figrecipe._editor import _resolve_source

        # Create a simple YAML recipe
        recipe_content = """
figrecipe: "1.0"
id: test_fig
figure:
  figsize: [8, 6]
  dpi: 100
axes:
  ax_0_0:
    calls:
      - id: plot_000
        function: plot
        args:
          - name: x
            data: [1, 2, 3]
          - name: y
            data: [1, 4, 9]
        kwargs: {}
    decorations: []
"""
        yaml_path = tmp_path / "test_figure.yaml"
        yaml_path.write_text(recipe_content)

        fig, recipe_path = _resolve_source(yaml_path)

        assert fig is not None
        assert recipe_path == yaml_path

    def test_edit_with_png_finds_yaml(self, tmp_path):
        """Test edit('/path/to/fig.png') finds associated YAML."""
        from figrecipe._editor import _resolve_source

        # Create both YAML and PNG
        recipe_content = """
figrecipe: "1.0"
id: test_fig
figure:
  figsize: [8, 6]
  dpi: 100
axes:
  ax_0_0:
    calls: []
    decorations: []
"""
        yaml_path = tmp_path / "test_figure.yaml"
        yaml_path.write_text(recipe_content)

        # Create dummy PNG
        png_path = tmp_path / "test_figure.png"
        png_path.write_bytes(b"PNG")

        # Pass PNG path - should find YAML
        fig, recipe_path = _resolve_source(png_path)

        assert fig is not None
        assert recipe_path == yaml_path

    def test_edit_with_png_no_yaml_raises(self, tmp_path):
        """Test edit('/path/to/fig.png') raises if no YAML found."""
        from figrecipe._editor import _resolve_source

        # Create only PNG (no YAML)
        png_path = tmp_path / "lonely_figure.png"
        png_path.write_bytes(b"PNG")

        with pytest.raises(FileNotFoundError) as exc_info:
            _resolve_source(png_path)

        assert "No recipe found" in str(exc_info.value)

    def test_edit_with_yml_extension(self, tmp_path):
        """Test edit() works with .yml extension."""
        from figrecipe._editor import _resolve_source

        recipe_content = """
figrecipe: "1.0"
id: test_fig
figure:
  figsize: [8, 6]
  dpi: 100
axes:
  ax_0_0:
    calls: []
    decorations: []
"""
        yml_path = tmp_path / "test_figure.yml"
        yml_path.write_text(recipe_content)

        fig, recipe_path = _resolve_source(yml_path)

        assert fig is not None
        assert recipe_path == yml_path

    def test_edit_with_matplotlib_figure(self):
        """Test edit(mpl_fig) wraps raw matplotlib Figure."""
        from figrecipe._editor import _resolve_source
        from figrecipe._wrappers import RecordingFigure

        # Create raw matplotlib figure
        mpl_fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        fig, recipe_path = _resolve_source(mpl_fig)

        # Should be wrapped in RecordingFigure
        assert isinstance(fig, RecordingFigure)
        assert recipe_path is None

    def test_edit_with_nonexistent_path_raises(self):
        """Test edit('/nonexistent/path.yaml') raises FileNotFoundError."""
        from figrecipe._editor import _resolve_source

        with pytest.raises(FileNotFoundError):
            _resolve_source("/nonexistent/path/figure.yaml")

    def test_edit_with_invalid_extension_raises(self, tmp_path):
        """Test edit() with unsupported extension raises ValueError."""
        from figrecipe._editor import _resolve_source

        # Create a file with unsupported extension
        txt_path = tmp_path / "figure.txt"
        txt_path.write_text("not a recipe")

        with pytest.raises(ValueError) as exc_info:
            _resolve_source(txt_path)

        assert "Expected .yaml, .yml, or .png file" in str(exc_info.value)


class TestResolveStyle:
    """Test the _resolve_style function."""

    def test_resolve_style_none_uses_global(self):
        """Test that None returns global style if loaded."""
        from figrecipe._editor import _resolve_style

        # Without global style loaded, should return None
        result = _resolve_style(None)
        # Result depends on whether SCITEX is loaded globally
        # Just check it doesn't raise
        assert result is None or isinstance(result, dict)

    def test_resolve_style_dict_passthrough(self):
        """Test that dict is passed through unchanged."""
        from figrecipe._editor import _resolve_style

        style = {"dpi": 150, "figsize": (10, 8)}
        result = _resolve_style(style)

        assert result == style

    def test_resolve_style_string_loads_preset(self):
        """Test that string loads preset style."""
        from figrecipe._editor import _resolve_style

        # SCITEX should always exist
        result = _resolve_style("SCITEX")

        assert isinstance(result, dict)

    def test_resolve_style_invalid_type_raises(self):
        """Test that invalid type raises TypeError."""
        from figrecipe._editor import _resolve_style

        with pytest.raises(TypeError):
            _resolve_style(123)


class TestFileSwitcherEndpoints:
    """Test file switcher API endpoints."""

    def test_api_files_endpoint_exists(self):
        """Test that /api/files route is registered."""
        from figrecipe._editor._routes_core import register_core_routes

        routes = []
        mock_app = MagicMock()

        def capture_route(rule, **kwargs):
            def decorator(func):
                routes.append(rule)
                return func

            return decorator

        mock_app.route = capture_route

        mock_editor = MagicMock()
        mock_editor.fig = MagicMock()
        mock_editor._color_map = {}

        register_core_routes(mock_app, mock_editor)

        assert "/api/files" in routes

    def test_api_switch_endpoint_exists(self):
        """Test that /api/switch route is registered."""
        from figrecipe._editor._routes_core import register_core_routes

        routes = []
        mock_app = MagicMock()

        def capture_route(rule, **kwargs):
            def decorator(func):
                routes.append(rule)
                return func

            return decorator

        mock_app.route = capture_route

        mock_editor = MagicMock()
        mock_editor.fig = MagicMock()
        mock_editor._color_map = {}

        register_core_routes(mock_app, mock_editor)

        assert "/api/switch" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
