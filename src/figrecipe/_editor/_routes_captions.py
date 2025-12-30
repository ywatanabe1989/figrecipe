#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Caption-related Flask route handlers for the figure editor.
Handles scientific figure captions and panel captions.
"""

from flask import jsonify, request


def register_caption_routes(app, editor):
    """Register caption-related routes with the Flask app."""

    @app.route("/get_captions")
    def get_captions():
        """Get current captions (figure and panel)."""
        captions = {
            "figure_number": 1,
            "figure_caption": "",
            "panel_captions": [],  # List of panel captions
        }

        # Try to get caption from RecordingFigure's recorder
        fig = editor.fig
        if hasattr(fig, "caption") and fig.caption:
            captions["figure_caption"] = fig.caption

        # Get panel captions from axes
        if hasattr(fig, "flat"):
            for ax in fig.flat:
                if hasattr(ax, "caption") and ax.caption:
                    captions["panel_captions"].append(ax.caption)
                else:
                    captions["panel_captions"].append("")

        # Check if we have recipe metadata (fallback)
        if not captions["figure_caption"] and hasattr(fig, "_recipe_metadata"):
            metadata = fig._recipe_metadata
            if hasattr(metadata, "caption") and metadata.caption:
                captions["figure_caption"] = metadata.caption
            if hasattr(metadata, "figure_number") and metadata.figure_number:
                captions["figure_number"] = metadata.figure_number

        # Check editor's manual overrides for captions (highest priority)
        if hasattr(editor, "style_overrides"):
            manual = getattr(editor.style_overrides, "manual_overrides", {})
            if "caption_figure_number" in manual:
                captions["figure_number"] = manual["caption_figure_number"]
            if "caption_figure_text" in manual:
                captions["figure_caption"] = manual["caption_figure_text"]
            # Load individual panel overrides
            for i in range(len(captions["panel_captions"])):
                key = f"caption_panel_{i}_text"
                if key in manual:
                    captions["panel_captions"][i] = manual[key]

        return jsonify(captions)

    @app.route("/update_caption", methods=["POST"])
    def update_caption():
        """Update figure or panel caption."""
        data = request.get_json() or {}
        caption_type = data.get("type")  # 'figure' or 'panel'

        if not caption_type:
            return jsonify({"error": "Missing caption type"}), 400

        try:
            if caption_type == "figure":
                figure_number = data.get("figure_number", 1)
                text = data.get("text", "")

                # Store in manual overrides
                editor.style_overrides.manual_overrides["caption_figure_number"] = (
                    figure_number
                )
                editor.style_overrides.manual_overrides["caption_figure_text"] = text

                # Also store in recipe metadata if available
                if hasattr(editor.fig, "_recipe_metadata"):
                    editor.fig._recipe_metadata.caption = text
                    editor.fig._recipe_metadata.figure_number = figure_number

                return jsonify(
                    {
                        "success": True,
                        "caption_type": "figure",
                        "figure_number": figure_number,
                        "text": text,
                    }
                )

            elif caption_type == "panel":
                panel_index = data.get("panel_index", 0)
                text = data.get("text", "")

                # Store in manual overrides
                key = f"caption_panel_{panel_index}_text"
                editor.style_overrides.manual_overrides[key] = text
                # Also store general panel caption for current selection
                editor.style_overrides.manual_overrides["caption_panel_text"] = text

                # Store in axes metadata if available
                if hasattr(editor.fig, "_axes_metadata"):
                    axes_meta = editor.fig._axes_metadata
                    if panel_index < len(axes_meta):
                        axes_meta[panel_index].caption = text

                return jsonify(
                    {
                        "success": True,
                        "caption_type": "panel",
                        "panel_index": panel_index,
                        "text": text,
                    }
                )

            else:
                return jsonify({"error": f"Unknown caption type: {caption_type}"}), 400

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Caption update failed: {str(e)}"}), 500


__all__ = ["register_caption_routes"]

# EOF
