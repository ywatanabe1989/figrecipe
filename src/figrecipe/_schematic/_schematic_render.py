#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rendering functions for schematic diagrams."""

from typing import TYPE_CHECKING, Dict

from matplotlib.axes import Axes
from matplotlib.patches import (
    FancyArrowPatch,
    FancyBboxPatch,
)

from .._diagram._styles_native import COLORS as _COLORS
from .._diagram._styles_native import get_edge_style, get_emphasis_style
from .._utils._units import mm_to_pt

if TYPE_CHECKING:
    from ._schematic import ArrowSpec, BoxSpec, Schematic


def _render_cylinder(ax, pos, fill, border, zorder=2):
    """Draw a database cylinder shape (rectangle body + top/bottom ellipses)."""
    from matplotlib.patches import Ellipse, Rectangle

    x = pos.x_mm - pos.width_mm / 2
    y = pos.y_mm - pos.height_mm / 2
    w = pos.width_mm
    h = pos.height_mm
    ry = min(h * 0.18, w * 0.15)  # ellipse half-height

    # Body rectangle (between ellipse centers)
    body = Rectangle(
        (x, y + ry), w, h - 2 * ry, facecolor=fill, edgecolor="none", zorder=zorder
    )
    ax.add_patch(body)

    # Left and right edges of body
    ax.plot(
        [x, x], [y + ry, y + h - ry], color=border, linewidth=2, zorder=zorder + 0.1
    )
    ax.plot(
        [x + w, x + w],
        [y + ry, y + h - ry],
        color=border,
        linewidth=2,
        zorder=zorder + 0.1,
    )

    # Bottom ellipse (front half only — arc)
    bot = Ellipse(
        (x + w / 2, y + ry),
        w,
        2 * ry,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder + 0.2,
    )
    ax.add_patch(bot)

    # Top ellipse (full, visible)
    top = Ellipse(
        (x + w / 2, y + h - ry),
        w,
        2 * ry,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder + 0.3,
    )
    ax.add_patch(top)


def _render_codeblock(ax, pos, fill, border, zorder=2):
    """Draw a code block shape (rectangle with a colored title bar at top)."""
    from matplotlib.patches import Rectangle

    x = pos.x_mm - pos.width_mm / 2
    y = pos.y_mm - pos.height_mm / 2
    w = pos.width_mm
    h = pos.height_mm
    bar_h = min(h * 0.18, 4.5)  # Title bar height

    # Main body (code area)
    body = Rectangle(
        (x, y),
        w,
        h - bar_h,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder,
    )
    ax.add_patch(body)

    # Title bar (darker strip at top)
    bar = Rectangle(
        (x, y + h - bar_h),
        w,
        bar_h,
        facecolor=border,
        edgecolor=border,
        linewidth=2,
        zorder=zorder + 0.1,
    )
    ax.add_patch(bar)

    # Window dots (three small circles in the title bar)
    dot_r = min(bar_h * 0.2, 0.8)
    dot_y = y + h - bar_h / 2
    for i, dot_color in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
        dot_x = x + 2.5 + i * (dot_r * 3)
        ax.plot(
            dot_x,
            dot_y,
            "o",
            color=dot_color,
            markersize=max(dot_r * 1.5, 2),
            zorder=zorder + 0.2,
            markeredgewidth=0,
        )


def _render_document(ax, pos, fill, border, zorder=2):
    """Draw a document/paper shape (rectangle with folded top-right corner)."""
    from matplotlib.patches import Polygon

    x = pos.x_mm - pos.width_mm / 2
    y = pos.y_mm - pos.height_mm / 2
    w = pos.width_mm
    h = pos.height_mm
    fold = min(w * 0.15, h * 0.2, 5.0)

    # Main body (pentagon — top-right corner cut)
    body = Polygon(
        [
            (x, y),
            (x + w, y),
            (x + w, y + h - fold),
            (x + w - fold, y + h),
            (x, y + h),
        ],
        closed=True,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder,
    )
    ax.add_patch(body)

    # Fold triangle (dog-ear)
    fold_tri = Polygon(
        [
            (x + w - fold, y + h),
            (x + w - fold, y + h - fold),
            (x + w, y + h - fold),
        ],
        closed=True,
        facecolor=border,
        edgecolor=border,
        linewidth=1,
        alpha=0.3,
        zorder=zorder + 0.1,
    )
    ax.add_patch(fold_tri)


def _render_file(ax, pos, fill, border, zorder=2):
    """Draw a file/folder shape (rectangle with tab on top-left)."""
    from matplotlib.patches import Polygon, Rectangle

    x = pos.x_mm - pos.width_mm / 2
    y = pos.y_mm - pos.height_mm / 2
    w = pos.width_mm
    h = pos.height_mm
    tab_w = w * 0.35
    tab_h = min(h * 0.15, 3.0)

    # Main body
    body = Rectangle(
        (x, y),
        w,
        h - tab_h,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder,
    )
    ax.add_patch(body)

    # Tab on top-left
    tab = Polygon(
        [
            (x, y + h - tab_h),
            (x + tab_w, y + h - tab_h),
            (x + tab_w + tab_h, y + h),
            (x, y + h),
        ],
        closed=True,
        facecolor=fill,
        edgecolor=border,
        linewidth=2,
        zorder=zorder + 0.1,
    )
    ax.add_patch(tab)


# Aesthetic pad for FancyBboxPatch rounding (does NOT affect layout) - now 1mm
_AESTHETIC_PAD = 1.0


def render_container(
    schematic: "Schematic", ax: Axes, cid: str, container: Dict
) -> None:
    """Render a container box."""
    pos = schematic._positions[cid]
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
        _bg = dict(facecolor=fill, edgecolor="none", pad=1.0, alpha=0.85)
        loc = container.get("title_loc", "upper center")
        _v, _h = (loc.split() + ["center"])[:2]
        hw = pos.width_mm / 2
        hh = pos.height_mm / 2
        ty = pos.y_mm + (hh - 1.5 if _v == "upper" else -hh + 1.5)
        tx = pos.x_mm + (-hw + 3 if _h == "left" else hw - 3 if _h == "right" else 0)
        ha = {"left": "left", "right": "right"}.get(_h, "center")
        va = "top" if _v == "upper" else "bottom"
        ax.text(
            tx,
            ty,
            container["title"],
            ha=ha,
            va=va,
            fontsize=11,
            fontweight="bold",
            color=colors["text"],
            zorder=7,
            bbox=_bg,
        )

    schematic._render_info[cid] = {"pos": pos}


def render_box(schematic: "Schematic", ax: Axes, bid: str, box: "BoxSpec") -> None:
    """Render a rich text box."""
    pos = schematic._positions[bid]
    colors = get_emphasis_style(box.emphasis)
    fill = box.fill_color or colors["fill"]
    border = box.border_color or colors["stroke"]
    title_color = box.title_color or colors["text"]
    pad = _AESTHETIC_PAD

    if box.shape == "cylinder":
        _render_cylinder(ax, pos, fill, border)
    elif box.shape == "codeblock":
        _render_codeblock(ax, pos, fill, border)
    elif box.shape == "document":
        _render_document(ax, pos, fill, border)
    elif box.shape == "file":
        _render_file(ax, pos, fill, border)
    else:
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

    # Codeblock with syntax highlighting gets special text rendering
    if box.shape == "codeblock" and box.content and box.language:
        from ._schematic_codeblock import render_codeblock_text

        render_codeblock_text(ax, pos, box, fill, title_color, colors)
        schematic._render_info[bid] = {"pos": pos}
        return

    # Build text items: list of (text, fontsize, fontweight, color)
    is_code = box.shape == "codeblock"
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
            items.append((str(line), 8 if not is_code else 7, "normal", colors["text"]))

    # Text area = PositionSpec minus padding on all sides
    inner_h = pos.height_mm - 2 * box.padding_mm
    n = len(items)
    gap = min(inner_h / max(n, 1) * 0.85, 6.0) if n > 1 else 0
    block_h = gap * (n - 1)
    top_y = pos.y_mm + block_h / 2

    _txt_bg = dict(facecolor=fill, edgecolor="none", pad=0.5, alpha=0.85)
    ha = "left" if is_code else "center"
    x_text = (pos.x_mm - pos.width_mm / 2 + box.padding_mm) if is_code else pos.x_mm
    for i, (text, fsize, fweight, fcolor) in enumerate(items):
        ax.text(
            x_text,
            top_y - i * gap,
            text,
            ha=ha,
            va="center",
            fontsize=fsize,
            fontweight=fweight,
            color=fcolor,
            fontfamily="monospace" if is_code and i > 0 else "sans-serif",
            fontstyle="normal",
            zorder=7,
            bbox=_txt_bg,
        )

    schematic._render_info[bid] = {"pos": pos}


def render_icon(schematic, ax, iid, icon):
    """Delegate to icons module."""
    from ._schematic_icons import render_icon as _ri

    _ri(schematic, ax, iid, icon)


def render_arrow(schematic: "Schematic", ax: Axes, arrow: "ArrowSpec") -> None:
    """Render an arrow."""
    if (
        arrow.source not in schematic._positions
        or arrow.target not in schematic._positions
    ):
        return

    src_pos = schematic._positions[arrow.source]
    tgt_pos = schematic._positions[arrow.target]

    # Determine anchors
    if arrow.source_anchor == "auto" or arrow.target_anchor == "auto":
        auto_src, auto_tgt = schematic._auto_anchor(src_pos, tgt_pos)
        src_anc = auto_src if arrow.source_anchor == "auto" else arrow.source_anchor
        tgt_anc = auto_tgt if arrow.target_anchor == "auto" else arrow.target_anchor
    else:
        src_anc, tgt_anc = arrow.source_anchor, arrow.target_anchor

    start = schematic._get_anchor(src_pos, src_anc)
    end = schematic._get_anchor(tgt_pos, tgt_anc)

    # Apply angle-aware margin accounting for visual box padding
    import math

    _DEFAULT_CLEARANCE = 1.0  # Perpendicular gap from visual box edge (mm)

    dx, dy = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dx, dy)
    if dist > 1e-6:
        ux, uy = dx / dist, dy / dist
        clearance = (
            arrow.margin_mm if arrow.margin_mm is not None else _DEFAULT_CLEARANCE
        )
        # Offset from logical anchor = clearance + pad (visual edge extends by pad)
        total_perp = clearance + _AESTHETIC_PAD

        def _margin_for_anchor(anc):
            if anc in ("top-left", "top-right", "bottom-left", "bottom-right"):
                return total_perp * math.sqrt(2)
            elif anc in ("top", "bottom"):
                return total_perp / abs(uy) if abs(uy) > 1e-6 else total_perp
            elif anc in ("left", "right"):
                return total_perp / abs(ux) if abs(ux) > 1e-6 else total_perp
            else:
                return total_perp

        src_margin = _margin_for_anchor(src_anc)
        tgt_margin = _margin_for_anchor(tgt_anc)
        # Use same margin at both ends for visual symmetry
        margin = max(src_margin, tgt_margin)
        # Cap at 25% of arrow length to prevent disappearing arrows
        margin = min(margin, dist * 0.25)
        if dist > margin * 2:
            start = (start[0] + ux * margin, start[1] + uy * margin)
            end = (end[0] - ux * margin, end[1] - uy * margin)

    style = get_edge_style(arrow.style)
    color = _COLORS.get(arrow.color, arrow.color) if arrow.color else style["color"]
    conn = f"arc3,rad={arrow.curve}" if arrow.curve else "arc3,rad=0"
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
