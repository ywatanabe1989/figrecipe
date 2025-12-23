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

        # Defer hitmap generation until first request (lazy loading)
        # This makes the editor start immediately
        self._hitmap_generated = self._hitmap_base64 is not None

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
            """Get hitmap image and color map (lazy generation on first request)."""
            # Generate hitmap on first request if not already done
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

        @app.route("/theme")
        def get_theme():
            """Get current theme YAML content for display."""
            import io as yaml_io

            from ruamel.yaml import YAML

            style = editor.get_effective_style()
            style_name = style.get("_name", "SCITEX")

            # Serialize to YAML
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
                # Load the new preset
                new_style = load_preset(theme_name)

                if new_style is None:
                    return jsonify({"error": f"Theme '{theme_name}' not found"}), 404

                # Update the base style
                editor.style_overrides.base_style = dict(new_style)
                editor.style_overrides.base_style["_name"] = theme_name

                # Reproduce the figure from the record
                if hasattr(editor.fig, "record") and editor.fig.record is not None:
                    # Update the record's style to use new theme
                    old_style = editor.fig.record.style
                    editor.fig.record.style = dict(new_style)

                    # Reproduce figure with new style
                    new_fig, new_ax = reproduce_from_record(editor.fig.record)
                    editor.fig = new_fig

                    # Restore original style in record for future reference
                    editor.fig.record.style = old_style

                # Apply behavior settings from new theme directly to figure
                mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
                behavior = new_style.get("behavior", {})
                for ax in mpl_fig.get_axes():
                    # Apply spine visibility
                    hide_top = behavior.get("hide_top_spine", True)
                    hide_right = behavior.get("hide_right_spine", True)
                    ax.spines["top"].set_visible(not hide_top)
                    ax.spines["right"].set_visible(not hide_right)

                    # Apply grid setting
                    if behavior.get("grid", False):
                        ax.grid(True, alpha=0.3)
                    else:
                        ax.grid(False)

                # Re-render with new theme
                base64_img, bboxes, img_size = _render_with_overrides(
                    editor.fig,
                    editor.get_effective_style(),
                    editor.dark_mode,
                )

                # Get updated form values from new style
                form_values = _get_form_values_from_style(editor.get_effective_style())

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

        @app.route("/update_label", methods=["POST"])
        def update_label():
            """Update axis labels (title, xlabel, ylabel, suptitle).

            These are editable text elements that don't affect data integrity.
            """
            data = request.get_json() or {}
            label_type = data.get("label_type")  # title, xlabel, ylabel, suptitle
            text = data.get("text", "")
            ax_index = data.get("ax_index", 0)  # For multi-axes figures

            if not label_type:
                return jsonify({"error": "Missing label_type"}), 400

            # Get the underlying matplotlib figure
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes = mpl_fig.get_axes()

            if not axes:
                return jsonify({"error": "No axes found"}), 400

            # Get target axes (default to first)
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
                        # Clear suptitle by setting to empty string
                        if mpl_fig._suptitle:
                            mpl_fig._suptitle.set_text("")
                else:
                    return jsonify({"error": f"Unknown label_type: {label_type}"}), 400

                # Track override
                editor.style_overrides.manual_overrides[f"label_{label_type}"] = text

                # Re-render
                base64_img, bboxes, img_size = _render_with_overrides(
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

            labels = {
                "title": "",
                "xlabel": "",
                "ylabel": "",
                "suptitle": "",
            }

            if axes:
                ax = axes[0]  # Use first axes for now
                labels["title"] = ax.get_title()
                labels["xlabel"] = ax.get_xlabel()
                labels["ylabel"] = ax.get_ylabel()

            if mpl_fig._suptitle:
                labels["suptitle"] = mpl_fig._suptitle.get_text()

            return jsonify(labels)

        @app.route("/update_axis_type", methods=["POST"])
        def update_axis_type():
            """Update axis type (numerical vs categorical).

            Numerical: linear scale with auto ticks
            Categorical: discrete labels at integer positions
            """
            data = request.get_json() or {}
            axis = data.get("axis")  # "x" or "y"
            axis_type = data.get("type")  # "numerical" or "categorical"
            labels = data.get("labels", [])  # For categorical: list of labels
            ax_index = data.get("ax_index", 0)

            if not axis or not axis_type:
                return jsonify({"error": "Missing axis or type"}), 400

            # Get the underlying matplotlib figure
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes_list = mpl_fig.get_axes()

            if not axes_list:
                return jsonify({"error": "No axes found"}), 400

            ax = axes_list[min(ax_index, len(axes_list) - 1)]

            try:
                if axis == "x":
                    if axis_type == "categorical" and labels:
                        # Set categorical x-axis
                        positions = list(range(len(labels)))
                        ax.set_xticks(positions)
                        ax.set_xticklabels(labels)
                    else:
                        # Reset to numerical
                        ax.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
                        ax.xaxis.set_major_formatter(
                            matplotlib.ticker.ScalarFormatter()
                        )
                elif axis == "y":
                    if axis_type == "categorical" and labels:
                        # Set categorical y-axis
                        positions = list(range(len(labels)))
                        ax.set_yticks(positions)
                        ax.set_yticklabels(labels)
                    else:
                        # Reset to numerical
                        ax.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())
                        ax.yaxis.set_major_formatter(
                            matplotlib.ticker.ScalarFormatter()
                        )

                # Track override
                key = f"axis_{axis}_type"
                editor.style_overrides.manual_overrides[key] = axis_type
                if labels:
                    editor.style_overrides.manual_overrides[f"axis_{axis}_labels"] = (
                        labels
                    )

                # Re-render
                base64_img, bboxes, img_size = _render_with_overrides(
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

                # Check if x-axis has custom tick labels
                x_ticklabels = [t.get_text() for t in ax.get_xticklabels()]
                if x_ticklabels and any(t for t in x_ticklabels):
                    info["x_type"] = "categorical"
                    info["x_labels"] = x_ticklabels

                # Check if y-axis has custom tick labels
                y_ticklabels = [t.get_text() for t in ax.get_yticklabels()]
                if y_ticklabels and any(t for t in y_ticklabels):
                    info["y_type"] = "categorical"
                    info["y_labels"] = y_ticklabels

            return jsonify(info)

        @app.route("/update_legend_position", methods=["POST"])
        def update_legend_position():
            """Update legend position, visibility, or custom xy coordinates.

            For custom positioning, uses bbox_to_anchor with axes coordinates.
            """
            data = request.get_json() or {}
            loc = data.get("loc")  # 'best', 'upper right', 'custom', etc.
            x = data.get("x")  # For custom: 0-1+ (axes coordinates)
            y = data.get("y")  # For custom: 0-1+ (axes coordinates)
            visible = data.get("visible")  # True/False for show/hide
            ax_index = data.get("ax_index", 0)

            # Get the underlying matplotlib figure
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes_list = mpl_fig.get_axes()

            if not axes_list:
                return jsonify({"error": "No axes found"}), 400

            ax = axes_list[min(ax_index, len(axes_list) - 1)]
            legend = ax.get_legend()

            if legend is None:
                return jsonify({"error": "No legend found on this axes"}), 400

            try:
                # Handle visibility toggle
                if visible is not None:
                    legend.set_visible(visible)
                    editor.style_overrides.manual_overrides["legend_visible"] = visible

                # Handle position update only if loc is provided
                if loc is not None:
                    if loc == "custom" and x is not None and y is not None:
                        # Custom positioning with bbox_to_anchor
                        legend.set_bbox_to_anchor((float(x), float(y)))
                        legend._loc = 2  # upper left as reference point
                    else:
                        # Standard location string
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
                        # Clear bbox_to_anchor when using standard loc
                        legend.set_bbox_to_anchor(None)

                    # Track override
                    editor.style_overrides.manual_overrides["legend_loc"] = loc
                    if loc == "custom":
                        editor.style_overrides.manual_overrides["legend_x"] = x
                        editor.style_overrides.manual_overrides["legend_y"] = y

                # Re-render
                base64_img, bboxes, img_size = _render_with_overrides(
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

                    # Get location code and convert to string
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

                    # Check for bbox_to_anchor (custom position)
                    bbox = legend.get_bbox_to_anchor()
                    if bbox is not None:
                        # Get coordinates from bbox
                        try:
                            bounds = bbox.bounds
                            if bounds[0] != 0 or bounds[1] != 0:
                                info["loc"] = "custom"
                                info["x"] = bounds[0]
                                info["y"] = bounds[1]
                        except Exception:
                            pass

            return jsonify(info)

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
                from ._hitmap import hitmap_to_base64

                hitmap_img, color_map = generate_hitmap(
                    new_fig, img_size[0], img_size[1]
                )
                editor._color_map = color_map
                editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
                editor._hitmap_generated = True

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


def _get_form_values_from_style(style: Dict[str, Any]) -> Dict[str, Any]:
    """Extract form field values from a style dictionary.

    Maps style dictionary values to HTML form input IDs.

    Parameters
    ----------
    style : dict
        Style configuration dictionary

    Returns
    -------
    dict
        Mapping of form input IDs to values
    """
    values = {}

    # Axes dimensions
    if "axes" in style:
        values["axes_width_mm"] = style["axes"].get("width_mm", 80)
        values["axes_height_mm"] = style["axes"].get("height_mm", 55)
        values["axes_thickness_mm"] = style["axes"].get("thickness_mm", 0.2)

    # Margins
    if "margins" in style:
        values["margins_left_mm"] = style["margins"].get("left_mm", 12)
        values["margins_right_mm"] = style["margins"].get("right_mm", 3)
        values["margins_bottom_mm"] = style["margins"].get("bottom_mm", 10)
        values["margins_top_mm"] = style["margins"].get("top_mm", 3)

    # Spacing
    if "spacing" in style:
        values["spacing_horizontal_mm"] = style["spacing"].get("horizontal_mm", 8)
        values["spacing_vertical_mm"] = style["spacing"].get("vertical_mm", 8)

    # Fonts
    if "fonts" in style:
        values["fonts_family"] = style["fonts"].get("family", "Arial")
        values["fonts_axis_label_pt"] = style["fonts"].get("axis_label_pt", 7)
        values["fonts_tick_label_pt"] = style["fonts"].get("tick_label_pt", 6)
        values["fonts_title_pt"] = style["fonts"].get("title_pt", 8)
        values["fonts_legend_pt"] = style["fonts"].get("legend_pt", 6)

    # Ticks
    if "ticks" in style:
        values["ticks_length_mm"] = style["ticks"].get("length_mm", 1.0)
        values["ticks_thickness_mm"] = style["ticks"].get("thickness_mm", 0.2)
        values["ticks_direction"] = style["ticks"].get("direction", "out")

    # Lines
    if "lines" in style:
        values["lines_trace_mm"] = style["lines"].get("trace_mm", 0.2)

    # Markers
    if "markers" in style:
        values["markers_size_mm"] = style["markers"].get("size_mm", 0.8)

    # Output
    if "output" in style:
        values["output_dpi"] = style["output"].get("dpi", 300)

    # Behavior
    if "behavior" in style:
        values["behavior_hide_top_spine"] = style["behavior"].get(
            "hide_top_spine", True
        )
        values["behavior_hide_right_spine"] = style["behavior"].get(
            "hide_right_spine", True
        )
        values["behavior_grid"] = style["behavior"].get("grid", False)

    # Legend
    if "legend" in style:
        values["legend_frameon"] = style["legend"].get("frameon", True)

    return values


def _render_with_overrides(
    fig, overrides: Optional[Dict[str, Any]], dark_mode: bool = False
):
    """
    Re-render figure with overrides applied directly.

    Applies style overrides directly to the existing figure for reliable rendering.
    """
    import base64
    import io
    import warnings

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from PIL import Image

    from ._bbox import extract_bboxes
    from ._renderer import _apply_dark_mode, _apply_overrides

    # Get the underlying matplotlib figure
    new_fig = fig.fig if hasattr(fig, "fig") else fig

    # Safety check: validate figure size before rendering
    fig_width, fig_height = new_fig.get_size_inches()
    dpi = 150
    pixel_width = fig_width * dpi
    pixel_height = fig_height * dpi

    # Sanity check: prevent enormous figures (max 10000x10000 pixels)
    MAX_PIXELS = 10000
    if pixel_width > MAX_PIXELS or pixel_height > MAX_PIXELS:
        # Reset to reasonable size
        new_fig.set_size_inches(
            min(fig_width, MAX_PIXELS / dpi), min(fig_height, MAX_PIXELS / dpi)
        )

    # Switch to Agg backend to avoid Tkinter thread issues
    new_fig.set_canvas(FigureCanvasAgg(new_fig))

    # Disable constrained_layout if present (can cause rendering issues on repeated calls)
    # Store original state to restore later
    layout_engine = new_fig.get_layout_engine()
    if layout_engine is not None and hasattr(layout_engine, "__class__"):
        layout_name = layout_engine.__class__.__name__
        if "Constrained" in layout_name:
            new_fig.set_layout_engine("none")

    # Apply overrides directly to existing figure
    if overrides:
        _apply_overrides(new_fig, overrides)

    # Apply dark mode if requested
    if dark_mode:
        _apply_dark_mode(new_fig)

    # Validate axes bounds before rendering (prevent infinite/invalid extents)
    for ax in new_fig.get_axes():
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        # Check for invalid limits (inf, nan, or extremely large)
        if any(not (-1e10 < v < 1e10) for v in xlim + ylim):
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)

    # Save to PNG using same params as static save
    # Catch constrained_layout warnings and handle gracefully
    buf = io.BytesIO()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "constrained_layout not applied")
        try:
            new_fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        except (MemoryError, ValueError):
            # Fall back to saving without bbox_inches="tight"
            buf = io.BytesIO()
            new_fig.savefig(buf, format="png", dpi=150)
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
