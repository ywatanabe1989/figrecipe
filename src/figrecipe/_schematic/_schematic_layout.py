#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-layout algorithms for schematic diagrams.

Provides automatic positioning of boxes based on graph structure.
Uses networkx for layout computation with graceful fallback.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ._schematic import Schematic

# Default box sizes in mm (must fit text + padding comfortably)
DEFAULT_WIDTH_MM = 40.0
DEFAULT_HEIGHT_MM = 25.0


def auto_layout(
    info: "Schematic",
    layout: str = "lr",
    margin_mm: float = 15.0,
    box_size_mm: Optional[Tuple[float, float]] = None,
    gap_mm: float = 10.0,
    avoid_overlap: bool = True,
    justify: str = "space-between",
    align_items: str = "center",
) -> None:
    """Automatically position boxes. See Schematic.auto_layout for full docs."""
    from ._schematic import PositionSpec

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

    # Compute needed extent and expand coordinate space if necessary
    n_boxes = len(box_ids)
    is_horizontal = layout_key in ("lr", "rl")
    is_vertical = layout_key in ("tb", "bt")
    title_space_mm = 12.0 if info.title else 0.0

    if is_horizontal or is_vertical:
        if is_horizontal:
            needed_main = n_boxes * w + (n_boxes - 1) * gap_mm + 2 * margin_mm
            needed_cross = h + 2 * margin_mm + title_space_mm
            if info.xlim[1] - info.xlim[0] < needed_main:
                info.xlim = (info.xlim[0], info.xlim[0] + needed_main)
            if info.ylim[1] - info.ylim[0] < needed_cross:
                center_y = (info.ylim[0] + info.ylim[1]) / 2
                info.ylim = (center_y - needed_cross / 2, center_y + needed_cross / 2)
        else:
            needed_main = (
                n_boxes * h + (n_boxes - 1) * gap_mm + 2 * margin_mm + title_space_mm
            )
            needed_cross = w + 2 * margin_mm
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
        )
    elif layout_key == "spring":
        positions = _spring_layout(box_ids, edges, dx_min, dx_max, dy_min, dy_max)
    elif layout_key == "circular":
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
        _resolve_overlaps(info, gap_mm, x_min, x_max, y_min, y_max)


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
) -> Dict[str, Tuple[float, float]]:
    """Compute flow-based layout using topological ordering with CSS-like options.

    Parameters
    ----------
    justify : str
        Main axis: start, center, end, space-between, space-around
    align_items : str
        Cross axis: start, center, end
    """
    # Build graph structure
    successors = {bid: [] for bid in box_ids}
    predecessors = {bid: [] for bid in box_ids}
    for src, tgt in edges:
        if src in successors and tgt in predecessors:
            successors[src].append(tgt)
            predecessors[tgt].append(src)

    # Topological sort (Kahn's algorithm)
    in_degree = {bid: len(predecessors[bid]) for bid in box_ids}
    queue = [bid for bid in box_ids if in_degree[bid] == 0]
    sorted_ids = []

    while queue:
        node = queue.pop(0)
        sorted_ids.append(node)
        for succ in successors[node]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    # Handle cycles or disconnected - add remaining
    for bid in box_ids:
        if bid not in sorted_ids:
            sorted_ids.append(bid)

    # Assign layers based on longest path from sources
    layers = _assign_layers(sorted_ids, predecessors)

    # Group by layer
    layer_groups: Dict[int, List[str]] = {}
    for bid, layer in layers.items():
        layer_groups.setdefault(layer, []).append(bid)

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

    positions = {}

    if direction == "lr":
        # Left to right: main=X, cross=Y
        main_positions = distribute(n_layers, x_min, x_max, justify)
        for layer_idx, members in layer_groups.items():
            x = main_positions[layer_idx] if layer_idx < len(main_positions) else x_max
            n = len(members)
            cross_positions = distribute(n, y_min, y_max, "space-between")
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
            cross_positions = distribute(n, y_min, y_max, "space-between")
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
            cross_positions = distribute(n, x_min, x_max, "space-between")
            for i, bid in enumerate(members):
                x = cross_positions[i] if n > 1 else align(x_min, x_max, align_items)
                positions[bid] = (x, y)

    elif direction == "bt":
        # Bottom to top: main=Y, cross=X
        main_positions = distribute(n_layers, y_min, y_max, justify)
        for layer_idx, members in layer_groups.items():
            y = main_positions[layer_idx] if layer_idx < len(main_positions) else y_max
            n = len(members)
            cross_positions = distribute(n, x_min, x_max, "space-between")
            for i, bid in enumerate(members):
                x = cross_positions[i] if n > 1 else align(x_min, x_max, align_items)
                positions[bid] = (x, y)

    return positions


def _assign_layers(
    sorted_ids: List[str], predecessors: Dict[str, List[str]]
) -> Dict[str, int]:
    """Assign layer numbers based on longest path from sources."""
    layers = {}
    for bid in sorted_ids:
        if not predecessors[bid]:
            layers[bid] = 0
        else:
            layers[bid] = max(layers.get(p, 0) for p in predecessors[bid]) + 1
    return layers


def _spring_layout(
    box_ids: List[str],
    edges: List[Tuple[str, str]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> Dict[str, Tuple[float, float]]:
    """Compute spring (force-directed) layout using networkx."""
    try:
        import networkx as nx

        G = nx.DiGraph()
        G.add_nodes_from(box_ids)
        G.add_edges_from(edges)

        # Use kamada-kawai for better results
        try:
            pos = nx.kamada_kawai_layout(G)
        except Exception:
            pos = nx.spring_layout(G, seed=42)

        # Scale to bounds
        return _scale_positions(pos, x_min, x_max, y_min, y_max)

    except ImportError:
        # Fallback to flow layout
        import warnings

        warnings.warn("networkx not available, falling back to flow layout")
        return _flow_layout(box_ids, edges, "flow-lr", x_min, x_max, y_min, y_max)


def _circular_layout(
    box_ids: List[str],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> Dict[str, Tuple[float, float]]:
    """Compute circular layout."""
    import math

    n = len(box_ids)
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    radius = min(x_max - x_min, y_max - y_min) / 2 * 0.8

    positions = {}
    for i, bid in enumerate(box_ids):
        angle = 2 * math.pi * i / n - math.pi / 2  # Start from top
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions[bid] = (x, y)

    return positions


def _scale_positions(
    pos: Dict[str, Tuple[float, float]],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> Dict[str, Tuple[float, float]]:
    """Scale positions to fit within bounds."""
    if not pos:
        return {}

    # Get current bounds
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    cur_x_min, cur_x_max = min(xs), max(xs)
    cur_y_min, cur_y_max = min(ys), max(ys)

    # Scale factors
    x_scale = (x_max - x_min) / (cur_x_max - cur_x_min) if cur_x_max != cur_x_min else 1
    y_scale = (y_max - y_min) / (cur_y_max - cur_y_min) if cur_y_max != cur_y_min else 1

    # Apply scaling
    scaled = {}
    for bid, (x, y) in pos.items():
        new_x = (
            x_min + (x - cur_x_min) * x_scale
            if cur_x_max != cur_x_min
            else (x_min + x_max) / 2
        )
        new_y = (
            y_min + (y - cur_y_min) * y_scale
            if cur_y_max != cur_y_min
            else (y_min + y_max) / 2
        )
        scaled[bid] = (new_x, new_y)

    return scaled


def _resolve_overlaps(
    info: "Schematic",
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


__all__ = ["auto_layout"]
