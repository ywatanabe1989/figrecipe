#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-fix layout violations for Diagram diagrams.

Phase 1 (pre-render): Resolves geometric violations (R1, R2, R8, R9).
Phase 2 (post-render): Offsets arrow labels to fix text collisions (R5/R6, R7).
Called from ``Diagram.render(auto_fix=True)``.

Implementation is split across modules by concern:
- ``_fix_layout``: container enclosure (R1), overlaps (R2), canvas bounds (R9)
- ``_fix_arrows``: arrow lengths, labels (R8), occlusion (R7), bidirectional split
"""

from typing import TYPE_CHECKING

from ._fix_arrows import (
    fix_arrow_labels,
    fix_arrow_lengths,
    fix_arrow_occlusion,
    fix_bidirectional_arrows,
    fix_post_render,
)
from ._fix_layout import (
    fix_canvas_bounds,
    fix_container_enclosure,
    fix_overlaps,
)

if TYPE_CHECKING:
    from ._core import Diagram


def auto_fix(schematic: "Diagram", max_passes: int = 3, auto_curve: bool = True) -> int:
    """Resolve pre-render layout violations by mutating positions.

    Applies fixes in dependency order:
    overlaps → arrow lengths → bidirectional → [auto_curve] → containers → labels → canvas.
    Iterates up to *max_passes* until no violations remain.
    Set auto_curve=False to skip R7 arrow occlusion auto-curving.
    """
    import warnings

    total = 0
    for _pass in range(max_passes):
        n = 0
        n += fix_overlaps(schematic)
        n += fix_arrow_lengths(schematic)
        n += fix_bidirectional_arrows(schematic)
        if auto_curve:
            n += fix_arrow_occlusion(schematic)
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


__all__ = ["auto_fix", "fix_post_render"]
