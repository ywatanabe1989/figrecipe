#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for panel position editing feature."""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def editor_app():
    """Create a test Flask app with editor routes."""
    import figrecipe as fr
    from figrecipe._editor._flask_app import FigureEditor
    from figrecipe._editor._routes_axis import register_axis_routes
    from figrecipe._editor._routes_core import register_core_routes
    from figrecipe._editor._routes_element import register_element_routes
    from figrecipe._editor._routes_style import register_style_routes

    # Create a test figure with 2x2 grid
    fig, axes = fr.subplots(2, 2)
    for i, ax in enumerate(axes.flat):
        ax.plot([1, 2, 3], [i, i + 1, i + 2])

    # Create editor instance
    editor = FigureEditor(fig)

    # Create Flask app and register routes
    app = Flask(__name__)
    register_core_routes(app, editor)
    register_style_routes(app, editor)
    register_axis_routes(app, editor)
    register_element_routes(app, editor)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    plt.close("all")


class TestGetAxesPositions:
    """Tests for /get_axes_positions route."""

    def test_returns_positions_for_all_axes(self, editor_app):
        """Test that positions are returned for all 4 axes."""
        response = editor_app.get("/get_axes_positions")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 4  # 2x2 grid

    def test_position_values_are_valid(self, editor_app):
        """Test that position values are in valid range."""
        response = editor_app.get("/get_axes_positions")
        data = json.loads(response.data)

        for ax_key, pos in data.items():
            assert 0 <= pos["left"] <= 1
            assert 0 <= pos["bottom"] <= 1
            assert 0 <= pos["width"] <= 1
            assert 0 <= pos["height"] <= 1
            assert pos["right"] == pytest.approx(pos["left"] + pos["width"], rel=0.01)
            assert pos["top"] == pytest.approx(pos["bottom"] + pos["height"], rel=0.01)

    def test_position_has_all_fields(self, editor_app):
        """Test that position data has all required fields."""
        response = editor_app.get("/get_axes_positions")
        data = json.loads(response.data)

        for ax_key, pos in data.items():
            assert "index" in pos
            assert "left" in pos
            assert "bottom" in pos
            assert "width" in pos
            assert "height" in pos
            assert "right" in pos
            assert "top" in pos


class TestUpdateAxesPosition:
    """Tests for /update_axes_position route."""

    def test_update_position_succeeds(self, editor_app):
        """Test that updating position succeeds."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": 0.1,
                    "bottom": 0.1,
                    "width": 0.4,
                    "height": 0.4,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "image" in data
        assert "bboxes" in data

    def test_update_validates_range(self, editor_app):
        """Test that out-of-range values are rejected."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": 1.5,  # Invalid
                    "bottom": 0.1,
                    "width": 0.4,
                    "height": 0.4,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data
        assert "left" in data["error"]

    def test_update_requires_all_values(self, editor_app):
        """Test that missing values are rejected."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": 0.1,
                    # Missing bottom, width, height
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_update_validates_ax_index(self, editor_app):
        """Test that invalid ax_index is rejected."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 99,  # Invalid
                    "left": 0.1,
                    "bottom": 0.1,
                    "width": 0.4,
                    "height": 0.4,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
