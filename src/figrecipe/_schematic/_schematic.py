#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schematic diagram builder for rich scientific diagrams."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from .._diagram._styles_native import get_edge_style, get_emphasis_style
from .._utils._units import mm_to_pt

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


@dataclass
class PositionSpec:
    """Position and size specification in mm."""

    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float


class Schematic:
    """Builder for rich schematic diagrams."""

    def __init__(
        self,
        title: Optional[str] = None,
        width_mm: float = 170.0,
        height_mm: float = 120.0,
    ):
        import warnings

        if width_mm > 185.0:
            warnings.warn(
                f"Schematic width {width_mm}mm exceeds 185mm (double-column max).",
                stacklevel=2,
            )
        self.title = title
        self.width_mm = width_mm
        self.height_mm = height_mm

        # Compute figsize and limits (1 data unit = 1 mm)
        self.figsize = (width_mm / 25.4, height_mm / 25.4)
        self.xlim = (0, width_mm)
        self.ylim = (0, height_mm)

        self._boxes: Dict[str, BoxSpec] = {}
        self._containers: Dict[str, Dict] = {}
        self._arrows: List[ArrowSpec] = []
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
        position_mm: Optional[Tuple[float, float]] = None,
        size_mm: Optional[Tuple[float, float]] = None,
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
        title_color: Optional[str] = None,
        padding_mm: float = 5.0,
        margin_mm: float = 0.0,
    ) -> "Schematic":
        """Add a rich text box."""
        self._boxes[id] = BoxSpec(
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
        )
        if position_mm and size_mm:
            self._positions[id] = PositionSpec(
                x_mm=position_mm[0],
                y_mm=position_mm[1],
                width_mm=size_mm[0],
                height_mm=size_mm[1],
            )
        return self

    def add_container(
        self,
        id: str,
        title: Optional[str] = None,
        children: Optional[List[str]] = None,
        emphasis: str = "muted",
        position_mm: Optional[Tuple[float, float]] = None,
        size_mm: Optional[Tuple[float, float]] = None,
        fill_color: Optional[str] = None,
        border_color: Optional[str] = None,
    ) -> "Schematic":
        """Add a container that groups other boxes."""
        self._containers[id] = {
            "title": title,
            "children": children or [],
            "emphasis": emphasis,
            "fill_color": fill_color,
            "border_color": border_color,
        }
        if position_mm and size_mm:
            self._positions[id] = PositionSpec(
                x_mm=position_mm[0],
                y_mm=position_mm[1],
                width_mm=size_mm[0],
                height_mm=size_mm[1],
            )
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
    ) -> "Schematic":
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
            )
        )
        return self

    def validate_containers(self) -> None:
        """Check every container fully encloses its declared children."""
        from ._schematic_validate import validate_containers

        validate_containers(self)

    def validate_no_overlap(self) -> None:
        """Check that no two boxes overlap each other."""
        from ._schematic_validate import validate_no_overlap

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
    ) -> "Schematic":
        """Automatically position boxes. See _schematic_layout for details."""
        from ._schematic_layout import auto_layout

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

    def render(self, ax: Optional[Axes] = None) -> Tuple[Figure, Axes]:
        """Render the schematic."""
        figsize = (
            (self.xlim[1] - self.xlim[0]) / 25.4,
            (self.ylim[1] - self.ylim[0]) / 25.4,
        )
        owns_fig = ax is None
        if owns_fig:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        ax.set_xlim(self.xlim)
        ax.set_ylim(self.ylim)
        ax.set_aspect("equal")
        ax.axis("off")

        from . import _schematic_validate as _sv

        # Render everything first (so errored figures can be inspected)
        for cid, container in self._containers.items():
            if cid in self._positions:
                self._render_container(ax, cid, container)
        for bid, box in self._boxes.items():
            if bid in self._positions:
                self._render_box(ax, bid, box)
        for arrow in self._arrows:
            self._render_arrow(ax, arrow)
        if self.title:
            ax.text(
                (self.xlim[0] + self.xlim[1]) / 2,
                self.ylim[1] - 5.0,
                self.title,
                ha="center",
                va="top",
                fontsize=16,
                fontweight="bold",
            )

        # Validate when we own the figure; when ax is external,
        # the caller (schematic_plot) handles validation with error capture
        if owns_fig:
            _sv.validate_all(self, fig=fig, ax=ax)

        return fig, ax

    def _render_container(self, ax: Axes, cid: str, container: Dict) -> None:
        """Render a container box."""
        pos = self._positions[cid]
        colors = get_emphasis_style(container["emphasis"])
        fill = container.get("fill_color") or colors["fill"]
        border = container.get("border_color") or colors["stroke"]

        box = FancyBboxPatch(
            (pos.x_mm - pos.width_mm / 2, pos.y_mm - pos.height_mm / 2),
            pos.width_mm,
            pos.height_mm,
            boxstyle="round,pad=1.0,rounding_size=3.0",
            facecolor=fill,
            edgecolor=border,
            linewidth=2.5,
            zorder=1,
        )
        ax.add_patch(box)

        if container.get("title"):
            _ct_bg = dict(facecolor=fill, edgecolor="none", pad=1.0, alpha=0.85)
            ax.text(
                pos.x_mm,
                pos.y_mm + pos.height_mm / 2 - 1.5,
                container["title"],
                ha="center",
                va="top",
                fontsize=11,
                fontweight="bold",
                color=colors["text"],
                zorder=7,
                bbox=_ct_bg,
            )

        self._render_info[cid] = {"pos": pos}

    # Aesthetic pad for FancyBboxPatch rounding (does NOT affect layout) - now 1mm
    _aesthetic_pad = 1.0

    def _render_box(self, ax: Axes, bid: str, box: BoxSpec) -> None:
        """Render a rich text box."""
        pos = self._positions[bid]
        colors = get_emphasis_style(box.emphasis)
        fill = box.fill_color or colors["fill"]
        border = box.border_color or colors["stroke"]
        title_color = box.title_color or colors["text"]
        pad = self._aesthetic_pad

        shape_styles = {
            "box": f"square,pad={pad}",
            "rounded": f"round,pad={pad},rounding_size=2.0",
            "stadium": f"round,pad={pad},rounding_size=5.0",
        }
        boxstyle = shape_styles.get(box.shape, shape_styles["rounded"])

        patch = FancyBboxPatch(
            (pos.x_mm - pos.width_mm / 2, pos.y_mm - pos.height_mm / 2),
            pos.width_mm,
            pos.height_mm,
            boxstyle=boxstyle,
            facecolor=fill,
            edgecolor=border,
            linewidth=2,
            zorder=2,
        )
        ax.add_patch(patch)

        # Build text items: list of (text, fontsize, fontweight, color)
        items = [(box.title, 11, "bold", title_color)]
        if box.subtitle:
            items.append((box.subtitle, 9, "normal", colors["text"]))
        for line in box.content:
            if isinstance(line, dict):
                items.append(
                    (
                        line.get("text", ""),
                        line.get("fontsize", 8),
                        line.get("fontweight", "normal"),
                        line.get("color", colors["text"]),
                    )
                )
            else:
                items.append((str(line), 8, "normal", colors["text"]))

        # Text area = PositionSpec minus padding on all sides
        inner_h = pos.height_mm - 2 * box.padding_mm
        n = len(items)
        gap = min(inner_h / max(n, 1) * 0.85, 6.0) if n > 1 else 0
        block_h = gap * (n - 1)
        top_y = pos.y_mm + block_h / 2

        _txt_bg = dict(facecolor=fill, edgecolor="none", pad=0.5, alpha=0.85)
        for i, (text, fsize, fweight, fcolor) in enumerate(items):
            ax.text(
                pos.x_mm,
                top_y - i * gap,
                text,
                ha="center",
                va="center",
                fontsize=fsize,
                fontweight=fweight,
                color=fcolor,
                fontstyle="normal",
                zorder=7,
                bbox=_txt_bg,
            )

        self._render_info[bid] = {"pos": pos}

    def _render_arrow(self, ax: Axes, arrow: ArrowSpec) -> None:
        """Render an arrow."""
        if arrow.source not in self._positions or arrow.target not in self._positions:
            return

        src_pos = self._positions[arrow.source]
        tgt_pos = self._positions[arrow.target]

        # Determine anchors
        if arrow.source_anchor == "auto" or arrow.target_anchor == "auto":
            auto_src, auto_tgt = self._auto_anchor(src_pos, tgt_pos)
            src_anc = auto_src if arrow.source_anchor == "auto" else arrow.source_anchor
            tgt_anc = auto_tgt if arrow.target_anchor == "auto" else arrow.target_anchor
        else:
            src_anc, tgt_anc = arrow.source_anchor, arrow.target_anchor

        start = self._get_anchor(src_pos, src_anc)
        end = self._get_anchor(tgt_pos, tgt_anc)

        style = get_edge_style(arrow.style)
        from .._diagram._styles_native import COLORS as _COLORS

        color = _COLORS.get(arrow.color, arrow.color) if arrow.color else style["color"]
        conn = f"arc3,rad={arrow.curve}" if arrow.curve else "arc3,rad=0"

        # Convert linewidth from mm to pt
        linewidth_pt = mm_to_pt(arrow.linewidth_mm)

        patch = FancyArrowPatch(
            posA=start,
            posB=end,
            arrowstyle="-|>",
            color=color,
            linestyle=style["linestyle"],
            linewidth=linewidth_pt,
            connectionstyle=conn,
            mutation_scale=15,
            zorder=5,
        )
        ax.add_patch(patch)

        if arrow.label:
            from ._schematic_validate import compute_arrow_label_position

            lx, ly = compute_arrow_label_position(
                start, end, arrow.curve, arrow.label_offset_mm
            )
            _label_bg = dict(facecolor="white", edgecolor="none", pad=1.0, alpha=0.85)
            ax.text(
                lx,
                ly,
                arrow.label,
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
                fontstyle="italic",
                zorder=6,
                bbox=_label_bg,
            )

    def render_to_file(self, path: Union[str, Path], dpi: int = 200) -> Path:
        """Render and save. On validation failure, saves as *_FAILED.png."""
        path = Path(path)
        try:
            fig, ax = self.render()
        except ValueError:
            fig = plt.gcf()
            failed = path.with_stem(f"{path.stem}_FAILED")
            fig.savefig(failed, dpi=dpi, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            raise
        fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    def to_dict(self) -> Dict[str, Any]:
        """Convert schematic to dictionary for serialization."""
        from ._schematic_io import schematic_to_dict

        return schematic_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schematic":
        """Create Schematic from dictionary (recipe reproduction)."""
        from ._schematic_io import schematic_from_dict

        return schematic_from_dict(data)


__all__ = ["Schematic", "ArrowSpec", "BoxSpec", "PositionSpec"]
