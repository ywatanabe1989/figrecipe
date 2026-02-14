#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSS flexbox-like layout resolver for schematic diagrams.

When a Schematic is created with ``gap_mm`` set, elements added without
explicit x_mm/y_mm are stacked vertically (top-to-bottom) with uniform
spacing.  Containers arrange their children horizontally (direction="row")
or vertically (direction="column").
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._schematic import Schematic


def resolve_flex_layout(info: "Schematic") -> None:
    """Resolve positions for all flex-layout elements.

    Called from ``_finalize_canvas_size()`` before bounding-box computation.
    No-op when ``gap_mm`` is not set on the Schematic.
    """
    if info._gap_mm is None:
        return
    if not info._flow_items:
        return

    # Identify top-level items (not children of any container)
    all_children: set = set()
    for container in info._containers.values():
        all_children.update(container["children"])
    top_items = [eid for eid in info._flow_items if eid not in all_children]

    # Pass 1: compute container sizes from children (boxes already sized)
    for cid in info._flow_items:
        if cid in info._containers:
            _compute_container_size(info, cid)

    # Pass 2: stack top-level items vertically (top-to-bottom)
    cx = info.width_mm / 2
    heights = [info._positions[eid].height_mm for eid in top_items]
    total = sum(heights) + info._gap_mm * max(len(top_items) - 1, 0)

    pad = info._padding_mm
    y = total + pad  # start from top of content area

    for eid in top_items:
        h = info._positions[eid].height_mm
        y -= h / 2
        info._positions[eid].x_mm = cx
        info._positions[eid].y_mm = y
        y -= h / 2 + info._gap_mm

        # Position container children within the container
        if eid in info._containers:
            _position_children(info, eid)


def _compute_container_size(info: "Schematic", cid: str) -> None:
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
                _compute_container_size(info, child)

    child_sizes = [
        (info._positions[c].width_mm, info._positions[c].height_mm)
        for c in children
        if c in info._positions
    ]
    if not child_sizes:
        return

    if direction == "row":
        w = sum(s[0] for s in child_sizes) + c_gap * (len(child_sizes) - 1) + 2 * c_pad
        h = max(s[1] for s in child_sizes) + title_h + 2 * c_pad
    else:
        w = max(s[0] for s in child_sizes) + 2 * c_pad
        h = (
            sum(s[1] for s in child_sizes)
            + c_gap * (len(child_sizes) - 1)
            + title_h
            + 2 * c_pad
        )

    # Respect explicit width/height overrides (non-zero placeholder)
    pos = info._positions.get(cid)
    if pos and pos.width_mm > 0:
        w = pos.width_mm
    if pos and pos.height_mm > 0:
        h = pos.height_mm

    info._positions[cid] = PositionSpec(0, 0, w, h)


def _position_children(info: "Schematic", cid: str) -> None:
    """Position children within a resolved container."""
    container = info._containers[cid]
    pos = info._positions[cid]
    direction = container.get("direction", "row")
    c_gap = container.get("gap_mm", 8.0)
    c_pad = container.get("padding_mm", 8.0)
    title_h = 8.0 if container.get("title") else 0.0
    children = container["children"]

    # Content center offset for title
    content_cy = pos.y_mm - title_h / 2

    if direction == "row":
        child_widths = [info._positions[c].width_mm for c in children]
        total_w = sum(child_widths) + c_gap * (len(children) - 1)
        x = pos.x_mm - total_w / 2
        for child_id in children:
            cp = info._positions[child_id]
            x += cp.width_mm / 2
            cp.x_mm = x
            cp.y_mm = content_cy
            x += cp.width_mm / 2 + c_gap
            if child_id in info._containers:
                _position_children(info, child_id)
    else:
        y = pos.y_mm + pos.height_mm / 2 - c_pad - title_h
        for child_id in children:
            cp = info._positions[child_id]
            y -= cp.height_mm / 2
            cp.x_mm = pos.x_mm
            cp.y_mm = y
            y -= cp.height_mm / 2 + c_gap
            if child_id in info._containers:
                _position_children(info, child_id)


__all__ = ["resolve_flex_layout"]
