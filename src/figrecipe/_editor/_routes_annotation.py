#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation-related Flask route handlers for the figure editor.

Handles updating positions of decorative elements like panel labels,
text annotations, and arrows.
"""

from flask import jsonify, request

from ._helpers import render_with_overrides


def register_annotation_routes(app, editor):
    """Register annotation-related routes with the Flask app."""

    @app.route("/update_annotation_position", methods=["POST"])
    def update_annotation_position():
        """Update annotation position (panel label, text, arrow).

        Expects JSON: {
            ax_index: int,
            annotation_type: str ('panel_label', 'text', 'arrow'),
            text_index: int,
            x: float (axes-relative 0-1),
            y: float (axes-relative 0-1)
        }
        """
        data = request.get_json() or {}
        ax_index = data.get("ax_index", 0)
        annotation_type = data.get("annotation_type", "text")
        text_index = data.get("text_index", 0)
        new_x = data.get("x")
        new_y = data.get("y")

        if new_x is None or new_y is None:
            return jsonify({"error": "Missing x or y coordinate"}), 400

        try:
            # Get the matplotlib figure
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes_list = mpl_fig.get_axes()

            if ax_index >= len(axes_list):
                return jsonify({"error": f"Invalid axis index: {ax_index}"}), 400

            ax = axes_list[ax_index]

            if annotation_type in ("panel_label", "text"):
                # Update text position
                if text_index >= len(ax.texts):
                    return jsonify({"error": f"Invalid text index: {text_index}"}), 400

                text_obj = ax.texts[text_index]

                # Set new position (in axes coordinates for transAxes transform)
                if text_obj.get_transform() == ax.transAxes:
                    text_obj.set_position((new_x, new_y))
                else:
                    # For data coordinates, convert from axes-relative
                    xlim = ax.get_xlim()
                    ylim = ax.get_ylim()
                    data_x = xlim[0] + new_x * (xlim[1] - xlim[0])
                    data_y = ylim[0] + new_y * (ylim[1] - ylim[0])
                    text_obj.set_position((data_x, data_y))

                # Store in manual_overrides for persistence and undo support
                override_key = f"annotation_pos_ax{ax_index}_text{text_index}"
                editor.style_overrides.manual_overrides[override_key] = {
                    "x": new_x,
                    "y": new_y,
                    "type": annotation_type,
                }

            elif annotation_type == "arrow":
                # Update arrow position (FancyArrowPatch)
                from matplotlib.patches import FancyArrowPatch

                arrow_patches = [
                    p for p in ax.patches if isinstance(p, FancyArrowPatch)
                ]
                arrow_index = data.get("arrow_index", 0)

                if arrow_index >= len(arrow_patches):
                    return jsonify(
                        {"error": f"Invalid arrow index: {arrow_index}"}
                    ), 400

                # Arrow position update is more complex - skip for now
                return jsonify({"error": "Arrow drag not yet implemented"}), 501

            # Re-render the figure
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
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500


__all__ = ["register_annotation_routes"]
