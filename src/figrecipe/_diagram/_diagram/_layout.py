#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-layout algorithms for diagram positioning.

Provides automatic positioning of boxes based on graph structure.
Uses networkx for layout computation with graceful fallback.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ._core import Diagram

# Default box sizes in mm (must fit text + padding comfortably)
DEFAULT_WIDTH_MM = 40.0
DEFAULT_HEIGHT_MM = 25.0


def auto_layout(
    info: "Diagram",
    layout: str = "lr",
    margin_mm: float = 15.0,
    box_size_mm: Optional[Tuple[float, float]] = None,
    gap_mm: float = 10.0,
    avoid_overlap: bool = True,
    justify: str = "space-between",
    align_items: str = "center",
) -> None:
    """Automatically position boxes. See Diagram.auto_layout for full docs."""
    from ._core import PositionSpec

    # Default box size
    w, h = box_size_mm or (DEFAULT_WIDTH_MM, DEFAULT_HEIGHT_MM)

    # Get all box IDs
    box_ids = list(info._boxes.keys())
    if not box_ids:
        return

    # Build adjacency for topological analysis
    edges = [(a.source, a.target) for a in info._arrows]

    # Normalize layout name
    layout_map = {
        "lr": "lr",
        "left-to-right": "lr",
        "flow-lr": "lr",
        "rl": "rl",
        "right-to-left": "rl",
        "flow-rl": "rl",
        "tb": "tb",
        "top-to-bottom": "tb",
        "flow-tb": "tb",
        "bt": "bt",
        "bottom-to-top": "bt",
        "flow-bt": "bt",
        "spring": "spring",
        "circular": "circular",
    }
    layout_key = layout_map.get(layout.lower(), "lr")

    # Compute actual layer assignment for accurate canvas sizing
    n_boxes = len(box_ids)
    is_horizontal = layout_key in ("lr", "rl")
    is_vertical = layout_key in ("tb", "bt")
    title_space_mm = 12.0 if info.title else 0.0

    containers = info._containers if info._containers else None
    _layers, _layer_groups = _compute_layers(box_ids, edges, containers)
    n_cols = max(_layers.values()) + 1 if _layers else 1
    max_per_col = max((len(g) for g in _layer_groups.values()), default=1)

    if is_horizontal or is_vertical:
        if is_horizontal:
            needed_main = n_cols * w + (n_cols - 1) * gap_mm + 2 * margin_mm
            needed_cross = (
                max_per_col * h
                + (max_per_col - 1) * gap_mm
                + 2 * margin_mm
                + title_space_mm
            )
            if info.xlim[1] - info.xlim[0] < needed_main:
                info.xlim = (info.xlim[0], info.xlim[0] + needed_main)
            if info.ylim[1] - info.ylim[0] < needed_cross:
                center_y = (info.ylim[0] + info.ylim[1]) / 2
                info.ylim = (center_y - needed_cross / 2, center_y + needed_cross / 2)
        else:
            needed_main = (
                n_cols * h + (n_cols - 1) * gap_mm + 2 * margin_mm + title_space_mm
            )
            needed_cross = max_per_col * w + (max_per_col - 1) * gap_mm + 2 * margin_mm
            if info.ylim[1] - info.ylim[0] < needed_main:
                info.ylim = (info.ylim[0], info.ylim[0] + needed_main)
            if info.xlim[1] - info.xlim[0] < needed_cross:
                center_x = (info.xlim[0] + info.xlim[1]) / 2
                info.xlim = (center_x - needed_cross / 2, center_x + needed_cross / 2)

    # Match coordinate space to figsize aspect ratio for set_aspect("equal")
    fig_aspect = info.width_mm / info.height_mm
    x_r = info.xlim[1] - info.xlim[0]
    y_r = info.ylim[1] - info.ylim[0]
    if y_r > 0 and x_r / y_r < fig_aspect:
        hw = y_r * fig_aspect / 2
        cx = (info.xlim[0] + info.xlim[1]) / 2
        info.xlim = (cx - hw, cx + hw)
    elif y_r > 0 and x_r / y_r > fig_aspect:
        hh = x_r / fig_aspect / 2
        cy = (info.ylim[0] + info.ylim[1]) / 2
        info.ylim = (cy - hh, cy + hh)

    # Compute margins from (potentially expanded) bounds (absolute mm, not fraction)
    x_min = info.xlim[0] + margin_mm
    x_max = info.xlim[1] - margin_mm
    y_min = info.ylim[0] + margin_mm
    y_max = info.ylim[1] - margin_mm

    # Distribution bounds: inset by half box size so box edges stay within margins
    dx_min = x_min + w / 2
    dx_max = x_max - w / 2
    dy_min = y_min + h / 2
    dy_max = y_max - h / 2

    # Reserve space for title at top
    if info.title:
        dy_max -= title_space_mm

    # Compute positions based on layout type
    if layout_key in ("lr", "rl", "tb", "bt"):
        positions = _flow_layout(
            box_ids,
            edges,
            layout_key,
            dx_min,
            dx_max,
            dy_min,
            dy_max,
            gap_mm,
            justify,
            align_items,
            containers=containers,
            layers=_layers,
            layer_groups=_layer_groups,
        )
    elif layout_key == "spring":
        from ._layout_graph import _spring_layout

        positions = _spring_layout(box_ids, edges, dx_min, dx_max, dy_min, dy_max)
    elif layout_key == "circular":
        from ._layout_graph import _circular_layout

        positions = _circular_layout(box_ids, dx_min, dx_max, dy_min, dy_max)
    else:
        positions = _flow_layout(
            box_ids,
            edges,
            "lr",
            dx_min,
            dx_max,
            dy_min,
            dy_max,
            gap_mm,
            justify,
            align_items,
            containers=containers,
            layers=_layers,
            layer_groups=_layer_groups,
        )

    # Apply positions
    for box_id, (x, y) in positions.items():
        # Preserve existing size if set, otherwise use default
        if box_id in info._positions:
            existing = info._positions[box_id]
            info._positions[box_id] = PositionSpec(
                x_mm=x, y_mm=y, width_mm=existing.width_mm, height_mm=existing.height_mm
            )
        else:
            info._positions[box_id] = PositionSpec(
                x_mm=x, y_mm=y, width_mm=w, height_mm=h
            )

    # Apply collision avoidance if requested
    if avoid_overlap:
        from ._overlap import resolve_overlaps

        resolve_overlaps(info, gap_mm, x_min, x_max, y_min, y_max)


def _flow_layout(
    box_ids: List[str],
    edges: List[Tuple[str, str]],
    direction: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    gap: float = 10.0,
    justify: str = "space-between",
    align_items: str = "center",
    containers: Optional[Dict] = None,
    layers: Optional[Dict[str, int]] = None,
    layer_groups: Optional[Dict[int, List[str]]] = None,
) -> Dict[str, Tuple[float, float]]:
    """Compute flow-based layout using topological ordering with CSS-like options.

    Parameters
    ----------
    justify : str
        Main axis: start, center, end, space-between, space-around
    align_items : str
        Cross axis: start, center, end
    layers : dict, optional
        Pre-computed layer assignment from _compute_layers.
    layer_groups : dict, optional
        Pre-computed layer grouping from _compute_layers.
    """
    # Use pre-computed layers or compute from scratch
    if layers is None or layer_groups is None:
        layers, layer_groups = _compute_layers(box_ids, edges, containers)

    # Reorder members within layers to minimize edge crossings
    _reorder_by_barycenter(layer_groups, layers, edges)

    n_layers = max(layers.values()) + 1 if layers else 1

    # Helper to compute positions along an axis with justify
    def distribute(n: int, axis_min: float, axis_max: float, j: str) -> List[float]:
        if n == 1:
            if j == "start":
                return [axis_min + (axis_max - axis_min) * 0.15]
            elif j == "end":
                return [axis_max - (axis_max - axis_min) * 0.15]
            return [(axis_min + axis_max) / 2]
        total = axis_max - axis_min
        # Compact spacing for start/end/center (use 30% of available space)
        compact_spacing = total * 0.3 / (n - 1) if n > 1 else 0
        if j == "start":
            return [axis_min + compact_spacing * i for i in range(n)]
        elif j == "end":
            return [axis_max - compact_spacing * (n - 1 - i) for i in range(n)]
        elif j == "center":
            span = compact_spacing * (n - 1)
            start = (axis_min + axis_max - span) / 2
            return [start + compact_spacing * i for i in range(n)]
        elif j == "space-around":
            spacing = total / n
            return [axis_min + spacing * (i + 0.5) for i in range(n)]
        else:  # space-between (default)
            return [axis_min + total * i / (n - 1) for i in range(n)]

    # Helper for cross-axis alignment
    def align(axis_min: float, axis_max: float, a: str) -> float:
        if a == "start":
            return axis_min
        elif a == "end":
            return axis_max
        return (axis_min + axis_max) / 2  # center (default)

    # Cross-axis distribution: space-between spreads items evenly
    cross_justify = "space-between"

    positions = {}

    if direction == "lr":
        # Left to right: main=X, cross=Y
        main_positions = distribute(n_layers, x_min, x_max, justify)
        for layer_idx, members in layer_groups.items():
            x = main_positions[layer_idx] if layer_idx < len(main_positions) else x_max
            n = len(members)
            cross_positions = distribute(n, y_min, y_max, cross_justify)
            for i, bid in enumerate(members):
                y = (
                    cross_positions[n - 1 - i]
                    if n > 1
                    else align(y_min, y_max, align_items)
                )
                positions[bid] = (x, y)

    elif direction == "rl":
        # Right to left
        main_positions = distribute(n_layers, x_min, x_max, justify)
        for layer_idx, members in layer_groups.items():
            x = (
                main_positions[n_layers - 1 - layer_idx]
                if layer_idx < n_layers
                else x_min
            )
            n = len(members)
            cross_positions = distribute(n, y_min, y_max, cross_justify)
            for i, bid in enumerate(members):
                y = (
                    cross_positions[n - 1 - i]
                    if n > 1
                    else align(y_min, y_max, align_items)
                )
                positions[bid] = (x, y)

    elif direction == "tb":
        # Top to bottom: main=Y (reversed), cross=X
        main_positions = distribute(n_layers, y_min, y_max, justify)
        for layer_idx, members in layer_groups.items():
            y = (
                main_positions[n_layers - 1 - layer_idx]
                if layer_idx < n_layers
                else y_min
            )
            n = len(members)
            cross_positions = distribute(n, x_min, x_max, cross_justify)
            for i, bid in enumerate(members):
                x = cross_positions[i] if n > 1 else align(x_min, x_max, align_items)
                positions[bid] = (x, y)

    elif direction == "bt":
        # Bottom to top: main=Y, cross=X
        main_positions = distribute(n_layers, y_min, y_max, justify)
        for layer_idx, members in layer_groups.items():
            y = main_positions[layer_idx] if layer_idx < len(main_positions) else y_max
            n = len(members)
            cross_positions = distribute(n, x_min, x_max, cross_justify)
            for i, bid in enumerate(members):
                x = cross_positions[i] if n > 1 else align(x_min, x_max, align_items)
                positions[bid] = (x, y)

    return positions


def _assign_layers(
    sorted_ids: List[str],
    predecessors: Dict[str, List[str]],
    containers: Optional[Dict] = None,
) -> Dict[str, int]:
    """Assign layer numbers based on longest path from sources.

    When containers are provided, uses container ordering as layer hints
    for boxes without incoming edges, preventing them from all piling
    into Layer 0.
    """
    # Build container→layer hint from container definition order
    container_layer: Dict[str, int] = {}
    if containers:
        for layer_idx, (_, cdata) in enumerate(containers.items()):
            for child in cdata.get("children", []):
                container_layer[child] = layer_idx

    layers = {}
    for bid in sorted_ids:
        if not predecessors[bid]:
            layers[bid] = container_layer.get(bid, 0)
        else:
            layers[bid] = max(layers.get(p, 0) for p in predecessors[bid]) + 1
            # Ensure layer is at least the container hint
            if bid in container_layer:
                layers[bid] = max(layers[bid], container_layer[bid])
    return layers


def _compute_layers(
    box_ids: List[str],
    edges: List[Tuple[str, str]],
    containers: Optional[Dict] = None,
) -> Tuple[Dict[str, int], Dict[int, List[str]]]:
    """Build graph, topo sort, and assign layers.

    Returns (layers, layer_groups) for use in canvas sizing and layout.
    """
    successors = {bid: [] for bid in box_ids}
    predecessors = {bid: [] for bid in box_ids}
    for src, tgt in edges:
        if src in successors and tgt in predecessors:
            successors[src].append(tgt)
            predecessors[tgt].append(src)

    in_degree = {bid: len(predecessors[bid]) for bid in box_ids}
    queue = [bid for bid in box_ids if in_degree[bid] == 0]
    sorted_ids: List[str] = []
    while queue:
        node = queue.pop(0)
        sorted_ids.append(node)
        for succ in successors[node]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)
    for bid in box_ids:
        if bid not in sorted_ids:
            sorted_ids.append(bid)

    layers = _assign_layers(sorted_ids, predecessors, containers=containers)
    layer_groups: Dict[int, List[str]] = {}
    for bid, layer in layers.items():
        layer_groups.setdefault(layer, []).append(bid)
    return layers, layer_groups


def _reorder_by_barycenter(
    layer_groups: Dict[int, List[str]],
    layers: Dict[str, int],
    edges: List[Tuple[str, str]],
) -> None:
    """Reorder members within layers to minimize edge crossings (in-place).

    Uses the barycenter heuristic with forward + backward sweeps.
    """
    preds: Dict[str, List[str]] = {}
    succs: Dict[str, List[str]] = {}
    for src, tgt in edges:
        preds.setdefault(tgt, []).append(src)
        succs.setdefault(src, []).append(tgt)

    member_idx: Dict[str, int] = {}
    for members in layer_groups.values():
        for i, bid in enumerate(members):
            member_idx[bid] = i

    sorted_keys = sorted(layer_groups.keys())

    # Forward sweep: reorder by predecessor positions
    for layer_idx in sorted_keys:
        if layer_idx == sorted_keys[0]:
            continue
        members = layer_groups[layer_idx]
        n = len(members)
        bary: Dict[str, float] = {}
        for bid in members:
            pi = [
                member_idx[p]
                for p in preds.get(bid, [])
                if layers.get(p, -1) < layer_idx and p in member_idx
            ]
            bary[bid] = sum(pi) / len(pi) if pi else n / 2
        layer_groups[layer_idx] = sorted(members, key=lambda b: bary[b])
        for i, bid in enumerate(layer_groups[layer_idx]):
            member_idx[bid] = i

    # Backward sweep: reorder by successor positions
    for layer_idx in reversed(sorted_keys):
        if layer_idx == sorted_keys[-1]:
            continue
        members = layer_groups[layer_idx]
        n = len(members)
        bary = {}
        for bid in members:
            si = [
                member_idx[s]
                for s in succs.get(bid, [])
                if layers.get(s, -1) > layer_idx and s in member_idx
            ]
            bary[bid] = sum(si) / len(si) if si else n / 2
        layer_groups[layer_idx] = sorted(members, key=lambda b: bary[b])
        for i, bid in enumerate(layer_groups[layer_idx]):
            member_idx[bid] = i


__all__ = ["auto_layout"]
