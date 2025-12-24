#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kwargs expansion utilities for matplotlib signature extraction."""

import re
from typing import Any, Dict, List, Optional


def get_setter_type(obj: Any, prop_name: str) -> Optional[str]:
    """Get type from set_* method docstring."""
    setter_name = f"set_{prop_name}"
    if not hasattr(obj, setter_name):
        return None

    method = getattr(obj, setter_name)
    if not method.__doc__:
        return None

    match = re.search(
        r"Parameters\s*[-]+\s*\n\s*(\w+)\s*:\s*(.+?)(?:\n\s*\n|\Z)",
        method.__doc__,
        re.DOTALL,
    )
    if match:
        type_str = match.group(2).split("\n")[0].strip()
        return type_str
    return None


def build_kwargs_with_types() -> (
    tuple[
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
    ]
):
    """Build kwargs lists with types from matplotlib classes."""
    from matplotlib.artist import Artist
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.text import Text

    line = Line2D([0], [0])
    patch = Patch()
    text = Text()
    artist = Artist()

    def get_type(obj, name):
        return get_setter_type(obj, name)

    ARTIST_KWARGS = [
        {"name": "agg_filter", "type": get_type(artist, "agg_filter"), "default": None},
        {"name": "alpha", "type": get_type(artist, "alpha"), "default": None},
        {"name": "animated", "type": get_type(artist, "animated"), "default": False},
        {"name": "clip_box", "type": get_type(artist, "clip_box"), "default": None},
        {"name": "clip_on", "type": get_type(artist, "clip_on"), "default": True},
        {"name": "clip_path", "type": get_type(artist, "clip_path"), "default": None},
        {"name": "gid", "type": get_type(artist, "gid"), "default": None},
        {"name": "label", "type": get_type(artist, "label"), "default": ""},
        {
            "name": "path_effects",
            "type": get_type(artist, "path_effects"),
            "default": None,
        },
        {"name": "picker", "type": get_type(artist, "picker"), "default": None},
        {"name": "rasterized", "type": get_type(artist, "rasterized"), "default": None},
        {
            "name": "sketch_params",
            "type": get_type(artist, "sketch_params"),
            "default": None,
        },
        {"name": "snap", "type": get_type(artist, "snap"), "default": None},
        {"name": "transform", "type": get_type(artist, "transform"), "default": None},
        {"name": "url", "type": get_type(artist, "url"), "default": None},
        {"name": "visible", "type": get_type(artist, "visible"), "default": True},
        {"name": "zorder", "type": get_type(artist, "zorder"), "default": None},
    ]

    LINE2D_KWARGS = [
        {"name": "color", "type": get_type(line, "color"), "default": None},
        {"name": "linestyle", "type": get_type(line, "linestyle"), "default": "-"},
        {"name": "linewidth", "type": get_type(line, "linewidth"), "default": None},
        {"name": "marker", "type": get_type(line, "marker"), "default": ""},
        {
            "name": "markeredgecolor",
            "type": get_type(line, "markeredgecolor"),
            "default": None,
        },
        {
            "name": "markeredgewidth",
            "type": get_type(line, "markeredgewidth"),
            "default": None,
        },
        {
            "name": "markerfacecolor",
            "type": get_type(line, "markerfacecolor"),
            "default": None,
        },
        {"name": "markersize", "type": get_type(line, "markersize"), "default": None},
        {"name": "antialiased", "type": get_type(line, "antialiased"), "default": True},
        {
            "name": "dash_capstyle",
            "type": get_type(line, "dash_capstyle"),
            "default": "butt",
        },
        {
            "name": "dash_joinstyle",
            "type": get_type(line, "dash_joinstyle"),
            "default": "round",
        },
        {
            "name": "solid_capstyle",
            "type": get_type(line, "solid_capstyle"),
            "default": "projecting",
        },
        {
            "name": "solid_joinstyle",
            "type": get_type(line, "solid_joinstyle"),
            "default": "round",
        },
        {
            "name": "drawstyle",
            "type": get_type(line, "drawstyle"),
            "default": "default",
        },
        {"name": "fillstyle", "type": get_type(line, "fillstyle"), "default": "full"},
    ]

    PATCH_KWARGS = [
        {"name": "color", "type": get_type(patch, "color"), "default": None},
        {"name": "edgecolor", "type": get_type(patch, "edgecolor"), "default": None},
        {"name": "facecolor", "type": get_type(patch, "facecolor"), "default": None},
        {"name": "fill", "type": get_type(patch, "fill"), "default": True},
        {"name": "hatch", "type": get_type(patch, "hatch"), "default": None},
        {"name": "linestyle", "type": get_type(patch, "linestyle"), "default": "-"},
        {"name": "linewidth", "type": get_type(patch, "linewidth"), "default": None},
        {
            "name": "antialiased",
            "type": get_type(patch, "antialiased"),
            "default": None,
        },
        {"name": "capstyle", "type": get_type(patch, "capstyle"), "default": "butt"},
        {"name": "joinstyle", "type": get_type(patch, "joinstyle"), "default": "miter"},
    ]

    TEXT_KWARGS = [
        {"name": "color", "type": get_type(text, "color"), "default": "black"},
        {"name": "fontfamily", "type": get_type(text, "fontfamily"), "default": None},
        {"name": "fontsize", "type": get_type(text, "fontsize"), "default": None},
        {"name": "fontstretch", "type": get_type(text, "fontstretch"), "default": None},
        {"name": "fontstyle", "type": get_type(text, "fontstyle"), "default": "normal"},
        {
            "name": "fontvariant",
            "type": get_type(text, "fontvariant"),
            "default": "normal",
        },
        {
            "name": "fontweight",
            "type": get_type(text, "fontweight"),
            "default": "normal",
        },
        {
            "name": "horizontalalignment",
            "type": get_type(text, "horizontalalignment"),
            "default": "center",
        },
        {
            "name": "verticalalignment",
            "type": get_type(text, "verticalalignment"),
            "default": "center",
        },
        {"name": "rotation", "type": get_type(text, "rotation"), "default": None},
        {"name": "linespacing", "type": get_type(text, "linespacing"), "default": None},
        {
            "name": "multialignment",
            "type": get_type(text, "multialignment"),
            "default": None,
        },
        {"name": "wrap", "type": get_type(text, "wrap"), "default": False},
    ]

    return ARTIST_KWARGS, LINE2D_KWARGS, PATCH_KWARGS, TEXT_KWARGS


# Lazy cache for kwargs mapping
_KWARGS_CACHE: Optional[Dict[str, List[Dict[str, Any]]]] = None


def get_kwargs_mapping() -> Dict[str, List[Dict[str, Any]]]:
    """Get kwargs mapping, building it lazily on first call."""
    global _KWARGS_CACHE
    if _KWARGS_CACHE is not None:
        return _KWARGS_CACHE

    ARTIST_KWARGS, LINE2D_KWARGS, PATCH_KWARGS, TEXT_KWARGS = build_kwargs_with_types()

    _KWARGS_CACHE = {
        "plot": LINE2D_KWARGS + ARTIST_KWARGS,
        "scatter": ARTIST_KWARGS,
        "bar": PATCH_KWARGS + ARTIST_KWARGS,
        "barh": PATCH_KWARGS + ARTIST_KWARGS,
        "fill": PATCH_KWARGS + ARTIST_KWARGS,
        "fill_between": PATCH_KWARGS + ARTIST_KWARGS,
        "fill_betweenx": PATCH_KWARGS + ARTIST_KWARGS,
        "step": LINE2D_KWARGS + ARTIST_KWARGS,
        "errorbar": LINE2D_KWARGS + ARTIST_KWARGS,
        "hist": PATCH_KWARGS + ARTIST_KWARGS,
        "hist2d": ARTIST_KWARGS,
        "imshow": ARTIST_KWARGS,
        "pcolor": ARTIST_KWARGS,
        "pcolormesh": ARTIST_KWARGS,
        "pcolorfast": ARTIST_KWARGS,
        "contour": ARTIST_KWARGS,
        "contourf": ARTIST_KWARGS,
        "hexbin": ARTIST_KWARGS,
        "quiver": ARTIST_KWARGS,
        "barbs": ARTIST_KWARGS,
        "specgram": ARTIST_KWARGS,
        "psd": LINE2D_KWARGS + ARTIST_KWARGS,
        "csd": LINE2D_KWARGS + ARTIST_KWARGS,
        "cohere": LINE2D_KWARGS + ARTIST_KWARGS,
        "acorr": LINE2D_KWARGS + ARTIST_KWARGS,
        "xcorr": LINE2D_KWARGS + ARTIST_KWARGS,
        "angle_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "magnitude_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "phase_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "stackplot": PATCH_KWARGS + ARTIST_KWARGS,
        "stairs": PATCH_KWARGS + ARTIST_KWARGS,
        "eventplot": ARTIST_KWARGS,
        "broken_barh": PATCH_KWARGS + ARTIST_KWARGS,
        "loglog": LINE2D_KWARGS + ARTIST_KWARGS,
        "semilogx": LINE2D_KWARGS + ARTIST_KWARGS,
        "semilogy": LINE2D_KWARGS + ARTIST_KWARGS,
        "annotate": TEXT_KWARGS + ARTIST_KWARGS,
        "text": TEXT_KWARGS + ARTIST_KWARGS,
        "arrow": PATCH_KWARGS + ARTIST_KWARGS,
        "axhline": LINE2D_KWARGS + ARTIST_KWARGS,
        "axvline": LINE2D_KWARGS + ARTIST_KWARGS,
        "hlines": ARTIST_KWARGS,
        "vlines": ARTIST_KWARGS,
        "axhspan": PATCH_KWARGS + ARTIST_KWARGS,
        "axvspan": PATCH_KWARGS + ARTIST_KWARGS,
        "axline": LINE2D_KWARGS + ARTIST_KWARGS,
        "legend": ARTIST_KWARGS,
        "grid": LINE2D_KWARGS + ARTIST_KWARGS,
        "table": ARTIST_KWARGS,
        "clabel": TEXT_KWARGS + ARTIST_KWARGS,
        "bar_label": TEXT_KWARGS + ARTIST_KWARGS,
        "quiverkey": ARTIST_KWARGS,
        "ecdf": LINE2D_KWARGS + ARTIST_KWARGS,
        "tricontour": ARTIST_KWARGS,
        "tricontourf": ARTIST_KWARGS,
        "tripcolor": ARTIST_KWARGS,
        "triplot": LINE2D_KWARGS + ARTIST_KWARGS,
        "matshow": ARTIST_KWARGS,
        "spy": ARTIST_KWARGS + LINE2D_KWARGS,
        "boxplot": ARTIST_KWARGS,
        "violinplot": ARTIST_KWARGS,
        "pie": PATCH_KWARGS + ARTIST_KWARGS,
        "stem": LINE2D_KWARGS + ARTIST_KWARGS,
    }

    return _KWARGS_CACHE


__all__ = [
    "get_setter_type",
    "build_kwargs_with_types",
    "get_kwargs_mapping",
]

# EOF
