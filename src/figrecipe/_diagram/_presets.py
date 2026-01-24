#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-01-24
# File: figrecipe/_diagram/_presets.py

"""
Presets for common diagram types in scientific papers.

Each preset defines rules for compiling the semantic spec to backend formats.
These encode domain knowledge about "what makes a good paper figure."
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class DiagramPreset:
    """Rules for compiling a diagram type."""

    # Mermaid settings
    mermaid_direction: str  # TB, LR, RL, BT
    mermaid_theme: Dict[str, str]

    # Graphviz settings
    graphviz_rankdir: str  # TB, LR, RL, BT
    graphviz_ranksep: float
    graphviz_nodesep: float

    # Spacing mappings
    spacing_map: Dict[str, Dict[str, float]]

    # Shape mappings (semantic -> backend)
    mermaid_shapes: Dict[str, str]
    graphviz_shapes: Dict[str, str]

    # Emphasis styles (colors, borders)
    emphasis_styles: Dict[str, Dict[str, str]]


# Workflow preset: sequential processes, emphasize flow
WORKFLOW_PRESET = DiagramPreset(
    mermaid_direction="LR",  # Left-to-right for workflows
    mermaid_theme={
        "primaryColor": "#1a2634",
        "primaryTextColor": "#e0e0e0",
        "primaryBorderColor": "#3a4a5a",
        "lineColor": "#5a9fcf",
    },
    graphviz_rankdir="LR",
    graphviz_ranksep=0.8,
    graphviz_nodesep=0.5,
    spacing_map={
        "tight": {"ranksep": 0.3, "nodesep": 0.2},  # Publication: minimal
        "compact": {"ranksep": 0.4, "nodesep": 0.3},
        "medium": {"ranksep": 0.8, "nodesep": 0.5},
        "large": {"ranksep": 1.2, "nodesep": 0.8},
    },
    mermaid_shapes={
        "box": '["__LABEL__"]',
        "rounded": '("__LABEL__")',
        "diamond": '{"__LABEL__"}',
        "circle": '(("__LABEL__"))',
        "stadium": '(["__LABEL__"])',
    },
    graphviz_shapes={
        "box": "box",
        "rounded": "box",  # with style=rounded
        "diamond": "diamond",
        "circle": "circle",
        "stadium": "box",  # with style=rounded
    },
    emphasis_styles={
        "primary": {"fill": "#0d4a6b", "stroke": "#5a9fcf", "stroke-width": "2px"},
        "success": {"fill": "#ccffcc", "stroke": "#00cc00"},
        "warning": {"fill": "#ffcccc", "stroke": "#cc0000"},
        "muted": {"fill": "#f0f0f0", "stroke": "#999999"},
        "normal": {"fill": "#1a2634", "stroke": "#3a4a5a"},
    },
)

# Decision tree preset: top-to-bottom with branches
DECISION_PRESET = DiagramPreset(
    mermaid_direction="TB",
    mermaid_theme={
        "primaryColor": "#f5f5f5",
        "primaryTextColor": "#333333",
        "primaryBorderColor": "#666666",
        "lineColor": "#666666",
    },
    graphviz_rankdir="TB",
    graphviz_ranksep=1.0,
    graphviz_nodesep=0.6,
    spacing_map={
        "tight": {"ranksep": 0.4, "nodesep": 0.3},
        "compact": {"ranksep": 0.6, "nodesep": 0.4},
        "medium": {"ranksep": 1.0, "nodesep": 0.6},
        "large": {"ranksep": 1.5, "nodesep": 1.0},
    },
    mermaid_shapes={
        "box": '["__LABEL__"]',
        "rounded": '("__LABEL__")',
        "diamond": '{"__LABEL__"}',
        "circle": '(("__LABEL__"))',
        "stadium": '(["__LABEL__"])',
    },
    graphviz_shapes={
        "box": "box",
        "rounded": "box",
        "diamond": "diamond",
        "circle": "circle",
        "stadium": "box",
    },
    emphasis_styles={
        "primary": {"fill": "#e6f3ff", "stroke": "#0066cc", "stroke-width": "2px"},
        "success": {"fill": "#e6ffe6", "stroke": "#00aa00"},
        "warning": {"fill": "#ffe6e6", "stroke": "#cc0000"},
        "muted": {"fill": "#f0f0f0", "stroke": "#aaaaaa"},
        "normal": {"fill": "#ffffff", "stroke": "#666666"},
    },
)

# Pipeline preset: strict horizontal stages
PIPELINE_PRESET = DiagramPreset(
    mermaid_direction="LR",
    mermaid_theme={
        "primaryColor": "#ffffff",
        "primaryTextColor": "#333333",
        "primaryBorderColor": "#0066cc",
        "lineColor": "#0066cc",
    },
    graphviz_rankdir="LR",
    graphviz_ranksep=1.2,
    graphviz_nodesep=0.4,
    spacing_map={
        "tight": {"ranksep": 0.5, "nodesep": 0.2},
        "compact": {"ranksep": 0.8, "nodesep": 0.3},
        "medium": {"ranksep": 1.2, "nodesep": 0.4},
        "large": {"ranksep": 1.8, "nodesep": 0.6},
    },
    mermaid_shapes={
        "box": '["__LABEL__"]',
        "rounded": '("__LABEL__")',
        "diamond": '{"__LABEL__"}',
        "circle": '(("__LABEL__"))',
        "stadium": '(["__LABEL__"])',
    },
    graphviz_shapes={
        "box": "box",
        "rounded": "box",
        "diamond": "diamond",
        "circle": "circle",
        "stadium": "box",
    },
    emphasis_styles={
        "primary": {"fill": "#e6f0ff", "stroke": "#0044aa", "stroke-width": "2px"},
        "success": {"fill": "#e6ffe6", "stroke": "#00aa00"},
        "warning": {"fill": "#fff3e6", "stroke": "#ff8800"},
        "muted": {"fill": "#f5f5f5", "stroke": "#cccccc"},
        "normal": {"fill": "#ffffff", "stroke": "#0066cc"},
    },
)


# Scientific preset: clean, publication-ready, matches SCITEX figure style
SCIENTIFIC_PRESET = DiagramPreset(
    mermaid_direction="LR",
    mermaid_theme={
        "primaryColor": "#ffffff",
        "primaryTextColor": "#333333",
        "primaryBorderColor": "#0080C0",  # SCITEX blue
        "lineColor": "#0080C0",
        "secondaryColor": "#f8f9fa",
        "tertiaryColor": "#e9ecef",
    },
    graphviz_rankdir="LR",
    graphviz_ranksep=0.6,
    graphviz_nodesep=0.4,
    spacing_map={
        "tight": {"ranksep": 0.3, "nodesep": 0.2},
        "compact": {"ranksep": 0.4, "nodesep": 0.3},
        "medium": {"ranksep": 0.6, "nodesep": 0.4},
        "large": {"ranksep": 1.0, "nodesep": 0.6},
    },
    mermaid_shapes={
        "box": '["__LABEL__"]',
        "rounded": '("__LABEL__")',
        "diamond": '{"__LABEL__"}',
        "circle": '(("__LABEL__"))',
        "stadium": '(["__LABEL__"])',
    },
    graphviz_shapes={
        "box": "box",
        "rounded": "box",
        "diamond": "diamond",
        "circle": "circle",
        "stadium": "box",
    },
    emphasis_styles={
        # SCITEX color palette
        "primary": {
            "fill": "#0080C0",
            "stroke": "#0060A0",
            "stroke-width": "1.5px",
        },  # blue
        "success": {
            "fill": "#14B414",
            "stroke": "#0f8f0f",
            "stroke-width": "1.5px",
        },  # green
        "warning": {
            "fill": "#FF4632",
            "stroke": "#cc382a",
            "stroke-width": "1.5px",
        },  # red
        "muted": {"fill": "#f0f0f0", "stroke": "#999999", "stroke-width": "0.5px"},
        "normal": {"fill": "#ffffff", "stroke": "#0080C0", "stroke-width": "1px"},
    },
)


def get_preset(diagram_type: str) -> DiagramPreset:
    """Get preset for diagram type."""
    presets = {
        "workflow": WORKFLOW_PRESET,
        "decision": DECISION_PRESET,
        "pipeline": PIPELINE_PRESET,
        "hierarchy": DECISION_PRESET,
        "comparison": WORKFLOW_PRESET,
        "scientific": SCIENTIFIC_PRESET,
        "scitex": SCIENTIFIC_PRESET,  # Alias
    }
    return presets.get(diagram_type.lower(), WORKFLOW_PRESET)


def list_presets() -> dict:
    """List all available presets with descriptions."""
    return {
        "workflow": "Sequential process, left-to-right flow",
        "decision": "Decision tree, top-to-bottom with branches",
        "pipeline": "Data pipeline, strict horizontal stages",
        "hierarchy": "Tree structure, top-to-bottom with levels",
        "comparison": "Side-by-side comparison layout",
        "scientific": "Publication-ready, SCITEX color palette",
    }
