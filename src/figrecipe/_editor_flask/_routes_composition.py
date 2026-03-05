#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composition-related Flask routes for the figure editor.

Provides API endpoints for:
- Panel visibility (hide/show)
- Panel alignment
- Panel distribution
- Smart alignment
- Importing axes from external recipes
"""

from pathlib import Path

from flask import jsonify, request

from ._helpers import render_with_overrides


def register_composition_routes(app, editor):
    """Register composition routes with the Flask app."""

    @app.route("/api/panel-visibility", methods=["POST"])
    def set_panel_visibility():
        """Toggle panel visibility.

        Request JSON:
            position: [row, col] - Panel position
            visible: bool - Target visibility state

        Returns:
            success: bool
            image: str - Updated preview as base64
            bboxes: dict - Updated bounding boxes
        """
        from .._composition import hide_panel, show_panel

        data = request.get_json() or {}
        position = tuple(data.get("position", [0, 0]))
        visible = data.get("visible", True)

        try:
            if visible:
                show_panel(editor.fig, position)
            else:
                hide_panel(editor.fig, position)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/align-panels", methods=["POST"])
    def align_panels_route():
        """Align selected panels.

        Request JSON:
            panels: [[row, col], ...] - List of panel positions
            mode: str - Alignment mode (left, right, top, bottom, etc.)
            reference: [row, col] - Optional reference panel

        Returns:
            success: bool
            image: str - Updated preview as base64
            bboxes: dict - Updated bounding boxes
        """
        from .._composition import align_panels

        data = request.get_json() or {}
        panels = [tuple(p) for p in data.get("panels", [])]
        mode = data.get("mode", "left")
        reference = tuple(data.get("reference")) if data.get("reference") else None

        try:
            align_panels(editor.fig, panels, mode, reference)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/distribute-panels", methods=["POST"])
    def distribute_panels_route():
        """Distribute panels evenly.

        Request JSON:
            panels: [[row, col], ...] - List of panel positions
            direction: str - 'horizontal' or 'vertical'
            spacing_mm: float - Optional fixed spacing in mm

        Returns:
            success: bool
            image: str - Updated preview as base64
            bboxes: dict - Updated bounding boxes
        """
        from .._composition import distribute_panels

        data = request.get_json() or {}
        panels = [tuple(p) for p in data.get("panels", [])]
        direction = data.get("direction", "horizontal")
        spacing_mm = data.get("spacing_mm")

        try:
            distribute_panels(editor.fig, panels, direction, spacing_mm)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/smart-align", methods=["POST"])
    def smart_align_route():
        """Auto-align all panels based on grid structure.

        Request JSON:
            panels: [[row, col], ...] - Optional specific panels to align

        Returns:
            success: bool
            image: str - Updated preview as base64
            bboxes: dict - Updated bounding boxes
        """
        from .._composition import smart_align

        data = request.get_json() or {}
        panels = None
        if data.get("panels"):
            panels = [tuple(p) for p in data["panels"]]

        try:
            smart_align(editor.fig, panels)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/import-panel", methods=["POST"])
    def import_panel():
        """Import axes from another recipe into current figure.

        Request JSON:
            source: str - Path to source recipe file
            source_axes: str - Axes key in source (default: 'ax_0_0')
            target_position: [row, col] - Target panel position

        Returns:
            success: bool
            image: str - Updated preview as base64
            bboxes: dict - Updated bounding boxes
        """
        from .._composition import import_axes

        data = request.get_json() or {}
        source_path = data.get("source")
        source_axes = data.get("source_axes", "ax_0_0")
        target_position = tuple(data.get("target_position", [0, 0]))

        if not source_path:
            return jsonify({"success": False, "error": "No source path provided"}), 400

        try:
            # Resolve relative paths against working directory
            working_dir = getattr(editor, "working_dir", Path.cwd())
            source_path = Path(source_path)
            if not source_path.is_absolute():
                source_path = working_dir / source_path

            import_axes(editor.fig, target_position, source_path, source_axes)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/panel-info")
    def get_panel_info():
        """Get information about all panels in the figure.

        Returns:
            panels: list of {position, visible, has_content}
        """
        panels = []
        for ax_key, ax_record in editor.fig.record.axes.items():
            parts = ax_key.split("_")
            if len(parts) >= 3:
                row, col = int(parts[1]), int(parts[2])
            else:
                row, col = 0, 0

            panels.append(
                {
                    "key": ax_key,
                    "position": [row, col],
                    "visible": getattr(ax_record, "visible", True),
                    "has_content": len(ax_record.calls) > 0,
                    "call_count": len(ax_record.calls),
                }
            )

        return jsonify({"panels": panels})


__all__ = ["register_composition_routes"]
