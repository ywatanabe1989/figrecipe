#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Artist processing package for hitmap generation."""

from ._collections import process_collections
from ._images import process_images
from ._lines import process_lines
from ._patches import process_patches
from ._text import process_figure_text, process_legend, process_text

__all__ = [
    "process_lines",
    "process_collections",
    "process_patches",
    "process_images",
    "process_text",
    "process_legend",
    "process_figure_text",
]

# EOF
