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
        s.add_arrow("a", "b")
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


class TestAutoHeight:
    """Test auto-height feature (height_mm=None)."""

    def test_auto_box_height_rounded(self):
        """Test auto-height for rounded box with title+subtitle+content."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box(
            "a",
            title="A",
            subtitle="Sub",
            content=["line1", "line2"],
            x_mm=90,
            y_mm=50,
            width_mm=40,
        )
        assert "a" in s._positions
        pos = s._positions["a"]
        # title(6) + subtitle(5) + 2*content(10) + 2*padding(10) = 31
        assert pos.height_mm == 31.0

    def test_auto_box_height_codeblock(self):
        """Test auto-height for codeblock shape."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box(
            "code",
            title="script.py",
            shape="codeblock",
            content=["import foo", "foo.bar()", "print('done')"],
            x_mm=90,
            y_mm=50,
            width_mm=60,
        )
        assert "code" in s._positions
        pos = s._positions["code"]
        # title_bar(6) + 3*3.5(10.5) + 2*padding(10) = 26.5 (codeblock unchanged)
        assert pos.height_mm == 26.5

    def test_auto_box_height_minimum(self):
        """Test auto-height minimum of 18mm for small boxes."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("tiny", title="T", x_mm=90, y_mm=50, width_mm=40)
        pos = s._positions["tiny"]
        # title(6) + 0 content + 2*padding(10) = 16 → clamped to 18
        assert pos.height_mm == 18.0

    def test_auto_canvas_height(self):
        """Test Schematic(height_mm=None) computes canvas from elements."""
        s = fr.Schematic(title="Auto", width_mm=100, height_mm=None)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=20)
        s.add_box("b", title="B", x_mm=50, y_mm=20, width_mm=40, height_mm=20)
        s._finalize_canvas_size()
        # Elements span from y=10 (20-10) to y=60 (50+10) = 50mm
        # + title_space(12) + 2*margin(16) = 78mm
        assert s.height_mm == 78.0
        assert s.ylim[0] == 2.0  # min_bottom(10) - margin(8)
        assert s.ylim[1] == 80.0  # max_top(60) + title_space(12) + margin(8)

    def test_auto_canvas_height_no_title(self):
        """Test auto-canvas without title."""
        s = fr.Schematic(width_mm=100, height_mm=None)
        s.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=20)
        s._finalize_canvas_size()
        # span: 40-60 = 20mm; no title; + 2*margin(16) = 36mm
        assert s.height_mm == 36.0

    def test_auto_canvas_renders(self):
        """Test that auto-canvas can render without error."""
        s = fr.Schematic(title="Auto Render", width_mm=100, height_mm=None)
        s.add_box("a", title="A", x_mm=30, y_mm=50, width_mm=30, height_mm=20)
        s.add_box("b", title="B", x_mm=70, y_mm=50, width_mm=30, height_mm=20)
        s.add_arrow("a", "b")
        fig, ax = s.render()
        assert fig is not None
        assert s.height_mm > 0

    def test_explicit_height_unchanged(self):
        """Test that explicit height_mm is not modified."""
        s = fr.Schematic(width_mm=100, height_mm=200)
        s.add_box("a", title="A", x_mm=50, y_mm=100, width_mm=40, height_mm=25)
        s._finalize_canvas_size()
        assert s.height_mm == 200
        assert s.ylim == (0, 200)

    def test_explicit_box_height_unchanged(self):
        """Test that explicit box height_mm is not overridden."""
        s = fr.Schematic(width_mm=180, height_mm=100)
        s.add_box("a", title="A", x_mm=90, y_mm=50, width_mm=40, height_mm=30)
        assert s._positions["a"].height_mm == 30


class TestFlexLayout:
    """Tests for CSS flexbox-like layout (gap_mm on Schematic)."""

    def test_flex_basic_stacking(self):
        """Three boxes stacked vertically with gap_mm=10."""
        s = fr.Schematic(width_mm=100, gap_mm=10, padding_mm=5)
        s.add_box("a", "A", width_mm=40)
        s.add_box("b", "B", width_mm=40)
        s.add_box("c", "C", width_mm=40)
        s._finalize_canvas_size()
        pa, pb, pc = s._positions["a"], s._positions["b"], s._positions["c"]
        # All centered horizontally
        assert pa.x_mm == pb.x_mm == pc.x_mm == 50.0
        # Stacked top-to-bottom: a on top, c on bottom
        assert pa.y_mm > pb.y_mm > pc.y_mm
        # Uniform gap between adjacent boxes
        gap_ab = (pa.y_mm - pa.height_mm / 2) - (pb.y_mm + pb.height_mm / 2)
        gap_bc = (pb.y_mm - pb.height_mm / 2) - (pc.y_mm + pc.height_mm / 2)
        assert abs(gap_ab - 10.0) < 0.1
        assert abs(gap_bc - 10.0) < 0.1

    def test_flex_container_row(self):
        """Container with direction='row' places children horizontally."""
        s = fr.Schematic(width_mm=120, gap_mm=15)
        s.add_container(
            "c",
            title="Group",
            children=["x", "y"],
            direction="row",
            container_gap_mm=6,
            container_padding_mm=6,
        )
        s.add_box("x", "X", width_mm=30)
        s.add_box("y", "Y", width_mm=30)
        s._finalize_canvas_size()
        px, py = s._positions["x"], s._positions["y"]
        # Children side by side: x on left, y on right
        assert px.x_mm < py.x_mm
        # Same y (horizontal row)
        assert abs(px.y_mm - py.y_mm) < 0.1

    def test_flex_container_column(self):
        """Container with direction='column' stacks children vertically."""
        s = fr.Schematic(width_mm=120, gap_mm=15)
        s.add_container(
            "c",
            title="Stack",
            children=["x", "y"],
            direction="column",
            container_gap_mm=6,
            container_padding_mm=6,
        )
        s.add_box("x", "X", width_mm=40)
        s.add_box("y", "Y", width_mm=40)
        s._finalize_canvas_size()
        px, py = s._positions["x"], s._positions["y"]
        # Stacked: x on top, y below
        assert px.y_mm > py.y_mm
        # Same x (centered column)
        assert abs(px.x_mm - py.x_mm) < 0.1

    def test_flex_auto_container_size(self):
        """Container size computed from children."""
        s = fr.Schematic(width_mm=120, gap_mm=15)
        s.add_container(
            "c",
            children=["a", "b"],
            direction="row",
            container_gap_mm=8,
            container_padding_mm=10,
        )
        s.add_box("a", "A", width_mm=30)
        s.add_box("b", "B", width_mm=30)
        s._finalize_canvas_size()
        pc = s._positions["c"]
        # width = 30 + 30 + 8 (gap) + 20 (2*pad) = 88
        assert abs(pc.width_mm - 88.0) < 0.1
        # height = max(child_h) + title_h(0) + 2*pad(20)
        child_h = s._positions["a"].height_mm
        assert abs(pc.height_mm - (child_h + 20.0)) < 0.1

    def test_flex_renders(self):
        """Full flex diagram renders without error."""
        s = fr.Schematic(title="Flex Test", width_mm=120, gap_mm=18, padding_mm=10)
        s.add_box("top", "Top Box", width_mm=80)
        s.add_container(
            "mid",
            title="Middle",
            children=["a", "b"],
            direction="row",
            container_gap_mm=8,
        )
        s.add_box("a", "A", subtitle="Left", width_mm=35)
        s.add_box("b", "B", subtitle="Right", width_mm=35)
        s.add_box("bot", "Bottom", width_mm=60)
        s.add_arrow("top", "mid")
        s.add_arrow("mid", "bot")
        fig, ax = s.render()
        assert fig is not None
        assert s.height_mm > 0

    def test_flex_explicit_width_override(self):
        """Container explicit width_mm overrides auto-computed width."""
        s = fr.Schematic(width_mm=120, gap_mm=10)
        s.add_container("c", children=["a"], width_mm=100, container_padding_mm=5)
        s.add_box("a", "A", width_mm=30)
        s._finalize_canvas_size()
        assert s._positions["c"].width_mm == 100.0

    def test_flex_forces_auto_height(self):
        """gap_mm forces auto-height even if height_mm was given."""
        s = fr.Schematic(width_mm=100, height_mm=200, gap_mm=10)
        assert s._auto_height is True

    def test_flex_nested_containers_3x2_grid(self):
        """Nested containers: 2 row containers forming a 3x2 grid."""
        s = fr.Schematic(width_mm=120, gap_mm=10, padding_mm=5)
        s.add_container(
            "row1",
            direction="row",
            children=["a", "b", "c"],
            container_gap_mm=6,
            container_padding_mm=4,
        )
        s.add_container(
            "row2",
            direction="row",
            children=["d", "e", "f"],
            container_gap_mm=6,
            container_padding_mm=4,
        )
        for name in ["a", "b", "c", "d", "e", "f"]:
            s.add_box(name, name.upper(), width_mm=30)
        s._finalize_canvas_size()
        # Row1 above row2
        assert s._positions["row1"].y_mm > s._positions["row2"].y_mm
        # Within row1: a < b < c horizontally
        assert s._positions["a"].x_mm < s._positions["b"].x_mm < s._positions["c"].x_mm
        # Within row2: d < e < f horizontally
        assert s._positions["d"].x_mm < s._positions["e"].x_mm < s._positions["f"].x_mm
        # Same y within each row
        assert abs(s._positions["a"].y_mm - s._positions["c"].y_mm) < 0.1
        assert abs(s._positions["d"].y_mm - s._positions["f"].y_mm) < 0.1

    def test_flex_deeply_nested_container(self):
        """Container within container: outer column contains inner row."""
        s = fr.Schematic(width_mm=120, gap_mm=10, padding_mm=5)
        s.add_container(
            "outer",
            direction="column",
            children=["header", "inner"],
            container_gap_mm=6,
            container_padding_mm=4,
        )
        s.add_box("header", "Header", width_mm=60)
        s.add_container(
            "inner",
            direction="row",
            children=["x", "y"],
            container_gap_mm=4,
            container_padding_mm=4,
        )
        s.add_box("x", "X", width_mm=30)
        s.add_box("y", "Y", width_mm=30)
        s._finalize_canvas_size()
        # Outer contains both header and inner
        assert "outer" in s._positions
        assert "inner" in s._positions
        # Header above inner row
        assert s._positions["header"].y_mm > s._positions["inner"].y_mm
        # x left of y within inner
        assert s._positions["x"].x_mm < s._positions["y"].x_mm


# EOF
