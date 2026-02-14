#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mermaid compilation from DiagramSpec."""

import json
from typing import Optional

from .._shared._compile_utils import _sanitize_id
from .._shared._presets import DiagramPreset, get_preset
from .._shared._schema import ColumnLayout, DiagramSpec


def compile_to_mermaid(
    spec: DiagramSpec, preset: Optional[DiagramPreset] = None
) -> str:
    """
    Compile DiagramSpec to Mermaid format with paper-optimized settings.

    Parameters
    ----------
    spec : DiagramSpec
        The semantic diagram specification.
    preset : DiagramPreset, optional
        Override preset (default: inferred from spec.type).

    Returns
    -------
    str
        Mermaid diagram source code.
    """
    if preset is None:
        preset = get_preset(spec.type.value)

    lines = []

    # Theme initialization
    theme_vars = {**preset.mermaid_theme, **spec.theme}
    theme_json = json.dumps({"theme": "base", "themeVariables": theme_vars})
    lines.append(f"%%{{init: {theme_json}}}%%")

    # Determine direction based on paper constraints
    direction = preset.mermaid_direction
    if spec.paper.reading_direction == "top_to_bottom":
        direction = "TB"
    elif spec.paper.column == ColumnLayout.DOUBLE:
        # Double column prefers vertical to save horizontal space
        direction = "TB"

    lines.append(f"graph {direction}")

    # Build node ID to spec mapping
    node_map = {n.id: n for n in spec.nodes}

    # Generate subgraphs for groups
    indent = "    "
    for group_name, group_nodes in spec.layout.groups.items():
        lines.append(f'{indent}subgraph {_sanitize_id(group_name)}["{group_name}"]')
        for node_id in group_nodes:
            if node_id in node_map:
                node = node_map[node_id]
                lines.append(f"{indent}{indent}{_mermaid_node(node, preset)}")
        lines.append(f"{indent}end")

    # Generate standalone nodes (not in any group)
    grouped_nodes = set()
    for group_nodes in spec.layout.groups.values():
        grouped_nodes.update(group_nodes)

    for node in spec.nodes:
        if node.id not in grouped_nodes:
            lines.append(f"{indent}{_mermaid_node(node, preset)}")

    # Generate edges
    for edge in spec.edges:
        edge_str = _mermaid_edge(edge)
        lines.append(f"{indent}{edge_str}")

    # Generate styles for emphasized nodes
    for node in spec.nodes:
        if node.emphasis != "normal" or node.id in spec.paper.emphasize:
            emphasis = "primary" if node.id in spec.paper.emphasize else node.emphasis
            style = preset.emphasis_styles.get(emphasis, {})
            if style:
                style_parts = [f"{k}:{v}" for k, v in style.items()]
                lines.append(
                    f"{indent}style {_sanitize_id(node.id)} {','.join(style_parts)}"
                )

    return "\n".join(lines)


def _mermaid_node(node, preset: DiagramPreset) -> str:
    """Generate Mermaid node definition."""
    shape_template = preset.mermaid_shapes.get(node.shape, '["__LABEL__"]')
    shape_str = shape_template.replace("__LABEL__", node.label)
    return f"{_sanitize_id(node.id)}{shape_str}"


def _escape_mermaid_label(label: str) -> str:
    """Escape special characters in Mermaid labels."""
    # Replace characters that Mermaid interprets as markdown
    label = label.replace(">", "&gt;")
    label = label.replace("<", "&lt;")
    label = label.replace("#", "&num;")
    return label


def _mermaid_edge(edge) -> str:
    """Generate Mermaid edge definition."""
    arrow = "-->" if edge.arrow == "normal" else "---"
    if edge.style == "dashed":
        arrow = "-.->" if edge.arrow == "normal" else "-.-"
    elif edge.style == "dotted":
        arrow = "..>" if edge.arrow == "normal" else "..."

    src = _sanitize_id(edge.source)
    tgt = _sanitize_id(edge.target)

    if edge.label:
        escaped = _escape_mermaid_label(edge.label)
        return f'{src} {arrow}|"{escaped}"| {tgt}'
    return f"{src} {arrow} {tgt}"


__all__ = ["compile_to_mermaid"]
