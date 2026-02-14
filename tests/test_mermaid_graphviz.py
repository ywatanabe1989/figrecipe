#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for figrecipe.Mermaid and figrecipe.Graphviz wrappers."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import figrecipe as fr
from figrecipe import Graphviz, Mermaid


class TestMermaidClass:
    """Test Mermaid wrapper class."""

    def test_import_from_figrecipe(self):
        assert hasattr(fr, "Mermaid")

    def test_instantiation(self):
        m = Mermaid("graph TD; A-->B;")
        assert m.code == "graph TD; A-->B;"

    def test_strips_whitespace(self):
        m = Mermaid("  graph TD; A-->B;  \n")
        assert m.code == "graph TD; A-->B;"

    def test_repr(self):
        m = Mermaid("graph TD; A-->B;")
        assert "Mermaid(" in repr(m)
        assert "chars)" in repr(m)

    def test_is_available_returns_bool(self):
        result = Mermaid.is_available()
        assert isinstance(result, bool)

    def test_render_mermaid_cli(self):
        if not Mermaid.is_available():
            pytest.skip("mmdc not installed")
        m = Mermaid("graph TD; A-->B;")
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test.png"
            result = m.render(out, backend="mermaid-cli")
            assert result.exists()

    def test_render_mermaid_ink(self):
        import urllib.error

        m = Mermaid("graph TD; A-->B;")
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test.png"
            try:
                result = m.render(out, backend="mermaid.ink")
                assert result.exists()
            except urllib.error.URLError:
                pytest.skip("mermaid.ink API unavailable")

    def test_render_unknown_backend_raises(self):
        m = Mermaid("graph TD; A-->B;")
        with pytest.raises(ValueError, match="Unknown backend"):
            m.render("/tmp/test.png", backend="nonexistent")

    def test_render_pdf_mermaid_ink_raises(self):
        m = Mermaid("graph TD; A-->B;")
        with pytest.raises(ValueError, match="PDF"):
            m.render("/tmp/test.pdf", format="pdf", backend="mermaid.ink")

    @patch("figrecipe.mermaid._check_mermaid_cli", return_value=False)
    def test_render_mermaid_cli_not_found(self, _mock):
        m = Mermaid("graph TD; A-->B;")
        with pytest.raises(RuntimeError, match="mmdc"):
            m.render("/tmp/test.png", backend="mermaid-cli")

    @patch("figrecipe.mermaid._check_mermaid_cli", return_value=False)
    def test_auto_fallback_warns(self, _mock):
        """Auto backend warns when falling back to mermaid.ink."""
        import urllib.error

        m = Mermaid("graph TD; A-->B;")
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test.png"
            try:
                with pytest.warns(UserWarning, match="mermaid.ink"):
                    m.render(out, backend="auto")
            except urllib.error.URLError:
                pytest.skip("mermaid.ink API unavailable")


class TestGraphvizClass:
    """Test Graphviz wrapper class."""

    def test_import_from_figrecipe(self):
        assert hasattr(fr, "Graphviz")

    def test_instantiation(self):
        g = Graphviz("digraph { A -> B }")
        assert g.code == "digraph { A -> B }"

    def test_strips_whitespace(self):
        g = Graphviz("  digraph { A -> B }  \n")
        assert g.code == "digraph { A -> B }"

    def test_repr(self):
        g = Graphviz("digraph { A -> B }")
        assert "Graphviz(" in repr(g)
        assert "chars)" in repr(g)

    def test_is_available_returns_bool(self):
        result = Graphviz.is_available()
        assert isinstance(result, bool)

    def test_render(self):
        if not Graphviz.is_available():
            pytest.skip("graphviz (dot) not installed")
        g = Graphviz("digraph { A -> B }")
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test.png"
            result = g.render(out)
            assert result.exists()

    def test_render_svg(self):
        if not Graphviz.is_available():
            pytest.skip("graphviz (dot) not installed")
        g = Graphviz("digraph { A -> B }")
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test.svg"
            result = g.render(out, format="svg")
            assert result.exists()
            content = result.read_text()
            assert "<svg" in content

    @patch("figrecipe.graphviz._check_graphviz", return_value=False)
    def test_render_not_found(self, _mock):
        g = Graphviz("digraph { A -> B }")
        with pytest.raises(RuntimeError, match="dot"):
            g.render("/tmp/test.png")


class TestAllExports:
    """Test __all__ exports."""

    def test_mermaid_in_all(self):
        assert "Mermaid" in fr.__all__

    def test_graphviz_in_all(self):
        assert "Graphviz" in fr.__all__
