#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layout validation for Schematic diagrams.

Rules (all enforced programmatically):
  R1  Container must enclose all children          → ValueError
  R2  No two boxes may overlap                     → ValueError
  R3  Container title must clear children (5mm)    → UserWarning
  R4  Box text must fit within padded inner area    → UserWarning
  R5  Text-to-text margin >= MIN_MARGIN_MM          → ValueError
  R6  Text-to-edge margin >= MIN_MARGIN_MM          → ValueError
  R7  Arrow visible-length ratio >= MIN_VISIBLE     → ValueError
  R8  Curved-arrow label on same side as arc        → ValueError
"""

from typing import TYPE_CHECKING

# Centralised thresholds
MIN_MARGIN_MM = 2.0  # R5, R6
MIN_VISIBLE = 0.9  # R7

if TYPE_CHECKING:
    from ._schematic import Schematic


def validate_containers(schematic: "Schematic") -> None:
    """Check that every container fully encloses its declared children.

    Parameters
    ----------
    schematic : Schematic
        The schematic to validate.

    Raises
    ------
    ValueError
        If any child box extends outside its parent container.
    """
    for cid, container in schematic._containers.items():
        if cid not in schematic._positions:
            continue
        cpos = schematic._positions[cid]
        c_left = cpos.x_mm - cpos.width_mm / 2
        c_right = cpos.x_mm + cpos.width_mm / 2
        c_bottom = cpos.y_mm - cpos.height_mm / 2
        c_top = cpos.y_mm + cpos.height_mm / 2

        for child_id in container.get("children", []):
            if child_id not in schematic._positions:
                continue
            chpos = schematic._positions[child_id]
            ch_left = chpos.x_mm - chpos.width_mm / 2
            ch_right = chpos.x_mm + chpos.width_mm / 2
            ch_bottom = chpos.y_mm - chpos.height_mm / 2
            ch_top = chpos.y_mm + chpos.height_mm / 2

            violations = []
            if ch_left < c_left:
                violations.append(
                    f"left edge ({ch_left:.1f}) < container left ({c_left:.1f})"
                )
            if ch_right > c_right:
                violations.append(
                    f"right edge ({ch_right:.1f}) > container right ({c_right:.1f})"
                )
            if ch_bottom < c_bottom:
                violations.append(
                    f"bottom edge ({ch_bottom:.1f}) < container bottom ({c_bottom:.1f})"
                )
            if ch_top > c_top:
                violations.append(
                    f"top edge ({ch_top:.1f}) > container top ({c_top:.1f})"
                )

            if violations:
                raise ValueError(
                    f"Child '{child_id}' extends outside container "
                    f"'{cid}': " + "; ".join(violations)
                )


def _box_rect(pos):
    """Return (left, bottom, right, top) from a PositionSpec."""
    return (
        pos.x_mm - pos.width_mm / 2,
        pos.y_mm - pos.height_mm / 2,
        pos.x_mm + pos.width_mm / 2,
        pos.y_mm + pos.height_mm / 2,
    )


def _rects_overlap(r1, r2):
    """Check if two (left, bottom, right, top) rectangles overlap."""
    return r1[0] < r2[2] and r2[0] < r1[2] and r1[1] < r2[3] and r2[1] < r1[3]


def validate_no_overlap(schematic: "Schematic") -> None:
    """Check that no two boxes overlap each other.

    Containers are excluded — only boxes are checked.

    Raises
    ------
    ValueError
        If any two boxes overlap.
    """
    from itertools import combinations

    box_ids = [bid for bid in schematic._boxes if bid in schematic._positions]
    for id_a, id_b in combinations(box_ids, 2):
        r_a = _box_rect(schematic._positions[id_a])
        r_b = _box_rect(schematic._positions[id_b])
        if _rects_overlap(r_a, r_b):
            raise ValueError(
                f"Boxes '{id_a}' and '{id_b}' overlap: "
                f"'{id_a}' rect=({r_a[0]:.1f},{r_a[1]:.1f})-"
                f"({r_a[2]:.1f},{r_a[3]:.1f}), "
                f"'{id_b}' rect=({r_b[0]:.1f},{r_b[1]:.1f})-"
                f"({r_b[2]:.1f},{r_b[3]:.1f})"
            )


def _overlap_area(bb_a, bb_b):
    """Compute overlap area of two Bbox objects. Returns 0 if no overlap."""
    x_overlap = max(0, min(bb_a.x1, bb_b.x1) - max(bb_a.x0, bb_b.x0))
    y_overlap = max(0, min(bb_a.y1, bb_b.y1) - max(bb_a.y0, bb_b.y0))
    return x_overlap * y_overlap


def _bbox_gap(bb_a, bb_b):
    """Minimum gap (mm) between two Bbox objects. Negative = overlap."""
    x_gap = max(bb_a.x0 - bb_b.x1, bb_b.x0 - bb_a.x1)
    y_gap = max(bb_a.y0 - bb_b.y1, bb_b.y0 - bb_a.y1)
    return max(x_gap, y_gap)


def validate_text_margins(fig, ax, schematic, min_margin_mm=MIN_MARGIN_MM) -> None:
    """Check all text has minimum margin from other text and box edges.

    Raises ValueError if text-to-text or text-to-edge gap < min_margin_mm.
    Arrows are excluded (accepted by design).
    Must be called after render.
    """
    from itertools import combinations

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    texts = [t for t in ax.texts if t.get_text().strip()]
    if not texts:
        return

    # Build box rects for ownership lookup
    box_rects = {}
    for eid in list(schematic._boxes) + list(schematic._containers):
        if eid in schematic._positions:
            box_rects[eid] = _box_rect(schematic._positions[eid])

    def _owner(bb):
        """Return the box/container ID whose rect contains bb center."""
        cx, cy = (bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2
        for eid, (el, eb, er, et) in box_rects.items():
            if el <= cx <= er and eb <= cy <= et and eid in schematic._boxes:
                return eid
        return None

    entries = []
    for t in texts:
        bb = t.get_window_extent(renderer).transformed(ax.transData.inverted())
        entries.append((t.get_text(), bb, _owner(bb)))

    # 1. Text-to-text margin check (skip pairs in same box)
    for (txt_a, bb_a, own_a), (txt_b, bb_b, own_b) in combinations(entries, 2):
        if own_a is not None and own_a == own_b:
            continue
        gap = _bbox_gap(bb_a, bb_b)
        if gap < min_margin_mm:
            raise ValueError(
                f"Text margin violation: '{txt_a}' and '{txt_b}' "
                f"gap={gap:.1f}mm (min={min_margin_mm}mm)"
            )

    # 2. Text-to-box/container-edge margin check
    edges = []
    for eid in list(schematic._boxes) + list(schematic._containers):
        if eid in schematic._positions:
            edges.append((eid, _box_rect(schematic._positions[eid])))

    for txt, bb, _own in entries:
        for eid, (el, eb, er, et) in edges:
            # Skip if text center is inside this box (it belongs there)
            cx = (bb.x0 + bb.x1) / 2
            cy = (bb.y0 + bb.y1) / 2
            if el <= cx <= er and eb <= cy <= et:
                continue
            # Check gap to this edge rect
            from matplotlib.transforms import Bbox

            edge_bb = Bbox([[el, eb], [er, et]])
            gap = _bbox_gap(bb, edge_bb)
            if gap < min_margin_mm:
                raise ValueError(
                    f"Text '{txt}' too close to '{eid}' edge: "
                    f"gap={gap:.1f}mm (min={min_margin_mm}mm)"
                )


def validate_text_no_overlap(fig, ax, min_overlap_ratio=0.05) -> None:
    """Legacy wrapper — kept for backward compatibility."""
    pass  # Superseded by validate_text_margins


def validate_container_title_clearance(
    schematic: "Schematic", min_gap_mm: float = 3.0
) -> None:
    """Warn if container title area overlaps with children.

    The title occupies approximately 5mm from the container top edge.
    Children whose top edge is within this zone get a warning.
    """
    import warnings

    _TITLE_ZONE_MM = 5.0  # approximate height of title text region

    for cid, container in schematic._containers.items():
        if cid not in schematic._positions or not container.get("title"):
            continue
        cpos = schematic._positions[cid]
        c_top = cpos.y_mm + cpos.height_mm / 2
        title_bottom = c_top - _TITLE_ZONE_MM

        for child_id in container.get("children", []):
            if child_id not in schematic._positions:
                continue
            chpos = schematic._positions[child_id]
            ch_top = chpos.y_mm + chpos.height_mm / 2
            gap = title_bottom - ch_top
            if gap < min_gap_mm:
                warnings.warn(
                    f"Container '{cid}' title too close to child "
                    f"'{child_id}': gap={gap:.1f}mm (min={min_gap_mm}mm). "
                    f"Increase container height or lower child.",
                    UserWarning,
                    stacklevel=3,
                )


def validate_text_fits_boxes(schematic: "Schematic") -> None:
    """Warn if a box has more text lines than fit within its padded area.

    Estimates text height from font sizes (1pt ≈ 0.35mm) and checks
    against the box inner height (height - 2*padding).
    """
    import warnings

    _PT_TO_MM = 0.35  # approximate pt → mm conversion

    for bid, box in schematic._boxes.items():
        if bid not in schematic._positions:
            continue
        pos = schematic._positions[bid]
        inner_h = pos.height_mm - 2 * box.padding_mm

        # Estimate total text height
        text_h = 11 * _PT_TO_MM  # title always present
        if box.subtitle:
            text_h += 9 * _PT_TO_MM
        text_h += len(box.content) * 8 * _PT_TO_MM

        if text_h > inner_h:
            warnings.warn(
                f"Box '{bid}' text (~{text_h:.1f}mm) exceeds "
                f"inner height ({inner_h:.1f}mm). "
                f"Increase box height or reduce content.",
                UserWarning,
                stacklevel=3,
            )


def validate_text_arrow_no_overlap(fig, ax, schematic=None, min_visible=MIN_VISIBLE):
    """Raise if arrow visible-length ratio drops below min_visible.

    Flattens each arrow's Bezier curve into line segments, measures
    total arc length, and subtracts the length occluded by text bboxes.
    """
    import math

    from matplotlib.patches import FancyArrowPatch

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    texts = [t for t in ax.texts if t.get_text().strip()]
    arrows = [p for p in ax.patches if isinstance(p, FancyArrowPatch)]
    if not texts or not arrows:
        return

    arrow_ids = []
    if schematic is not None:
        arrow_ids = [a.id or f"arrow#{i}" for i, a in enumerate(schematic._arrows)]

    text_bbs = []
    for t in texts:
        bb = t.get_window_extent(renderer).transformed(inv)
        text_bbs.append((t.get_text(), bb))

    for i, arrow in enumerate(arrows):
        aid = arrow_ids[i] if i < len(arrow_ids) else f"arrow#{i}"
        # Flatten Bezier curves into dense polygon points
        disp_path = arrow.get_path().transformed(arrow.get_transform())
        polys = disp_path.to_polygons(closed_only=False)
        if not polys:
            continue
        # Transform polygon points to data coords
        pts_disp = polys[0]
        pts = inv.transform(pts_disp)
        if len(pts) < 2:
            continue
        # Measure total length and occluded length per segment
        total_len = 0.0
        occluded_len = 0.0
        occluders = set()
        for j in range(len(pts) - 1):
            x0, y0 = pts[j]
            x1, y1 = pts[j + 1]
            seg_len = math.hypot(x1 - x0, y1 - y0)
            total_len += seg_len
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            for txt, bb in text_bbs:
                if bb.x0 <= mx <= bb.x1 and bb.y0 <= my <= bb.y1:
                    occluded_len += seg_len
                    occluders.add(txt)
                    break
        if total_len < 1e-6:
            continue
        visible_ratio = 1.0 - occluded_len / total_len
        if visible_ratio < min_visible:
            occ_str = ", ".join(f"'{t}'" for t in sorted(occluders))
            raise ValueError(
                f"'{aid}' visibility {visible_ratio:.0%} < {min_visible:.0%}. "
                f"Occluded by: {occ_str}"
            )


def validate_arrow_label_side(schematic: "Schematic") -> None:
    """R8: Curved-arrow label must be on same side as arc bulge.

    For each arrow with curve != 0 and a label, checks that the final
    label position is on the same side of the straight line as the arc.
    """
    import math

    for arrow in schematic._arrows:
        if not arrow.curve or not arrow.label:
            continue
        src_pos = schematic._positions.get(arrow.source)
        tgt_pos = schematic._positions.get(arrow.target)
        if not src_pos or not tgt_pos:
            continue
        # Resolve anchors
        if arrow.source_anchor == "auto" or arrow.target_anchor == "auto":
            auto_s, auto_t = schematic._auto_anchor(src_pos, tgt_pos)
            sa = auto_s if arrow.source_anchor == "auto" else arrow.source_anchor
            ta = auto_t if arrow.target_anchor == "auto" else arrow.target_anchor
        else:
            sa, ta = arrow.source_anchor, arrow.target_anchor
        start = schematic._get_anchor(src_pos, sa)
        end = schematic._get_anchor(tgt_pos, ta)
        lx, ly = compute_arrow_label_position(
            start, end, arrow.curve, arrow.label_offset_mm
        )
        # Arc side: perpendicular of (start→end), scaled by curve sign
        dx, dy = end[0] - start[0], end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            continue
        nx, ny = dy / dist, -dx / dist  # same as in compute_arrow_label_position
        arc_side = nx * arrow.curve, ny * arrow.curve  # direction of bulge
        # Label offset from straight-line midpoint
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        label_off = (lx - mx, ly - my)
        # Dot product: positive means same side
        dot = label_off[0] * arc_side[0] + label_off[1] * arc_side[1]
        if dot < 0:
            aid = arrow.id or f"{arrow.source}->{arrow.target}"
            raise ValueError(
                f"R8: '{aid}' label '{arrow.label}' is on the wrong side "
                f"of the arc. Flip curve sign or adjust label_offset_mm."
            )


def compute_arrow_label_position(start, end, curve, label_offset_mm=None):
    """Compute label position for an arrow, accounting for curve.

    For curved arrows (arc3), the label is placed at the curve's peak
    rather than the straight-line midpoint.

    Returns (x_mm, y_mm) for the label center.
    """
    import math

    mx = (start[0] + end[0]) / 2
    my = (start[1] + end[1]) / 2

    if curve:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            # Perpendicular matching arc3: control = mid + rad*(dy, -dx)
            nx, ny = dy / dist, -dx / dist
            # arc3 peak deviation ≈ rad * dist * 0.5
            mx += nx * curve * dist * 0.5
            my += ny * curve * dist * 0.5

    # Base offset above the line/curve
    my += 2.0

    # Manual override
    if label_offset_mm:
        mx += label_offset_mm[0]
        my += label_offset_mm[1]

    return mx, my


def validate_all(schematic, fig=None, ax=None):
    """Run all validation rules, collect errors, raise combined summary.

    Pre-render rules (R1-R4, R8) always run. Post-render rules (R5-R7)
    only run when fig and ax are provided.
    """
    errors = []

    # Pre-render rules
    pre_checks = [
        ("R1", validate_containers),
        ("R2", validate_no_overlap),
        ("R8", validate_arrow_label_side),
    ]
    for tag, fn in pre_checks:
        try:
            fn(schematic)
        except ValueError as e:
            errors.append(f"{tag}: {e}")

    # Warning-level pre-render (R3, R4) — run but don't collect
    validate_container_title_clearance(schematic)
    validate_text_fits_boxes(schematic)

    # Post-render rules (need fig/ax with rendered text)
    if fig is not None and ax is not None:
        post_checks = [
            ("R5/R6", validate_text_margins),
            ("R7", validate_text_arrow_no_overlap),
        ]
        for tag, fn in post_checks:
            try:
                if "schematic" in fn.__code__.co_varnames:
                    fn(fig, ax, schematic)
                else:
                    fn(fig, ax)
            except ValueError as e:
                errors.append(f"{tag}: {e}")

    if errors:
        header = f"{len(errors)} validation error(s):"
        detail = "\n  ".join(errors)
        raise ValueError(f"{header}\n  {detail}")


# EOF
