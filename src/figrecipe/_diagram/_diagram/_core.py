#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram builder for rich scientific diagrams."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ._constants import ANCHOR_POINTS, NODE_CLASSES, VERIFICATION_STATES

if TYPE_CHECKING:
    from matplotlib.axes import Axes  # noqa: F401; from matplotlib.figure import Figure


@dataclass
class BoxSpec:
    """Specification for a rich text box."""

    id: str
    title: str
    subtitle: Optional[str] = None
    content: List[Dict] = field(default_factory=list)
    emphasis: str = "normal"
    shape: str = "rounded"
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    title_color: Optional[str] = None
    padding_mm: float = 5.0  # Inner spacing from box edge to text (mm)
    margin_mm: float = 0.0  # Outer spacing for collision detection (mm)
    node_class: Optional[str] = None  # source/input/processing/output/claim
    state: Optional[str] = None  # verified/tampered/invalidated/ignored
    language: Optional[str] = None  # syntax highlighting language (e.g. "python")
    bullet: Optional[str] = None  # "circle" (·), "dash" (–), "arrow" (→)


@dataclass
class ArrowSpec:
    """Specification for an arrow."""

    id: Optional[str] = None
    source: str = ""
    target: str = ""
    source_anchor: str = "auto"
    target_anchor: str = "auto"
    label: Optional[str] = None
    style: str = "solid"
    color: Optional[str] = None
    curve: float = 0.0  # Dimensionless curve parameter
    linewidth_mm: float = 0.5  # Line width in mm
    label_offset_mm: Optional[Tuple[float, float]] = None  # Manual (dx, dy) nudge
    margin_mm: Optional[float] = (
        None  # Override default arrow-to-box gap (visual gap from box edge)
    )


@dataclass
class IconSpec:
    """Specification for an icon (SVG/PNG file or built-in name)."""

    id: str
    source: str  # file path or built-in name ("warning", "check", "cross", "info")
    color: Optional[str] = None
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


class Diagram:
    """Builder for rich box-and-arrow diagrams with mm-based coordinates."""

    def __init__(
        self,
        title: Optional[str] = None,
        width_mm: float = 170.0,
        height_mm: Optional[float] = 120.0,
        padding_mm: float = 10.0,
        gap_mm: Optional[float] = None,
    ):
        import warnings

        if width_mm > 185.0:
            warnings.warn(
                f"Diagram width {width_mm}mm exceeds 185mm (double-column max).",
                stacklevel=2,
            )
        self.title = title
        self.width_mm = width_mm
        self._padding_mm = padding_mm
        self._gap_mm = gap_mm
        self._flow_items: List[str] = []
        if gap_mm is not None:
            height_mm = None  # force auto-height in flex mode
        self._auto_height = height_mm is None
        self.height_mm = height_mm if height_mm is not None else 0
        self.figsize = (width_mm / 25.4, self.height_mm / 25.4)
        self.xlim = (0, width_mm)
        self.ylim = (0, self.height_mm)
        self._boxes: Dict[str, BoxSpec] = {}
        self._containers: Dict[str, Dict] = {}
        self._arrows: List[ArrowSpec] = []
        self._icons: Dict[str, IconSpec] = {}
        self._positions: Dict[str, PositionSpec] = {}
        self._render_info: Dict[str, Dict[str, Any]] = {}

    def add_box(
        self,
        id: str,
        title: str,
        subtitle: Optional[str] = None,
        content: Optional[List] = None,
        emphasis: str = "normal",
        shape: str = "rounded",
        x_mm: Optional[float] = None,
        y_mm: Optional[float] = None,
        width_mm: Optional[float] = None,
        height_mm: Optional[float] = None,
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
        title_color: Optional[str] = None,
        padding_mm: float = 5.0,
        margin_mm: float = 0.0,
        node_class: Optional[str] = None,
        state: Optional[str] = None,
        language: Optional[str] = None,
        bullet: Optional[str] = None,
    ) -> "Diagram":
        """Add a rich text box. See BoxSpec for node_class/state/language/bullet."""
        # Resolve node_class → default shape (explicit shape wins)
        if node_class and shape == "rounded" and node_class in NODE_CLASSES:
            shape = NODE_CLASSES[node_class]
        # Resolve state/emphasis → explicit colors (explicit colors always win)
        if state and state in VERIFICATION_STATES:
            s_fill, s_border = VERIFICATION_STATES[state]
            fill_color = fill_color or s_fill
            border_color = border_color or s_border
        fill_color, border_color, title_color = _resolve_emphasis(
            emphasis,
            fill_color,
            border_color,
            title_color,
        )
        box = BoxSpec(
            id=id,
            title=title,
            subtitle=subtitle,
            content=content or [],
            emphasis=emphasis,
            shape=shape,
            fill_color=fill_color,
            border_color=border_color,
            title_color=title_color,
            padding_mm=padding_mm,
            margin_mm=margin_mm,
            node_class=node_class,
            state=state,
            language=language,
            bullet=bullet,
        )
        self._boxes[id] = box
        # Flex mode: auto-size and defer positioning
        if self._gap_mm is not None and x_mm is None and y_mm is None:
            if height_mm is None:
                height_mm = self._auto_box_height(box)
            from ._flex import auto_box_width

            w = width_mm if width_mm is not None else auto_box_width(box)
            self._positions[id] = PositionSpec(0, 0, w, height_mm)
            self._flow_items.append(id)
            return self
        # Auto-compute height when x/y/width given but height is None
        if height_mm is None and None not in (x_mm, y_mm, width_mm):
            height_mm = self._auto_box_height(box)
        if None not in (x_mm, y_mm, width_mm, height_mm):
            self._positions[id] = PositionSpec(x_mm, y_mm, width_mm, height_mm)
        return self

    def add_container(
        self,
        id: str,
        title: Optional[str] = None,
        children: Optional[List[str]] = None,
        emphasis: str = "muted",
        x_mm: Optional[float] = None,
        y_mm: Optional[float] = None,
        width_mm: Optional[float] = None,
        height_mm: Optional[float] = None,
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
        title_loc: str = "upper center",
        direction: str = "row",
        container_gap_mm: float = 8.0,
        container_padding_mm: float = 8.0,
        equalize_heights: bool = True,
        equalize_widths: bool = True,
    ) -> "Diagram":
        """Add a container. equalize_heights/widths: match children in row/column."""
        fill_color, border_color, _ = _resolve_emphasis(
            emphasis, fill_color, border_color
        )
        self._containers[id] = {
            "title": title,
            "children": children or [],
            "emphasis": emphasis,
            "fill_color": fill_color,
            "border_color": border_color,
            "title_loc": title_loc,
            "direction": direction,
            "gap_mm": container_gap_mm,
            "padding_mm": container_padding_mm,
            "equalize_heights": equalize_heights,
            "equalize_widths": equalize_widths,
        }
        if self._gap_mm is not None and x_mm is None and y_mm is None:
            self._positions[id] = PositionSpec(0, 0, width_mm or 0, height_mm or 0)
            self._flow_items.append(id)
            return self
        if None not in (x_mm, y_mm, width_mm, height_mm):
            self._positions[id] = PositionSpec(x_mm, y_mm, width_mm, height_mm)
        return self

    def add_arrow(
        self,
        source: str,
        target: str,
        source_anchor: str = "auto",
        target_anchor: str = "auto",
        label: Optional[str] = None,
        style: str = "solid",
        color: Optional[str] = None,
        curve: float = 0.0,
        linewidth_mm: float = 0.5,
        label_offset_mm: Optional[Tuple[float, float]] = None,
        margin_mm: Optional[float] = None,
    ) -> "Diagram":
        """Add an arrow connecting two boxes."""
        auto_id = f"arrow:{source}->{target}"
        self._arrows.append(
            ArrowSpec(
                id=auto_id,
                source=source,
                target=target,
                source_anchor=source_anchor,
                target_anchor=target_anchor,
                label=label,
                style=style,
                color=color,
                curve=curve,
                linewidth_mm=linewidth_mm,
                label_offset_mm=label_offset_mm,
                margin_mm=margin_mm,
            )
        )
        return self

    def add_icon(
        self,
        id: str,
        source: str,
        x_mm: float,
        y_mm: float,
        width_mm: float = 8.0,
        height_mm: float = 8.0,
        color: Optional[str] = None,
        opacity: float = 1.0,
    ) -> "Diagram":
        """Add an icon (SVG/PNG or built-in: warning/check/cross/info/lock)."""
        self._icons[id] = IconSpec(
            id=id,
            source=source,
            color=color,
            opacity=opacity,
        )
        self._positions[id] = PositionSpec(
            x_mm=x_mm,
            y_mm=y_mm,
            width_mm=width_mm,
            height_mm=height_mm,
        )
        return self

    def validate_containers(self) -> None:
        """Check every container fully encloses its declared children."""
        from ._validate import validate_containers

        validate_containers(self)

    def validate_no_overlap(self) -> None:
        """Check that no two boxes overlap each other."""
        from ._validate import validate_no_overlap

        validate_no_overlap(self)

    def auto_layout(
        self,
        layout: str = "lr",
        margin_mm: float = 15.0,
        box_size_mm: Optional[Tuple[float, float]] = None,
        gap_mm: float = 10.0,
        avoid_overlap: bool = True,
        justify: str = "space-between",
        align_items: str = "center",
    ) -> "Diagram":
        """Automatically position boxes. See _layout for details."""
        from ._layout import auto_layout

        auto_layout(
            self,
            layout=layout,
            margin_mm=margin_mm,
            box_size_mm=box_size_mm,
            gap_mm=gap_mm,
            avoid_overlap=avoid_overlap,
            justify=justify,
            align_items=align_items,
        )
        return self

    def _auto_box_height(self, box: BoxSpec) -> float:
        """Compute box height from content when height_mm is not specified."""
        pad = box.padding_mm
        if box.shape == "codeblock":
            title_bar = 6.0
            n_lines = len(box.content)
            return title_bar + n_lines * 3.5 + 2 * pad
        h = 6.0  # title (bold, 11pt)
        if box.subtitle:
            h += 5.0  # subtitle (9pt + gap)
        h += len(box.content) * 5.0  # content lines (8pt + gap)
        h += 2 * pad
        return max(h, 18.0)

    def _finalize_canvas_size(self) -> None:
        """Compute canvas height from element positions when height_mm=None."""
        from ._flex import resolve_flex_layout

        resolve_flex_layout(self)
        if not self._auto_height:
            return
        if not self._positions:
            self.height_mm = 120.0  # fallback
            self.ylim = (0, 120.0)
            self.figsize = (self.width_mm / 25.4, 120.0 / 25.4)
            return

        max_top = max(p.y_mm + p.height_mm / 2 for p in self._positions.values())
        min_bottom = min(p.y_mm - p.height_mm / 2 for p in self._positions.values())

        title_space = 12.0 if self.title else 0.0
        margin = 8.0

        self.height_mm = max_top - min_bottom + title_space + 2 * margin
        self.ylim = (min_bottom - margin, max_top + title_space + margin)
        self.figsize = (self.width_mm / 25.4, self.height_mm / 25.4)

    def _get_anchor(self, pos: PositionSpec, anchor: str) -> Tuple[float, float]:
        """Get absolute position of an anchor point on the visual box edge."""
        if anchor not in ANCHOR_POINTS:
            anchor = "center"
        rx, ry = ANCHOR_POINTS[anchor]
        x = pos.x_mm - pos.width_mm / 2 + rx * pos.width_mm
        y = pos.y_mm - pos.height_mm / 2 + ry * pos.height_mm
        return x, y

    def _auto_anchor(self, src: PositionSpec, tgt: PositionSpec) -> Tuple[str, str]:
        """Determine best anchor points automatically."""
        dx, dy = tgt.x_mm - src.x_mm, tgt.y_mm - src.y_mm
        if abs(dx) > abs(dy):
            return ("right", "left") if dx > 0 else ("left", "right")
        return ("top", "bottom") if dy > 0 else ("bottom", "top")

    def render(
        self,
        ax: Optional[Axes] = None,
        auto_fix: bool = False,
        auto_curve: bool = True,
    ) -> Tuple["Figure", Axes]:
        """Render. auto_fix=True resolves violations; auto_curve=False skips R7."""
        import matplotlib.pyplot as plt

        from . import _render as _sr
        from . import _validate as _sv

        self._finalize_canvas_size()
        if auto_fix:
            from ._autofix import auto_fix as _af

            _af(self, auto_curve=auto_curve)

        figsize = (
            (self.xlim[1] - self.xlim[0]) / 25.4,
            (self.ylim[1] - self.ylim[0]) / 25.4,
        )
        owns_fig = ax is None
        if owns_fig:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        _sr.draw_all_elements(self, ax)

        def _draw_all():
            _sr.draw_all_elements(self, ax)

        # Phase 2: post-render auto-fix for text collisions (R5/R6/R7)
        if auto_fix:
            from ._autofix import fix_post_render

            for _ in range(3):
                if fix_post_render(self, fig, ax) == 0:
                    break
                _draw_all()

        # Validate and set diagram markers only when owns_fig (not in composed)
        if owns_fig:
            fig._figrecipe_diagram_failed = False
            fig._figrecipe_validation_errors = []
            try:
                _sv.validate_all(self, fig=fig, ax=ax)
            except ValueError as e:
                import warnings

                fig._figrecipe_diagram_failed = True
                fig._figrecipe_validation_errors = str(e).split("\n")
                warnings.warn(str(e), UserWarning, stacklevel=2)
            fig._figrecipe_diagram = self
        return fig, ax

    def render_to_file(
        self,
        path: Union[str, Path],
        dpi: int = 200,
        save_recipe: bool = True,
        save_hitmap: bool = False,
    ) -> Path:
        """Render and save. On validation failure, saves as *_FAILED.png."""
        from ._io import render_to_file as _rtf

        return _rtf(
            self, path, dpi=dpi, save_recipe=save_recipe, save_hitmap=save_hitmap
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert diagram to dictionary for serialization."""
        from ._io import diagram_to_dict

        return diagram_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Diagram":
        """Create Diagram from dictionary (recipe reproduction)."""
        from ._io import diagram_from_dict

        return diagram_from_dict(data)


__all__ = [
    "Diagram",
    "ArrowSpec",
    "BoxSpec",
    "PositionSpec",
    "NODE_CLASSES",
    "VERIFICATION_STATES",
]
