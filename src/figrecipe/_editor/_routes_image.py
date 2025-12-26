#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image drop Flask route handlers for the figure editor.

Handles drag & drop of external images to create imshow panels.
"""

import base64
import io
import urllib.request

import numpy as np
from flask import jsonify, request
from PIL import Image

from ._helpers import render_with_overrides


def _add_image_panel_to_figure(editor, img_array, filename, drop_x, drop_y):
    """Add an image panel using the figrecipe recording system.

    This ensures dropped images become proper panels (C, D, E...) that
    integrate with the existing coordinate system and pipeline.
    """
    from .._wrappers._axes import RecordingAxes

    # Get the underlying matplotlib figure
    mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig

    # Calculate panel position based on drop location
    # Default size: 40% of figure in each dimension
    panel_width = 0.4
    panel_height = 0.4

    # Convert drop position to axes position (bottom-left origin for matplotlib)
    left = max(0.05, min(0.55, drop_x - panel_width / 2))
    bottom = max(0.05, min(0.55, (1 - drop_y) - panel_height / 2))

    # Add new axes at the drop position
    mpl_ax = mpl_fig.add_axes([left, bottom, panel_width, panel_height])

    # If we have a RecordingFigure with recorder, wrap the axes properly
    if hasattr(editor.fig, "_recorder"):
        recorder = editor.fig._recorder
        # Determine position index for the new panel
        existing_axes = len(mpl_fig.get_axes()) - 1  # -1 because we just added one
        position = (existing_axes, 0)  # Simple sequential positioning

        # Create RecordingAxes wrapper
        wrapped_ax = RecordingAxes(mpl_ax, recorder, position=position)

        # Call imshow through wrapper so it gets recorded
        wrapped_ax.imshow(img_array, id=f"dropped_{filename[:15]}")
        wrapped_ax.set_title(filename[:20])
        wrapped_ax.axis("off")

        # Add to figure's axes list
        if hasattr(editor.fig, "_axes"):
            # Append as a new row
            editor.fig._axes.append([wrapped_ax])
    else:
        # Fallback: raw matplotlib (no recording)
        mpl_ax.imshow(img_array)
        mpl_ax.set_title(filename[:20])
        mpl_ax.axis("off")


def _render_and_update_hitmap(editor):
    """Re-render figure and regenerate hitmap after modification.

    Returns JSON-serializable response dict with image, bboxes, and size.
    """
    from ._hitmap import generate_hitmap, hitmap_to_base64

    base64_img, bboxes, img_size = render_with_overrides(
        editor.fig,
        editor.get_effective_style(),
        editor.dark_mode,
    )

    hitmap_img, color_map = generate_hitmap(editor.fig, dpi=150)
    editor._color_map = color_map
    editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
    editor._hitmap_generated = True

    return {
        "success": True,
        "image": base64_img,
        "bboxes": bboxes,
        "img_size": {"width": img_size[0], "height": img_size[1]},
    }


def register_image_routes(app, editor):
    """Register image drop routes with the Flask app."""

    @app.route("/add_image_panel", methods=["POST"])
    def add_image_panel():
        """Add a new panel with an imshow of the dropped image.

        Expects JSON: {image_data: base64, filename: str, drop_x: float, drop_y: float}
        drop_x, drop_y are normalized (0-1) positions where the image was dropped.
        """
        data = request.get_json() or {}
        image_data = data.get("image_data")
        filename = data.get("filename", "dropped_image")
        drop_x = data.get("drop_x", 0.5)
        drop_y = data.get("drop_y", 0.5)

        if not image_data:
            return jsonify({"error": "Missing image_data"}), 400

        try:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            _add_image_panel_to_figure(editor, img_array, filename, drop_x, drop_y)
            return jsonify(_render_and_update_hitmap(editor))

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Failed to add image: {str(e)}"}), 500

    @app.route("/add_image_from_url", methods=["POST"])
    def add_image_from_url():
        """Add a new panel with an imshow from a URL.

        Expects JSON: {url: str, drop_x: float, drop_y: float}
        """
        data = request.get_json() or {}
        url = data.get("url")
        drop_x = data.get("drop_x", 0.5)
        drop_y = data.get("drop_y", 0.5)

        if not url:
            return jsonify({"error": "Missing url"}), 400

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                image_bytes = response.read()

            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)
            filename = url.split("/")[-1].split("?")[0][:20]

            _add_image_panel_to_figure(editor, img_array, filename, drop_x, drop_y)
            return jsonify(_render_and_update_hitmap(editor))

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Failed to add image from URL: {str(e)}"}), 500

    @app.route("/load_recipe", methods=["POST"])
    def load_recipe():
        """Load a recipe file dropped onto the editor.

        Expects JSON: {recipe_content: str, filename: str}
        """
        data = request.get_json() or {}
        recipe_content = data.get("recipe_content")
        filename = data.get("filename", "recipe.yaml")

        if not recipe_content:
            return jsonify({"error": "Missing recipe_content"}), 400

        try:
            import tempfile

            import figrecipe as fr

            # Write recipe to temp file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(recipe_content)
                temp_path = f.name

            # Reproduce figure from recipe
            fig, axes = fr.reproduce(temp_path)

            # Update editor's figure
            editor.fig = fig
            editor._hitmap_generated = False

            return jsonify({"success": True, "message": f"Loaded {filename}"})

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Failed to load recipe: {str(e)}"}), 500


__all__ = ["register_image_routes"]
