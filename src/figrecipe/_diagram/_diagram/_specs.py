#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dataclass specifications for diagram elements."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple, Union

from ._color import Color

# Anchor type: any of the 9 canonical forms (IDE autocomplete), or any str (runtime normalized)
Anchor = Union[
    Literal[
        "auto",
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ],
    str,
]


@dataclass
class BoxSpec:
    """Specification for a rich text box."""

    id: str
    title: str
    subtitle: Optional[str] = None
    content: List[Dict] = field(default_factory=list)
    emphasis: str = "normal"
    shape: str = "rounded"
    fill_color: Color = None
    border_color: Color = None
    title_color: Color = None
    padding_mm: float = 5.0
    margin_mm: float = 0.0
    node_class: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = None
    bullet: Optional[str] = None


@dataclass
class ArrowSpec:
    """Specification for an arrow."""

    id: Optional[str] = None
    source: str = ""
    target: str = ""
    source_anchor: Anchor = "auto"
    target_anchor: Anchor = "auto"
    source_dx: float = 0.0
    source_dy: float = 0.0
    target_dx: float = 0.0
    target_dy: float = 0.0
    label: Optional[str] = None
    style: str = "solid"
    color: Color = None
    curve: float = 0.0
    linewidth_mm: float = 0.5
    label_offset_mm: Optional[Tuple[float, float]] = None
    margin_mm: Optional[float] = None


@dataclass
class IconSpec:
    """Specification for an icon (SVG/PNG file or built-in name)."""

    id: str
    source: str
    color: Color = None
    opacity: float = 1.0


@dataclass
class PositionSpec:
    """Position and size specification in mm."""

    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float


def _resolve_emphasis(emphasis, fill_color, border_color, title_color=None):
    """Resolve emphasis shorthand to explicit colors (explicit colors always win)."""
    from .._shared._styles_native import get_emphasis_style

    ec = get_emphasis_style(emphasis)
    return (
        fill_color or ec["fill"],
        border_color or ec["stroke"],
        title_color or ec.get("text"),
    )


__all__ = [
    "Anchor",
    "ArrowSpec",
    "BoxSpec",
    "IconSpec",
    "PositionSpec",
    "_resolve_emphasis",
]
