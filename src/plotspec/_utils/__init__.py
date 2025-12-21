#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility modules for plotspec."""

from ._numpy_io import load_array, save_array
from ._diff import get_non_default_kwargs, is_default_value

__all__ = [
    "save_array",
    "load_array",
    "get_non_default_kwargs",
    "is_default_value",
]

# Optional: image comparison (requires PIL)
try:
    from ._image_diff import compare_images, create_comparison_figure
    __all__.extend(["compare_images", "create_comparison_figure"])
except ImportError:
    pass
