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

Utility Functions
-----------------
For advanced use cases, utility functions are available via the utils submodule:

>>> from figrecipe import utils
>>> utils.mm_to_inch(25.4)  # Unit conversions
>>> utils.check_font('Arial')  # Font utilities
>>> utils.load_recipe('recipe.yaml')  # Low-level recipe access
"""
__doc__ = _rebrand_text(_RAW_DOC)

# Version
try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("figrecipe")
except Exception:
    __version__ = "0.0.0"  # Fallback for development

# Public API functions (re-exported from _api._public)
# Seaborn proxy and notebook support
from ._api._notebook import enable_svg
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
from ._api._seaborn_proxy import sns

# Style management
from ._api._style_manager import (
    STYLE,
    apply_style,
    list_presets,
    load_style,
    unload_style,
)

# Composition - matplotlib-based (reproducible, editable)
from ._composition import (
    align_panels,
    compose,
    distribute_panels,
    smart_align,
)
from ._composition._compose_mm import (
    compose_figures,
    load_compose_recipe,
    recompose,
)

# Diagram visualization
from ._diagram import Diagram

# Graph visualization presets
from ._graph_presets import (
    get_preset as get_graph_preset,
)
from ._graph_presets import (
    list_presets as list_graph_presets,
)
from ._graph_presets import (
    register_preset as register_graph_preset,
)

# Plot styling utilities
from .styles._plot_styling import (
    style_barplot,
    style_boxplot,
    style_errorbar,
    style_scatter,
    style_violinplot,
)

# Axis helper utilities
from .styles.axis_helpers import (
    OOMFormatter,
    extend,
    force_aspect,
    hide_spines,
    map_ticks,
    rotate_labels,
    sci_note,
    set_n_ticks,
    set_ticks,
    set_x_ticks,
    set_y_ticks,
    show_all_spines,
    show_classic_spines,
    show_spines,
    toggle_spines,
)

__all__ = [
    # Core
    "subplots",
    "save",
    "reproduce",
    "load",
    "info",
    "edit",
    "validate",
    "crop",
    "extract_data",
    # Style
    "load_style",
    "unload_style",
    "list_presets",
    "apply_style",
    "STYLE",
    # Plot styling
    "style_boxplot",
    "style_violinplot",
    "style_barplot",
    "style_scatter",
    "style_errorbar",
    # Axis helpers
    "rotate_labels",
    "hide_spines",
    "show_spines",
    "show_all_spines",
    "show_classic_spines",
    "toggle_spines",
    "set_n_ticks",
    "set_ticks",
    "set_x_ticks",
    "set_y_ticks",
    "map_ticks",
    "OOMFormatter",
    "sci_note",
    "force_aspect",
    "extend",
    # Composition
    "compose",
    "compose_figures",
    "load_compose_recipe",
    "recompose",
    "align_panels",
    "distribute_panels",
    "smart_align",
    # Graph & Diagram
    "get_graph_preset",
    "list_graph_presets",
    "register_graph_preset",
    "Diagram",
    # Extensions
    "sns",
    "enable_svg",
    "__version__",
]
