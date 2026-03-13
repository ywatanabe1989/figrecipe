#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: figrecipe/presets/_journals.py

"""Journal presets — static reference data for figure specifications.

Based on official journal submission guidelines. These are standardized
sizes that work for Nature, Science, Cell, PNAS, and most major journals.
"""

from __future__ import annotations

from typing import Any

# Static journal presets — single source of truth.
# Based on official submission guidelines of each journal.
# No database needed; these rarely change.
_JOURNAL_PRESETS: list[dict[str, Any]] = [
    # ── Standard (safe defaults) ──────────────────────────────────
    {
        "id": "standard-single",
        "name": "Standard",
        "column_type": "single",
        "width_mm": 90,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "standard-double",
        "name": "Standard",
        "column_type": "double",
        "width_mm": 180,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── Nature (Nature family including Nature Methods, etc.) ────
    {
        "id": "nature-single",
        "name": "Nature",
        "column_type": "single",
        "width_mm": 90,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "nature-double",
        "name": "Nature",
        "column_type": "double",
        "width_mm": 180,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── Science ───────────────────────────────────────────────────
    {
        "id": "science-single",
        "name": "Science",
        "column_type": "single",
        "width_mm": 90,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "science-double",
        "name": "Science",
        "column_type": "double",
        "width_mm": 180,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── Cell ──────────────────────────────────────────────────────
    {
        "id": "cell-single",
        "name": "Cell",
        "column_type": "single",
        "width_mm": 85,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 6,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "cell-double",
        "name": "Cell",
        "column_type": "double",
        "width_mm": 174,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Helvetica",
        "font_size_pt": 6,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── PNAS ──────────────────────────────────────────────────────
    {
        "id": "pnas-single",
        "name": "PNAS",
        "column_type": "single",
        "width_mm": 87,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "pnas-double",
        "name": "PNAS",
        "column_type": "double",
        "width_mm": 178,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── PLOS ONE ──────────────────────────────────────────────────
    {
        "id": "plos-single",
        "name": "PLOS ONE",
        "column_type": "single",
        "width_mm": 83,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 10,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "plos-double",
        "name": "PLOS ONE",
        "column_type": "double",
        "width_mm": 173,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 10,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── IEEE ──────────────────────────────────────────────────────
    {
        "id": "ieee-single",
        "name": "IEEE",
        "column_type": "single",
        "width_mm": 88,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Times New Roman",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "ieee-double",
        "name": "IEEE",
        "column_type": "double",
        "width_mm": 181,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Times New Roman",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── The Lancet ────────────────────────────────────────────────
    {
        "id": "lancet-single",
        "name": "The Lancet",
        "column_type": "single",
        "width_mm": 89,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "lancet-double",
        "name": "The Lancet",
        "column_type": "double",
        "width_mm": 180,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── JAMA ──────────────────────────────────────────────────────
    {
        "id": "jama-single",
        "name": "JAMA",
        "column_type": "single",
        "width_mm": 86,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "jama-double",
        "name": "JAMA",
        "column_type": "double",
        "width_mm": 178,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 8,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── eLife ─────────────────────────────────────────────────────
    {
        "id": "elife-single",
        "name": "eLife",
        "column_type": "single",
        "width_mm": 86,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "elife-double",
        "name": "eLife",
        "column_type": "double",
        "width_mm": 178,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Arial",
        "font_size_pt": 7,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    # ── NeurIPS / ICML / ICLR (ML conferences) ───────────────────
    {
        "id": "neurips-single",
        "name": "NeurIPS",
        "column_type": "single",
        "width_mm": 84,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Times New Roman",
        "font_size_pt": 10,
        "line_width_pt": 0.5,
        "is_active": True,
    },
    {
        "id": "neurips-double",
        "name": "NeurIPS",
        "column_type": "double",
        "width_mm": 174,
        "height_mm": None,
        "dpi": 300,
        "font_family": "Times New Roman",
        "font_size_pt": 10,
        "line_width_pt": 0.5,
        "is_active": True,
    },
]


def get_journals(active_only: bool = True) -> list[dict[str, Any]]:
    """Get all journal presets.

    Parameters
    ----------
    active_only : bool
        If True, return only active presets.

    Returns
    -------
    list of dict
        Journal preset records.
    """
    if active_only:
        return [p for p in _JOURNAL_PRESETS if p.get("is_active", True)]
    return list(_JOURNAL_PRESETS)


def get_journal(name: str, column_type: str) -> dict[str, Any] | None:
    """Get a specific journal preset by name and column type.

    Parameters
    ----------
    name : str
        Journal name (e.g., "Standard").
    column_type : str
        Column type: "single", "double", or "full".

    Returns
    -------
    dict or None
        The matching preset, or None if not found.
    """
    for preset in _JOURNAL_PRESETS:
        if preset["name"] == name and preset["column_type"] == column_type:
            return dict(preset)
    return None


def get_journal_by_id(preset_id: str) -> dict[str, Any] | None:
    """Get a journal preset by its ID.

    Parameters
    ----------
    preset_id : str
        Preset ID (e.g., "standard-single").

    Returns
    -------
    dict or None
        The matching preset, or None if not found.
    """
    for preset in _JOURNAL_PRESETS:
        if preset["id"] == preset_id:
            return dict(preset)
    return None


def mm_to_pixels(mm: float, dpi: int) -> int:
    """Convert millimeters to pixels at a given DPI.

    Parameters
    ----------
    mm : float
        Size in millimeters.
    dpi : int
        Dots per inch.

    Returns
    -------
    int
        Size in pixels.
    """
    inches = mm / 25.4
    return int(inches * dpi)


# EOF
