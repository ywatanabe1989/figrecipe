#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Flask route handlers for the figure editor.
Handles main page, preview, update, hitmap, and file switching routes.
"""

from flask import jsonify, render_template_string, request

from ._helpers import render_with_overrides


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

    @app.route("/api/files")
    def list_files():
        """List available recipe files in working directory."""
        from pathlib import Path

        working_dir = getattr(editor, "working_dir", Path.cwd())
        files = []

        # Find all YAML recipe files
        for pattern in ["*.yaml", "*.yml"]:
            for f in working_dir.glob(pattern):
                # Skip hidden files and overrides files
                if f.name.startswith(".") or f.name.endswith(".overrides.yaml"):
                    continue

                # Check for associated PNG
                png_path = f.with_suffix(".png")
                has_png = png_path.exists()

                files.append(
                    {
                        "path": str(f.relative_to(working_dir)),
                        "name": f.stem,
                        "has_image": has_png,
                        "is_current": (
                            editor.recipe_path
                            and f.resolve() == editor.recipe_path.resolve()
                        ),
                    }
                )

        # Sort by name
        files.sort(key=lambda x: x["name"].lower())

        return jsonify(
            {
                "files": files,
                "working_dir": str(working_dir),
                "current_file": (
                    str(editor.recipe_path.name) if editor.recipe_path else None
                ),
            }
        )

    @app.route("/api/switch", methods=["POST"])
    def switch_file():
        """Switch to a different recipe file."""
        from pathlib import Path

        from .._reproducer import reproduce

        data = request.get_json() or {}
        file_path = data.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        if not full_path.exists():
            return jsonify({"error": f"File not found: {file_path}"}), 404

        try:
            # Reproduce the figure from the new recipe
            fig, axes = reproduce(full_path)

            # Wrap in RecordingFigure if needed
            from .._wrappers._figure import RecordingFigure

            if not isinstance(fig, RecordingFigure):
                from .._recorder import FigureRecord, Recorder

                wrapped_fig = RecordingFigure.__new__(RecordingFigure)
                wrapped_fig._fig = fig
                wrapped_fig._axes = [[ax] for ax in fig.axes]
                wrapped_fig._recorder = Recorder()
                wrapped_fig._recorder._figure_record = FigureRecord(
                    figsize=tuple(fig.get_size_inches()),
                    dpi=int(fig.dpi),
                )
                fig = wrapped_fig

            # Update editor state
            editor.fig = fig
            editor.recipe_path = full_path
            editor._hitmap_generated = False
            editor._color_map = {}

            # Re-init style overrides
            editor._init_style_overrides(None)

            # Regenerate hitmap
            hitmap_img, editor._color_map = generate_hitmap(editor.fig)
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

            # Render new preview
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
                    "color_map": editor._color_map,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                    "file": file_path,
                }
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/new", methods=["POST"])
    def new_figure():
        """Create a new blank figure."""
        from .. import subplots

        try:
            # Create new blank figure
            fig, ax = subplots()
            ax.set_title("New Figure")
            ax.text(
                0.5,
                0.5,
                "Add plots using fr.edit(fig)",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=12,
                color="gray",
            )

            # Update editor state
            editor.fig = fig
            editor.recipe_path = None
            editor._hitmap_generated = False
            editor._color_map = {}

            # Re-init style overrides
            editor._init_style_overrides(None)

            # Regenerate hitmap
            hitmap_img, editor._color_map = generate_hitmap(editor.fig)
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

            # Render new preview
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
                    "color_map": editor._color_map,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500


__all__ = ["register_core_routes"]
