#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2E tests for layout stability in the figure editor.

These tests verify that changing element properties (like colors) doesn't
cause unintended layout shifts. Uses pixel comparison to detect changes.
"""

import base64
import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def image_from_base64(base64_str: str) -> np.ndarray:
    """Convert base64 PNG to numpy array."""
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes))
    return np.array(img)


def calculate_layout_diff(
    img1: np.ndarray, img2: np.ndarray, color_tolerance: int = 50
) -> dict:
    """Calculate layout differences between two images.

    Returns a dict with:
    - total_changed_pixels: Total pixels that changed
    - color_only_changes: Pixels where only color changed (not position)
    - layout_changes: Pixels that suggest layout shift
    - layout_stable: True if layout appears stable (only color changes)
    """
    if img1.shape != img2.shape:
        return {
            "total_changed_pixels": -1,
            "color_only_changes": 0,
            "layout_changes": -1,
            "layout_stable": False,
            "error": f"Shape mismatch: {img1.shape} vs {img2.shape}",
        }

    # Calculate pixel-wise difference
    diff = np.abs(img1.astype(int) - img2.astype(int))

    # Pixels that changed at all
    changed_mask = np.any(diff > 0, axis=-1) if len(diff.shape) > 2 else diff > 0
    total_changed = np.sum(changed_mask)

    # For layout stability: check if changes are localized
    # Find bounding box of changes
    if total_changed > 0:
        rows = np.any(changed_mask, axis=1)
        cols = np.any(changed_mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        change_area = (rmax - rmin + 1) * (cmax - cmin + 1)
        change_density = total_changed / change_area if change_area > 0 else 0
    else:
        change_density = 0
        change_area = 0

    # Layout is stable if changes are localized (high density in small area)
    # This indicates color changes in specific elements vs scattered layout shifts
    total_pixels = img1.shape[0] * img1.shape[1]
    change_ratio = total_changed / total_pixels

    # Heuristic: layout shift causes scattered, low-density changes
    # Color changes cause localized, high-density changes
    layout_stable = change_ratio < 0.3 and (
        change_density > 0.1 or total_changed < 1000
    )

    return {
        "total_changed_pixels": int(total_changed),
        "change_ratio": float(change_ratio),
        "change_density": float(change_density),
        "change_area": int(change_area),
        "layout_stable": layout_stable,
    }


class TestLayoutStability:
    """Test that element property changes don't cause layout shifts."""

    @pytest.fixture
    def editor_client(self):
        """Create a test client for the editor."""
        import matplotlib

        matplotlib.use("Agg")

        from flask import Flask

        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor
        from figrecipe._editor._hitmap import generate_hitmap, hitmap_to_base64
        from figrecipe._editor._routes_axis import register_axis_routes
        from figrecipe._editor._routes_core import register_core_routes
        from figrecipe._editor._routes_element import register_element_routes
        from figrecipe._editor._routes_style import register_style_routes

        # Create a simple test figure with a pie chart
        fig, axes = fr.subplots(1, 2, figsize=(8, 4))

        # Left: line plot
        axes[0].plot([1, 2, 3], [1, 4, 2], label="test")
        axes[0].set_title("Line Plot")

        # Right: pie chart
        axes[1].pie([25, 30, 20, 25], labels=["A", "B", "C", "D"])
        axes[1].set_title("Pie Chart")

        # Generate hitmap
        hitmap_img, color_map = generate_hitmap(fig)
        hitmap_base64 = hitmap_to_base64(hitmap_img)

        # Create editor
        editor = FigureEditor(
            fig=fig,
            hitmap_base64=hitmap_base64,
            color_map=color_map,
        )
        editor._hitmap_generated = True

        # Create Flask app (mimics FigureEditor.run() logic)
        app = Flask(__name__)
        register_core_routes(app, editor)
        register_style_routes(app, editor)
        register_axis_routes(app, editor)
        register_element_routes(app, editor)

        client = app.test_client()

        yield client, editor

        # Cleanup - close the underlying matplotlib figure
        import matplotlib.pyplot as plt

        plt.close(fig.fig if hasattr(fig, "fig") else fig)

    def test_initial_render_consistent(self, editor_client):
        """Test that multiple renders without changes produce identical images."""
        client, editor = editor_client

        # Get first render
        response1 = client.get("/preview")
        assert response1.status_code == 200
        data1 = response1.get_json()
        img1 = image_from_base64(data1["image"])

        # Get second render (should be identical)
        response2 = client.get("/preview")
        assert response2.status_code == 200
        data2 = response2.get_json()
        img2 = image_from_base64(data2["image"])

        # Compare
        diff = calculate_layout_diff(img1, img2)

        # Should be exactly identical
        assert (
            diff["total_changed_pixels"] == 0
        ), f"Expected identical renders, but {diff['total_changed_pixels']} pixels changed"

    def test_color_change_no_layout_shift(self, editor_client):
        """Test that changing a color doesn't shift layout."""
        client, editor = editor_client

        # Get initial render
        response1 = client.get("/preview")
        data1 = response1.get_json()
        img1 = image_from_base64(data1["image"])

        # Change a line color via override
        override_data = {
            "key": "ax0_line0_color",
            "value": "#ff0000",  # Change to red
        }
        response = client.post("/update", json=override_data)
        assert response.status_code == 200

        # Get new render
        response2 = client.get("/preview")
        data2 = response2.get_json()
        img2 = image_from_base64(data2["image"])

        # Compare - layout should be stable
        diff = calculate_layout_diff(img1, img2)

        assert diff[
            "layout_stable"
        ], f"Layout shifted after color change! Stats: {diff}"

    def test_pie_color_change_no_layout_shift(self, editor_client):
        """Test that changing pie wedge colors doesn't shift layout."""
        client, editor = editor_client

        # Get initial render
        response1 = client.get("/preview")
        data1 = response1.get_json()
        img1 = image_from_base64(data1["image"])
        initial_size = (
            data1.get("img_size", {}).get("width"),
            data1.get("img_size", {}).get("height"),
        )

        # Find pie call_id from editor's record
        pie_call_id = None
        if hasattr(editor.fig, "record") and editor.fig.record:
            record = editor.fig.record
            # record.axes is Dict[str, AxesRecord], each AxesRecord has .calls
            for ax_key, ax_record in record.axes.items():
                for call in ax_record.calls:
                    if call.function == "pie":
                        pie_call_id = call.id
                        break
                if pie_call_id:
                    break

        if not pie_call_id:
            pytest.skip("No pie call found in figure record")

        # Change pie colors via the /update_call endpoint (used by color list UI)
        pie_colors_data = {
            "call_id": pie_call_id,
            "param": "colors",
            "value": ["#ff0000", "#00ff00", "#0000ff", "#ffff00"],
        }
        response = client.post("/update_call", json=pie_colors_data)
        assert response.status_code == 200, f"update_call failed: {response.data}"

        # Get new render
        response2 = client.get("/preview")
        data2 = response2.get_json()
        img2 = image_from_base64(data2["image"])
        new_size = (
            data2.get("img_size", {}).get("width"),
            data2.get("img_size", {}).get("height"),
        )

        # Image size should be identical
        assert (
            initial_size == new_size
        ), f"Image size changed from {initial_size} to {new_size}"

        # Compare - layout should be stable
        diff = calculate_layout_diff(img1, img2)

        # Allow some changes (the pie colors themselves), but layout should be stable
        assert diff[
            "layout_stable"
        ], f"Layout shifted after pie color change! Stats: {diff}"


class TestImageSizeConsistency:
    """Test that image dimensions remain consistent."""

    @pytest.fixture
    def simple_figure(self):
        """Create a simple figure for testing."""
        import matplotlib

        matplotlib.use("Agg")
        import figrecipe as fr

        fig, ax = fr.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [1, 4, 2])
        ax.set_title("Test")

        yield fig

        import matplotlib.pyplot as plt

        # Close the underlying matplotlib figure
        plt.close(fig.fig if hasattr(fig, "fig") else fig)

    def test_render_size_stable(self, simple_figure):
        """Test that repeated renders have consistent size."""
        from figrecipe._editor._helpers import render_with_overrides

        sizes = []
        for _ in range(5):
            _, _, img_size = render_with_overrides(simple_figure, {}, dark_mode=False)
            sizes.append(img_size)

        # All sizes should be identical
        assert all(s == sizes[0] for s in sizes), f"Image sizes vary: {sizes}"

    def test_render_size_after_color_change(self, simple_figure):
        """Test that image size doesn't change after color override."""
        from figrecipe._editor._helpers import render_with_overrides

        # Initial render
        _, _, size1 = render_with_overrides(simple_figure, {}, dark_mode=False)

        # Render with color override
        overrides = {"ax0_line0_color": "#ff0000"}
        _, _, size2 = render_with_overrides(simple_figure, overrides, dark_mode=False)

        assert (
            size1 == size2
        ), f"Image size changed from {size1} to {size2} after color override"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
