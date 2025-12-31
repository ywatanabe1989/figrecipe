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
from ._overrides import create_overrides_from_style, load_overrides


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
    - Hot reload: server restarts on source file changes (like Django)
    """

    def __init__(
        self,
        fig: RecordingFigure,
        recipe_path: Optional[Path] = None,
        style: Optional[Dict[str, Any]] = None,
        port: int = 5050,
        host: str = "127.0.0.1",
        static_png_path: Optional[Path] = None,
        hitmap_base64: Optional[str] = None,
        color_map: Optional[Dict] = None,
        hot_reload: bool = False,
        working_dir: Optional[Path] = None,
        desktop: bool = False,
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
        hot_reload : bool, optional
            Enable hot reload - server restarts on source file changes.
        working_dir : Path, optional
            Working directory for file switching (default: current directory).
        desktop : bool, optional
            Launch as native desktop window using pywebview.
        """
        self.fig = fig
        self.desktop = desktop
        self.recipe_path = Path(recipe_path) if recipe_path else None
        self.port = port
        self.host = host
        self.hot_reload = hot_reload
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()

        # Load user preferences
        from ._preferences import load_preferences

        prefs = load_preferences()
        self.dark_mode = prefs.get("dark_mode", False)

        # Pre-rendered static PNG (source of truth)
        self._static_png_path = static_png_path
        self._initial_base64 = None
        if static_png_path and static_png_path.exists():
            import base64

            with open(static_png_path, "rb") as f:
                self._initial_base64 = base64.b64encode(f.read()).decode("utf-8")

        # Initialize style overrides system (captures original positions into base_style)
        self._init_style_overrides(style)

        # Pre-generated hitmap and color_map
        # Use empty dict as default to prevent JavaScript errors
        # when page loads before hitmap is generated
        self._hitmap_base64 = hitmap_base64
        self._color_map = color_map if color_map is not None else {}

    def _init_style_overrides(self, programmatic_style: Optional[Dict[str, Any]]):
        """Initialize the layered style override system."""
        # Try to load existing overrides
        if self.recipe_path:
            existing = load_overrides(self.recipe_path)
            if existing:
                self.style_overrides = existing
                if programmatic_style:
                    self.style_overrides.programmatic_style = programmatic_style
                # Ensure original positions are captured even when loading existing overrides
                self._ensure_original_positions_in_base_style()
                return

        # Get base style from global preset
        base_style = {}
        style_name = "SCITEX"
        try:
            from ..styles._style_loader import (
                _CURRENT_STYLE_NAME,
                _STYLE_CACHE,
                load_style,
                to_subplots_kwargs,
            )

            if _STYLE_CACHE is None:
                load_style("SCITEX")

            from ..styles._style_loader import _STYLE_CACHE

            if _STYLE_CACHE is not None:
                base_style = to_subplots_kwargs(_STYLE_CACHE)
                style_name = _CURRENT_STYLE_NAME or "SCITEX"
        except Exception:
            pass

        self._style_name = style_name

        # Capture original annotation positions into base_style for restore
        annotation_positions = self._capture_annotation_positions()
        for key, pos_data in annotation_positions.items():
            base_style[f"_original_{key}"] = pos_data

        # Capture original axes positions into base_style for restore
        axes_positions = self._capture_axes_positions()
        for ax_idx, pos in axes_positions.items():
            base_style[f"_original_axes_position_{ax_idx}"] = pos

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

    def _ensure_original_positions_in_base_style(self) -> None:
        """Ensure original positions are captured in base_style (for existing overrides)."""
        base_style = self.style_overrides.base_style

        # Add annotation positions if not present
        annotation_positions = self._capture_annotation_positions()
        for key, pos_data in annotation_positions.items():
            base_key = f"_original_{key}"
            if base_key not in base_style:
                base_style[base_key] = pos_data

        # Add axes positions if not present
        axes_positions = self._capture_axes_positions()
        for ax_idx, pos in axes_positions.items():
            base_key = f"_original_axes_position_{ax_idx}"
            if base_key not in base_style:
                base_style[base_key] = pos

    def _capture_axes_positions(self) -> Dict[int, list]:
        """Capture current axes positions (matplotlib coords: [left, bottom, width, height])."""
        mpl_fig = self.fig.fig if hasattr(self.fig, "fig") else self.fig
        axes = mpl_fig.get_axes()
        positions = {}
        for i, ax in enumerate(axes):
            bbox = ax.get_position()
            positions[i] = [bbox.x0, bbox.y0, bbox.width, bbox.height]
        return positions

    def restore_axes_positions(self) -> None:
        """Restore axes to their original positions from base_style."""
        base_style = self.style_overrides.base_style
        mpl_fig = self.fig.fig if hasattr(self.fig, "fig") else self.fig
        axes = mpl_fig.get_axes()
        for i, ax in enumerate(axes):
            key = f"_original_axes_position_{i}"
            if key in base_style:
                pos = base_style[key]
                ax.set_position(pos)

    def _capture_annotation_positions(self) -> Dict[str, dict]:
        """Capture current annotation (text) positions for each axis."""
        mpl_fig = self.fig.fig if hasattr(self.fig, "fig") else self.fig
        axes = mpl_fig.get_axes()
        positions = {}
        for ax_idx, ax in enumerate(axes):
            for text_idx, text_obj in enumerate(ax.texts):
                key = f"ax{ax_idx}_text{text_idx}"
                pos = text_obj.get_position()
                positions[key] = {
                    "position": [
                        float(pos[0]),
                        float(pos[1]),
                    ],  # Convert to float for JSON
                    "transform_is_axes": bool(text_obj.get_transform() == ax.transAxes),
                }
        return positions

    def restore_annotation_positions(self) -> None:
        """Restore annotations to their original positions from base_style."""
        base_style = self.style_overrides.base_style
        mpl_fig = self.fig.fig if hasattr(self.fig, "fig") else self.fig
        axes = mpl_fig.get_axes()
        for ax_idx, ax in enumerate(axes):
            for text_idx, text_obj in enumerate(ax.texts):
                key = f"_original_ax{ax_idx}_text{text_idx}"
                if key in base_style:
                    orig = base_style[key]
                    text_obj.set_position(tuple(orig["position"]))

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
        from flask import Flask

        from ._routes_annotation import register_annotation_routes
        from ._routes_axis import register_axis_routes

        # DISABLED: Snapshot feature corrupts figure state via visibility changes
        # from ._routes_snapshot import register_snapshot_routes
        from ._routes_captions import register_caption_routes
        from ._routes_core import register_core_routes
        from ._routes_datatable import register_datatable_routes
        from ._routes_element import register_element_routes
        from ._routes_files import register_file_routes
        from ._routes_image import register_image_routes
        from ._routes_style import register_style_routes

        # Defer hitmap generation until first request (lazy loading)
        self._hitmap_generated = self._hitmap_base64 is not None

        # Create Flask app with static folder for assets (click sounds, etc.)
        static_folder = Path(__file__).parent / "static"
        app = Flask(
            __name__, static_folder=str(static_folder), static_url_path="/static"
        )

        # Register all routes
        register_core_routes(app, self)
        register_file_routes(app, self)
        register_style_routes(app, self)
        register_axis_routes(app, self)
        register_element_routes(app, self)
        register_image_routes(app, self)
        register_datatable_routes(app, self)
        register_annotation_routes(app, self)
        register_caption_routes(app, self)
        # DISABLED: register_snapshot_routes(app, self)

        # Start server
        url = f"http://{self.host}:{self.port}"

        if self.desktop:
            # Desktop mode using pywebview
            return self._run_desktop(app, url)
        else:
            # Browser mode
            return self._run_browser(app, url, open_browser)

    def _run_browser(self, app, url: str, open_browser: bool) -> Dict[str, Any]:
        """Run editor in browser mode."""
        print(f"Figure Editor running at {url}")

        if self.hot_reload:
            print("Hot reload ENABLED - server will restart on source file changes")
        print("Press Ctrl+C to stop and return overrides")

        if open_browser:
            webbrowser.open(url)

        try:
            app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True,
            )
        except KeyboardInterrupt:
            print("\nEditor closed")

        return self.overrides

    def _run_desktop(self, app, url: str) -> Dict[str, Any]:
        """Run editor as native desktop window using pywebview."""
        try:
            import webview
        except ImportError:
            raise ImportError(
                "pywebview is required for desktop mode. "
                "Install with: pip install figrecipe[desktop]"
            )

        import threading

        print("Figure Editor (Desktop Mode)")
        print("Close the window to stop and return overrides")

        # Start Flask in a background thread
        def run_flask():
            import logging

            # Suppress Flask logging in desktop mode
            log = logging.getLogger("werkzeug")
            log.setLevel(logging.ERROR)
            app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Wait briefly for Flask to start
        import time

        time.sleep(0.5)

        # Create native window (variable needed for pywebview lifecycle)
        _window = webview.create_window(
            title="FigRecipe Editor",
            url=url,
            width=1400,
            height=900,
            resizable=True,
            min_size=(800, 600),
        )

        # Start webview (blocks until window is closed)
        webview.start()

        print("\nEditor closed")
        return self.overrides


__all__ = ["FigureEditor"]
