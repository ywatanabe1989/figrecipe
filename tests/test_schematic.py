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
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A")
        s.add_box("b", title="B")
        s.add_arrow("a", "b")
        s.auto_layout("lr")
        assert "a" in s._positions
        assert "b" in s._positions
        assert s._positions["a"].x_mm < s._positions["b"].x_mm

    def test_auto_layout_tb(self):
        """Test top-to-bottom layout."""
        s = fr.Schematic(width_mm=180, height_mm=100)
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
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        fig, ax = s.render()
        assert fig is not None
        assert ax is not None

    def test_render_to_file(self):
        """Test rendering to file."""
        s = fr.Schematic()
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.png"
            result = s.render_to_file(path)
            assert result.exists()


class TestSerialization:
    """Test serialization and reproduction."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        s = fr.Schematic(title="Test")
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
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
        s.add_box("a", title="A", x_mm=100, y_mm=75, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=200, y_mm=75, width_mm=40, height_mm=25)
        s.add_arrow("a", "b")

        data = s.to_dict()
        s2 = fr.Schematic.from_dict(data)
        assert s2.width_mm == 250.0
        assert s2.height_mm == 150.0
        assert s2._positions["a"].x_mm == 100
        assert s2._positions["b"].x_mm == 200


class TestContainerValidation:
    """Test container validation."""

    def test_valid_container_passes(self):
        """Test that properly contained children pass validation."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_container(
            "c",
            title="Container",
            children=["a"],
            x_mm=100,
            y_mm=50,
            width_mm=100,
            height_mm=60,
        )
        s.add_box("a", title="A", x_mm=100, y_mm=50, width_mm=40, height_mm=25)
        s.validate_containers()  # Should not raise

    def test_child_outside_container_raises(self):
        """Test that child outside container raises ValueError."""
        import pytest

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_container(
            "c",
            title="Container",
            children=["a"],
            x_mm=100,
            y_mm=50,
            width_mm=40,
            height_mm=30,
        )
        s.add_box("a", title="A", x_mm=200, y_mm=50, width_mm=40, height_mm=25)
        with pytest.raises(ValueError, match="extends outside container"):
            s.validate_containers()

    def test_render_validates_containers(self):
        """Test that render() calls validation automatically."""
        import pytest

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_container(
            "c",
            title="Container",
            children=["a"],
            x_mm=100,
            y_mm=50,
            width_mm=40,
            height_mm=30,
        )
        s.add_box("a", title="A", x_mm=200, y_mm=50, width_mm=40, height_mm=25)
        with pytest.raises(ValueError, match="extends outside container"):
            s.render()


class TestBoxOverlapValidation:
    """Test box overlap detection."""

    def test_non_overlapping_boxes_pass(self):
        """Test that separated boxes pass validation."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=150, y_mm=50, width_mm=40, height_mm=25)
        s.validate_no_overlap()  # Should not raise

    def test_overlapping_boxes_raises(self):
        """Test that overlapping boxes raise ValueError."""
        import pytest

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=55, y_mm=50, width_mm=40, height_mm=25)
        with pytest.raises(ValueError, match="overlap"):
            s.validate_no_overlap()

    def test_render_detects_overlap(self):
        """Test that render() catches box overlap."""
        import pytest

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=55, y_mm=50, width_mm=40, height_mm=25)
        with pytest.raises(ValueError, match="overlap"):
            s.render()


class TestTextOverlapValidation:
    """Test text bounding box overlap detection."""

    def test_non_overlapping_text_no_warning(self):
        """Test that separated text produces no warning."""
        import warnings

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=40, y_mm=50, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=140, y_mm=50, width_mm=40, height_mm=25)
        s.add_arrow("a", "b", label="arrow")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            s.render()  # owns_fig=True, text validation runs
        overlap_warns = [x for x in w if "Text overlap" in str(x.message)]
        assert len(overlap_warns) == 0

    def test_overlapping_text_raises(self):
        """Test that overlapping arrow labels raise ValueError."""
        import pytest

        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        s.add_box("b", title="B", x_mm=150, y_mm=50, width_mm=40, height_mm=25)
        s.add_arrow("a", "b", label="forward")
        s.add_arrow("b", "a", label="backward")
        with pytest.raises(ValueError, match="Text margin violation"):
            s.render()


class TestArrowBoxOcclusion:
    """Test R7: arrow-through-box occlusion detection."""

    def test_arrow_through_intermediate_box_raises(self):
        """Arrow passing through an intermediate box triggers R7."""
        import pytest

        s = fr.Schematic(width_mm=100, height_mm=80)
        s.add_box("top", "Top", x_mm=50, y_mm=65, width_mm=20, height_mm=10)
        s.add_box("mid", "Mid", x_mm=50, y_mm=40, width_mm=20, height_mm=10)
        s.add_box("bot", "Bot", x_mm=50, y_mm=15, width_mm=20, height_mm=10)
        s.add_arrow("top", "bot")
        with pytest.raises(ValueError, match="visibility"):
            s.render()

    def test_no_intermediate_box_passes(self):
        """Arrow between two boxes with nothing between passes R7."""
        s = fr.Schematic(width_mm=100, height_mm=80)
        s.add_box("a", "A", x_mm=25, y_mm=40, width_mm=20, height_mm=10)
        s.add_box("b", "B", x_mm=75, y_mm=40, width_mm=20, height_mm=10)
        s.add_arrow("a", "b")
        s.render()  # Should not raise

    def test_source_target_boxes_not_counted(self):
        """Arrow's own source/target boxes are excluded from occlusion."""
        s = fr.Schematic(width_mm=100, height_mm=60)
        s.add_box("a", "A", x_mm=25, y_mm=30, width_mm=20, height_mm=15)
        s.add_box("b", "B", x_mm=75, y_mm=30, width_mm=20, height_mm=15)
        s.add_arrow("a", "b")
        s.render()  # Should not raise — source/target excluded


class TestGeomHelpers:
    """Test geometry helper functions."""

    def test_seg_rect_clip_len_through(self):
        """Segment fully inside rect returns correct clipped length."""
        from figrecipe._schematic._schematic_geom import seg_rect_clip_len

        # Horizontal segment y=5, from x=0 to x=10, box [2,0,8,10]
        clip = seg_rect_clip_len(0, 5, 10, 5, 2, 0, 8, 10)
        assert abs(clip - 6.0) < 0.01  # clipped from x=2 to x=8

    def test_seg_rect_clip_len_miss(self):
        """Segment missing rect returns 0."""
        from figrecipe._schematic._schematic_geom import seg_rect_clip_len

        clip = seg_rect_clip_len(0, 20, 10, 20, 0, 0, 10, 10)
        assert clip == 0.0  # segment at y=20, box only up to y=10

    def test_seg_rect_clip_len_diagonal(self):
        """Diagonal segment partially inside rect."""
        import math

        from figrecipe._schematic._schematic_geom import seg_rect_clip_len

        # Diagonal from (0,0) to (10,10), box [3,3,7,7]
        clip = seg_rect_clip_len(0, 0, 10, 10, 3, 3, 7, 7)
        expected = math.hypot(4, 4)  # from (3,3) to (7,7)
        assert abs(clip - expected) < 0.01


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
