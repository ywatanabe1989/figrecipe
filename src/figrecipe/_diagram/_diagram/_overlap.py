#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Overlap resolution for auto-layout positioning."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._core import Diagram


def resolve_overlaps(
    info: "Diagram",
    gap: float,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    max_iterations: int = 50,
) -> None:
    """Resolve overlapping boxes by pushing them apart.

    Uses iterative collision detection and resolution.
    """

    box_ids = list(info._positions.keys())
    if len(box_ids) < 2:
        return

    for _ in range(max_iterations):
        moved = False

        for i, id1 in enumerate(box_ids):
            pos1 = info._positions[id1]
            box1 = info._boxes.get(id1)
            margin1 = box1.margin_mm if box1 else 0.0

            for id2 in box_ids[i + 1 :]:
                pos2 = info._positions[id2]
                box2 = info._boxes.get(id2)
                margin2 = box2.margin_mm if box2 else 0.0

                # Calculate overlap with gap and margins
                total_gap = gap + margin1 + margin2
                half_w1 = pos1.width_mm / 2 + total_gap / 2
                half_h1 = pos1.height_mm / 2 + total_gap / 2
                half_w2 = pos2.width_mm / 2 + total_gap / 2
                half_h2 = pos2.height_mm / 2 + total_gap / 2

                dx = pos2.x_mm - pos1.x_mm
                dy = pos2.y_mm - pos1.y_mm

                overlap_x = half_w1 + half_w2 - abs(dx)
                overlap_y = half_h1 + half_h2 - abs(dy)

                # Check if overlapping
                if overlap_x > 0 and overlap_y > 0:
                    moved = True

                    # Push apart along axis with smaller overlap
                    if overlap_x < overlap_y:
                        # Push horizontally
                        push = overlap_x / 2 + 0.1
                        if dx >= 0:
                            pos1.x_mm -= push
                            pos2.x_mm += push
                        else:
                            pos1.x_mm += push
                            pos2.x_mm -= push
                    else:
                        # Push vertically
                        push = overlap_y / 2 + 0.1
                        if dy >= 0:
                            pos1.y_mm -= push
                            pos2.y_mm += push
                        else:
                            pos1.y_mm += push
                            pos2.y_mm -= push

                    # Clamp to bounds
                    pos1.x_mm = max(
                        x_min + pos1.width_mm / 2,
                        min(x_max - pos1.width_mm / 2, pos1.x_mm),
                    )
                    pos1.y_mm = max(
                        y_min + pos1.height_mm / 2,
                        min(y_max - pos1.height_mm / 2, pos1.y_mm),
                    )
                    pos2.x_mm = max(
                        x_min + pos2.width_mm / 2,
                        min(x_max - pos2.width_mm / 2, pos2.x_mm),
                    )
                    pos2.y_mm = max(
                        y_min + pos2.height_mm / 2,
                        min(y_max - pos2.height_mm / 2, pos2.y_mm),
                    )

                    info._positions[id1] = pos1
                    info._positions[id2] = pos2

        if not moved:
            break


__all__ = ["resolve_overlaps"]
