#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility modules for figrecipe."""

from ._diff import get_non_default_kwargs, is_default_value
from ._numpy_io import load_array, save_array
from ._units import inch_to_mm, mm_to_inch, mm_to_pt, pt_to_mm

__all__ = [
    "save_array",
    "load_array",
    "get_non_default_kwargs",
    "is_default_value",
    "mm_to_inch",
    "inch_to_mm",
    "mm_to_pt",
    "pt_to_mm",
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
