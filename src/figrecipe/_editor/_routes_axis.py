#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Axis-related Flask route handlers for the figure editor.
Handles labels, axis type, legend position, and ticks.
"""

import matplotlib
from flask import jsonify, request

from ._helpers import render_with_overrides


def register_axis_routes(app, editor):
    """Register axis-related routes with the Flask app."""

    @app.route("/update_label", methods=["POST"])
    def update_label():
        """Update axis labels (title, xlabel, ylabel, suptitle)."""
        data = request.get_json() or {}
        label_type = data.get("label_type")
        text = data.get("text", "")
        ax_index = data.get("ax_index", 0)

        if not label_type:
            return jsonify({"error": "Missing label_type"}), 400

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes = mpl_fig.get_axes()

        if not axes:
            return jsonify({"error": "No axes found"}), 400

        ax = axes[min(ax_index, len(axes) - 1)]

        try:
            if label_type == "title":
                ax.set_title(text)
            elif label_type == "xlabel":
                ax.set_xlabel(text)
            elif label_type == "ylabel":
                ax.set_ylabel(text)
            elif label_type == "suptitle":
                if text:
                    mpl_fig.suptitle(text)
                else:
                    if mpl_fig._suptitle:
                        mpl_fig._suptitle.set_text("")
            else:
                return jsonify({"error": f"Unknown label_type: {label_type}"}), 400

            editor.style_overrides.manual_overrides[f"label_{label_type}"] = text

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
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Update failed: {str(e)}"}), 500

    @app.route("/get_labels")
    def get_labels():
        """Get current axis labels (title, xlabel, ylabel, suptitle)."""
        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes = mpl_fig.get_axes()

        labels = {"title": "", "xlabel": "", "ylabel": "", "suptitle": ""}

        if axes:
            ax = axes[0]
            labels["title"] = ax.get_title()
            labels["xlabel"] = ax.get_xlabel()
            labels["ylabel"] = ax.get_ylabel()

        if mpl_fig._suptitle:
            labels["suptitle"] = mpl_fig._suptitle.get_text()

        return jsonify(labels)

    @app.route("/update_axis_type", methods=["POST"])
    def update_axis_type():
        """Update axis type (numerical vs categorical)."""
        data = request.get_json() or {}
        axis = data.get("axis")
        axis_type = data.get("type")
        labels = data.get("labels", [])
        ax_index = data.get("ax_index", 0)

        if not axis or not axis_type:
            return jsonify({"error": "Missing axis or type"}), 400

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes_list = mpl_fig.get_axes()

        if not axes_list:
            return jsonify({"error": "No axes found"}), 400

        ax = axes_list[min(ax_index, len(axes_list) - 1)]

        try:
            if axis == "x":
                if axis_type == "categorical" and labels:
                    positions = list(range(len(labels)))
                    ax.set_xticks(positions)
                    ax.set_xticklabels(labels)
                else:
                    ax.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
                    ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            elif axis == "y":
                if axis_type == "categorical" and labels:
                    positions = list(range(len(labels)))
                    ax.set_yticks(positions)
                    ax.set_yticklabels(labels)
                else:
                    ax.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
                    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

            key = f"axis_{axis}_type"
            editor.style_overrides.manual_overrides[key] = axis_type
            if labels:
                editor.style_overrides.manual_overrides[f"axis_{axis}_labels"] = labels

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
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Update failed: {str(e)}"}), 500

    @app.route("/get_axis_info")
    def get_axis_info():
        """Get current axis type info (numerical vs categorical)."""
        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes_list = mpl_fig.get_axes()

        info = {
            "x_type": "numerical",
            "y_type": "numerical",
            "x_labels": [],
            "y_labels": [],
        }

        if axes_list:
            ax = axes_list[0]

            x_ticklabels = [t.get_text() for t in ax.get_xticklabels()]
            if x_ticklabels and any(t for t in x_ticklabels):
                info["x_type"] = "categorical"
                info["x_labels"] = x_ticklabels

            y_ticklabels = [t.get_text() for t in ax.get_yticklabels()]
            if y_ticklabels and any(t for t in y_ticklabels):
                info["y_type"] = "categorical"
                info["y_labels"] = y_ticklabels

        return jsonify(info)

    @app.route("/update_legend_position", methods=["POST"])
    def update_legend_position():
        """Update legend position, visibility, or custom xy coordinates."""
        data = request.get_json() or {}
        loc = data.get("loc")
        x = data.get("x")
        y = data.get("y")
        visible = data.get("visible")
        ax_index = data.get("ax_index", 0)

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes_list = mpl_fig.get_axes()

        if not axes_list:
            return jsonify({"error": "No axes found"}), 400

        ax = axes_list[min(ax_index, len(axes_list) - 1)]
        legend = ax.get_legend()

        if legend is None:
            return jsonify({"error": "No legend found on this axes"}), 400

        try:
            if visible is not None:
                legend.set_visible(visible)
                editor.style_overrides.manual_overrides["legend_visible"] = visible

            if loc is not None:
                if loc == "custom" and x is not None and y is not None:
                    legend.set_bbox_to_anchor((float(x), float(y)))
                    legend._loc = 2
                else:
                    loc_map = {
                        "best": 0,
                        "upper right": 1,
                        "upper left": 2,
                        "lower left": 3,
                        "lower right": 4,
                        "right": 5,
                        "center left": 6,
                        "center right": 7,
                        "lower center": 8,
                        "upper center": 9,
                        "center": 10,
                    }
                    loc_code = loc_map.get(loc, 0)
                    legend._loc = loc_code
                    legend.set_bbox_to_anchor(None)

                editor.style_overrides.manual_overrides["legend_loc"] = loc
                if loc == "custom":
                    editor.style_overrides.manual_overrides["legend_x"] = x
                    editor.style_overrides.manual_overrides["legend_y"] = y

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
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Update failed: {str(e)}"}), 500

    @app.route("/get_legend_info")
    def get_legend_info():
        """Get current legend position info."""
        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes_list = mpl_fig.get_axes()

        info = {
            "has_legend": False,
            "visible": True,
            "loc": "best",
            "x": None,
            "y": None,
        }

        if axes_list:
            ax = axes_list[0]
            legend = ax.get_legend()

            if legend is not None:
                info["has_legend"] = True
                info["visible"] = legend.get_visible()

                loc_code = legend._loc
                loc_names = {
                    0: "best",
                    1: "upper right",
                    2: "upper left",
                    3: "lower left",
                    4: "lower right",
                    5: "right",
                    6: "center left",
                    7: "center right",
                    8: "lower center",
                    9: "upper center",
                    10: "center",
                }
                info["loc"] = loc_names.get(loc_code, "best")

                bbox = legend.get_bbox_to_anchor()
                if bbox is not None:
                    try:
                        bounds = bbox.bounds
                        if bounds[0] != 0 or bounds[1] != 0:
                            info["loc"] = "custom"
                            info["x"] = bounds[0]
                            info["y"] = bounds[1]
                    except Exception:
                        pass

        return jsonify(info)

    @app.route("/get_axes_positions")
    def get_axes_positions():
        """Get positions for all axes in figure coordinates [left, bottom, width, height]."""
        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes = mpl_fig.get_axes()

        positions = {}
        for i, ax in enumerate(axes):
            bbox = ax.get_position()
            positions[f"ax_{i}"] = {
                "index": i,
                "left": round(bbox.x0, 4),
                "bottom": round(bbox.y0, 4),
                "width": round(bbox.width, 4),
                "height": round(bbox.height, 4),
                # Convenience: also provide right/top
                "right": round(bbox.x1, 4),
                "top": round(bbox.y1, 4),
            }

        return jsonify(positions)

    @app.route("/update_axes_position", methods=["POST"])
    def update_axes_position():
        """Update position of a specific axes.

        Expects JSON: {ax_index: int, left, bottom, width, height}
        Values are in figure coordinates (0-1).
        """
        from ._hitmap import generate_hitmap, hitmap_to_base64

        data = request.get_json() or {}
        ax_index = data.get("ax_index", 0)
        left = data.get("left")
        bottom = data.get("bottom")
        width = data.get("width")
        height = data.get("height")

        if any(v is None for v in [left, bottom, width, height]):
            return jsonify({"error": "Missing position values"}), 400

        # Validate range
        for name, val in [
            ("left", left),
            ("bottom", bottom),
            ("width", width),
            ("height", height),
        ]:
            if not (0 <= val <= 1):
                return jsonify({"error": f"{name} must be between 0 and 1"}), 400

        mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
        axes = mpl_fig.get_axes()

        if ax_index >= len(axes):
            return jsonify({"error": f"Invalid ax_index: {ax_index}"}), 400

        try:
            ax = axes[ax_index]
            ax.set_position([left, bottom, width, height])

            # Update record if available
            if hasattr(editor.fig, "record"):
                # Find the axes record key
                ax_keys = sorted(editor.fig.record.axes.keys())
                if ax_index < len(ax_keys):
                    ax_key = ax_keys[ax_index]
                    ax_record = editor.fig.record.axes[ax_key]
                    ax_record.position_override = [left, bottom, width, height]

            # Re-render
            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            # Regenerate hitmap
            hitmap_img, color_map = generate_hitmap(mpl_fig, img_size[0], img_size[1])
            editor._color_map = color_map
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Update failed: {str(e)}"}), 500


__all__ = ["register_axis_routes"]
