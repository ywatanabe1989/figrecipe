#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Icon rendering for schematic diagrams.

Supports built-in icons (warning, check, cross, info, lock)
and file-based icons (PNG, JPG, SVG).
"""

from typing import TYPE_CHECKING

from matplotlib.axes import Axes

if TYPE_CHECKING:
    from ._schematic import Diagram, IconSpec


# ── Built-in icon renderers ──────────────────────────────────────────


def _icon_warning(ax, cx, cy, w, h, color, alpha):
    """Warning triangle with exclamation mark."""
    from matplotlib.patches import Polygon

    hw, hh = w / 2, h / 2
    tri = Polygon(
        [(cx, cy + hh), (cx - hw, cy - hh), (cx + hw, cy - hh)],
        closed=True,
        facecolor="#FFCC00",
        edgecolor=color,
        linewidth=1.5,
        alpha=alpha,
        zorder=6,
    )
    ax.add_patch(tri)
    ax.text(
        cx,
        cy - hh * 0.15,
        "!",
        ha="center",
        va="center",
        fontsize=h * 0.6,
        fontweight="bold",
        color=color,
        zorder=7,
    )


def _icon_check(ax, cx, cy, w, h, color, alpha):
    """Green checkmark circle."""
    from matplotlib.patches import Circle

    r = min(w, h) / 2
    circ = Circle(
        (cx, cy),
        r,
        facecolor="#90EE90",
        edgecolor=color,
        linewidth=1.5,
        alpha=alpha,
        zorder=6,
    )
    ax.add_patch(circ)
    ax.plot(
        [cx - r * 0.4, cx - r * 0.05, cx + r * 0.45],
        [cy, cy - r * 0.35, cy + r * 0.35],
        color=color,
        linewidth=2,
        solid_capstyle="round",
        zorder=7,
    )


def _icon_cross(ax, cx, cy, w, h, color, alpha):
    """Red X-mark circle."""
    from matplotlib.patches import Circle

    r = min(w, h) / 2
    circ = Circle(
        (cx, cy),
        r,
        facecolor="#FFB6C1",
        edgecolor=color,
        linewidth=1.5,
        alpha=alpha,
        zorder=6,
    )
    ax.add_patch(circ)
    d = r * 0.35
    ax.plot(
        [cx - d, cx + d],
        [cy - d, cy + d],
        color=color,
        linewidth=2,
        solid_capstyle="round",
        zorder=7,
    )
    ax.plot(
        [cx - d, cx + d],
        [cy + d, cy - d],
        color=color,
        linewidth=2,
        solid_capstyle="round",
        zorder=7,
    )


def _icon_info(ax, cx, cy, w, h, color, alpha):
    """Info circle with 'i'."""
    from matplotlib.patches import Circle

    r = min(w, h) / 2
    circ = Circle(
        (cx, cy),
        r,
        facecolor="#B0C4DE",
        edgecolor=color,
        linewidth=1.5,
        alpha=alpha,
        zorder=6,
    )
    ax.add_patch(circ)
    ax.text(
        cx,
        cy,
        "i",
        ha="center",
        va="center",
        fontsize=h * 0.55,
        fontweight="bold",
        fontstyle="italic",
        color=color,
        zorder=7,
    )


def _icon_lock(ax, cx, cy, w, h, color, alpha):
    """Padlock icon."""
    from matplotlib.patches import Arc, FancyBboxPatch

    bw, bh = w * 0.6, h * 0.45
    body = FancyBboxPatch(
        (cx - bw / 2, cy - h * 0.35),
        bw,
        bh,
        boxstyle="round,pad=0.3",
        facecolor="#FFD700",
        edgecolor=color,
        linewidth=1.5,
        alpha=alpha,
        zorder=6,
    )
    ax.add_patch(body)
    arc = Arc(
        (cx, cy + h * 0.05),
        bw * 0.6,
        h * 0.5,
        angle=0,
        theta1=0,
        theta2=180,
        color=color,
        linewidth=2,
        zorder=7,
    )
    ax.add_patch(arc)


_BUILTINS = {
    "warning": _icon_warning,
    "check": _icon_check,
    "cross": _icon_cross,
    "info": _icon_info,
    "lock": _icon_lock,
}


# ── Main render function ─────────────────────────────────────────────


def render_icon(
    schematic: "Diagram",
    ax: Axes,
    iid: str,
    icon: "IconSpec",
) -> None:
    """Render an icon (built-in path or image file)."""
    from pathlib import Path as _Path

    pos = schematic._positions[iid]
    color = icon.color or "#333333"
    alpha = icon.opacity
    cx, cy = pos.x_mm, pos.y_mm
    w, h = pos.width_mm, pos.height_mm

    if icon.source in _BUILTINS:
        _BUILTINS[icon.source](ax, cx, cy, w, h, color, alpha)
    else:
        fpath = _Path(icon.source)
        if fpath.exists() and fpath.suffix.lower() in (".png", ".jpg", ".jpeg"):
            _render_image_icon(ax, fpath, cx, cy, w, alpha)
        elif fpath.exists() and fpath.suffix.lower() == ".svg":
            _render_svg_icon(ax, fpath, cx, cy, w, alpha)

    schematic._render_info[iid] = {"pos": pos}


def _render_image_icon(ax, fpath, cx, cy, w, alpha):
    """Render a raster image icon (PNG/JPG)."""
    import matplotlib.image as mpimg
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage

    img = mpimg.imread(str(fpath))
    dpi = ax.figure.dpi
    fig_w_inch = ax.figure.get_figwidth()
    data_w = ax.get_xlim()[1] - ax.get_xlim()[0]
    px_per_mm = (fig_w_inch * dpi) / data_w
    target_px = w * px_per_mm
    img_px = img.shape[1]
    zoom = target_px / img_px if img_px > 0 else 1.0
    im = OffsetImage(img, zoom=zoom, alpha=alpha)
    ab = AnnotationBbox(im, (cx, cy), frameon=False, zorder=6)
    ax.add_artist(ab)


def _render_svg_icon(ax, fpath, cx, cy, w, alpha):
    """Render an SVG icon (requires svglib + reportlab)."""
    try:
        from io import BytesIO

        import matplotlib.image as mpimg
        from matplotlib.offsetbox import AnnotationBbox, OffsetImage
        from reportlab.graphics import renderPM
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(str(fpath))
        bio = BytesIO()
        renderPM.drawToFile(drawing, bio, fmt="PNG", dpi=300)
        bio.seek(0)
        img = mpimg.imread(bio, format="png")
        dpi = ax.figure.dpi
        fig_w_inch = ax.figure.get_figwidth()
        data_w = ax.get_xlim()[1] - ax.get_xlim()[0]
        px_per_mm = (fig_w_inch * dpi) / data_w
        target_px = w * px_per_mm
        img_px = img.shape[1]
        zoom = target_px / img_px if img_px > 0 else 1.0
        im = OffsetImage(img, zoom=zoom, alpha=alpha)
        ab = AnnotationBbox(im, (cx, cy), frameon=False, zorder=6)
        ax.add_artist(ab)
    except ImportError:
        ax.text(
            cx,
            cy,
            "[SVG]",
            ha="center",
            va="center",
            fontsize=6,
            color="#999999",
            zorder=7,
        )


# EOF
