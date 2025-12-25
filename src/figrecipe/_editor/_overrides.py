#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style override management with separation of base and manual styles.

This module handles the layered style system:
1. Base style (from preset like SCITEX)
2. Programmatic style (from code, e.g., fr.load_style())
3. Manual overrides (from GUI editor)

Manual overrides are stored separately with timestamps, allowing:
- Restoration to original (programmatic) style
- Tracking when manual edits were made
- Comparison between original and edited versions
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class StyleOverrides:
    """
    Manages layered style overrides with timestamp tracking.

    Attributes
    ----------
    base_style : dict
        Original style from preset (e.g., SCITEX values).
    programmatic_style : dict
        Style set programmatically via code.
    manual_overrides : dict
        Overrides from GUI editor.
    call_overrides : dict
        Call parameter overrides {call_id: {param: value}}.
    base_timestamp : str
        When base style was set (ISO format).
    manual_timestamp : str
        When manual overrides were last modified.
    """

    base_style: Dict[str, Any] = field(default_factory=dict)
    programmatic_style: Dict[str, Any] = field(default_factory=dict)
    manual_overrides: Dict[str, Any] = field(default_factory=dict)
    call_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    base_timestamp: Optional[str] = None
    manual_timestamp: Optional[str] = None

    def get_effective_style(self) -> Dict[str, Any]:
        """
        Get the final effective style by merging all layers.

        Priority: base < programmatic < manual

        Returns
        -------
        dict
            Merged style dictionary including call_overrides.
        """
        result = {}
        result.update(self.base_style)
        result.update(self.programmatic_style)
        result.update(self.manual_overrides)
        # Include call_overrides for apply_overrides to use
        if self.call_overrides:
            result["call_overrides"] = self.call_overrides
        return result

    def get_original_style(self) -> Dict[str, Any]:
        """
        Get style without manual overrides (for "Restore" function).

        Returns
        -------
        dict
            Style with only base + programmatic layers.
        """
        result = {}
        result.update(self.base_style)
        result.update(self.programmatic_style)
        return result

    def set_manual_override(self, key: str, value: Any) -> None:
        """
        Set a single manual override.

        Parameters
        ----------
        key : str
            Style property key (e.g., 'axes_width_mm').
        value : Any
            Property value.
        """
        self.manual_overrides[key] = value
        self.manual_timestamp = datetime.now().isoformat()

    def update_manual_overrides(self, overrides: Dict[str, Any]) -> None:
        """
        Update multiple manual overrides at once.

        Parameters
        ----------
        overrides : dict
            Dictionary of overrides to apply.
        """
        self.manual_overrides.update(overrides)
        self.manual_timestamp = datetime.now().isoformat()

    def clear_manual_overrides(self, clear_call_overrides: bool = True) -> None:
        """Clear all manual overrides (restore to original).

        Parameters
        ----------
        clear_call_overrides : bool
            Also clear call parameter overrides (default True).
        """
        self.manual_overrides = {}
        if clear_call_overrides:
            self.call_overrides = {}
        self.manual_timestamp = None

    def has_manual_overrides(self) -> bool:
        """Check if any manual overrides exist."""
        return len(self.manual_overrides) > 0

    def get_diff(self) -> Dict[str, Dict[str, Any]]:
        """
        Get differences between original and manual overrides.

        Returns
        -------
        dict
            Dictionary showing changes: {key: {'original': val, 'manual': val}}
        """
        original = self.get_original_style()
        diff = {}

        for key, manual_val in self.manual_overrides.items():
            original_val = original.get(key)
            if original_val != manual_val:
                diff[key] = {
                    "original": original_val,
                    "manual": manual_val,
                }

        return diff

    def set_call_override(self, call_id: str, param: str, value: Any) -> None:
        """
        Set a call parameter override.

        Parameters
        ----------
        call_id : str
            ID of the call (e.g., 'bp1', 'vp1').
        param : str
            Parameter name.
        value : Any
            Parameter value.
        """
        if call_id not in self.call_overrides:
            self.call_overrides[call_id] = {}
        self.call_overrides[call_id][param] = value
        self.manual_timestamp = datetime.now().isoformat()

    def get_call_overrides(self, call_id: str) -> Dict[str, Any]:
        """Get all overrides for a specific call."""
        return self.call_overrides.get(call_id, {})

    def has_call_overrides(self) -> bool:
        """Check if any call overrides exist."""
        return len(self.call_overrides) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "base_style": self.base_style,
            "programmatic_style": self.programmatic_style,
            "manual_overrides": self.manual_overrides,
            "call_overrides": self.call_overrides,
            "base_timestamp": self.base_timestamp,
            "manual_timestamp": self.manual_timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StyleOverrides":
        """Create from dictionary."""
        return cls(
            base_style=data.get("base_style", {}),
            programmatic_style=data.get("programmatic_style", {}),
            manual_overrides=data.get("manual_overrides", {}),
            call_overrides=data.get("call_overrides", {}),
            base_timestamp=data.get("base_timestamp"),
            manual_timestamp=data.get("manual_timestamp"),
        )


def get_overrides_path(recipe_path: Path) -> Path:
    """
    Get the path for storing overrides alongside a recipe.

    Parameters
    ----------
    recipe_path : Path
        Path to the recipe file.

    Returns
    -------
    Path
        Path to the overrides file.

    Examples
    --------
    >>> get_overrides_path(Path('figure.yaml'))
    Path('figure.overrides.json')
    """
    return recipe_path.with_suffix(".overrides.json")


def save_overrides(
    overrides: StyleOverrides,
    path: Path,
) -> Path:
    """
    Save style overrides to JSON file.

    Parameters
    ----------
    overrides : StyleOverrides
        Overrides to save.
    path : Path
        Path to save to (or recipe path to derive from).

    Returns
    -------
    Path
        Path where overrides were saved.
    """
    # If path is a recipe, derive overrides path
    if path.suffix in (".yaml", ".yml"):
        path = get_overrides_path(path)

    data = overrides.to_dict()
    data["_version"] = "1.0"
    data["_saved_at"] = datetime.now().isoformat()

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path


def load_overrides(path: Path) -> Optional[StyleOverrides]:
    """
    Load style overrides from JSON file.

    Parameters
    ----------
    path : Path
        Path to overrides file or recipe file.

    Returns
    -------
    StyleOverrides or None
        Loaded overrides, or None if file doesn't exist.
    """
    # If path is a recipe, derive overrides path
    if path.suffix in (".yaml", ".yml"):
        path = get_overrides_path(path)

    if not path.exists():
        return None

    with open(path) as f:
        data = json.load(f)

    # Remove metadata
    data.pop("_version", None)
    data.pop("_saved_at", None)

    return StyleOverrides.from_dict(data)


def create_overrides_from_style(
    base_style: Optional[Dict[str, Any]] = None,
    programmatic_style: Optional[Dict[str, Any]] = None,
) -> StyleOverrides:
    """
    Create StyleOverrides from existing style configuration.

    Parameters
    ----------
    base_style : dict, optional
        Base style from preset.
    programmatic_style : dict, optional
        Style set via code.

    Returns
    -------
    StyleOverrides
        New overrides object.
    """
    return StyleOverrides(
        base_style=base_style or {},
        programmatic_style=programmatic_style or {},
        manual_overrides={},
        base_timestamp=datetime.now().isoformat(),
        manual_timestamp=None,
    )


__all__ = [
    "StyleOverrides",
    "get_overrides_path",
    "save_overrides",
    "load_overrides",
    "create_overrides_from_style",
]
