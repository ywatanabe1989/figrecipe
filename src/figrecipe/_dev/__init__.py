#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Development utilities for figrecipe.

Provides demo plotters for all supported matplotlib plotting methods.
All plotters follow signature: (plt, rng, ax=None) -> (fig, ax)

Usage:
    import figrecipe as fr
    from figrecipe._dev import PLOTTERS, run_all_demos

    # Run a single demo
    fig, ax = PLOTTERS["plot"](fr, np.random.default_rng(42))

    # Run all demos
    results = run_all_demos(fr, output_dir="./outputs")
"""

from . import browser
from ._plotters import PLOTTERS, get_plotter, list_plotters
from ._run_demos import run_all_demos

__all__ = [
    "PLOTTERS",
    "list_plotters",
    "get_plotter",
    "run_all_demos",
    "browser",
]

# EOF
