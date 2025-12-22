#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML/CSS/JS template builder for figure editor.

Uses YAML-compatible flattened key names from to_subplots_kwargs() as the
single source of truth. No custom key mapping is needed since all keys
now match the HTML input IDs directly.
"""

import json
from typing import Any, Dict, Tuple

from ._html import HTML_TEMPLATE
from ._scripts import SCRIPTS
from ._styles import STYLES


def build_html_template(
    image_base64: str,
    bboxes: Dict[str, Any],
    color_map: Dict[str, Any],
    style: Dict[str, Any],
    overrides: Dict[str, Any],
    img_size: Tuple[int, int],
    style_name: str = "SCITEX",
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

    Returns
    -------
    str
        Complete HTML document.
    """
    # Merge style and overrides for initial values
    # Keys should already match HTML input IDs (YAML-compatible flattened)
    initial_values = {**style, **overrides}

    # Inject data into template
    html = HTML_TEMPLATE
    html = html.replace("/* STYLES_PLACEHOLDER */", STYLES)
    html = html.replace("/* SCRIPTS_PLACEHOLDER */", SCRIPTS)
    html = html.replace("IMAGE_BASE64_PLACEHOLDER", image_base64)
    html = html.replace("BBOXES_PLACEHOLDER", json.dumps(bboxes))
    html = html.replace("COLOR_MAP_PLACEHOLDER", json.dumps(color_map))
    html = html.replace("INITIAL_VALUES_PLACEHOLDER", json.dumps(initial_values))
    html = html.replace("IMG_WIDTH_PLACEHOLDER", str(img_size[0]))
    html = html.replace("IMG_HEIGHT_PLACEHOLDER", str(img_size[1]))
    html = html.replace("STYLE_NAME_PLACEHOLDER", style_name)

    return html


__all__ = ["build_html_template"]
