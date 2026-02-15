#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color type and normalization for diagram elements.

Supports str ("#RRGGBB", "#RRGGBBAA", named colors) and
RGBA tuple/list (0-1 float range) for all color parameters.
"""

from __future__ import annotations

from typing import List, Tuple, Union

# Color type: str, RGBA tuple/list, or None
Color = Union[str, Tuple[float, ...], List[float], None]


def normalize_color(c: Color) -> Color:
    """Validate and normalize a color value for matplotlib.

    Accepts
    -------
    - None (passthrough)
    - str: "#RRGGBB", "#RRGGBBAA", named colors, "none"
    - tuple/list: (R, G, B) or (R, G, B, A) with 0-1 float values

    Raises
    ------
    ValueError
        If tuple values are outside 0-1 range (e.g. 0-255).
    TypeError
        If color is not str, tuple, list, or None.
    """
    if c is None or isinstance(c, str):
        return c
    if isinstance(c, (tuple, list)):
        if len(c) not in (3, 4):
            raise ValueError(
                f"Color tuple must have 3 (RGB) or 4 (RGBA) elements, got {len(c)}"
            )
        if any(v > 1.0 for v in c if isinstance(v, (int, float))):
            raise ValueError(
                f"Color values must be 0-1 floats, got {c}. "
                f"Divide by 255 if using 0-255 range."
            )
        return tuple(float(v) for v in c)
    raise TypeError(f"Color must be str, tuple, or None, got {type(c).__name__}")


__all__ = ["Color", "normalize_color"]
