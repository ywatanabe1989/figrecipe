#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selection-related Flask route handlers for the figure editor.

Handles panel label positions and multi-selection state.
"""

from flask import jsonify, request


def register_selection_routes(app, editor):
    """Register selection-related routes with the Flask app."""

    @app.route("/api/label-positions", methods=["GET"])
    def get_label_positions():
        """Get stored panel label positions (offsets in mm)."""
        positions = getattr(editor, "_label_positions", {})
        return jsonify({"positions": positions})

    @app.route("/api/label-positions", methods=["POST"])
    def save_label_positions():
        """Save panel label positions (offsets in mm).

        Expects JSON: {positions: {ax_0: {offsetX, offsetY}, ...}}
        """
        data = request.get_json() or {}
        positions = data.get("positions", {})

        # Validate structure
        for key, pos in positions.items():
            if not isinstance(pos, dict):
                return jsonify({"error": f"Invalid position format for {key}"}), 400
            if "offsetX" not in pos or "offsetY" not in pos:
                return jsonify({"error": f"Missing offsetX/offsetY for {key}"}), 400

        # Store on editor instance
        editor._label_positions = positions

        # Also store in manual_overrides for persistence with recipe
        editor.style_overrides.manual_overrides["panel_label_positions"] = positions

        return jsonify({"success": True})


__all__ = ["register_selection_routes"]
