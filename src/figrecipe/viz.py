#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualization utilities for figrecipe.

Provides diagram generation and graph visualization presets.

Usage
-----
>>> from figrecipe import viz
>>> diagram = viz.Diagram(spec)
>>> diagram.to_mermaid()

>>> preset = viz.get_graph_preset('scientific')
"""

from ._diagram import Diagram
from ._graph_presets import (
    get_preset as get_graph_preset,
)
from ._graph_presets import (
    list_presets as list_graph_presets,
)
from ._graph_presets import (
    register_preset as register_graph_preset,
)

__all__ = [
    # Diagram
    "Diagram",
    # Graph presets
    "get_graph_preset",
    "list_graph_presets",
    "register_graph_preset",
]
