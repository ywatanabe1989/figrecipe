#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modular bbox extraction for figure elements.

This package provides functions for extracting bounding boxes from
matplotlib figure elements for hit detection in the GUI editor.

The main function `extract_bboxes` is re-exported from _bbox_main.py
for backward compatibility.

Modules:
- _transforms: Coordinate transformation utilities
- _elements: General element, text, and tick bbox extraction
- _lines: Line and quiver bbox extraction
- _collections: Collection (scatter, fill) and patch bbox extraction
"""

# Re-export main function from _extract.py
# Import modular helpers
from ._collections import get_collection_bbox, get_patch_bbox
from ._elements import get_element_bbox, get_text_bbox, get_tick_labels_bbox
from ._extract import extract_bboxes
from ._lines import get_line_bbox, get_quiver_bbox
from ._transforms import display_to_image, transform_bbox

__all__ = [
    # Main function
    "extract_bboxes",
    # Transforms
    "transform_bbox",
    "display_to_image",
    # Elements
    "get_element_bbox",
    "get_text_bbox",
    "get_tick_labels_bbox",
    # Lines
    "get_line_bbox",
    "get_quiver_bbox",
    # Collections
    "get_collection_bbox",
    "get_patch_bbox",
]
