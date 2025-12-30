#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for theme-aware datatable styling.

These tests verify:
- Variable assignment dropdowns have theme-aware styling
- Toolbar dropdowns have theme-aware styling
- CSS uses CSS variables for theming
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestVarAssignThemeAware:
    """Test variable assignment dropdown theme-aware styling."""

    def test_var_slot_select_uses_css_variables(self):
        """Verify var-assign select uses CSS variables for theming."""
        from figrecipe._editor._templates._styles._datatable._vars import (
            CSS_DATATABLE_VARS,
        )

        # Should use theme variables for background
        assert "var(--bg-secondary)" in CSS_DATATABLE_VARS
        assert "var(--text-primary)" in CSS_DATATABLE_VARS

    def test_var_slot_select_option_styled(self):
        """Verify select option elements have theme-aware styling."""
        from figrecipe._editor._templates._styles._datatable._vars import (
            CSS_DATATABLE_VARS,
        )

        # Should have option styling
        assert "select option" in CSS_DATATABLE_VARS
        assert (
            "option:checked" in CSS_DATATABLE_VARS
            or "option:hover" in CSS_DATATABLE_VARS
        )

    def test_var_slot_select_has_background(self):
        """Verify select has explicit background (not transparent for theme)."""
        from figrecipe._editor._templates._styles._datatable._vars import (
            CSS_DATATABLE_VARS,
        )

        # The select should have a background color using CSS variable
        assert ".var-assign-slot select" in CSS_DATATABLE_VARS
        # Check that background is set (could be secondary or tertiary)
        assert "background:" in CSS_DATATABLE_VARS


class TestToolbarThemeAware:
    """Test toolbar dropdown theme-aware styling."""

    def test_toolbar_select_uses_css_variables(self):
        """Verify toolbar select uses CSS variables."""
        from figrecipe._editor._templates._styles._datatable._toolbar import (
            CSS_DATATABLE_TOOLBAR,
        )

        assert "var(--bg-primary)" in CSS_DATATABLE_TOOLBAR
        assert "var(--text-primary)" in CSS_DATATABLE_TOOLBAR

    def test_toolbar_select_option_styled(self):
        """Verify toolbar select options have theme styling."""
        from figrecipe._editor._templates._styles._datatable._toolbar import (
            CSS_DATATABLE_TOOLBAR,
        )

        # Should have option styling for toolbar selects
        assert "select option" in CSS_DATATABLE_TOOLBAR

    def test_plot_type_select_option_styled(self):
        """Verify plot-type-select options have theme styling."""
        from figrecipe._editor._templates._styles._datatable._toolbar import (
            CSS_DATATABLE_TOOLBAR,
        )

        assert ".plot-type-select" in CSS_DATATABLE_TOOLBAR


class TestBaseThemeVariables:
    """Test base theme CSS variables are defined."""

    def test_light_mode_variables_defined(self):
        """Verify light mode CSS variables are defined in :root."""
        from figrecipe._editor._templates._styles._base import STYLES_BASE

        assert ":root" in STYLES_BASE
        assert "--bg-primary" in STYLES_BASE
        assert "--bg-secondary" in STYLES_BASE
        assert "--text-primary" in STYLES_BASE

    def test_dark_mode_variables_defined(self):
        """Verify dark mode CSS variables are defined."""
        from figrecipe._editor._templates._styles._base import STYLES_BASE

        assert '[data-theme="dark"]' in STYLES_BASE
        # Dark mode should override the same variables
        assert "--bg-primary:" in STYLES_BASE


class TestCombinedStylesIncludeThemeAware:
    """Test combined styles include all theme-aware components."""

    def test_combined_styles_include_vars(self):
        """Verify combined styles include var assignment styles."""
        from figrecipe._editor._templates._styles import STYLES

        assert "var-assign-slot" in STYLES

    def test_combined_styles_include_toolbar(self):
        """Verify combined styles include toolbar styles."""
        from figrecipe._editor._templates._styles import STYLES

        assert "datatable-toolbar" in STYLES
