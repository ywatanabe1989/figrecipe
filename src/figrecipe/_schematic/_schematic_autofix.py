#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-fix layout violations for Diagram diagrams.

Phase 1 (pre-render): Resolves geometric violations (R1, R2, R8, R9).
Phase 2 (post-render): Offsets arrow labels to fix text collisions (R5/R6, R7).
Called from ``Diagram.render(auto_fix=True)``.
"""

import math
from itertools import combinations
from typing import TYPE_CHECKING, Dict, List

from ._schematic_geom import box_rect, rects_overlap

if TYPE_CHECKING:
    from ._schematic import Diagram

# Margin added beyond the exact fix to prevent borderline re-violations.
_FIX_MARGIN_MM = 3.0
# Per-side inner padding when expanding containers to enclose children.
_CONTAINER_PAD_MM = 8.0
# Minimum visible gap between connected boxes for readable arrows.
_MIN_ARROW_GAP_MM = 15.0


# ── Collectors ──────────────────────────────────────────────────────


def _collect_container_violations(schematic: "Diagram") -> List[Dict]:
    """Collect all R1 container-enclosure violations."""
    results = []
    for cid, container in schematic._containers.items():
        if cid not in schematic._positions:
            continue
        cpos = schematic._positions[cid]
        cl = cpos.x_mm - cpos.width_mm / 2
        cr = cpos.x_mm + cpos.width_mm / 2
        cb = cpos.y_mm - cpos.height_mm / 2
        ct = cpos.y_mm + cpos.height_mm / 2
        for child_id in container.get("children", []):
            if child_id not in schematic._positions:
                continue
            ch = schematic._positions[child_id]
            chl = ch.x_mm - ch.width_mm / 2
            chr_ = ch.x_mm + ch.width_mm / 2
            chb = ch.y_mm - ch.height_mm / 2
            cht = ch.y_mm + ch.height_mm / 2
            excess = {
                "left": max(0, cl - chl),
                "right": max(0, chr_ - cr),
                "bottom": max(0, cb - chb),
                "top": max(0, cht - ct),
            }
            if any(v > 0 for v in excess.values()):
                results.append(
                    {"container_id": cid, "child_id": child_id, "excess": excess}
                )
    return results


def _collect_overlap_violations(schematic: "Diagram") -> List[Dict]:
    """Collect all R2 box-overlap violations."""
    results = []
    box_ids = [bid for bid in schematic._boxes if bid in schematic._positions]
    for id_a, id_b in combinations(box_ids, 2):
        r_a = box_rect(schematic._positions[id_a])
        r_b = box_rect(schematic._positions[id_b])
        if rects_overlap(r_a, r_b):
            results.append(
                {
                    "id_a": id_a,
                    "id_b": id_b,
                    "overlap_x": min(r_a[2], r_b[2]) - max(r_a[0], r_b[0]),
                    "overlap_y": min(r_a[3], r_b[3]) - max(r_a[1], r_b[1]),
                }
            )
    return results


def _collect_canvas_violations(schematic: "Diagram") -> List[Dict]:
    """Collect all R9 canvas-bounds violations."""
    x_lo, x_hi = schematic.xlim
    y_lo, y_hi = schematic.ylim
    results = []
    for eid in list(schematic._boxes) + list(schematic._containers):
        if eid not in schematic._positions:
            continue
        left, bottom, right, top = box_rect(schematic._positions[eid])
        excess = {
            "left": max(0, x_lo - left),
            "right": max(0, right - x_hi),
            "bottom": max(0, y_lo - bottom),
            "top": max(0, top - y_hi),
        }
        if any(v > 0 for v in excess.values()):
            results.append({"id": eid, "excess": excess})
    return results


def _collect_label_side_violations(schematic: "Diagram") -> List[Dict]:
    """Collect all R8 arrow-label-side violations."""
    from ._schematic_validate import compute_arrow_label_position

    results = []
    for arrow in schematic._arrows:
        if not arrow.curve or not arrow.label:
            continue
        src_pos = schematic._positions.get(arrow.source)
        tgt_pos = schematic._positions.get(arrow.target)
        if not src_pos or not tgt_pos:
            continue
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
        dx, dy = end[0] - start[0], end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            continue
        nx, ny = dy / dist, -dx / dist
        arc_side = (nx * arrow.curve, ny * arrow.curve)
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        dot = (lx - mx) * arc_side[0] + (ly - my) * arc_side[1]
        if dot < 0:
            results.append({"arrow": arrow, "current_curve": arrow.curve})
    return results


# ── Fixers ──────────────────────────────────────────────────────────


def fix_container_enclosure(schematic: "Diagram") -> int:
    """R1: Expand containers to enclose children and center them. Returns fix count."""
    violations = _collect_container_violations(schematic)
    if not violations:
        return 0
    # Aggregate max excess per container across all children.
    per_container: Dict[str, Dict[str, float]] = {}
    for v in violations:
        cid = v["container_id"]
        if cid not in per_container:
            per_container[cid] = {"left": 0, "right": 0, "bottom": 0, "top": 0}
        for edge in ("left", "right", "bottom", "top"):
            per_container[cid][edge] = max(per_container[cid][edge], v["excess"][edge])
    for cid, excess in per_container.items():
        pos = schematic._positions[cid]
        pad = _CONTAINER_PAD_MM
        grow_w = excess["left"] + excess["right"] + 2 * pad
        grow_h = excess["bottom"] + excess["top"] + 2 * pad
        pos.width_mm += grow_w
        pos.height_mm += grow_h
        # Shift center to stay balanced.
        pos.x_mm += (excess["right"] - excess["left"]) / 2
        pos.y_mm += (excess["top"] - excess["bottom"]) / 2

    # Center children within their (now-expanded) containers.
    _TITLE_RESERVE_MM = 8.0  # vertical space for container title
    for cid in per_container:
        cpos = schematic._positions[cid]
        children = schematic._containers[cid].get("children", [])
        child_positions = [
            schematic._positions[ch] for ch in children if ch in schematic._positions
        ]
        if not child_positions:
            continue
        # Bounding box of all children
        min_x = min(ch.x_mm - ch.width_mm / 2 for ch in child_positions)
        max_x = max(ch.x_mm + ch.width_mm / 2 for ch in child_positions)
        min_y = min(ch.y_mm - ch.height_mm / 2 for ch in child_positions)
        max_y = max(ch.y_mm + ch.height_mm / 2 for ch in child_positions)
        group_cx = (min_x + max_x) / 2
        group_cy = (min_y + max_y) / 2
        # Container inner center (shifted down to account for title)
        inner_cx = cpos.x_mm
        inner_cy = cpos.y_mm - _TITLE_RESERVE_MM / 2
        # Shift all children
        dx = inner_cx - group_cx
        dy = inner_cy - group_cy
        for ch in child_positions:
            ch.x_mm += dx
            ch.y_mm += dy
    return len(per_container)


def fix_overlaps(schematic: "Diagram") -> int:
    """R2: Push overlapping boxes apart. Returns fix count."""
    violations = _collect_overlap_violations(schematic)
    if not violations:
        return 0
    from ._schematic_overlap import resolve_overlaps

    x_lo, x_hi = schematic.xlim
    y_lo, y_hi = schematic.ylim
    resolve_overlaps(
        schematic, gap=_FIX_MARGIN_MM, x_min=x_lo, x_max=x_hi, y_min=y_lo, y_max=y_hi
    )
    return len(violations)


def fix_arrow_lengths(schematic: "Diagram") -> int:
    """Ensure minimum visible gap between connected boxes for readable arrows.

    For each arrow, measures the rectangle-to-rectangle gap between source
    and target boxes. If shorter than _MIN_ARROW_GAP_MM, pushes the target
    box further along the source-to-target direction.

    Returns number of arrows whose connected boxes were pushed apart.
    """
    from matplotlib.transforms import Bbox

    from ._schematic_geom import bbox_gap

    fixed = 0
    for arrow in schematic._arrows:
        src = schematic._positions.get(arrow.source)
        tgt = schematic._positions.get(arrow.target)
        if not src or not tgt:
            continue
        dx = tgt.x_mm - src.x_mm
        dy = tgt.y_mm - src.y_mm
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            continue
        src_bb = Bbox(
            [
                [src.x_mm - src.width_mm / 2, src.y_mm - src.height_mm / 2],
                [src.x_mm + src.width_mm / 2, src.y_mm + src.height_mm / 2],
            ]
        )
        tgt_bb = Bbox(
            [
                [tgt.x_mm - tgt.width_mm / 2, tgt.y_mm - tgt.height_mm / 2],
                [tgt.x_mm + tgt.width_mm / 2, tgt.y_mm + tgt.height_mm / 2],
            ]
        )
        gap = bbox_gap(src_bb, tgt_bb)
        if gap >= _MIN_ARROW_GAP_MM:
            continue
        shortfall = _MIN_ARROW_GAP_MM - gap
        nx, ny = dx / dist, dy / dist
        tgt.x_mm += nx * shortfall
        tgt.y_mm += ny * shortfall
        fixed += 1
    return fixed


def fix_arrow_labels(schematic: "Diagram") -> int:
    """R8: Flip curve sign so label is on same side as arc. Returns fix count."""
    violations = _collect_label_side_violations(schematic)
    for v in violations:
        v["arrow"].curve = -v["current_curve"]
    return len(violations)


def fix_canvas_bounds(schematic: "Diagram") -> int:
    """R9: Expand canvas xlim/ylim to encompass all elements. Returns fix count."""
    violations = _collect_canvas_violations(schematic)
    if not violations:
        return 0
    x_lo, x_hi = schematic.xlim
    y_lo, y_hi = schematic.ylim
    for v in violations:
        excess = v["excess"]
        x_lo -= excess["left"] + _FIX_MARGIN_MM if excess["left"] > 0 else 0
        x_hi += excess["right"] + _FIX_MARGIN_MM if excess["right"] > 0 else 0
        y_lo -= excess["bottom"] + _FIX_MARGIN_MM if excess["bottom"] > 0 else 0
        y_hi += excess["top"] + _FIX_MARGIN_MM if excess["top"] > 0 else 0
    schematic.xlim = (x_lo, x_hi)
    schematic.ylim = (y_lo, y_hi)
    schematic.width_mm = x_hi - x_lo
    schematic.height_mm = y_hi - y_lo
    return len(violations)


# ── Phase 2: Post-render fixers ─────────────────────────────────────


def _arrow_perp(schematic, arrow):
    """Return (nx, ny) perpendicular unit vector for an arrow."""
    src = schematic._positions.get(arrow.source)
    tgt = schematic._positions.get(arrow.target)
    if not src or not tgt:
        return (0, 1)
    dx = tgt.x_mm - src.x_mm
    dy = tgt.y_mm - src.y_mm
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return (0, 1)
    return (dy / dist, -dx / dist)


def fix_post_render(schematic, fig, ax, min_margin=2.0) -> int:
    """R5/R6/R7: Offset arrow labels to fix text collisions and occlusion.

    Detects two types of problems:
    - R5/R6: Arrow label too close to other text (gap < min_margin).
    - R7: Arrow label sitting on top of its own arrow path.

    Offsets affected labels perpendicular to the arrow direction.
    Returns number of arrow labels adjusted.
    """
    from ._schematic_geom import bbox_gap, box_rect, seg_rect_clip_len

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    # Collect all text bboxes
    text_entries = []
    for t in ax.texts:
        txt = t.get_text().strip()
        if not txt or t.get_label() == "__codeblock_internal__":
            continue
        bb = t.get_window_extent(renderer).transformed(inv)
        text_entries.append((txt, bb))

    arrow_labels = {a.label for a in schematic._arrows if a.label}

    fixed = 0
    for arrow in schematic._arrows:
        if not arrow.label:
            continue
        label_bb = None
        for txt, bb in text_entries:
            if txt == arrow.label:
                label_bb = bb
                break
        if label_bb is None:
            continue

        needs_fix = False

        # R7: Check if label bbox occludes the arrow path
        src = schematic._positions.get(arrow.source)
        tgt = schematic._positions.get(arrow.target)
        if src and tgt:
            clip = seg_rect_clip_len(
                src.x_mm,
                src.y_mm,
                tgt.x_mm,
                tgt.y_mm,
                label_bb.x0,
                label_bb.y0,
                label_bb.x1,
                label_bb.y1,
            )
            if clip > 0:
                needs_fix = True

        # R5/R6: Check collision with non-arrow-label text
        if not needs_fix:
            for txt, bb in text_entries:
                if txt == arrow.label or txt in arrow_labels:
                    continue
                if bbox_gap(label_bb, bb) < min_margin:
                    needs_fix = True
                    break

        # R5/R6: Check proximity to box/container edges
        if not needs_fix:
            from matplotlib.transforms import Bbox

            for eid in list(schematic._boxes) + list(schematic._containers):
                if eid not in schematic._positions:
                    continue
                el, eb, er, et = box_rect(schematic._positions[eid])
                cx = (label_bb.x0 + label_bb.x1) / 2
                cy = (label_bb.y0 + label_bb.y1) / 2
                if el <= cx <= er and eb <= cy <= et:
                    continue  # label inside this box
                edge_bb = Bbox([[el, eb], [er, et]])
                if bbox_gap(label_bb, edge_bb) < min_margin:
                    needs_fix = True
                    break

        if not needs_fix:
            continue

        # Offset label perpendicular to arrow direction
        nx, ny = _arrow_perp(schematic, arrow)
        base_offset = arrow.label_offset_mm or (0, 0)
        for offset_mm in (5, 8, 12, -5, -8, -12):
            arrow.label_offset_mm = (
                base_offset[0] + nx * offset_mm,
                base_offset[1] + ny * offset_mm,
            )
            fixed += 1
            break  # Apply first offset; re-render will re-check

    return fixed


# ── Orchestrator ────────────────────────────────────────────────────


def auto_fix(schematic: "Diagram", max_passes: int = 3) -> int:
    """Resolve pre-render layout violations by mutating positions.

    Applies fixes in dependency order:
    overlaps → arrow lengths → containers → labels → canvas.
    Iterates up to *max_passes* until no violations remain.

    Returns total number of fixes applied.
    """
    import warnings

    total = 0
    for _pass in range(max_passes):
        n = 0
        n += fix_overlaps(schematic)
        n += fix_arrow_lengths(schematic)
        n += fix_container_enclosure(schematic)
        n += fix_arrow_labels(schematic)
        n += fix_canvas_bounds(schematic)
        total += n
        if n == 0:
            break

    if total > 0:
        warnings.warn(
            f"auto_fix: applied {total} fix(es) in {_pass + 1} pass(es)",
            UserWarning,
            stacklevel=3,
        )
    return total


__all__ = ["auto_fix"]
