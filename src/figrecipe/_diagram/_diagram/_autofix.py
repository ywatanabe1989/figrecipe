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


def auto_fix(diagram: "Diagram", max_passes: int = 3, auto_curve: bool = True) -> int:
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
        n += fix_overlaps(diagram)
        n += fix_arrow_lengths(diagram)
        n += fix_bidirectional_arrows(diagram)
        if auto_curve:
            n += fix_arrow_occlusion(diagram)
        n += fix_container_enclosure(diagram)
        n += fix_arrow_labels(diagram)
        n += fix_canvas_bounds(diagram)
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
