#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the restore endpoint error handling.

These tests verify:
- Restore endpoint returns valid JSON
- Restore endpoint handles matplotlib/tkinter threading gracefully
"""

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from .conftest import requires_playwright


class TestRestoreEndpointUnit:
    """Unit tests for restore route code."""

    def test_restore_route_code_has_exception_handling(self):
        """Verify restore route has try-except for threading issues."""
        import inspect

        from figrecipe._editor._routes_style import register_style_routes

        # Get the source code of the module
        source = inspect.getsourcefile(register_style_routes)
        with open(source) as f:
            content = f.read()

        # Should have try-except around canvas.draw() and set_dpi()
        assert "try:" in content
        assert "except Exception:" in content or "except:" in content
        # Should mention threading or tkinter in comment
        assert "threading" in content.lower() or "tkinter" in content.lower()


@requires_playwright
class TestRestoreEndpointIntegration:
    """Integration tests for restore endpoint."""

    def test_restore_returns_json(self, editor_server):
        """Verify restore endpoint returns valid JSON, not HTML error."""
        req = urllib.request.Request(
            f"{editor_server.url}/restore",
            method="POST",
            data=b"",
            headers={"Content-Type": "application/json"},
        )

        try:
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read().decode("utf-8")

            # Should be valid JSON
            data = json.loads(content)

            # Should have success field
            assert "success" in data
            assert data["success"] is True

            # Should have image data
            assert "image" in data
            assert data["image"] is not None

        except urllib.error.HTTPError as e:
            # If it fails, it should NOT be returning HTML
            content = e.read().decode("utf-8")
            assert "<!doctype" not in content.lower(), (
                f"Restore returned HTML error instead of JSON: {content[:200]}"
            )
            raise

    def test_restore_returns_bboxes(self, editor_server):
        """Verify restore endpoint returns bounding boxes."""
        req = urllib.request.Request(
            f"{editor_server.url}/restore",
            method="POST",
            data=b"",
            headers={"Content-Type": "application/json"},
        )

        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode("utf-8"))

        assert "bboxes" in data
        assert isinstance(data["bboxes"], (list, dict))
