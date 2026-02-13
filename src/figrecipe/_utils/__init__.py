#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility modules for figrecipe."""

from ._bundle import is_bundle_path, resolve_recipe_path
from ._calc_nice_ticks import calc_nice_ticks
from ._diff import get_non_default_kwargs, is_default_value
from ._numpy_io import load_array, save_array
from ._units import inch_to_mm, mm_to_inch, mm_to_pt, pt_to_mm

__all__ = [
    "calc_nice_ticks",
    "save_array",
    "load_array",
    "get_non_default_kwargs",
    "is_default_value",
    "mm_to_inch",
    "inch_to_mm",
    "mm_to_pt",
    "pt_to_mm",
    "resolve_recipe_path",
    "is_bundle_path",
]

# Optional: image comparison (requires PIL)
try:
    from ._image_diff import compare_images, create_comparison_figure  # noqa: F401

    __all__.extend(["compare_images", "create_comparison_figure"])
except ImportError:
    pass

# Optional: crop utility (requires PIL)
try:
    from ._crop import crop, find_content_area  # noqa: F401

    __all__.extend(["crop", "find_content_area"])
except ImportError:
    pass

# Colorbar styling utilities
from ._colorbar import add_colorbar, style_colorbar  # noqa: F401
from ._mk_colorbar import mk_colorbar  # noqa: F401

__all__.extend(["style_colorbar", "add_colorbar", "mk_colorbar"])

# Optional: hitmap visualization (requires PIL, scipy for bbox detection)
try:
    from ._hitmap import create_hitmap, generate_hitmap_report  # noqa: F401

    __all__.extend(["create_hitmap", "generate_hitmap_report"])
except ImportError:
    pass
