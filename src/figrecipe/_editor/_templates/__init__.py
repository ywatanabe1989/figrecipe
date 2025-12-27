#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML/CSS/JS template builder for figure editor.

Uses YAML-compatible flattened key names from to_subplots_kwargs() as the
single source of truth. No custom key mapping is needed since all keys
now match the HTML input IDs directly.
"""

import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from ._html import HTML_TEMPLATE
from ._html_components import HTML_FILE_BROWSER
from ._html_datatable import HTML_DATATABLE_PANEL
from ._scripts import SCRIPTS
from ._styles import STYLES

# Server start time for debugging template reloads
_SERVER_START_TIME = datetime.now().strftime("%H:%M:%S")

# Load SciTeX icon as base64
_SCITEX_ICON_PATH = (
    Path(__file__).parent.parent.parent.parent.parent / "docs" / "scitex-icon.png"
)
_SCITEX_ICON_BASE64 = ""
if _SCITEX_ICON_PATH.exists():
    with open(_SCITEX_ICON_PATH, "rb") as f:
        _SCITEX_ICON_BASE64 = base64.b64encode(f.read()).decode("utf-8")


def build_html_template(
    image_base64: str,
    bboxes: Dict[str, Any],
    color_map: Dict[str, Any],
    style: Dict[str, Any],
    overrides: Dict[str, Any],
    img_size: Tuple[int, int],
    style_name: str = "SCITEX",
    hot_reload: bool = False,
    dark_mode: bool = False,
) -> str:
    """
    Build complete HTML template for figure editor.

    Style keys are expected to be YAML-compatible flattened names that
    match the HTML input IDs directly (e.g., 'fonts_axis_label_pt').

    Parameters
    ----------
    image_base64 : str
        Base64-encoded preview image.
    bboxes : dict
        Element bounding boxes.
    color_map : dict
        Hitmap color-to-element mapping.
    style : dict
        Base style configuration with YAML-compatible keys.
    overrides : dict
        Current style overrides with YAML-compatible keys.
    img_size : tuple
        (width, height) of preview image.
    style_name : str
        Name of the applied style preset (e.g., "SCITEX", "MATPLOTLIB").
    hot_reload : bool
        Enable hot reload auto-reconnect JavaScript.
    dark_mode : bool
        Initial dark mode state from saved preferences.

    Returns
    -------
    str
        Complete HTML document.
    """
    # Merge style and overrides for initial values
    # Keys should already match HTML input IDs (YAML-compatible flattened)
    initial_values = {**style, **overrides}

    # Hot reload JavaScript for auto-reconnect on server restart
    hot_reload_script = ""
    if hot_reload:
        hot_reload_script = """
// Hot Reload: Auto-reconnect when server restarts
(function() {
    let isReconnecting = false;
    let pingInterval = null;

    function showReloadBanner(show) {
        let banner = document.getElementById('hot-reload-banner');
        if (!banner && show) {
            banner = document.createElement('div');
            banner.id = 'hot-reload-banner';
            banner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#f59e0b;' +
                'color:#000;text-align:center;padding:8px;z-index:9999;font-weight:bold;';
            banner.textContent = 'Server restarting... will reload automatically';
            document.body.prepend(banner);
        }
        if (banner) {
            banner.style.display = show ? 'block' : 'none';
        }
    }

    function ping() {
        fetch('/ping', {cache: 'no-store'})
            .then(r => {
                if (r.ok && isReconnecting) {
                    // Server is back! Reload the page
                    console.log('[Hot Reload] Server is back, reloading...');
                    window.location.reload();
                }
            })
            .catch(() => {
                if (!isReconnecting) {
                    console.log('[Hot Reload] Server disconnected, waiting for restart...');
                    isReconnecting = true;
                    showReloadBanner(true);
                }
            });
    }

    // Start pinging every 500ms
    pingInterval = setInterval(ping, 500);
    console.log('[Hot Reload] Enabled - watching for server restarts');
})();
"""

    # Inject data into template
    html = HTML_TEMPLATE
    html = html.replace("<!-- FILE_BROWSER_PLACEHOLDER -->", HTML_FILE_BROWSER)

    # Insert datatable panel before preview panel
    html = html.replace(
        "<!-- Preview Panel -->",
        HTML_DATATABLE_PANEL + "\n        <!-- Preview Panel -->",
    )
    html = html.replace("/* STYLES_PLACEHOLDER */", STYLES)
    html = html.replace("/* SCRIPTS_PLACEHOLDER */", SCRIPTS + hot_reload_script)
    html = html.replace("IMAGE_BASE64_PLACEHOLDER", image_base64)
    html = html.replace("BBOXES_PLACEHOLDER", json.dumps(bboxes))
    html = html.replace("COLOR_MAP_PLACEHOLDER", json.dumps(color_map))
    html = html.replace("INITIAL_VALUES_PLACEHOLDER", json.dumps(initial_values))
    html = html.replace("IMG_WIDTH_PLACEHOLDER", str(img_size[0]))
    html = html.replace("IMG_HEIGHT_PLACEHOLDER", str(img_size[1]))
    html = html.replace("STYLE_NAME_PLACEHOLDER", style_name)
    html = html.replace("SCITEX_ICON_PLACEHOLDER", _SCITEX_ICON_BASE64)

    # Dark mode preference - set initial state
    html = html.replace("DARK_MODE_THEME_PLACEHOLDER", "dark" if dark_mode else "light")
    html = html.replace("DARK_MODE_CHECKED_PLACEHOLDER", "checked" if dark_mode else "")

    # Server start time for debugging
    html = html.replace("SERVER_START_TIME_PLACEHOLDER", _SERVER_START_TIME)

    return html


__all__ = ["build_html_template"]
