#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style and theme Flask route handlers for the figure editor.
"""

from flask import jsonify, request

from ._helpers import get_form_values_from_style, render_with_overrides


def register_style_routes(app, editor):
    """Register style/theme routes with the Flask app."""
    from ._overrides import save_overrides

    @app.route("/style")
    def get_style():
        """Get current style configuration."""
        return jsonify(
            {
                "base_style": editor.style_overrides.base_style,
                "programmatic_style": editor.style_overrides.programmatic_style,
                "manual_overrides": editor.style_overrides.manual_overrides,
                "effective_style": editor.get_effective_style(),
                "has_overrides": editor.style_overrides.has_manual_overrides(),
                "manual_timestamp": editor.style_overrides.manual_timestamp,
            }
        )

    @app.route("/overrides")
    def get_overrides():
        """Get current manual overrides."""
        return jsonify(editor.style_overrides.manual_overrides)

    @app.route("/theme")
    def get_theme():
        """Get current theme YAML content for display."""
        import io as yaml_io

        from ruamel.yaml import YAML

        style = editor.get_effective_style()
        style_name = style.get("_name", "SCITEX")

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        stream = yaml_io.StringIO()
        yaml.dump(style, stream)
        yaml_content = stream.getvalue()

        return jsonify(
            {
                "name": style_name,
                "content": yaml_content,
            }
        )

    @app.route("/list_themes")
    def list_themes():
        """List available theme presets."""
        from ..styles._style_loader import list_presets

        presets = list_presets()
        current = editor.get_effective_style().get("_name", "SCITEX")

        return jsonify(
            {
                "themes": presets,
                "current": current,
            }
        )

    @app.route("/switch_theme", methods=["POST"])
    def switch_theme():
        """Switch to a different theme preset by reproducing the figure."""
        from .._reproducer import reproduce_from_record
        from ..styles._style_loader import load_preset

        data = request.get_json() or {}
        theme_name = data.get("theme")

        if not theme_name:
            return jsonify({"error": "No theme specified"}), 400

        try:
            new_style = load_preset(theme_name)

            if new_style is None:
                return jsonify({"error": f"Theme '{theme_name}' not found"}), 404

            # Convert nested style to flat style dict with color_palette
            flat_style = dict(new_style)
            flat_style["_name"] = theme_name

            # Extract color_palette from nested colors.palette
            if "colors" in new_style and isinstance(new_style["colors"], dict):
                colors_dict = new_style["colors"]
                if "palette" in colors_dict:
                    flat_style["color_palette"] = list(colors_dict["palette"])

            editor.style_overrides.base_style = flat_style

            if hasattr(editor.fig, "record") and editor.fig.record is not None:
                editor.fig.record.style = flat_style
                new_fig, _ = reproduce_from_record(editor.fig.record)
                editor.fig = new_fig
                # Keep the new style (don't restore old style)

            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            behavior = new_style.get("behavior", {})
            for ax in mpl_fig.get_axes():
                hide_top = behavior.get("hide_top_spine", True)
                hide_right = behavior.get("hide_right_spine", True)
                ax.spines["top"].set_visible(not hide_top)
                ax.spines["right"].set_visible(not hide_right)

                if behavior.get("grid", False):
                    ax.grid(True, alpha=0.3)
                else:
                    ax.grid(False)

            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            form_values = get_form_values_from_style(editor.get_effective_style())

            return jsonify(
                {
                    "success": True,
                    "theme": theme_name,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                    "values": form_values,
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Failed to switch theme: {str(e)}"}), 500

    @app.route("/save", methods=["POST"])
    def save():
        """Save style overrides (stored separately from recipe)."""
        data = request.get_json() or {}
        editor.style_overrides.update_manual_overrides(data.get("overrides", {}))

        if editor.recipe_path:
            path = save_overrides(editor.style_overrides, editor.recipe_path)
            return jsonify(
                {
                    "success": True,
                    "path": str(path),
                    "has_overrides": editor.style_overrides.has_manual_overrides(),
                    "timestamp": editor.style_overrides.manual_timestamp,
                }
            )

        return jsonify(
            {
                "success": True,
                "overrides": editor.overrides,
                "has_overrides": editor.style_overrides.has_manual_overrides(),
            }
        )

    @app.route("/restore", methods=["POST"])
    def restore():
        """Restore to original style (clear manual overrides and axes positions)."""
        from ._bbox import extract_bboxes

        # Clear all manual overrides (including position overrides)
        editor.style_overrides.clear_manual_overrides()

        # Restore original axes positions
        editor.restore_axes_positions()

        if editor._initial_base64 and not editor.dark_mode:
            base64_img = editor._initial_base64
            import base64 as b64
            import io

            from PIL import Image

            img_data = b64.b64decode(base64_img)
            img = Image.open(io.BytesIO(img_data))
            img_size = img.size
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            original_dpi = mpl_fig.dpi
            mpl_fig.set_dpi(150)
            mpl_fig.canvas.draw()
            bboxes = extract_bboxes(mpl_fig, img_size[0], img_size[1])
            mpl_fig.set_dpi(original_dpi)
        else:
            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                None,
                editor.dark_mode,
            )

        return jsonify(
            {
                "success": True,
                "image": base64_img,
                "bboxes": bboxes,
                "img_size": {"width": img_size[0], "height": img_size[1]},
                "original_style": editor.style,
            }
        )

    @app.route("/diff")
    def get_diff():
        """Get differences between original and manual overrides."""
        return jsonify(
            {
                "diff": editor.style_overrides.get_diff(),
                "has_overrides": editor.style_overrides.has_manual_overrides(),
            }
        )


__all__ = ["register_style_routes"]
