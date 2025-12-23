#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask-based GUI editor for figure styling.

This module provides a web-based interface for interactively adjusting
figure styles with hitmap-based element selection.

Style Override Architecture
---------------------------
Styles are managed in layers with separate storage:

1. Base style (from preset like SCITEX)
2. Programmatic style (from code)
3. Manual overrides (from GUI editor)

Manual overrides are stored separately in `.overrides.json` files,
allowing restoration to original programmatic styles.
"""

# Force Agg backend before any pyplot import to avoid Tkinter threading issues
import matplotlib

matplotlib.use("Agg")

import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from .._wrappers import RecordingFigure
from ._overrides import (
    create_overrides_from_style,
    load_overrides,
    save_overrides,
)


class FigureEditor:
    """
    Browser-based figure style editor using Flask.

    Features:
    - Real-time figure preview with style overrides
    - Hitmap-based element selection
    - Full style property editing (dimensions, fonts, lines, colors, etc.)
    - Dark/light theme toggle
    - Download in PNG/SVG/PDF formats
    - Separate storage of manual overrides (can restore to original)
    """

    def __init__(
        self,
        fig: RecordingFigure,
        recipe_path: Optional[Path] = None,
        style: Optional[Dict[str, Any]] = None,
        port: int = 5050,
        static_png_path: Optional[Path] = None,
        hitmap_base64: Optional[str] = None,
        color_map: Optional[Dict] = None,
    ):
        """
        Initialize figure editor.

        Parameters
        ----------
        fig : RecordingFigure
            Figure to edit.
        recipe_path : Path, optional
            Path to recipe file (if loaded from file).
        style : dict, optional
            Initial style configuration (programmatic).
        port : int
            Flask server port.
        static_png_path : Path, optional
            Path to pre-rendered static PNG (source of truth for initial display).
        hitmap_base64 : str, optional
            Pre-generated hitmap as base64.
        color_map : dict, optional
            Pre-generated color map for hitmap.
        """
        self.fig = fig
        self.recipe_path = Path(recipe_path) if recipe_path else None
        self.port = port
        self.dark_mode = False

        # Pre-rendered static PNG (source of truth)
        self._static_png_path = static_png_path
        self._initial_base64 = None
        if static_png_path and static_png_path.exists():
            import base64

            with open(static_png_path, "rb") as f:
                self._initial_base64 = base64.b64encode(f.read()).decode("utf-8")

        # Initialize style overrides system
        self._init_style_overrides(style)

        # Pre-generated hitmap and color_map
        self._hitmap_base64 = hitmap_base64
        self._color_map = color_map

    def _init_style_overrides(self, programmatic_style: Optional[Dict[str, Any]]):
        """Initialize the layered style override system."""
        # Try to load existing overrides
        if self.recipe_path:
            existing = load_overrides(self.recipe_path)
            if existing:
                self.style_overrides = existing
                # Update programmatic style if provided
                if programmatic_style:
                    self.style_overrides.programmatic_style = programmatic_style
                return

        # Get base style from global preset (always ensure we have a base style)
        base_style = {}
        style_name = "SCITEX"  # Default
        try:
            from ..styles._style_loader import (
                _CURRENT_STYLE_NAME,
                _STYLE_CACHE,
                load_style,
                to_subplots_kwargs,
            )

            # If no style is loaded, load the default SCITEX style
            if _STYLE_CACHE is None:
                load_style("SCITEX")

            # Get the style cache (now guaranteed to exist)
            from ..styles._style_loader import _STYLE_CACHE

            if _STYLE_CACHE is not None:
                base_style = to_subplots_kwargs(_STYLE_CACHE)
                style_name = _CURRENT_STYLE_NAME or "SCITEX"
        except Exception:
            pass

        # Store the style name for UI display
        self._style_name = style_name

        # Create new overrides
        self.style_overrides = create_overrides_from_style(
            base_style=base_style,
            programmatic_style=programmatic_style or {},
        )

    @property
    def style(self) -> Dict[str, Any]:
        """Get the original style (without manual overrides)."""
        return self.style_overrides.get_original_style()

    @property
    def overrides(self) -> Dict[str, Any]:
        """Get current manual overrides."""
        return self.style_overrides.manual_overrides

    @overrides.setter
    def overrides(self, value: Dict[str, Any]):
        """Set manual overrides."""
        self.style_overrides.manual_overrides = value

    def get_effective_style(self) -> Dict[str, Any]:
        """Get the final merged style."""
        return self.style_overrides.get_effective_style()

    def run(self, open_browser: bool = True) -> Dict[str, Any]:
        """
        Run the editor server.

        Parameters
        ----------
        open_browser : bool
            Whether to open browser automatically.

        Returns
        -------
        dict
            Final style overrides after editing session.
        """
        from flask import Flask, jsonify, render_template_string, request, send_file

        from ._bbox import extract_bboxes
        from ._hitmap import generate_hitmap, hitmap_to_base64
        from ._renderer import render_download
        from ._templates import build_html_template

        # Use specified port strictly (no fallback)

        # Use pre-generated hitmap or generate now
        if self._hitmap_base64 is None or self._color_map is None:
            # Pass RecordingFigure to preserve record for plot type detection
            hitmap, self._color_map = generate_hitmap(self.fig)
            self._hitmap_base64 = hitmap_to_base64(hitmap)

        # Create Flask app
        app = Flask(__name__)
        editor = self

        @app.route("/")
        def index():
            """Main editor page."""
            # Always render with effective style (base + programmatic + manual)
            # to ensure YAML style settings are applied
            base64_img, bboxes, img_size = _render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            # Get style name (default to SCITEX if not set)
            style_name = getattr(editor, "_style_name", "SCITEX")

            # Build HTML template
            html = build_html_template(
                image_base64=base64_img,
                bboxes=bboxes,
                color_map=editor._color_map,
                style=editor.style,
                overrides=editor.get_effective_style(),
                img_size=img_size,
                style_name=style_name,
            )

            return render_template_string(html)

        @app.route("/preview")
        def preview():
            """Get current preview image."""
            # Always render with effective style (base + programmatic + manual)
            base64_img, bboxes, img_size = _render_with_overrides(
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

        @app.route("/update", methods=["POST"])
        def update():
            """Update preview with new style overrides."""
            data = request.get_json() or {}

            # Update manual overrides
            editor.overrides.update(data.get("overrides", {}))
            editor.dark_mode = data.get("dark_mode", editor.dark_mode)

            # Re-render with effective style (base + programmatic + manual)
            base64_img, bboxes, img_size = _render_with_overrides(
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
            """Get hitmap image and color map."""
            return jsonify(
                {
                    "image": editor._hitmap_base64,
                    "color_map": editor._color_map,
                }
            )

        def _to_json_serializable(obj):
            """Convert numpy arrays and other non-serializable objects to JSON-safe types."""
            import numpy as np

            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: _to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [_to_json_serializable(item) for item in obj]
            return obj

        @app.route("/calls")
        def get_calls():
            """Get all recorded calls with their signatures."""
            from .._signatures import get_signature

            calls_data = {}
            if hasattr(editor.fig, "record"):
                for ax_key, ax_record in editor.fig.record.axes.items():
                    for call in ax_record.calls:
                        call_id = call.id
                        func_name = call.function
                        sig = get_signature(func_name)

                        calls_data[call_id] = {
                            "function": func_name,
                            "ax_key": ax_key,
                            "args": _to_json_serializable(call.args),
                            "kwargs": _to_json_serializable(call.kwargs),
                            "signature": {
                                "args": sig.get("args", []),
                                "kwargs": {
                                    k: v
                                    for k, v in sig.get("kwargs", {}).items()
                                    if k != "**kwargs"
                                },
                            },
                        }

            return jsonify(calls_data)

        @app.route("/call/<call_id>")
        def get_call(call_id):
            """Get recorded call data by call_id."""
            from .._signatures import get_signature

            if hasattr(editor.fig, "record"):
                for ax_key, ax_record in editor.fig.record.axes.items():
                    for call in ax_record.calls:
                        if call.id == call_id:
                            sig = get_signature(call.function)
                            return jsonify(
                                {
                                    "call_id": call_id,
                                    "function": call.function,
                                    "ax_key": ax_key,
                                    "args": call.args,
                                    "kwargs": call.kwargs,
                                    "signature": {
                                        "args": sig.get("args", []),
                                        "kwargs": {
                                            k: v
                                            for k, v in sig.get("kwargs", {}).items()
                                            if k != "**kwargs"
                                        },
                                    },
                                }
                            )

            return jsonify({"error": f"Call {call_id} not found"}), 404

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

        @app.route("/save", methods=["POST"])
        def save():
            """Save style overrides (stored separately from recipe)."""
            data = request.get_json() or {}
            editor.style_overrides.update_manual_overrides(data.get("overrides", {}))

            # Save to .overrides.json file
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
            """Restore to original style (clear manual overrides)."""
            editor.style_overrides.clear_manual_overrides()

            # Use pre-rendered static PNG (source of truth)
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
                # Fallback: re-render with reproduce pipeline
                base64_img, bboxes, img_size = _render_with_overrides(
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

        @app.route("/update_call", methods=["POST"])
        def update_call():
            """Update a call's kwargs and re-render.

            Only display kwargs are editable (orientation, colors, etc.).
            Data (x, y arrays) remains read-only for scientific integrity.
            """
            from .._reproducer import reproduce_from_record

            data = request.get_json() or {}
            call_id = data.get("call_id")
            param = data.get("param")
            value = data.get("value")

            if not call_id or not param:
                return jsonify({"error": "Missing call_id or param"}), 400

            # Find and update the call in the record
            updated = False
            if hasattr(editor.fig, "record"):
                for ax_key, ax_record in editor.fig.record.axes.items():
                    for call in ax_record.calls:
                        if call.id == call_id:
                            # Track the override in style_overrides
                            editor.style_overrides.set_call_override(
                                call_id, param, value
                            )

                            # Update the kwarg in the record
                            if value is None or value == "" or value == "null":
                                call.kwargs.pop(param, None)
                            else:
                                call.kwargs[param] = value
                            updated = True
                            break
                    if updated:
                        break

            if not updated:
                return jsonify({"error": f"Call {call_id} not found"}), 404

            # Re-reproduce the figure from the updated record
            try:
                new_fig, new_axes = reproduce_from_record(editor.fig.record)

                # Apply style overrides to the new figure
                effective_style = editor.get_effective_style()
                base64_img, bboxes, img_size = _render_with_overrides(
                    new_fig,
                    effective_style if effective_style else None,
                    editor.dark_mode,
                )

                # Update editor's figure reference
                editor.fig = new_fig

                # Reload hitmap and color map
                hitmap_b64, color_map = generate_hitmap(
                    new_fig, img_size[0], img_size[1]
                )
                editor._color_map = color_map

            except Exception as e:
                import traceback

                traceback.print_exc()
                return jsonify({"error": f"Re-render failed: {str(e)}"}), 500

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                    "call_id": call_id,
                    "param": param,
                    "value": value,
                    "has_call_overrides": editor.style_overrides.has_call_overrides(),
                }
            )

        @app.route("/download/<fmt>")
        def download(fmt: str):
            """Download figure in specified format.

            Note: Downloads always use light mode for scientific document compatibility.
            Transparent backgrounds are preserved.
            """
            import io

            fmt = fmt.lower()
            if fmt not in ("png", "svg", "pdf"):
                return jsonify({"error": f"Unsupported format: {fmt}"}), 400

            # Use effective style (base + programmatic + manual)
            effective_style = editor.get_effective_style()
            # Always use light mode for scientific documents (dark_mode=False)
            content = render_download(
                editor.fig,
                fmt=fmt,
                dpi=300,
                overrides=effective_style if effective_style else None,
                dark_mode=False,  # Scientific documents require light mode
            )

            mimetype = {
                "png": "image/png",
                "svg": "image/svg+xml",
                "pdf": "application/pdf",
            }[fmt]

            filename = f"figure.{fmt}"
            if editor.recipe_path:
                filename = f"{editor.recipe_path.stem}.{fmt}"

            return send_file(
                io.BytesIO(content),
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
            )

        @app.route("/shutdown", methods=["POST"])
        def shutdown():
            """Shutdown the server."""
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
            return jsonify({"success": True})

        # Start server
        url = f"http://127.0.0.1:{self.port}"
        print(f"Figure Editor running at {url}")
        print("Press Ctrl+C to stop and return overrides")

        if open_browser:
            webbrowser.open(url)

        try:
            app.run(host="127.0.0.1", port=self.port, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print("\nEditor closed")

        return self.overrides


def _render_with_overrides(
    fig, overrides: Optional[Dict[str, Any]], dark_mode: bool = False
):
    """
    Re-render figure with overrides applied directly.

    Applies style overrides directly to the existing figure for reliable rendering.
    """
    import base64
    import io

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from PIL import Image

    from ._bbox import extract_bboxes
    from ._renderer import _apply_dark_mode, _apply_overrides

    # Get the underlying matplotlib figure
    new_fig = fig.fig if hasattr(fig, "fig") else fig

    # Switch to Agg backend to avoid Tkinter thread issues
    new_fig.set_canvas(FigureCanvasAgg(new_fig))

    # Apply overrides directly to existing figure
    if overrides:
        _apply_overrides(new_fig, overrides)

    # Apply dark mode if requested
    if dark_mode:
        _apply_dark_mode(new_fig)

    # Save to PNG using same params as static save
    buf = io.BytesIO()
    new_fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    png_bytes = buf.read()
    base64_str = base64.b64encode(png_bytes).decode("utf-8")

    # Get image size
    buf.seek(0)
    img = Image.open(buf)
    img_size = img.size

    # Extract bboxes
    original_dpi = new_fig.dpi
    new_fig.set_dpi(150)
    new_fig.canvas.draw()
    bboxes = extract_bboxes(new_fig, img_size[0], img_size[1])
    new_fig.set_dpi(original_dpi)

    return base64_str, bboxes, img_size


__all__ = ["FigureEditor"]
