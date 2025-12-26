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
        """Create a new blank figure and save it as a physical file."""
        from pathlib import Path

        from .. import reproduce, save, subplots
        from .._wrappers._figure import RecordingFigure

        try:
            # Create new blank figure
            fig, ax = subplots()
            ax.set_title("New Figure")

            # Generate unique filename
            working_dir = getattr(editor, "working_dir", Path.cwd())
            base_name = "new_figure"
            counter = 1
            while True:
                file_path = working_dir / f"{base_name}_{counter:03d}.yaml"
                if not file_path.exists():
                    break
                counter += 1

            # Save figure to physical file (creates both .yaml and .png)
            # Skip validation for new blank figures
            png_path = file_path.with_suffix(".png")
            save(fig, png_path, validate=False, verbose=False)

            # Reproduce the figure from the saved file to get a clean state
            reproduced_fig, axes = reproduce(file_path)

            # Wrap in RecordingFigure if needed
            if not isinstance(reproduced_fig, RecordingFigure):
                from .._recorder import FigureRecord, Recorder

                wrapped_fig = RecordingFigure.__new__(RecordingFigure)
                wrapped_fig._fig = reproduced_fig
                wrapped_fig._axes = (
                    [[ax] for ax in reproduced_fig.axes]
                    if hasattr(reproduced_fig, "axes")
                    else [[axes]]
                )
                wrapped_fig._recorder = Recorder()
                wrapped_fig._recorder._figure_record = FigureRecord(
                    figsize=tuple(reproduced_fig.get_size_inches()),
                    dpi=int(reproduced_fig.dpi),
                )
                reproduced_fig = wrapped_fig

            # Update editor state
            editor.fig = reproduced_fig
            editor.recipe_path = file_path
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
                    "file": str(file_path.relative_to(working_dir)),
                    "file_name": file_path.stem,
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/delete", methods=["POST"])
    def delete_figure():
        """Delete a figure file and its associated files (.yaml, .png, .overrides.yaml)."""
        from pathlib import Path

        data = request.get_json() or {}
        file_path = data.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        # Determine base path (without extension)
        if full_path.suffix.lower() in (".yaml", ".yml"):
            base_path = full_path.with_suffix("")
        elif full_path.suffix.lower() == ".png":
            base_path = full_path.with_suffix("")
        else:
            return jsonify({"error": "Invalid file type"}), 400

        # Check if it's the currently open file
        is_current = editor.recipe_path and base_path == editor.recipe_path.with_suffix(
            ""
        )

        deleted_files = []
        errors = []

        # Delete associated files
        for ext in [".yaml", ".yml", ".png", ".overrides.yaml"]:
            target = base_path.with_suffix(ext)
            if target.exists():
                try:
                    target.unlink()
                    deleted_files.append(target.name)
                except Exception as e:
                    errors.append(f"{target.name}: {e}")

        if not deleted_files:
            return jsonify({"error": "No files found to delete"}), 404

        # If we deleted the current file, switch to another or create new
        switch_to = None
        if is_current:
            # Find another file to switch to
            for pattern in ["*.yaml", "*.yml"]:
                for f in working_dir.glob(pattern):
                    if not f.name.startswith(".") and not f.name.endswith(
                        ".overrides.yaml"
                    ):
                        switch_to = str(f.relative_to(working_dir))
                        break
                if switch_to:
                    break

        return jsonify(
            {
                "success": True,
                "deleted": deleted_files,
                "errors": errors if errors else None,
                "was_current": is_current,
                "switch_to": switch_to,
            }
        )

    @app.route("/api/rename", methods=["POST"])
    def rename_figure():
        """Rename a figure file and its associated files (.yaml, .png, .overrides.yaml)."""
        from pathlib import Path

        data = request.get_json() or {}
        old_path = data.get("path")
        new_name = data.get("new_name")

        if not old_path:
            return jsonify({"error": "No file path provided"}), 400
        if not new_name:
            return jsonify({"error": "No new name provided"}), 400

        # Sanitize new name (remove extension if provided, remove path separators)
        new_name = Path(new_name).stem
        if not new_name or "/" in new_name or "\\" in new_name:
            return jsonify({"error": "Invalid new name"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / old_path

        # Determine base paths
        if full_path.suffix.lower() in (".yaml", ".yml"):
            old_base = full_path.with_suffix("")
        elif full_path.suffix.lower() == ".png":
            old_base = full_path.with_suffix("")
        else:
            return jsonify({"error": "Invalid file type"}), 400

        new_base = working_dir / new_name

        # Check if target already exists
        for ext in [".yaml", ".png"]:
            if new_base.with_suffix(ext).exists():
                return jsonify({"error": f"File {new_name}{ext} already exists"}), 400

        renamed_files = []
        errors = []

        # Rename associated files
        for ext in [".yaml", ".yml", ".png", ".overrides.yaml"]:
            old_file = old_base.with_suffix(ext)
            new_file = new_base.with_suffix(ext)
            if old_file.exists():
                try:
                    old_file.rename(new_file)
                    renamed_files.append({"from": old_file.name, "to": new_file.name})
                except Exception as e:
                    errors.append(f"{old_file.name}: {e}")

        if not renamed_files:
            return jsonify({"error": "No files found to rename"}), 404

        # Update editor state if current file was renamed
        if editor.recipe_path and old_base == editor.recipe_path.with_suffix(""):
            editor.recipe_path = new_base.with_suffix(".yaml")

        return jsonify(
            {
                "success": True,
                "renamed": renamed_files,
                "new_name": new_name,
                "errors": errors if errors else None,
            }
        )


__all__ = ["register_core_routes"]
