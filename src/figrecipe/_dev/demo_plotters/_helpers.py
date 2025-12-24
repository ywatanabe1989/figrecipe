#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper functions for demo plotters."""

from typing import Callable, Dict, List, Optional

from ._categories import CATEGORIES, REPRESENTATIVES
from ._registry import REGISTRY


def list_plots() -> List[str]:
    """List all available plot types."""
    return list(REGISTRY.keys())


def list_plots_by_category() -> Dict[str, List[str]]:
    """List all available plot types organized by category."""
    return CATEGORIES.copy()


def get_representative_plots() -> List[str]:
    """Get one representative plot from each category for demos."""
    return [p for p in REPRESENTATIVES.values() if p in REGISTRY]


def get_plotter(name: str) -> Optional[Callable]:
    """Get plotter function by name."""
    return REGISTRY.get(name)


# EOF
