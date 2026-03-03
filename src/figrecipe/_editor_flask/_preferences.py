#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""User preferences management for the figure editor.

Preferences are stored in ~/.figrecipe/preferences.json and persist
across sessions. This allows users to set defaults like dark mode.
"""

import json
from pathlib import Path
from typing import Any, Dict

# Default preferences
DEFAULT_PREFERENCES = {
    "dark_mode": False,
    "default_style": "SCITEX",
    "auto_save": True,
    "show_hit_regions": False,
}

# Preferences file location
PREFERENCES_DIR = Path.home() / ".figrecipe"
PREFERENCES_FILE = PREFERENCES_DIR / "preferences.json"


def get_preferences_path() -> Path:
    """Get the path to the preferences file."""
    return PREFERENCES_FILE


def load_preferences() -> Dict[str, Any]:
    """Load user preferences from disk.

    Returns
    -------
    dict
        User preferences merged with defaults.
    """
    prefs = DEFAULT_PREFERENCES.copy()

    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE, "r") as f:
                saved = json.load(f)
                prefs.update(saved)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, use defaults
            pass

    return prefs


def save_preferences(prefs: Dict[str, Any]) -> bool:
    """Save user preferences to disk.

    Parameters
    ----------
    prefs : dict
        Preferences to save.

    Returns
    -------
    bool
        True if save was successful.
    """
    try:
        PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)
        with open(PREFERENCES_FILE, "w") as f:
            json.dump(prefs, f, indent=2)
        return True
    except IOError:
        return False


def get_preference(key: str, default: Any = None) -> Any:
    """Get a single preference value.

    Parameters
    ----------
    key : str
        Preference key.
    default : Any, optional
        Default value if key not found.

    Returns
    -------
    Any
        Preference value.
    """
    prefs = load_preferences()
    return prefs.get(key, default)


def set_preference(key: str, value: Any) -> bool:
    """Set a single preference value.

    Parameters
    ----------
    key : str
        Preference key.
    value : Any
        Value to set.

    Returns
    -------
    bool
        True if save was successful.
    """
    prefs = load_preferences()
    prefs[key] = value
    return save_preferences(prefs)


def reset_preferences() -> bool:
    """Reset all preferences to defaults.

    Returns
    -------
    bool
        True if reset was successful.
    """
    return save_preferences(DEFAULT_PREFERENCES.copy())


__all__ = [
    "DEFAULT_PREFERENCES",
    "get_preferences_path",
    "load_preferences",
    "save_preferences",
    "get_preference",
    "set_preference",
    "reset_preferences",
]

# EOF
