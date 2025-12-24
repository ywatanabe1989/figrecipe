#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for user preferences management in the figure editor."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


@pytest.fixture
def temp_prefs_dir(tmp_path):
    """Create a temporary preferences directory."""
    prefs_dir = tmp_path / ".figrecipe"
    prefs_file = prefs_dir / "preferences.json"
    return prefs_dir, prefs_file


class TestPreferencesModule:
    """Test the preferences module functions."""

    def test_default_preferences(self):
        """Test default preferences values."""
        from figrecipe._editor._preferences import DEFAULT_PREFERENCES

        assert "dark_mode" in DEFAULT_PREFERENCES
        assert DEFAULT_PREFERENCES["dark_mode"] is False
        assert "default_style" in DEFAULT_PREFERENCES

    def test_load_preferences_defaults(self, temp_prefs_dir):
        """Test loading preferences returns defaults when file doesn't exist."""
        from figrecipe._editor._preferences import (
            load_preferences,
        )

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            prefs = load_preferences()
            assert prefs["dark_mode"] is False
            assert prefs["default_style"] == "SCITEX"

    def test_save_and_load_preferences(self, temp_prefs_dir):
        """Test saving and loading preferences."""
        from figrecipe._editor._preferences import (
            load_preferences,
            save_preferences,
        )

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Save preferences
            test_prefs = {"dark_mode": True, "default_style": "TEST"}
            result = save_preferences(test_prefs)
            assert result is True
            assert prefs_file.exists()

            # Load and verify
            loaded = load_preferences()
            assert loaded["dark_mode"] is True
            assert loaded["default_style"] == "TEST"

    def test_set_preference(self, temp_prefs_dir):
        """Test setting a single preference."""
        from figrecipe._editor._preferences import (
            get_preference,
            set_preference,
        )

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Set dark mode
            result = set_preference("dark_mode", True)
            assert result is True

            # Verify it was saved
            value = get_preference("dark_mode")
            assert value is True

    def test_get_preference_with_default(self, temp_prefs_dir):
        """Test getting preference with default value."""
        from figrecipe._editor._preferences import get_preference

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Get non-existent preference with default
            value = get_preference("nonexistent", "my_default")
            assert value == "my_default"

    def test_reset_preferences(self, temp_prefs_dir):
        """Test resetting preferences to defaults."""
        from figrecipe._editor._preferences import (
            DEFAULT_PREFERENCES,
            load_preferences,
            reset_preferences,
            set_preference,
        )

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Set custom preferences
            set_preference("dark_mode", True)
            set_preference("default_style", "CUSTOM")

            # Reset
            result = reset_preferences()
            assert result is True

            # Verify defaults are restored
            prefs = load_preferences()
            assert prefs["dark_mode"] == DEFAULT_PREFERENCES["dark_mode"]
            assert prefs["default_style"] == DEFAULT_PREFERENCES["default_style"]

    def test_load_corrupted_preferences(self, temp_prefs_dir):
        """Test loading corrupted preferences file returns defaults."""
        from figrecipe._editor._preferences import load_preferences

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Create corrupted preferences file
            prefs_dir.mkdir(parents=True, exist_ok=True)
            with open(prefs_file, "w") as f:
                f.write("{ invalid json")

            # Should return defaults
            prefs = load_preferences()
            assert prefs["dark_mode"] is False
            assert prefs["default_style"] == "SCITEX"


class TestFigureEditorPreferences:
    """Test that FigureEditor loads preferences correctly."""

    def test_editor_loads_dark_mode_preference(self, temp_prefs_dir):
        """Test that FigureEditor loads dark_mode from preferences."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor

        prefs_dir, prefs_file = temp_prefs_dir

        # Save dark mode preference as True
        prefs_dir.mkdir(parents=True, exist_ok=True)
        with open(prefs_file, "w") as f:
            json.dump({"dark_mode": True}, f)

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            fig, ax = fr.subplots()
            ax.plot([1, 2, 3])

            editor = FigureEditor(fig)
            assert editor.dark_mode is True

    def test_editor_defaults_light_mode(self, temp_prefs_dir):
        """Test that FigureEditor defaults to light mode when no preferences."""
        import figrecipe as fr
        from figrecipe._editor._flask_app import FigureEditor

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            fig, ax = fr.subplots()
            ax.plot([1, 2, 3])

            editor = FigureEditor(fig)
            assert editor.dark_mode is False


class TestDarkModeTemplate:
    """Test that dark mode is properly applied to HTML template."""

    def test_html_template_dark_mode_enabled(self):
        """Test that HTML template includes dark mode when enabled."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
            dark_mode=True,
        )

        # Check data-theme attribute is set to dark
        assert 'data-theme="dark"' in html
        # Check checkbox is checked
        assert 'id="dark-mode-toggle" checked' in html

    def test_html_template_dark_mode_disabled(self):
        """Test that HTML template excludes dark mode when disabled."""
        from figrecipe._editor._templates import build_html_template

        html = build_html_template(
            image_base64="",
            bboxes={},
            color_map={},
            style={},
            overrides={},
            img_size=(100, 100),
            dark_mode=False,
        )

        # Check data-theme attribute is set to light
        assert 'data-theme="light"' in html
        # Check checkbox is not checked (empty placeholder replaced)
        assert 'id="dark-mode-toggle" >' in html or 'id="dark-mode-toggle">' in html


class TestPreferencesPersistence:
    """Test that preferences persist across editor sessions."""

    def test_dark_mode_persists(self, temp_prefs_dir):
        """Test that changing dark mode persists the preference."""
        from figrecipe._editor._preferences import get_preference, set_preference

        prefs_dir, prefs_file = temp_prefs_dir

        with (
            patch("figrecipe._editor._preferences.PREFERENCES_FILE", prefs_file),
            patch("figrecipe._editor._preferences.PREFERENCES_DIR", prefs_dir),
        ):
            # Initially False
            assert get_preference("dark_mode", False) is False

            # Set to True
            set_preference("dark_mode", True)

            # Verify it persists
            assert get_preference("dark_mode", False) is True

            # File should contain the setting
            with open(prefs_file) as f:
                data = json.load(f)
            assert data["dark_mode"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
