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

import json
import socket
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

from .._wrappers import RecordingFigure
from ._overrides import (
    StyleOverrides,
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
        """
        self.fig = fig
        self.recipe_path = Path(recipe_path) if recipe_path else None
        self.port = port
        self.dark_mode = False

        # Initialize style overrides system
        self._init_style_overrides(style)

        # Cache for hitmap and color_map
        self._hitmap = None
        self._color_map = None
        self._hitmap_base64 = None

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

        # Get base style from global preset
        base_style = {}
        try:
            from ..styles._style_loader import _STYLE_CACHE
            if _STYLE_CACHE is not None:
                from ..styles import to_subplots_kwargs
                base_style = to_subplots_kwargs(_STYLE_CACHE)
        except Exception:
            pass

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

        from ._hitmap import generate_hitmap, hitmap_to_base64
        from ._renderer import render_download, render_to_base64
        from ._templates import build_html_template

        # Find available port
        self.port = _find_available_port(self.port)

        # Generate initial hitmap
        mpl_fig = self.fig.fig if hasattr(self.fig, 'fig') else self.fig
        self._hitmap, self._color_map = generate_hitmap(mpl_fig)
        self._hitmap_base64 = hitmap_to_base64(self._hitmap)

        # Create Flask app
        app = Flask(__name__)
        editor = self

        @app.route('/')
        def index():
            """Main editor page."""
            # Render initial preview
            base64_img, bboxes, img_size = render_to_base64(
                editor.fig,
                overrides=editor.overrides,
                dark_mode=editor.dark_mode,
            )

            # Build HTML template
            html = build_html_template(
                image_base64=base64_img,
                bboxes=bboxes,
                color_map=editor._color_map,
                style=editor.style,
                overrides=editor.overrides,
                img_size=img_size,
            )

            return render_template_string(html)

        @app.route('/preview')
        def preview():
            """Get current preview image."""
            base64_img, bboxes, img_size = render_to_base64(
                editor.fig,
                overrides=editor.overrides,
                dark_mode=editor.dark_mode,
            )

            return jsonify({
                'image': base64_img,
                'bboxes': bboxes,
                'img_size': {'width': img_size[0], 'height': img_size[1]},
            })

        @app.route('/update', methods=['POST'])
        def update():
            """Update preview with new style overrides."""
            data = request.get_json() or {}

            # Update overrides
            editor.overrides.update(data.get('overrides', {}))
            editor.dark_mode = data.get('dark_mode', editor.dark_mode)

            # Render with new overrides
            base64_img, bboxes, img_size = render_to_base64(
                editor.fig,
                overrides=editor.overrides,
                dark_mode=editor.dark_mode,
            )

            return jsonify({
                'image': base64_img,
                'bboxes': bboxes,
                'img_size': {'width': img_size[0], 'height': img_size[1]},
            })

        @app.route('/hitmap')
        def hitmap():
            """Get hitmap image and color map."""
            return jsonify({
                'image': editor._hitmap_base64,
                'color_map': editor._color_map,
            })

        @app.route('/style')
        def get_style():
            """Get current style configuration."""
            return jsonify({
                'base_style': editor.style_overrides.base_style,
                'programmatic_style': editor.style_overrides.programmatic_style,
                'manual_overrides': editor.style_overrides.manual_overrides,
                'effective_style': editor.get_effective_style(),
                'has_overrides': editor.style_overrides.has_manual_overrides(),
                'manual_timestamp': editor.style_overrides.manual_timestamp,
            })

        @app.route('/save', methods=['POST'])
        def save():
            """Save style overrides (stored separately from recipe)."""
            data = request.get_json() or {}
            editor.style_overrides.update_manual_overrides(data.get('overrides', {}))

            # Save to .overrides.json file
            if editor.recipe_path:
                path = save_overrides(editor.style_overrides, editor.recipe_path)
                return jsonify({
                    'success': True,
                    'path': str(path),
                    'has_overrides': editor.style_overrides.has_manual_overrides(),
                    'timestamp': editor.style_overrides.manual_timestamp,
                })

            return jsonify({
                'success': True,
                'overrides': editor.overrides,
                'has_overrides': editor.style_overrides.has_manual_overrides(),
            })

        @app.route('/restore', methods=['POST'])
        def restore():
            """Restore to original style (clear manual overrides)."""
            editor.style_overrides.clear_manual_overrides()

            # Re-render with original style
            base64_img, bboxes, img_size = render_to_base64(
                editor.fig,
                overrides={},  # No manual overrides
                dark_mode=editor.dark_mode,
            )

            return jsonify({
                'success': True,
                'image': base64_img,
                'bboxes': bboxes,
                'img_size': {'width': img_size[0], 'height': img_size[1]},
                'original_style': editor.style,
            })

        @app.route('/diff')
        def get_diff():
            """Get differences between original and manual overrides."""
            return jsonify({
                'diff': editor.style_overrides.get_diff(),
                'has_overrides': editor.style_overrides.has_manual_overrides(),
            })

        @app.route('/download/<fmt>')
        def download(fmt: str):
            """Download figure in specified format."""
            import io

            fmt = fmt.lower()
            if fmt not in ('png', 'svg', 'pdf'):
                return jsonify({'error': f'Unsupported format: {fmt}'}), 400

            content = render_download(
                editor.fig,
                fmt=fmt,
                dpi=300,
                overrides=editor.overrides,
                dark_mode=editor.dark_mode,
            )

            mimetype = {
                'png': 'image/png',
                'svg': 'image/svg+xml',
                'pdf': 'application/pdf',
            }[fmt]

            filename = f'figure.{fmt}'
            if editor.recipe_path:
                filename = f'{editor.recipe_path.stem}.{fmt}'

            return send_file(
                io.BytesIO(content),
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
            )

        @app.route('/shutdown', methods=['POST'])
        def shutdown():
            """Shutdown the server."""
            func = request.environ.get('werkzeug.server.shutdown')
            if func:
                func()
            return jsonify({'success': True})

        # Start server
        url = f'http://127.0.0.1:{self.port}'
        print(f'Figure Editor running at {url}')
        print('Press Ctrl+C to stop and return overrides')

        if open_browser:
            webbrowser.open(url)

        try:
            app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print('\nEditor closed')

        return self.overrides


def _find_available_port(start_port: int = 5050, max_attempts: int = 100) -> int:
    """
    Find an available port starting from start_port.

    Parameters
    ----------
    start_port : int
        Port to start searching from.
    max_attempts : int
        Maximum number of ports to try.

    Returns
    -------
    int
        Available port number.

    Raises
    ------
    RuntimeError
        If no available port found.
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue

    raise RuntimeError(f'No available ports found in range {start_port}-{start_port + max_attempts}')


__all__ = ['FigureEditor']
