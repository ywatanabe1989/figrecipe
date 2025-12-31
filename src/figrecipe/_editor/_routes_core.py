#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Flask route handlers for the figure editor.
Handles main page, preview, update, and hitmap routes.
File operations moved to _routes_files.py.
"""

import os

from flask import jsonify, render_template_string, request

from . import _check_figure_has_content
from ._helpers import render_with_overrides


def _is_debug_mode() -> bool:
    """Check if debug mode is enabled via FIGRECIPE_DEBUG_MODE env var."""
    return os.environ.get("FIGRECIPE_DEBUG_MODE", "").lower() in ("1", "true", "yes")


def register_core_routes(app, editor):
    """Register core routes with the Flask app."""
    from ._hitmap import generate_hitmap, hitmap_to_base64
    from ._templates import build_html_template

    @app.route("/")
    def index():
        """Main editor page."""
        base64_img, bboxes, img_size = render_with_overrides(
            editor.fig,
            editor.get_effective_style(),
            editor.dark_mode,
        )

        style_name = getattr(editor, "_style_name", "SCITEX")

        # Check if figure has plot content
        figure_has_content = _check_figure_has_content(editor.fig)

        html = build_html_template(
            image_base64=base64_img,
            bboxes=bboxes,
            color_map=editor._color_map,
            style=editor.style,
            overrides=editor.get_effective_style(),
            img_size=img_size,
            style_name=style_name,
            hot_reload=editor.hot_reload,
            dark_mode=editor.dark_mode,
            figure_has_content=figure_has_content,
            debug_mode=_is_debug_mode(),
        )

        return render_template_string(html)

    @app.route("/preview")
    def preview():
        """Get current preview image."""
        base64_img, bboxes, img_size = render_with_overrides(
            editor.fig,
            editor.get_effective_style(),
            editor.dark_mode,
        )

        return jsonify(
            {
                "image": base64_img,
                "bboxes": bboxes,
                "img_size": {"width": img_size[0], "height": img_size[1]},
            }
        )

    @app.route("/ping")
    def ping():
        """Health check endpoint for hot reload detection."""
        return jsonify({"status": "ok"})

    @app.route("/update", methods=["POST"])
    def update():
        """Update preview with new style overrides."""
        from ._preferences import set_preference

        data = request.get_json() or {}

        editor.overrides.update(data.get("overrides", {}))

        # Update and persist dark mode preference
        new_dark_mode = data.get("dark_mode")
        if new_dark_mode is not None and new_dark_mode != editor.dark_mode:
            editor.dark_mode = new_dark_mode
            set_preference("dark_mode", new_dark_mode)

        base64_img, bboxes, img_size = render_with_overrides(
            editor.fig,
            editor.get_effective_style(),
            editor.dark_mode,
        )

        return jsonify(
            {
                "image": base64_img,
                "bboxes": bboxes,
                "img_size": {"width": img_size[0], "height": img_size[1]},
            }
        )

    @app.route("/hitmap")
    def hitmap():
        """Get hitmap image and color map (lazy generation on first request)."""
        if not editor._hitmap_generated:
            print("Generating hitmap (first request)...")
            hitmap_img, editor._color_map = generate_hitmap(editor.fig)
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True
            print("Hitmap ready.")

        return jsonify(
            {
                "image": editor._hitmap_base64,
                "color_map": editor._color_map,
            }
        )


__all__ = ["register_core_routes"]
