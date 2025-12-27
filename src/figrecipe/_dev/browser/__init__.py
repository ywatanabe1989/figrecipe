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

from ._audio import generate_tts_segments, mix_narration_with_bgm
from ._caption import hide_caption, show_caption, show_title_screen
from ._click_effect import inject_click_effect, remove_click_effect
from ._cursor import (
    inject_cursor,
    move_cursor_to,
    move_cursor_to_element,
    remove_cursor,
)
from ._highlight import highlight_element
from ._narration import (
    add_narration_to_video,
    estimate_caption_times,
    extract_captions_from_script,
    get_video_duration,
)
from ._recorder import DemoRecorder
from ._utils import concatenate_videos, convert_to_gif
from ._video_trim import (
    detect_markers,
    inject_end_marker,
    inject_start_marker,
    process_video_with_markers,
    trim_video_by_markers,
)

__all__ = [
    "inject_cursor",
    "remove_cursor",
    "move_cursor_to",
    "move_cursor_to_element",
    "inject_click_effect",
    "remove_click_effect",
    "show_caption",
    "hide_caption",
    "show_title_screen",
    "highlight_element",
    "DemoRecorder",
    "convert_to_gif",
    "concatenate_videos",
    "inject_start_marker",
    "inject_end_marker",
    "detect_markers",
    "trim_video_by_markers",
    "process_video_with_markers",
    "generate_tts_segments",
    "mix_narration_with_bgm",
    "extract_captions_from_script",
    "get_video_duration",
    "estimate_caption_times",
    "add_narration_to_video",
]

# EOF
