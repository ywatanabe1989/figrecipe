#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared graph-spec infrastructure for diagram compilation."""

from ._graph import Diagram as GraphDiagram
from ._presets import (
    DECISION_PRESET,
    PIPELINE_PRESET,
    SCIENTIFIC_PRESET,
    WORKFLOW_PRESET,
    DiagramPreset,
    get_preset,
    list_presets,
)
from ._render import get_available_backends
from ._schema import (
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
from ._split import SplitConfig, SplitResult, SplitStrategy

__all__ = [
    # Main class (graph compilation Diagram, aliased to avoid conflict)
    "GraphDiagram",
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

# EOF
