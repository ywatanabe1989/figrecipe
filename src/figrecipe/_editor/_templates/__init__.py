#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML/CSS/JS template builder for figure editor.
"""

import json
from typing import Any, Dict, Tuple

from ._html import HTML_TEMPLATE
from ._scripts import SCRIPTS
from ._styles import STYLES


# Mapping from internal style keys to HTML input IDs
STYLE_TO_HTML_MAP = {
    # Dimensions - Axes
    'axes_width_mm': 'axes_width_mm',
    'axes_height_mm': 'axes_height_mm',
    'axes_thickness_mm': 'axes_thickness_mm',
    # Dimensions - Margins
    'margin_left_mm': 'margins_left_mm',
    'margin_right_mm': 'margins_right_mm',
    'margin_bottom_mm': 'margins_bottom_mm',
    'margin_top_mm': 'margins_top_mm',
    # Dimensions - Spacing
    'space_w_mm': 'spacing_horizontal_mm',
    'space_h_mm': 'spacing_vertical_mm',
    # Fonts
    'font_family': 'fonts_family',
    'axis_font_size_pt': 'fonts_axis_label_pt',
    'tick_font_size_pt': 'fonts_tick_label_pt',
    'title_font_size_pt': 'fonts_title_pt',
    'suptitle_font_size_pt': 'fonts_suptitle_pt',
    'legend_font_size_pt': 'fonts_legend_pt',
    'annotation_font_size_pt': 'fonts_annotation_pt',
    # Lines
    'trace_thickness_mm': 'lines_trace_mm',
    'errorbar_thickness_mm': 'lines_errorbar_mm',
    'errorbar_cap_mm': 'lines_errorbar_cap_mm',
    # Markers
    'marker_size_mm': 'markers_size_mm',
    'scatter_size_mm': 'markers_scatter_mm',
    'marker_edge_width_mm': 'markers_edge_width_mm',
    # Ticks
    'tick_length_mm': 'ticks_length_mm',
    'tick_thickness_mm': 'ticks_thickness_mm',
    'tick_direction': 'ticks_direction',
    'n_ticks': 'ticks_n_ticks',
    # Legend
    'legend_frameon': 'legend_frameon',
    'legend_loc': 'legend_loc',
    'legend_alpha': 'legend_alpha',
    # Behavior
    'grid': 'behavior_grid',
    'hide_top_spine': 'behavior_hide_top_spine',
    'hide_right_spine': 'behavior_hide_right_spine',
    'auto_scale_axes': 'behavior_auto_scale_axes',
    # Output
    'dpi': 'output_dpi',
    'transparent': 'output_transparent',
    'output_format': 'output_format',
}

# Reverse mapping for converting HTML IDs back to style keys
HTML_TO_STYLE_MAP = {v: k for k, v in STYLE_TO_HTML_MAP.items()}


def style_to_html_values(style: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert style dict keys to HTML input IDs.

    Parameters
    ----------
    style : dict
        Style dictionary with internal keys.

    Returns
    -------
    dict
        Dictionary with HTML input ID keys.
    """
    result = {}
    for style_key, value in style.items():
        html_key = STYLE_TO_HTML_MAP.get(style_key, style_key)
        result[html_key] = value
    return result


def html_to_style_values(html_values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert HTML input IDs back to style dict keys.

    Parameters
    ----------
    html_values : dict
        Dictionary with HTML input ID keys.

    Returns
    -------
    dict
        Style dictionary with internal keys.
    """
    result = {}
    for html_key, value in html_values.items():
        style_key = HTML_TO_STYLE_MAP.get(html_key, html_key)
        result[style_key] = value
    return result


def build_html_template(
    image_base64: str,
    bboxes: Dict[str, Any],
    color_map: Dict[str, Any],
    style: Dict[str, Any],
    overrides: Dict[str, Any],
    img_size: Tuple[int, int],
) -> str:
    """
    Build complete HTML template for figure editor.

    Parameters
    ----------
    image_base64 : str
        Base64-encoded preview image.
    bboxes : dict
        Element bounding boxes.
    color_map : dict
        Hitmap color-to-element mapping.
    style : dict
        Base style configuration.
    overrides : dict
        Current style overrides.
    img_size : tuple
        (width, height) of preview image.

    Returns
    -------
    str
        Complete HTML document.
    """
    # Convert style keys to HTML input IDs
    html_style = style_to_html_values(style)
    html_overrides = style_to_html_values(overrides)

    # Merge for initial values
    initial_values = {**html_style, **html_overrides}

    # Inject data into template
    html = HTML_TEMPLATE
    html = html.replace('/* STYLES_PLACEHOLDER */', STYLES)
    html = html.replace('/* SCRIPTS_PLACEHOLDER */', SCRIPTS)
    html = html.replace('IMAGE_BASE64_PLACEHOLDER', image_base64)
    html = html.replace('BBOXES_PLACEHOLDER', json.dumps(bboxes))
    html = html.replace('COLOR_MAP_PLACEHOLDER', json.dumps(color_map))
    html = html.replace('INITIAL_VALUES_PLACEHOLDER', json.dumps(initial_values))
    html = html.replace('IMG_WIDTH_PLACEHOLDER', str(img_size[0]))
    html = html.replace('IMG_HEIGHT_PLACEHOLDER', str(img_size[1]))

    return html


__all__ = ['build_html_template', 'style_to_html_values', 'html_to_style_values']
