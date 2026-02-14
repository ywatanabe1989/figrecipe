#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS flexbox-like layout resolver for schematic diagrams.

When a Diagram is created with ``gap_mm`` set, elements added without
explicit x_mm/y_mm are stacked vertically (top-to-bottom) with uniform
spacing.  Containers arrange their children horizontally (direction="row")
or vertically (direction="column").
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._schematic import Diagram

# Minimum gap between elements connected by an arrow (mm).
# Ensures the arrow shaft is visible beyond the arrowhead.
_MIN_ARROW_GAP_MM = 15.0


def _arrow_connected_pairs(info: "Diagram") -> set:
    """Return set of (source, target) pairs that have arrows between them."""
    return {(a.source, a.target) for a in info._arrows}


def _effective_gap(
    base_gap: float, prev_id: str, next_id: str, connected: set
) -> float:
    """Return gap between two adjacent items, enlarged if arrow-connected."""
    if (prev_id, next_id) in connected or (next_id, prev_id) in connected:
        return max(base_gap, _MIN_ARROW_GAP_MM)
    return base_gap


def resolve_flex_layout(info: "Diagram") -> None:
    """Resolve positions for all flex-layout elements.

    Called from ``_finalize_canvas_size()`` before bounding-box computation.
    No-op when ``gap_mm`` is not set on the Diagram.
    """
    if info._gap_mm is None:
        return
    if not info._flow_items:
        return

    connected = _arrow_connected_pairs(info)

    # Identify top-level items (not children of any container)
    all_children: set = set()
    for container in info._containers.values():
        all_children.update(container["children"])
    top_items = [eid for eid in info._flow_items if eid not in all_children]

    # Pass 1: compute container sizes from children (boxes already sized)
    for cid in info._flow_items:
        if cid in info._containers:
            _compute_container_size(info, cid, connected)

    # Pass 2: stack top-level items vertically (top-to-bottom)
    cx = info.width_mm / 2
    heights = [info._positions[eid].height_mm for eid in top_items]
    gaps = _pairwise_gaps(info._gap_mm, top_items, connected)
    total = sum(heights) + sum(gaps)

    pad = info._padding_mm
    y = total + pad  # start from top of content area

    for i, eid in enumerate(top_items):
        h = info._positions[eid].height_mm
        y -= h / 2
        info._positions[eid].x_mm = cx
        info._positions[eid].y_mm = y
        gap = gaps[i] if i < len(gaps) else 0
        y -= h / 2 + gap

        # Position container children within the container
        if eid in info._containers:
            _position_children(info, eid, connected)


def _pairwise_gaps(base_gap: float, items: list, connected: set) -> list:
    """Compute gap after each item (except the last)."""
    gaps = []
    for i in range(len(items) - 1):
        gaps.append(_effective_gap(base_gap, items[i], items[i + 1], connected))
    return gaps


def _compute_container_size(info: "Diagram", cid: str, connected: set) -> None:
    """Compute container intrinsic size from its children (recursive)."""
    from ._schematic import PositionSpec

    container = info._containers[cid]
    children = container["children"]
    direction = container.get("direction", "row")
    c_gap = container.get("gap_mm", 8.0)
    c_pad = container.get("padding_mm", 8.0)
    title_h = 8.0 if container.get("title") else 0.0

    # Recursively compute child containers first (bottom-up)
    for child in children:
        if child in info._containers:
            pos = info._positions.get(child)
            if pos is None or pos.height_mm == 0:
                _compute_container_size(info, child, connected)

    child_sizes = [
        (info._positions[c].width_mm, info._positions[c].height_mm)
        for c in children
        if c in info._positions
    ]
    if not child_sizes:
        return

    gaps = _pairwise_gaps(c_gap, children, connected)
    total_gaps = sum(gaps)

    if direction == "row":
        w = sum(s[0] for s in child_sizes) + total_gaps + 2 * c_pad
        h = max(s[1] for s in child_sizes) + title_h + 2 * c_pad
    else:
        w = max(s[0] for s in child_sizes) + 2 * c_pad
        h = sum(s[1] for s in child_sizes) + total_gaps + title_h + 2 * c_pad

    # Respect explicit width/height overrides (non-zero placeholder)
    pos = info._positions.get(cid)
    if pos and pos.width_mm > 0:
        w = pos.width_mm
    if pos and pos.height_mm > 0:
        h = pos.height_mm

    info._positions[cid] = PositionSpec(0, 0, w, h)


def _position_children(info: "Diagram", cid: str, connected: set) -> None:
    """Position children within a resolved container."""
    container = info._containers[cid]
    pos = info._positions[cid]
    direction = container.get("direction", "row")
    c_gap = container.get("gap_mm", 8.0)
    c_pad = container.get("padding_mm", 8.0)
    title_h = 8.0 if container.get("title") else 0.0
    children = container["children"]
    gaps = _pairwise_gaps(c_gap, children, connected)

    # Content center offset for title
    content_cy = pos.y_mm - title_h / 2

    if direction == "row":
        child_widths = [info._positions[c].width_mm for c in children]
        total_w = sum(child_widths) + sum(gaps)
        x = pos.x_mm - total_w / 2
        for i, child_id in enumerate(children):
            cp = info._positions[child_id]
            x += cp.width_mm / 2
            cp.x_mm = x
            cp.y_mm = content_cy
            gap = gaps[i] if i < len(gaps) else 0
            x += cp.width_mm / 2 + gap
            if child_id in info._containers:
                _position_children(info, child_id, connected)
    else:
        y = pos.y_mm + pos.height_mm / 2 - c_pad - title_h
        for i, child_id in enumerate(children):
            cp = info._positions[child_id]
            y -= cp.height_mm / 2
            cp.x_mm = pos.x_mm
            cp.y_mm = y
            gap = gaps[i] if i < len(gaps) else 0
            y -= cp.height_mm / 2 + gap
            if child_id in info._containers:
                _position_children(info, child_id, connected)


def auto_box_width(box) -> float:
    """Compute box width from text content when width_mm is not specified.

    Estimates width from the longest text line using ~2.2mm per character
    (approximate for 10pt sans-serif), plus padding.
    """
    mm_per_char = 2.2
    texts = [box.title]
    if box.subtitle:
        texts.append(box.subtitle)
    texts.extend(box.content)
    max_chars = max((len(t) for t in texts), default=4)
    return max(max_chars * mm_per_char + 2 * box.padding_mm, 24.0)


__all__ = ["auto_box_width", "resolve_flex_layout"]
