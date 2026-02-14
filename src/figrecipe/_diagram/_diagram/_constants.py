#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constants for schematic diagram rendering."""

# Anchor point definitions (relative to box: 0-1 range)
ANCHOR_POINTS = {
    "center": (0.5, 0.5),
    "top": (0.5, 1.0),
    "bottom": (0.5, 0.0),
    "left": (0.0, 0.5),
    "right": (1.0, 0.5),
    "top-left": (0.0, 1.0),
    "top-right": (1.0, 1.0),
    "bottom-left": (0.0, 0.0),
    "bottom-right": (1.0, 0.0),
}

# Semantic node classes → default shape
NODE_CLASSES = {
    "source": "rounded",
    "input": "cylinder",
    "processing": "rounded",
    "output": "cylinder",
    "claim": "document",
    "code": "codeblock",
}

# Verification states → default (fill_color, border_color)
VERIFICATION_STATES = {
    "verified": ("#90EE90", "#228B22"),
    "tampered": ("#FFB6C1", "#DC143C"),
    "invalidated": ("#FFD580", "#E67E00"),
    "ignored": ("#D3D3D3", "#808080"),
}


__all__ = ["ANCHOR_POINTS", "NODE_CLASSES", "VERIFICATION_STATES"]
