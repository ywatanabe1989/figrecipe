#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Browser automation utilities for demo generation.

This module provides tools for creating visual demos of figrecipe features
using Playwright for browser automation.

Features:
- Mouse cursor visualization
- Click effect animations
- Caption overlays
- Element highlighting
- Video/GIF recording
"""

from ._caption import hide_caption, show_caption
from ._click_effect import inject_click_effect, remove_click_effect
from ._cursor import inject_cursor, remove_cursor
from ._highlight import highlight_element
from ._recorder import DemoRecorder
from ._utils import concatenate_videos, convert_to_gif

__all__ = [
    "inject_cursor",
    "remove_cursor",
    "inject_click_effect",
    "remove_click_effect",
    "show_caption",
    "hide_caption",
    "highlight_element",
    "DemoRecorder",
    "convert_to_gif",
    "concatenate_videos",
]

# EOF
