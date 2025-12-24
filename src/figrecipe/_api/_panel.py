#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panel label helper for the public API."""

from typing import Optional, Tuple


def get_panel_label_fontsize(explicit_fontsize: Optional[float] = None) -> float:
    """Get fontsize for panel labels from style or default."""
    if explicit_fontsize is not None:
        return explicit_fontsize

    try:
        from ..styles._style_loader import _STYLE_CACHE

        if _STYLE_CACHE is not None:
            return getattr(getattr(_STYLE_CACHE, "fonts", None), "panel_label_pt", 10)
    except Exception:
        pass
    return 10


def calculate_panel_position(
    loc: str,
    offset: Tuple[float, float],
) -> Tuple[float, float]:
    """Calculate x, y position based on location and offset."""
    if loc == "upper left":
        x, y = offset
    elif loc == "upper right":
        x, y = 1.0 + abs(offset[0]), offset[1]
    elif loc == "lower left":
        x, y = offset[0], -abs(offset[1]) + 1.0
    elif loc == "lower right":
        x, y = 1.0 + abs(offset[0]), -abs(offset[1]) + 1.0
    else:
        x, y = offset
    return x, y


__all__ = [
    "get_panel_label_fontsize",
    "calculate_panel_position",
]

# EOF
