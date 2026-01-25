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

# Core workflow functions
# =============================================================================
# SCITEX COMPATIBILITY EXPORTS (not in __all__ for clean tab-completion)
# These are re-exported for backwards compatibility with scitex.plt
# noqa: F401 comments indicate intentional re-exports
# =============================================================================
from ._api._notebook import enable_svg as enable_svg  # noqa: F401
from ._api._public import (
    crop,
    edit,
    extract_data,
    info,
    load,
    reproduce,
    save,
    subplots,
)
from ._api._public import (
    validate_recipe as validate,
)
from ._api._seaborn_proxy import sns as sns  # noqa: F401
from ._api._style_manager import STYLE as STYLE  # noqa: F401
from ._api._style_manager import apply_style as apply_style  # noqa: F401

# Style management
from ._api._style_manager import (
    list_presets,
    load_style,
    unload_style,
)
from ._composition import align_panels as align_panels  # noqa: F401

# Composition
from ._composition import compose
from ._composition import distribute_panels as distribute_panels  # noqa: F401
from ._composition import smart_align as smart_align  # noqa: F401

# Diagram class (for scitex integration)
from ._diagram import Diagram as Diagram  # noqa: F401
from ._graph_presets import get_preset as get_graph_preset  # noqa: F401
from ._graph_presets import list_presets as list_graph_presets  # noqa: F401
from ._graph_presets import register_preset as register_graph_preset  # noqa: F401

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
    "edit",
    "crop",
    "info",
    "validate",
    "extract_data",
    # Style management
    "load_style",
    "unload_style",
    "list_presets",
    # Version
    "__version__",
]
