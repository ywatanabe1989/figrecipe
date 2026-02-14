#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FigRecipe Diagram module.

Unified diagram package with four sub-packages:
- _diagram/   : Box-and-arrow diagram builder (fr.Diagram)
- _shared/    : Graph-spec schema, presets, split, native rendering
- _mermaid/   : Mermaid compilation and rendering backend
- _graphviz/  : Graphviz compilation and rendering backend
"""

# Box-and-arrow Diagram builder (the primary public API: fr.Diagram)
from ._diagram._core import Diagram

# Graph compilation Diagram (for Mermaid/Graphviz workflows)
from ._shared._graph import Diagram as GraphDiagram

# Schema and presets (re-exported for external consumers)
from ._shared._presets import (
    DECISION_PRESET,
    PIPELINE_PRESET,
    SCIENTIFIC_PRESET,
    WORKFLOW_PRESET,
    DiagramPreset,
    get_preset,
    list_presets,
)
from ._shared._render import get_available_backends
from ._shared._schema import (
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
from ._shared._split import SplitConfig, SplitResult, SplitStrategy

__all__ = [
    # Box-and-arrow builder (public fr.Diagram)
    "Diagram",
    # Graph compilation
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
