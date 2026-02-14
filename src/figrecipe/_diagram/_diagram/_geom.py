#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geometry helpers for schematic validation."""

import math


def box_rect(pos):
    """Return (left, bottom, right, top) from a PositionSpec."""
    return (
        pos.x_mm - pos.width_mm / 2,
        pos.y_mm - pos.height_mm / 2,
        pos.x_mm + pos.width_mm / 2,
        pos.y_mm + pos.height_mm / 2,
    )


def rects_overlap(r1, r2):
    """Check if two (left, bottom, right, top) rectangles overlap."""
    return r1[0] < r2[2] and r2[0] < r1[2] and r1[1] < r2[3] and r2[1] < r1[3]


def overlap_area(bb_a, bb_b):
    """Compute overlap area of two Bbox objects. Returns 0 if no overlap."""
    x_overlap = max(0, min(bb_a.x1, bb_b.x1) - max(bb_a.x0, bb_b.x0))
    y_overlap = max(0, min(bb_a.y1, bb_b.y1) - max(bb_a.y0, bb_b.y0))
    return x_overlap * y_overlap


def bbox_gap(bb_a, bb_b):
    """Minimum gap (mm) between two Bbox objects. Negative = overlap."""
    x_gap = max(bb_a.x0 - bb_b.x1, bb_b.x0 - bb_a.x1)
    y_gap = max(bb_a.y0 - bb_b.y1, bb_b.y0 - bb_a.y1)
    return max(x_gap, y_gap)


def seg_rect_clip_len(x0, y0, x1, y1, left, bottom, right, top):
    """Clipped length of segment inside rectangle (Liang-Barsky)."""
    dx, dy = x1 - x0, y1 - y0
    seg_len = math.hypot(dx, dy)
    if seg_len < 1e-9:
        return 0.0
    t0, t1 = 0.0, 1.0
    for p, q in [
        (-dx, x0 - left),
        (dx, right - x0),
        (-dy, y0 - bottom),
        (dy, top - y0),
    ]:
        if abs(p) < 1e-12:
            if q < 0:
                return 0.0
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return (t1 - t0) * seg_len if t0 <= t1 else 0.0


# EOF
