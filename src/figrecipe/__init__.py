#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module docstring is defined below after branding import

# Branding support (must be imported first, before docstring is set)
from ._branding import rebrand_text as _rebrand_text

# Define module docstring with branding applied
_RAW_DOC = """
figrecipe - Record and reproduce matplotlib figures.

A lightweight library for capturing matplotlib plotting calls and
reproducing figures from saved recipes.

Usage
-----
>>> import figrecipe as fr
>>> fig, ax = fr.subplots()
>>> ax.plot(x, y, id='my_data')
>>> fr.save(fig, 'recipe.yaml')

Examples
--------
Recording a figure:

>>> import figrecipe as fr
>>> import numpy as np
>>>
>>> x = np.linspace(0, 10, 100)
>>> y = np.sin(x)
>>>
>>> fig, ax = fr.subplots()
>>> ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
>>> ax.set_xlabel('Time')
>>> ax.set_ylabel('Amplitude')
>>> fr.save(fig, 'my_figure.yaml')

Reproducing a figure:

>>> fig, ax = fr.reproduce('my_figure.yaml')
>>> plt.show()

Submodules
----------
- fr.utils: Unit conversions, font checks, low-level recipe access
- fr.styles: Axis helpers, spine management, plot styling functions
- fr.viz: Diagram and graph visualization utilities

>>> from figrecipe import utils
>>> utils.mm_to_inch(25.4)  # Unit conversions

>>> from figrecipe import styles
>>> styles.hide_spines(ax)  # Spine management
"""
__doc__ = _rebrand_text(_RAW_DOC)

# Version
try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("figrecipe")
except Exception:
    __version__ = "0.0.0"  # Fallback for development

# =============================================================================
# CORE PUBLIC API - Minimal, essential functions only
# =============================================================================
from . import colors
from ._api._public import (
    crop,
    extract_data,
    gui,
    info,
    load,
    reproduce,
    save,
    subplots,
)
from ._api._public import validate_recipe as validate
from ._api._signature import caption_with_signature, signature
from ._api._style_manager import list_presets, load_style, unload_style
from ._bundle import load_bundle, reproduce_bundle, save_bundle
from ._composition import align_panels, align_smart, compose, distribute_panels
from ._graph_presets import get_preset as get_graph_preset
from ._schematic import Diagram
from ._seaborn import get_seaborn_recorder as _get_sns


# Lazy seaborn access (avoids import error if seaborn not installed)
@property
def _sns_property(self):
    return _get_sns()


# Module-level property emulation for sns
class _SnsModule:
    def __getattr__(self, name):
        return getattr(_get_sns(), name)


sns = _SnsModule()
from ._graph_presets import list_presets as list_graph_presets
from ._graph_presets import register_preset as register_graph_preset

# =============================================================================
# PUBLIC API (__all__ controls tab-completion - keep minimal)
# =============================================================================

__all__ = [
    # Core workflow
    "subplots",
    "save",
    "reproduce",
    "load",
    "compose",
    "align_panels",
    "distribute_panels",
    "align_smart",
    "gui",
    "crop",
    "info",
    "validate",
    "extract_data",
    # Bundle format
    "save_bundle",
    "load_bundle",
    "reproduce_bundle",
    # Style management
    "load_style",
    "unload_style",
    "list_presets",
    # Graph presets
    "get_graph_preset",
    "list_graph_presets",
    "register_graph_preset",
    # Diagram
    "Diagram",
    # Color utilities
    "colors",
    # Signature
    "signature",
    "caption_with_signature",
    # Seaborn integration
    "sns",
    # Version
    "__version__",
]
