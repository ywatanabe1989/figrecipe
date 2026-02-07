#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle format for figrecipe figures.

A bundle is a self-contained directory that stores:
- spec.json: WHAT to plot (semantic specification, axes, traces, data mappings)
- style.json: HOW it looks (colors, fonts, sizes, appearance settings)
- data.csv: Raw data (immutable source data)
- exports/: Generated outputs (PNG, SVG, hitmap, etc.)
- cache/: Regenerable artifacts

Principles:
- spec.json + style.json = editable (can be modified to change appearance)
- data.csv = immutable (source data should not be modified)
- cache/ = regenerable (can be deleted and rebuilt)
- exports/ = output artifacts

Usage:
    import figrecipe as fr

    # Create figure
    fig, ax = fr.subplots()
    ax.plot(x, y, id='trace1')

    # Save as bundle (ZIP format)
    fr.save_bundle(fig, 'my_figure')  # → my_figure.zip

    # Load components
    spec, style, data = fr.load_bundle('my_figure.zip')

    # Reproduce from bundle
    fig, ax = fr.reproduce_bundle('my_figure.zip')
"""

from ._load import load_bundle, reproduce_bundle
from ._paths import (
    bundle_exists,
    create_bundle_structure,
    get_bundle_paths,
    is_bundle_path,
)
from ._save import save_bundle

__all__ = [
    "save_bundle",
    "load_bundle",
    "reproduce_bundle",
    "is_bundle_path",
    "bundle_exists",
    "get_bundle_paths",
    "create_bundle_structure",
]
