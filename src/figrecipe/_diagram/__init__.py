#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-01-24
# File: figrecipe/_diagram/__init__.py

"""
FigRecipe Diagram module.

Create paper-optimized diagrams that compile to Mermaid or Graphviz
with publication-ready layout constraints.

Examples
--------
>>> import figrecipe as fr

>>> # Programmatic creation
>>> d = fr.Diagram(type="pipeline")
>>> d.add_node("input", "Raw Data")
>>> d.add_node("process", "Transform", emphasis="primary")
>>> d.add_node("output", "Results")
>>> d.add_edge("input", "process")
>>> d.add_edge("process", "output")
>>> print(d.to_mermaid())

>>> # From YAML specification
>>> d = fr.Diagram.from_yaml("workflow.yaml")
>>> d.to_mermaid("workflow.mmd")
>>> d.to_graphviz("workflow.dot")

>>> # From existing Mermaid file
>>> d = fr.Diagram.from_mermaid("existing.mmd", diagram_type="workflow")
>>> d.to_yaml("spec.yaml")
"""

from figrecipe._diagram._diagram import Diagram
from figrecipe._diagram._presets import (
    DECISION_PRESET,
    PIPELINE_PRESET,
    SCIENTIFIC_PRESET,
    WORKFLOW_PRESET,
    DiagramPreset,
    get_preset,
    list_presets,
)
from figrecipe._diagram._render import get_available_backends
from figrecipe._diagram._schema import (
    ColumnLayout,
    DiagramSpec,
    DiagramType,
    EdgeSpec,
    LayoutHints,
    NodeSpec,
    PaperConstraints,
    PaperMode,
    SpacingLevel,
)
from figrecipe._diagram._split import SplitConfig, SplitResult, SplitStrategy

__all__ = [
    # Main class
    "Diagram",
    # Schema
    "DiagramSpec",
    "DiagramType",
    "NodeSpec",
    "EdgeSpec",
    "PaperConstraints",
    "LayoutHints",
    "ColumnLayout",
    "SpacingLevel",
    "PaperMode",
    # Presets
    "DiagramPreset",
    "get_preset",
    "list_presets",
    "WORKFLOW_PRESET",
    "DECISION_PRESET",
    "PIPELINE_PRESET",
    "SCIENTIFIC_PRESET",
    # Split
    "SplitConfig",
    "SplitResult",
    "SplitStrategy",
    # Render
    "get_available_backends",
]
