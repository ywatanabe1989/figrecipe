#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File management routes for the figure editor.
Handles file listing, switching, creation, deletion, renaming, duplication, and download.
"""

from flask import jsonify, request, send_file


def register_file_routes(app, editor):
    """Register file management routes with the Flask app."""
    from pathlib import Path

    from ._helpers import render_with_overrides
    from ._hitmap import generate_hitmap, hitmap_to_base64

    @app.route("/api/files")
    def list_files():
        """List available recipe files in working directory as a tree structure."""
        working_dir = getattr(editor, "working_dir", Path.cwd())

        def build_tree(directory: Path, relative_base: Path = None) -> list:
            """Recursively build tree structure from directory."""
            if relative_base is None:
                relative_base = directory

            items = []

            try:
                entries = sorted(
                    directory.iterdir(),
                    key=lambda x: (not x.is_dir(), x.name.lower()),
                )
            except PermissionError:
                return items

            for entry in entries:
                if entry.name.startswith("."):
                    continue
                if entry.name.endswith(".overrides.yaml"):
                    continue
                if entry.name == "__pycache__":
                    continue

                rel_path = str(entry.relative_to(relative_base))

                if entry.is_dir():
                    children = build_tree(entry, relative_base)
                    if children:
                        items.append(
                            {
                                "path": rel_path,
                                "name": entry.name,
                                "type": "directory",
                                "children": children,
                            }
                        )
                elif entry.suffix.lower() in (".yaml", ".yml"):
                    png_path = entry.with_suffix(".png")
                    has_png = png_path.exists()

                    items.append(
                        {
                            "path": rel_path,
                            "name": entry.stem,
                            "type": "file",
                            "has_image": has_png,
                            "is_current": (
                                editor.recipe_path
                                and entry.resolve() == editor.recipe_path.resolve()
                            ),
                        }
                    )

            return items

        tree = build_tree(working_dir)

        flat_files = []

        def flatten_tree(items):
            for item in items:
                if item["type"] == "directory":
                    flatten_tree(item.get("children", []))
                else:
                    flat_files.append(item)

        flatten_tree(tree)

        return jsonify(
            {
                "tree": tree,
                "files": flat_files,
                "working_dir": str(working_dir),
                "current_file": (
                    str(editor.recipe_path.name) if editor.recipe_path else None
                ),
            }
        )

    @app.route("/api/switch", methods=["POST"])
    def switch_file():
        """Switch to a different recipe file."""
        from .._reproducer import reproduce
        from .._wrappers._figure import RecordingFigure

        data = request.get_json() or {}
        file_path = data.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        if not full_path.exists():
            return jsonify({"error": f"File not found: {file_path}"}), 404

        try:
            fig, axes = reproduce(full_path)

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

            editor.fig = fig
            editor.recipe_path = full_path
            editor._hitmap_generated = False
            editor._color_map = {}

            editor._init_style_overrides(None)

            hitmap_img, editor._color_map = generate_hitmap(editor.fig)
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

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
        from .. import reproduce, save, subplots
        from .._wrappers._figure import RecordingFigure

        try:
            fig, ax = subplots()
            ax.set_title("New Figure")

            working_dir = getattr(editor, "working_dir", Path.cwd())
            base_name = "new_figure"
            counter = 1
            while True:
                file_path = working_dir / f"{base_name}_{counter:03d}.yaml"
                if not file_path.exists():
                    break
                counter += 1

            png_path = file_path.with_suffix(".png")
            save(fig, png_path, validate=False, verbose=False)

            reproduced_fig, axes = reproduce(file_path)

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

            editor.fig = reproduced_fig
            editor.recipe_path = file_path
            editor._hitmap_generated = False
            editor._color_map = {}

            editor._init_style_overrides(None)

            hitmap_img, editor._color_map = generate_hitmap(editor.fig)
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

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
        """Delete a figure file and its associated files."""
        data = request.get_json() or {}
        file_path = data.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        if full_path.suffix.lower() in (".yaml", ".yml"):
            base_path = full_path.with_suffix("")
        elif full_path.suffix.lower() == ".png":
            base_path = full_path.with_suffix("")
        else:
            return jsonify({"error": "Invalid file type"}), 400

        is_current = editor.recipe_path and base_path == editor.recipe_path.with_suffix(
            ""
        )

        deleted_files = []
        errors = []

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

        switch_to = None
        if is_current:
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
        """Rename a figure file and its associated files."""
        data = request.get_json() or {}
        old_path = data.get("path")
        new_name = data.get("new_name")

        if not old_path:
            return jsonify({"error": "No file path provided"}), 400
        if not new_name:
            return jsonify({"error": "No new name provided"}), 400

        new_name = Path(new_name).stem
        if not new_name or "/" in new_name or "\\" in new_name:
            return jsonify({"error": "Invalid new name"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / old_path

        if full_path.suffix.lower() in (".yaml", ".yml"):
            old_base = full_path.with_suffix("")
        elif full_path.suffix.lower() == ".png":
            old_base = full_path.with_suffix("")
        else:
            return jsonify({"error": "Invalid file type"}), 400

        new_base = working_dir / new_name

        for ext in [".yaml", ".png"]:
            if new_base.with_suffix(ext).exists():
                return jsonify({"error": f"File {new_name}{ext} already exists"}), 400

        renamed_files = []
        errors = []

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

    @app.route("/api/duplicate", methods=["POST"])
    def duplicate_figure():
        """Duplicate a figure file and its associated files."""
        import shutil

        data = request.get_json() or {}
        file_path = data.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        if full_path.suffix.lower() in (".yaml", ".yml"):
            base_path = full_path.with_suffix("")
        elif full_path.suffix.lower() == ".png":
            base_path = full_path.with_suffix("")
        else:
            return jsonify({"error": "Invalid file type"}), 400

        original_name = base_path.stem
        counter = 1
        while True:
            new_name = f"{original_name}_copy_{counter:02d}"
            new_base = base_path.parent / new_name
            if not new_base.with_suffix(".yaml").exists():
                break
            counter += 1

        copied_files = []
        errors = []

        for ext in [".yaml", ".yml", ".png", ".overrides.yaml"]:
            old_file = base_path.with_suffix(ext)
            new_file = new_base.with_suffix(ext)
            if old_file.exists():
                try:
                    shutil.copy2(old_file, new_file)
                    copied_files.append({"from": old_file.name, "to": new_file.name})
                except Exception as e:
                    errors.append(f"{old_file.name}: {e}")

        if not copied_files:
            return jsonify({"error": "No files found to duplicate"}), 404

        return jsonify(
            {
                "success": True,
                "copied": copied_files,
                "new_name": new_name,
                "new_path": str(new_base.with_suffix(".yaml").relative_to(working_dir)),
                "errors": errors if errors else None,
            }
        )

    @app.route("/api/download")
    def download_figure():
        """Download a figure file (YAML recipe)."""
        file_path = request.args.get("path")

        if not file_path:
            return jsonify({"error": "No file path provided"}), 400

        working_dir = getattr(editor, "working_dir", Path.cwd())
        full_path = working_dir / file_path

        if full_path.suffix.lower() not in (".yaml", ".yml"):
            yaml_path = full_path.with_suffix(".yaml")
            if yaml_path.exists():
                full_path = yaml_path
            else:
                return jsonify({"error": "File not found"}), 404

        if not full_path.exists():
            return jsonify({"error": "File not found"}), 404

        return send_file(full_path, as_attachment=True, download_name=full_path.name)


__all__ = ["register_file_routes"]
