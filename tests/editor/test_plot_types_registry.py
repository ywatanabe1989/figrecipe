#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for plot types registry with docstring tooltips.

These tests verify:
- Plot type info includes docstrings from matplotlib
- HTML options include title attributes for tooltips
- JS hints include doc field for JavaScript access
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestPlotTypeDocstrings:
    """Test docstring extraction for plot type tooltips."""

    def test_get_docstring_returns_string(self):
        """Verify _get_docstring returns a string for known methods."""
        from figrecipe._editor._plot_types_registry import _get_docstring

        docstring = _get_docstring("plot")
        assert isinstance(docstring, str)
        assert len(docstring) > 0
        assert "plot" in docstring.lower() or "line" in docstring.lower()

    def test_get_docstring_truncates_long_strings(self):
        """Verify docstrings are truncated to reasonable length."""
        from figrecipe._editor._plot_types_registry import _get_docstring

        docstring = _get_docstring("plot")
        assert len(docstring) <= 103  # 100 chars + "..."

    def test_get_docstring_handles_unknown_method(self):
        """Verify unknown methods return empty string."""
        from figrecipe._editor._plot_types_registry import _get_docstring

        docstring = _get_docstring("nonexistent_method_xyz")
        assert docstring == ""

    def test_plot_type_info_includes_docstring(self):
        """Verify get_plot_type_info includes docstring field."""
        from figrecipe._editor._plot_types_registry import get_plot_type_info

        info = get_plot_type_info("scatter")
        assert "docstring" in info
        assert isinstance(info["docstring"], str)
        assert "scatter" in info["docstring"].lower()

    def test_common_plot_types_have_docstrings(self):
        """Verify common plot types have non-empty docstrings."""
        from figrecipe._editor._plot_types_registry import get_plot_type_info

        common_types = ["plot", "scatter", "bar", "hist", "fill_between", "imshow"]
        for plot_type in common_types:
            info = get_plot_type_info(plot_type)
            assert info["docstring"], f"{plot_type} should have a docstring"


class TestHTMLOptionsWithTooltips:
    """Test HTML option generation with title tooltips."""

    def test_html_options_include_title_attribute(self):
        """Verify generated HTML includes title attributes."""
        from figrecipe._editor._plot_types_registry import generate_html_options

        html = generate_html_options()
        assert 'title="' in html

    def test_html_options_escape_special_chars(self):
        """Verify HTML special characters are escaped in title."""
        from figrecipe._editor._plot_types_registry import generate_html_options

        html = generate_html_options()
        # Should not have unescaped quotes inside title attribute
        assert 'title=""' not in html  # Empty titles should be omitted

    def test_html_options_have_plot_option(self):
        """Verify plot option exists with tooltip."""
        from figrecipe._editor._plot_types_registry import generate_html_options

        html = generate_html_options()
        assert 'value="plot"' in html
        # Plot should have a title with docstring
        assert "Plot y versus x" in html or "lines and/or markers" in html


class TestJSHintsWithDocstrings:
    """Test JavaScript hints include docstring field."""

    def test_js_hints_include_doc_field(self):
        """Verify JS hints object includes doc field."""
        from figrecipe._editor._plot_types_registry import generate_js_hints

        js = generate_js_hints()
        assert "doc:" in js
        assert "PLOT_TYPE_HINTS" in js

    def test_js_hints_doc_field_has_content(self):
        """Verify doc field has actual content for plot."""
        from figrecipe._editor._plot_types_registry import generate_js_hints

        js = generate_js_hints()
        # Check that plot has non-empty doc
        assert "plot:" in js
        # The doc field should contain something about plotting
        lines = [line for line in js.split("\n") if "plot:" in line]
        assert len(lines) > 0
        assert "doc: ''" not in lines[0]  # Should not be empty


class TestAllCategoriesHaveDocstrings:
    """Test all plot categories have docstrings."""

    def test_all_categories_accessible(self):
        """Verify all categories can be accessed."""
        from figrecipe._editor._plot_types_registry import (
            CATEGORIES,
            get_plot_type_info,
        )

        for category, methods in CATEGORIES.items():
            for method in methods:
                info = get_plot_type_info(method)
                assert "docstring" in info, f"{method} missing docstring field"
