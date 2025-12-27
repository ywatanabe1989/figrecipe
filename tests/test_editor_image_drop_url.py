#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for URL-based image adding and filename handling."""

import base64
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestAddImageFromUrl:
    """Test URL-based image adding route."""

    @pytest.fixture
    def app_client(self):
        """Create Flask test client."""
        from flask import Flask

        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import register_image_routes

        fig, ax = fr.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        editor = FigureEditor(fig, port=5991)
        app = Flask(__name__)
        register_image_routes(app, editor)
        app.config["TESTING"] = True

        return app.test_client(), editor

    def test_missing_url(self, app_client):
        """Test error handling when URL is missing."""
        client, editor = app_client

        response = client.post(
            "/add_image_from_url",
            json={"drop_x": 0.5, "drop_y": 0.5},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Missing url" in data["error"]

    def test_invalid_url(self, app_client):
        """Test error handling for invalid URL."""
        client, editor = app_client

        response = client.post(
            "/add_image_from_url",
            json={
                "url": "not-a-valid-url",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        # Should fail with 500 (network error)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data


class TestFilenameHandling:
    """Test filename handling in image drop."""

    @pytest.fixture
    def app_client(self):
        """Create Flask test client."""
        from flask import Flask

        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._routes_image import register_image_routes

        fig, ax = fr.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])

        editor = FigureEditor(fig, port=5990)
        app = Flask(__name__)
        register_image_routes(app, editor)
        app.config["TESTING"] = True

        return app.test_client(), editor

    def test_long_filename_truncated(self, app_client):
        """Test that long filenames are handled properly."""
        client, editor = app_client

        img = Image.new("RGB", (20, 20), color="orange")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        long_filename = "a" * 100 + ".png"
        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": long_filename,
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_default_filename(self, app_client):
        """Test default filename when not provided."""
        client, editor = app_client

        img = Image.new("RGB", (20, 20), color="pink")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                # No filename provided
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True

    def test_special_characters_in_filename(self, app_client):
        """Test handling of special characters in filename."""
        client, editor = app_client

        img = Image.new("RGB", (20, 20), color="brown")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.post(
            "/add_image_panel",
            json={
                "image_data": img_base64,
                "filename": "test (1) [2] {3}.png",
                "drop_x": 0.5,
                "drop_y": 0.5,
            },
        )

        assert response.status_code == 200
        assert response.get_json()["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
