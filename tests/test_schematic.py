#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-02 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/tests/test_schematic.py

"""Tests for Schematic API."""

import tempfile
from pathlib import Path

import figrecipe as fr


class TestSchematicCreation:
    """Test Schematic creation."""

    def test_create_empty_schematic(self):
        """Test creating an empty schematic."""
        s = fr.Schematic()
        assert s is not None
        assert s.title is None
        assert len(s._boxes) == 0

    def test_create_with_title(self):
        """Test creating schematic with title."""
        s = fr.Schematic(title="Test Diagram")
        assert s.title == "Test Diagram"

    def test_create_with_mm_dimensions(self):
        """Test creating schematic with mm dimensions."""
        s = fr.Schematic(width_mm=300.0, height_mm=200.0)
        assert s.width_mm == 300.0
        assert s.height_mm == 200.0
        assert s.xlim == (0, 300.0)
        assert s.ylim == (0, 200.0)

    def test_add_box(self):
        """Test adding boxes."""
        s = fr.Schematic()
        s.add_box("a", title="Box A")
        s.add_box("b", title="Box B", subtitle="With subtitle")
        assert len(s._boxes) == 2
        assert s._boxes["a"].title == "Box A"
        assert s._boxes["b"].subtitle == "With subtitle"

    def test_add_arrow(self):
        """Test adding arrows."""
        s = fr.Schematic()
        s.add_box("a", title="A")
        s.add_box("b", title="B")
        s.add_arrow("a", "b", label="connects")
        assert len(s._arrows) == 1
        assert s._arrows[0].source == "a"
        assert s._arrows[0].target == "b"


class TestAutoLayout:
    """Test auto_layout functionality."""

    def test_auto_layout_lr(self):
        """Test left-to-right layout."""
        s = fr.Schematic(width_mm=200, height_mm=100)
        s.add_box("a", title="A")
        s.add_box("b", title="B")
        s.add_arrow("a", "b")
        s.auto_layout("lr")
        assert "a" in s._positions
        assert "b" in s._positions
        assert s._positions["a"].x_mm < s._positions["b"].x_mm

    def test_auto_layout_tb(self):
        """Test top-to-bottom layout."""
        s = fr.Schematic(width_mm=200, height_mm=100)
        s.add_box("a", title="A")
        s.add_box("b", title="B")
        s.add_arrow("a", "b")
        s.auto_layout("tb")
        assert s._positions["a"].y_mm > s._positions["b"].y_mm

    def test_auto_layout_aliases(self):
        """Test layout name aliases."""
        s = fr.Schematic()
        s.add_box("a", title="A")
        s.add_box("b", title="B")

        # All these should work
        for layout in ["lr", "left-to-right", "tb", "top-to-bottom"]:
            s.auto_layout(layout)
            assert len(s._positions) == 2


class TestRender:
    """Test rendering."""

    def test_render_returns_fig_ax(self):
        """Test that render returns figure and axes."""
        s = fr.Schematic()
        s.add_box("a", title="A", position_mm=(50, 50), size_mm=(40, 25))
        fig, ax = s.render()
        assert fig is not None
        assert ax is not None

    def test_render_to_file(self):
        """Test rendering to file."""
        s = fr.Schematic()
        s.add_box("a", title="A", position_mm=(50, 50), size_mm=(40, 25))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.png"
            result = s.render_to_file(path)
            assert result.exists()


class TestSerialization:
    """Test serialization and reproduction."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        s = fr.Schematic(title="Test")
        s.add_box("a", title="A", position_mm=(50, 50), size_mm=(40, 25))
        data = s.to_dict()
        assert "title" in data
        assert "boxes" in data
        assert data["title"] == "Test"
        assert "width_mm" in data
        assert "height_mm" in data

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "title": "Test",
            "width_mm": 200.0,
            "height_mm": 120.0,
            "boxes": [{"id": "a", "title": "A", "emphasis": "normal"}],
            "arrows": [],
            "containers": [],
            "positions": {
                "a": {"x_mm": 100, "y_mm": 60, "width_mm": 40, "height_mm": 25}
            },
        }
        s = fr.Schematic.from_dict(data)
        assert s.title == "Test"
        assert "a" in s._boxes
        assert s._positions["a"].x_mm == 100

    def test_roundtrip(self):
        """Test serialization roundtrip."""
        s = fr.Schematic(title="Roundtrip", width_mm=250.0, height_mm=150.0)
        s.add_box("a", title="A", position_mm=(100, 75), size_mm=(40, 25))
        s.add_box("b", title="B", position_mm=(200, 75), size_mm=(40, 25))
        s.add_arrow("a", "b")

        data = s.to_dict()
        s2 = fr.Schematic.from_dict(data)
        assert s2.width_mm == 250.0
        assert s2.height_mm == 150.0
        assert s2._positions["a"].x_mm == 100
        assert s2._positions["b"].x_mm == 200


class TestRecipeIntegration:
    """Test FigRecipe integration."""

    def test_ax_schematic_method(self):
        """Test ax.schematic() method."""
        s = fr.Schematic()
        s.add_box("a", title="A")
        s.auto_layout("lr")

        fig, ax = fr.subplots()
        ax.schematic(s, id="test_schematic")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.png"
            fr.save(fig, path)
            assert path.exists()
            assert path.with_suffix(".yaml").exists()


# EOF
