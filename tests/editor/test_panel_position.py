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
        """Test that positions are returned for all 4 axes plus figsize."""
        response = editor_app.get("/get_axes_positions")
        assert response.status_code == 200

        data = json.loads(response.data)
        # 2x2 grid = 4 axes + 1 _figsize metadata
        assert len(data) == 5
        assert "_figsize" in data
        for i in range(4):
            assert f"ax_{i}" in data

    def test_position_values_are_in_mm(self, editor_app):
        """Test that position values are in mm (upper-left origin)."""
        response = editor_app.get("/get_axes_positions")
        data = json.loads(response.data)

        # Get figure dimensions
        figsize = data["_figsize"]
        fig_width_mm = figsize["width_mm"]
        fig_height_mm = figsize["height_mm"]

        for ax_key, pos in data.items():
            if ax_key == "_figsize":
                continue
            # Positions should be positive and within figure bounds
            assert 0 <= pos["left"] <= fig_width_mm
            assert 0 <= pos["top"] <= fig_height_mm
            assert pos["width"] > 0
            assert pos["height"] > 0
            assert pos["left"] + pos["width"] <= fig_width_mm + 0.1  # Small tolerance
            assert pos["top"] + pos["height"] <= fig_height_mm + 0.1

    def test_position_has_all_fields(self, editor_app):
        """Test that position data has all required fields (mm, upper-left origin)."""
        response = editor_app.get("/get_axes_positions")
        data = json.loads(response.data)

        for ax_key, pos in data.items():
            if ax_key == "_figsize":
                assert "width_mm" in pos
                assert "height_mm" in pos
            else:
                assert "index" in pos
                assert "left" in pos
                assert "top" in pos
                assert "width" in pos
                assert "height" in pos


class TestUpdateAxesPosition:
    """Tests for /update_axes_position route (mm coordinates, upper-left origin)."""

    def test_update_position_succeeds(self, editor_app):
        """Test that updating position succeeds with mm coordinates."""
        # Use mm values with upper-left origin
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": 20.0,  # mm from left
                    "top": 20.0,  # mm from top
                    "width": 50.0,  # mm width
                    "height": 40.0,  # mm height
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
        """Test that out-of-range mm values are rejected."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": -10.0,  # Invalid - negative
                    "top": 20.0,
                    "width": 50.0,
                    "height": 40.0,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_update_requires_all_values(self, editor_app):
        """Test that missing values are rejected."""
        response = editor_app.post(
            "/update_axes_position",
            data=json.dumps(
                {
                    "ax_index": 0,
                    "left": 20.0,
                    # Missing top, width, height
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
                    "ax_index": 99,  # Invalid - only 4 axes exist
                    "left": 20.0,
                    "top": 20.0,
                    "width": 50.0,
                    "height": 40.0,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
