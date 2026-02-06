#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layout algorithms for native diagram rendering.

Provides built-in algorithms with optional NetworkX fallback for advanced layouts.
"""

import warnings
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from ._schema import DiagramSpec


def compute_layout(
    spec: "DiagramSpec",
    algorithm: str = "layered",
    direction: str = "LR",
    margins: Tuple[float, float, float, float] = (0.15, 0.15, 0.15, 0.15),
) -> Dict[str, Tuple[float, float]]:
    """Compute node positions using specified layout algorithm.

    Parameters
    ----------
    spec : DiagramSpec
        The diagram specification.
    algorithm : str
        Layout algorithm: layered, grid, spring, kamada_kawai, manual
    direction : str
        Layout direction: LR (left-to-right), TB (top-to-bottom),
        RL (right-to-left), BT (bottom-to-top)
    margins : tuple
        (left, right, top, bottom) margins in axes coordinates.

    Returns
    -------
    dict
        Mapping from node_id to (x, y) position in axes coordinates (0-1).
    """
    if algorithm == "manual":
        return _manual_layout(spec)
    elif algorithm == "layered":
        return _layered_layout(spec, direction, margins)
    elif algorithm == "grid":
        return _grid_layout(spec, direction, margins)
    elif algorithm in ("spring", "kamada_kawai"):
        return _networkx_layout(spec, algorithm, margins)
    else:
        warnings.warn(f"Unknown layout algorithm '{algorithm}', using layered")
        return _layered_layout(spec, direction, margins)


def _manual_layout(spec: "DiagramSpec") -> Dict[str, Tuple[float, float]]:
    """Use manually specified positions from layout hints.

    Falls back to layered layout if positions not specified.
    """
    # Check if positions are in layout hints (future extension)
    # For now, just return empty to trigger default
    return {}


def _layered_layout(
    spec: "DiagramSpec",
    direction: str,
    margins: Tuple[float, float, float, float],
) -> Dict[str, Tuple[float, float]]:
    """Compute layered (hierarchical) layout.

    Assigns nodes to layers based on longest-path from sources.
    Handles cycles gracefully by processing remaining nodes after Kahn's.
    """
    left, right, top, bottom = margins

    # Build adjacency
    adj = defaultdict(list)
    predecessors = defaultdict(list)
    nodes = {n.id for n in spec.nodes}

    for edge in spec.edges:
        if edge.source in nodes and edge.target in nodes:
            adj[edge.source].append(edge.target)
            predecessors[edge.target].append(edge.source)

    in_degree = {n.id: 0 for n in spec.nodes}
    for edge in spec.edges:
        if edge.source in nodes and edge.target in nodes:
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

    # Topological sort to assign layers
    layers: List[List[str]] = []
    remaining = set(nodes)

    # Use spec.layout.layers if provided
    if spec.layout.layers:
        layers = [list(layer) for layer in spec.layout.layers]
        for layer in layers:
            remaining -= set(layer)
        if remaining:
            layers.append(list(remaining))
    else:
        # Kahn's algorithm for topological ordering
        sorted_order = []
        queue = [n for n in in_degree if in_degree[n] == 0]
        while queue:
            node = queue.pop(0)
            sorted_order.append(node)
            remaining.discard(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0 and neighbor in remaining:
                    queue.append(neighbor)

        # Append cycle-involved nodes in original order
        for n in spec.nodes:
            if n.id in remaining:
                sorted_order.append(n.id)

        # Assign layers via longest-path from sources
        layer_of = {}
        for nid in sorted_order:
            preds = [p for p in predecessors[nid] if p in layer_of]
            layer_of[nid] = (max(layer_of[p] for p in preds) + 1) if preds else 0

        # Group by layer
        layer_groups = defaultdict(list)
        for nid, layer_idx in layer_of.items():
            layer_groups[layer_idx].append(nid)
        layers = [layer_groups[i] for i in sorted(layer_groups.keys())]

    if not layers:
        # No nodes
        return {}

    # Compute positions with proper spacing
    n_layers = len(layers)
    positions = {}

    # Available space after margins
    width = 1.0 - left - right
    height = 1.0 - top - bottom

    # Calculate spacing between layers and within layers
    # Leave extra space for node dimensions
    node_padding = 0.08  # Padding around each node

    for layer_idx, layer in enumerate(layers):
        n_nodes = len(layer)
        if n_nodes == 0:
            continue

        # Position within layer
        for node_idx, node_id in enumerate(layer):
            if direction == "LR":
                # Horizontal: layers go left-to-right, nodes stack vertically
                if n_layers > 1:
                    x = (
                        left
                        + node_padding
                        + (layer_idx / (n_layers - 1)) * (width - 2 * node_padding)
                    )
                else:
                    x = 0.5
                if n_nodes > 1:
                    y = (
                        bottom
                        + node_padding
                        + (node_idx / (n_nodes - 1)) * (height - 2 * node_padding)
                    )
                else:
                    y = 0.5

            elif direction == "RL":
                # Right-to-left
                if n_layers > 1:
                    x = (
                        1.0
                        - left
                        - node_padding
                        - (layer_idx / (n_layers - 1)) * (width - 2 * node_padding)
                    )
                else:
                    x = 0.5
                if n_nodes > 1:
                    y = (
                        bottom
                        + node_padding
                        + (node_idx / (n_nodes - 1)) * (height - 2 * node_padding)
                    )
                else:
                    y = 0.5

            elif direction == "TB":
                # Top-to-bottom: layers go top-to-bottom, nodes spread horizontally
                if n_nodes > 1:
                    x = (
                        left
                        + node_padding
                        + (node_idx / (n_nodes - 1)) * (width - 2 * node_padding)
                    )
                else:
                    x = 0.5
                if n_layers > 1:
                    y = (
                        1.0
                        - top
                        - node_padding
                        - (layer_idx / (n_layers - 1)) * (height - 2 * node_padding)
                    )
                else:
                    y = 0.5

            else:  # BT
                # Bottom-to-top
                if n_nodes > 1:
                    x = (
                        left
                        + node_padding
                        + (node_idx / (n_nodes - 1)) * (width - 2 * node_padding)
                    )
                else:
                    x = 0.5
                if n_layers > 1:
                    y = (
                        bottom
                        + node_padding
                        + (layer_idx / (n_layers - 1)) * (height - 2 * node_padding)
                    )
                else:
                    y = 0.5

            positions[node_id] = (x, y)

    return positions


def _grid_layout(
    spec: "DiagramSpec",
    direction: str,
    margins: Tuple[float, float, float, float],
) -> Dict[str, Tuple[float, float]]:
    """Compute simple grid layout.

    Arranges nodes in a grid pattern, respecting groups if defined.
    """
    import math

    left, right, top, bottom = margins
    nodes = spec.nodes

    if not nodes:
        return {}

    n = len(nodes)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    width = 1.0 - left - right
    height = 1.0 - top - bottom
    node_padding = 0.08

    positions = {}
    for idx, node in enumerate(nodes):
        row = idx // cols
        col = idx % cols

        # Compute position with proper spacing
        if cols > 1:
            x = left + node_padding + (col / (cols - 1)) * (width - 2 * node_padding)
        else:
            x = 0.5

        if rows > 1:
            y = (
                1.0
                - top
                - node_padding
                - (row / (rows - 1)) * (height - 2 * node_padding)
            )
        else:
            y = 0.5

        if direction == "RL":
            x = 1.0 - x + 2 * left
        elif direction == "BT":
            y = 1.0 - y + 2 * bottom

        positions[node.id] = (x, y)

    return positions


def _networkx_layout(
    spec: "DiagramSpec",
    algorithm: str,
    margins: Tuple[float, float, float, float],
) -> Dict[str, Tuple[float, float]]:
    """Use NetworkX for spring or Kamada-Kawai layouts.

    Falls back to layered layout if NetworkX is not available.
    """
    try:
        import networkx as nx
    except ImportError:
        warnings.warn(
            f"NetworkX required for '{algorithm}' layout. "
            "Install with: pip install networkx. Falling back to layered layout."
        )
        return _layered_layout(spec, "LR", margins)

    left, right, top, bottom = margins
    node_padding = 0.08

    # Build NetworkX graph
    G = nx.DiGraph()
    for node in spec.nodes:
        G.add_node(node.id)
    for edge in spec.edges:
        G.add_edge(edge.source, edge.target)

    # Compute layout
    if algorithm == "spring":
        pos = nx.spring_layout(G, seed=42, k=0.5)
    elif algorithm == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    # Rescale to fit within margins with padding
    if pos:
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        x_range = x_max - x_min if x_max != x_min else 1.0
        y_range = y_max - y_min if y_max != y_min else 1.0

        width = 1.0 - left - right - 2 * node_padding
        height = 1.0 - top - bottom - 2 * node_padding

        positions = {}
        for node_id, (x, y) in pos.items():
            new_x = left + node_padding + (x - x_min) / x_range * width
            new_y = bottom + node_padding + (y - y_min) / y_range * height
            positions[node_id] = (new_x, new_y)

        return positions

    return {}


def optimize_edge_crossings(
    positions: Dict[str, Tuple[float, float]],
    spec: "DiagramSpec",
) -> Dict[str, Tuple[float, float]]:
    """Reorder nodes within layers to minimize edge crossings.

    This is a simple barycenter heuristic implementation.
    """
    # Group nodes by x-coordinate (layer)
    layers = defaultdict(list)
    for node_id, (x, y) in positions.items():
        # Round x to group into layers
        layer_key = round(x, 2)
        layers[layer_key].append((node_id, y))

    # Build adjacency
    adj = defaultdict(set)
    for edge in spec.edges:
        adj[edge.source].add(edge.target)
        adj[edge.target].add(edge.source)

    # Sort layers by x
    sorted_layers = sorted(layers.keys())

    # Barycenter heuristic
    new_positions = {}
    for layer_x in sorted_layers:
        layer_nodes = layers[layer_x]

        # Compute barycenter for each node
        barycenters = []
        for node_id, old_y in layer_nodes:
            neighbors = adj[node_id]
            if neighbors:
                neighbor_ys = [positions[n][1] for n in neighbors if n in positions]
                if neighbor_ys:
                    barycenter = sum(neighbor_ys) / len(neighbor_ys)
                else:
                    barycenter = old_y
            else:
                barycenter = old_y
            barycenters.append((node_id, barycenter))

        # Sort by barycenter
        barycenters.sort(key=lambda x: x[1])

        # Assign new y positions evenly spaced
        n = len(barycenters)
        y_positions = [positions[node_id][1] for node_id, _ in layer_nodes]
        y_min, y_max = min(y_positions), max(y_positions)

        for idx, (node_id, _) in enumerate(barycenters):
            if n > 1:
                new_y = y_min + idx * (y_max - y_min) / (n - 1)
            else:
                new_y = (y_min + y_max) / 2
            new_positions[node_id] = (layer_x, new_y)

    return new_positions if new_positions else positions


__all__ = [
    "compute_layout",
    "optimize_edge_crossings",
]
