#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for branding module."""

import os
from unittest.mock import patch

import pytest


class TestRebrandText:
    """Tests for rebrand_text function."""

    def test_no_branding_returns_unchanged(self):
        """When env vars are default, text is unchanged."""

        text = "import figrecipe as fr"
        # With default branding, should return unchanged
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "figrecipe", "FIGRECIPE_ALIAS": "fr"},
            clear=False,
        ):
            # Need to reimport to pick up env vars
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)
            result = branding.rebrand_text(text)
            assert result == text

    def test_rebrand_import_statement(self):
        """Test rebranding of import statement."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            text = "import figrecipe as fr"
            result = branding.rebrand_text(text)
            assert result == "import scitex.plt as plt"

    def test_rebrand_variable_usage(self):
        """Test rebranding of variable usage in examples."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            text = ">>> fr.subplots()"
            result = branding.rebrand_text(text)
            assert result == ">>> plt.subplots()"

    def test_rebrand_from_import(self):
        """Test rebranding of from...import statement."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            text = "from figrecipe import utils"
            result = branding.rebrand_text(text)
            assert result == "from scitex.plt import utils"

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        from figrecipe._branding import rebrand_text

        assert rebrand_text(None) is None

    def test_preserves_urls(self):
        """Test that URLs containing figrecipe are not mangled."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            text = "https://github.com/user/figrecipe"
            result = branding.rebrand_text(text)
            # URL should be preserved
            assert "github.com" in result


class TestGetBrandedImportExample:
    """Tests for get_branded_import_example function."""

    def test_default_import(self):
        """Test default import example."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "figrecipe", "FIGRECIPE_ALIAS": "fr"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            result = branding.get_branded_import_example()
            assert result == "import figrecipe as fr"

    def test_submodule_import(self):
        """Test submodule import example."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            result = branding.get_branded_import_example()
            assert result == "from scitex import plt as plt"


class TestGetMcpServerName:
    """Tests for get_mcp_server_name function."""

    def test_default_name(self):
        """Test default MCP server name."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "figrecipe", "FIGRECIPE_ALIAS": "fr"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            result = branding.get_mcp_server_name()
            assert result == "figrecipe"

    def test_submodule_name_converts_dots(self):
        """Test that dots are converted to dashes in MCP name."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            result = branding.get_mcp_server_name()
            assert result == "scitex-plt"


class TestGetMcpInstructions:
    """Tests for get_mcp_instructions function."""

    def test_instructions_contain_brand_name(self):
        """Test that instructions contain the brand name."""
        with patch.dict(
            os.environ,
            {"FIGRECIPE_BRAND": "scitex.plt", "FIGRECIPE_ALIAS": "plt"},
            clear=False,
        ):
            import importlib

            import figrecipe._branding as branding

            importlib.reload(branding)

            result = branding.get_mcp_instructions()
            assert "scitex.plt" in result
            assert "MCP server" in result


# Cleanup: restore default branding after tests
@pytest.fixture(autouse=True)
def restore_default_branding():
    """Restore default branding after each test."""
    yield
    # Restore defaults
    with patch.dict(
        os.environ,
        {"FIGRECIPE_BRAND": "figrecipe", "FIGRECIPE_ALIAS": "fr"},
        clear=False,
    ):
        import importlib

        import figrecipe._branding as branding

        importlib.reload(branding)


# EOF
