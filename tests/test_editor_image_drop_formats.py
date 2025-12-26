#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for different image formats in drag-and-drop functionality."""

import base64
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestImageFormats:
    """Test handling of different image formats."""

    @pytest.fixture
    def app_client(self):
        """Create Flask test client."""
        from flask import Flask

        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import register_image_routes

        fig, ax = fr.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        editor = FigureEditor(fig, port=5993)
        app = Flask(__name__)
        register_image_routes(app, editor)
        app.config["TESTING"] = True

        return app.test_client(), editor

    def test_jpeg_image(self, app_client):
        """Test adding a JPEG image."""
        client, editor = app_client

        img = Image.new("RGB", (40, 40), color="yellow")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "test.jpg",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_rgba_image_with_transparency(self, app_client):
        """Test adding an RGBA image with transparency."""
        client, editor = app_client

        img = Image.new("RGBA", (40, 40), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "transparent.png",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_gif_image(self, app_client):
        """Test adding a GIF image."""
        client, editor = app_client

        img = Image.new("P", (30, 30), color=1)
        buffer = io.BytesIO()
        img.save(buffer, format="GIF")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "test.gif",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_grayscale_image(self, app_client):
        """Test adding a grayscale image."""
        client, editor = app_client

        img = Image.new("L", (35, 35), color=128)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "grayscale.png",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True


class TestHitmapRegeneration:
    """Test hitmap regeneration after image drop."""

    @pytest.fixture
    def app_client(self):
        """Create Flask test client."""
        from flask import Flask

        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import register_image_routes

        fig, ax = fr.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        editor = FigureEditor(fig, port=5992)
        app = Flask(__name__)
        register_image_routes(app, editor)
        app.config["TESTING"] = True

        return app.test_client(), editor

    def test_hitmap_regenerated_after_drop(self, app_client):
        """Verify hitmap is regenerated after dropping an image."""
        client, editor = app_client

        # Initial state
        editor._hitmap_generated = False

        img = Image.new("RGB", (25, 25), color="purple")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "hitmap_test.png",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        # After successful drop, hitmap should be regenerated
        assert editor._hitmap_generated is True

    def test_color_map_updated_after_drop(self, app_client):
        """Verify color map is updated after dropping an image."""
        client, editor = app_client

        img = Image.new("RGB", (25, 25), color="cyan")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "colormap_test.png",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        # Color map should exist and have entries
        assert hasattr(editor, "_color_map")
        assert editor._color_map is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
