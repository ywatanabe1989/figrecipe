#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rich node rendering for enhanced diagram boxes.

Provides multi-line text boxes with title, subtitle, and content,
similar to professional schematic elements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from ._styles_native import get_emphasis_style

# Anchor point definitions (relative to box: 0-1 range)
ANCHOR_POINTS = {
    "center": (0.5, 0.5),
    "top": (0.5, 1.0),
    "bottom": (0.5, 0.0),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
    "top-left": (0.0, 1.0),
    "top-right": (1.0, 1.0),
    "bottom-left": (0.0, 0.0),
    "bottom-right": (1.0, 0.0),
}


@dataclass
class RichTextLine:
    """A single line of text with styling."""

    text: str
    fontsize: float = 9
    fontweight: str = "normal"
    fontstyle: str = "normal"
    color: Optional[str] = None  # None = use default text color
    family: str = "sans-serif"


@dataclass
class RichNodeSpec:
    """Specification for a rich multi-line node."""

    id: str
    title: str
    subtitle: Optional[str] = None
    content: List[Union[str, RichTextLine]] = field(default_factory=list)
    emphasis: str = "normal"
    shape: str = "rounded"

    # Sizing
    width: Optional[float] = None  # Auto-calculate if None
    height: Optional[float] = None  # Auto-calculate if None
    padding: float = 0.02  # Internal padding

    # Title styling
    title_size: float = 11
    subtitle_size: float = 9
    content_size: float = 8

    # Custom colors (override emphasis)
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    title_color: Optional[str] = None


@dataclass
class ContainerSpec:
    """Specification for a container that holds other nodes."""

    id: str
    title: Optional[str] = None
    children: List[str] = field(default_factory=list)  # Node IDs
    layout: Literal["horizontal", "vertical", "grid"] = "horizontal"
    emphasis: str = "muted"

    # Sizing
    padding: float = 0.03
    gap: float = 0.02  # Gap between children

    # Custom colors
    fill_color: Optional[str] = None
    border_color: Optional[str] = None


def estimate_rich_node_size(
    spec: RichNodeSpec,
    ax: Optional[Axes] = None,
) -> Tuple[float, float]:
    """Estimate the size needed for a rich node.

    Parameters
    ----------
    spec : RichNodeSpec
        The node specification.
    ax : Axes, optional
        Axes for text measurement (uses defaults if None).

    Returns
    -------
    tuple
        (width, height) in axes coordinates.
    """
    if spec.width is not None and spec.height is not None:
        return spec.width, spec.height

    # Estimate based on content
    line_height = 0.025  # Approximate line height
    char_width = 0.008  # Approximate character width

    # Calculate width from longest text
    max_chars = len(spec.title)
    if spec.subtitle:
        max_chars = max(max_chars, len(spec.subtitle))
    for line in spec.content:
        text = line.text if isinstance(line, RichTextLine) else line
        max_chars = max(max_chars, len(text))

    # Calculate height from number of lines
    n_lines = 1  # title
    if spec.subtitle:
        n_lines += 1
    n_lines += len(spec.content)

    # Add padding
    width = spec.width or max(max_chars * char_width + spec.padding * 2, 0.12)
    height = spec.height or max(n_lines * line_height + spec.padding * 2, 0.08)

    # Cap at reasonable max
    width = min(width, 0.35)
    height = min(height, 0.4)

    return width, height


def render_rich_node(
    ax: Axes,
    spec: RichNodeSpec,
    x: float,
    y: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
) -> Dict[str, Any]:
    """Render a rich multi-line node.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to render on.
    spec : RichNodeSpec
        Node specification.
    x, y : float
        Center position in axes coordinates.
    width, height : float, optional
        Override size (auto-calculated if None).

    Returns
    -------
    dict
        Rendering info including bounds, anchor points.
    """
    # Get colors
    colors = get_emphasis_style(spec.emphasis)
    fill = spec.fill_color or colors["fill"]
    border = spec.border_color or colors["stroke"]
    text_color = colors["text"]
    title_color = spec.title_color or border  # Title uses border color by default

    # Calculate size
    if width is None or height is None:
        auto_w, auto_h = estimate_rich_node_size(spec, ax)
        width = width or auto_w
        height = height or auto_h

    # Shape style
    shape_styles = {
        "box": "square,pad=0.005",
        "rounded": "round,pad=0.005,rounding_size=0.015",
        "stadium": "round,pad=0.005,rounding_size=0.05",
    }
    boxstyle = shape_styles.get(spec.shape, shape_styles["rounded"])

    # Create box patch
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle=boxstyle,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=2,
    )
    ax.add_patch(box)

    # Calculate text positions (top-aligned within box)
    padding = spec.padding
    text_top = y + height / 2 - padding
    line_spacing = 0.022

    current_y = text_top

    # Render title
    ax.text(
        x,
        current_y,
        spec.title,
        ha="center",
        va="top",
        fontsize=spec.title_size,
        fontweight="bold",
        color=title_color,
        zorder=3,
    )
    current_y -= line_spacing * 1.2

    # Render subtitle
    if spec.subtitle:
        ax.text(
            x,
            current_y,
            spec.subtitle,
            ha="center",
            va="top",
            fontsize=spec.subtitle_size,
            color=text_color,
            zorder=3,
        )
        current_y -= line_spacing

    # Render content lines
    for line in spec.content:
        if isinstance(line, RichTextLine):
            ax.text(
                x,
                current_y,
                line.text,
                ha="center",
                va="top",
                fontsize=line.fontsize,
                fontweight=line.fontweight,
                fontstyle=line.fontstyle,
                color=line.color or text_color,
                family=line.family,
                zorder=3,
            )
        else:
            ax.text(
                x,
                current_y,
                line,
                ha="center",
                va="top",
                fontsize=spec.content_size,
                color=text_color,
                zorder=3,
            )
        current_y -= line_spacing

    # Calculate anchor points
    anchors = {}
    for name, (rx, ry) in ANCHOR_POINTS.items():
        ax_x = x - width / 2 + rx * width
        ax_y = y - height / 2 + ry * height
        anchors[name] = (ax_x, ax_y)

    return {
        "bounds": (x - width / 2, y - height / 2, width, height),
        "center": (x, y),
        "anchors": anchors,
        "width": width,
        "height": height,
    }


def render_container(
    ax: Axes,
    spec: ContainerSpec,
    x: float,
    y: float,
    width: float,
    height: float,
    title_position: str = "top",
) -> Dict[str, Any]:
    """Render a container box (without children - they're rendered separately).

    Parameters
    ----------
    ax : Axes
        Matplotlib axes.
    spec : ContainerSpec
        Container specification.
    x, y : float
        Center position.
    width, height : float
        Container size.
    title_position : str
        Where to place title: "top", "top-left", etc.

    Returns
    -------
    dict
        Rendering info.
    """
    colors = get_emphasis_style(spec.emphasis)
    fill = spec.fill_color or colors["fill"]
    border = spec.border_color or colors["stroke"]

    # Render container box
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor=fill,
        edgecolor=border,
        linewidth=2.5,
        zorder=1,  # Behind child nodes
    )
    ax.add_patch(box)

    # Render title if present
    if spec.title:
        title_y = y + height / 2 - 0.02
        ax.text(
            x,
            title_y,
            spec.title,
            ha="center",
            va="top",
            fontsize=11,
            fontweight="bold",
            color=border,
            zorder=3,
        )

    # Calculate anchor points
    anchors = {}
    for name, (rx, ry) in ANCHOR_POINTS.items():
        ax_x = x - width / 2 + rx * width
        ax_y = y - height / 2 + ry * height
        anchors[name] = (ax_x, ax_y)

    return {
        "bounds": (x - width / 2, y - height / 2, width, height),
        "center": (x, y),
        "anchors": anchors,
        "content_area": (
            x - width / 2 + spec.padding,
            y - height / 2 + spec.padding,
            width - 2 * spec.padding,
            height - 2 * spec.padding - (0.04 if spec.title else 0),
        ),
    }


def get_anchor_point(
    node_info: Dict[str, Any],
    anchor: str = "center",
) -> Tuple[float, float]:
    """Get the position of an anchor point on a node.

    Parameters
    ----------
    node_info : dict
        Node rendering info from render_rich_node or render_container.
    anchor : str
        Anchor name: center, top, bottom, left, right, top-left, etc.

    Returns
    -------
    tuple
        (x, y) position.
    """
    if anchor in node_info.get("anchors", {}):
        return node_info["anchors"][anchor]
    return node_info.get("center", (0.5, 0.5))


__all__ = [
    "RichTextLine",
    "RichNodeSpec",
    "ContainerSpec",
    "ANCHOR_POINTS",
    "estimate_rich_node_size",
    "render_rich_node",
    "render_container",
    "get_anchor_point",
]
