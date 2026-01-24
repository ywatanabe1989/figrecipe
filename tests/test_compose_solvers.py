#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for layout solvers.

These tests verify that solvers correctly convert list sources to mm specs.
"""

import matplotlib

matplotlib.use("Agg")

import pytest
from PIL import Image

from figrecipe._api._compose._solvers import (
    LAYOUT_SOLVERS,
    solve_grid,
    solve_horizontal,
    solve_layout,
    solve_vertical,
)


class TestSolveHorizontal:
    """Tests for horizontal layout solver."""

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create source image files."""
        img1 = Image.new("RGBA", (200, 150), (255, 0, 0, 255))
        img1_path = tmp_path / "img1.png"
        img1.save(img1_path)

        img2 = Image.new("RGBA", (300, 150), (0, 255, 0, 255))
        img2_path = tmp_path / "img2.png"
        img2.save(img2_path)

        return str(img1_path), str(img2_path)

    def test_horizontal_basic(self, source_images):
        """Horizontal solver produces correct mm positions."""
        img1, img2 = source_images
        sources_mm, canvas_size_mm = solve_horizontal([img1, img2], gap_mm=5.0, dpi=300)

        # Should have two sources
        assert len(sources_mm) == 2
        assert img1 in sources_mm
        assert img2 in sources_mm

        # First panel at origin
        assert sources_mm[img1]["xy_mm"][0] == 0.0
        assert sources_mm[img1]["xy_mm"][1] == 0.0

        # Second panel after first + gap
        first_width = sources_mm[img1]["size_mm"][0]
        assert sources_mm[img2]["xy_mm"][0] == pytest.approx(
            first_width + 5.0, rel=0.01
        )
        assert sources_mm[img2]["xy_mm"][1] == 0.0

    def test_horizontal_canvas_size(self, source_images):
        """Horizontal solver calculates correct canvas size."""
        img1, img2 = source_images
        sources_mm, canvas_size_mm = solve_horizontal([img1, img2], gap_mm=5.0, dpi=300)

        # Canvas width = sum of widths + gap
        total_w = sum(s["size_mm"][0] for s in sources_mm.values())
        assert canvas_size_mm[0] == pytest.approx(total_w + 5.0, rel=0.01)

        # Canvas height = max height
        max_h = max(s["size_mm"][1] for s in sources_mm.values())
        assert canvas_size_mm[1] == pytest.approx(max_h, rel=0.01)


class TestSolveVertical:
    """Tests for vertical layout solver."""

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create source image files."""
        img1 = Image.new("RGBA", (200, 150), (255, 0, 0, 255))
        img1_path = tmp_path / "img1.png"
        img1.save(img1_path)

        img2 = Image.new("RGBA", (200, 100), (0, 255, 0, 255))
        img2_path = tmp_path / "img2.png"
        img2.save(img2_path)

        return str(img1_path), str(img2_path)

    def test_vertical_basic(self, source_images):
        """Vertical solver produces correct mm positions."""
        img1, img2 = source_images
        sources_mm, canvas_size_mm = solve_vertical([img1, img2], gap_mm=5.0, dpi=300)

        # First panel at origin
        assert sources_mm[img1]["xy_mm"][0] == 0.0
        assert sources_mm[img1]["xy_mm"][1] == 0.0

        # Second panel below first + gap
        first_height = sources_mm[img1]["size_mm"][1]
        assert sources_mm[img2]["xy_mm"][0] == 0.0
        assert sources_mm[img2]["xy_mm"][1] == pytest.approx(
            first_height + 5.0, rel=0.01
        )

    def test_vertical_canvas_size(self, source_images):
        """Vertical solver calculates correct canvas size."""
        img1, img2 = source_images
        sources_mm, canvas_size_mm = solve_vertical([img1, img2], gap_mm=5.0, dpi=300)

        # Canvas width = max width
        max_w = max(s["size_mm"][0] for s in sources_mm.values())
        assert canvas_size_mm[0] == pytest.approx(max_w, rel=0.01)

        # Canvas height = sum of heights + gap
        total_h = sum(s["size_mm"][1] for s in sources_mm.values())
        assert canvas_size_mm[1] == pytest.approx(total_h + 5.0, rel=0.01)


class TestSolveGrid:
    """Tests for grid layout solver."""

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create 4 source image files for grid testing."""
        images = []
        for i, color in enumerate(
            [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        ):
            img = Image.new("RGBA", (100, 80), (*color, 255))
            img_path = tmp_path / f"img{i}.png"
            img.save(img_path)
            images.append(str(img_path))
        return images

    def test_grid_basic(self, source_images):
        """Grid solver produces correct mm positions for 4 images."""
        sources_mm, canvas_size_mm = solve_grid(source_images, gap_mm=5.0, dpi=300)

        # Should have 4 sources in 2x2 grid
        assert len(sources_mm) == 4

        # All panels should have xy_mm and size_mm
        for source, spec in sources_mm.items():
            assert "xy_mm" in spec
            assert "size_mm" in spec

    def test_grid_auto_columns(self, source_images):
        """Grid solver auto-calculates columns correctly."""
        # 4 images -> 2x2 grid (ceil(sqrt(4)) = 2)
        sources_mm, _ = solve_grid(source_images, gap_mm=5.0, dpi=300)

        # Check positions form a 2x2 grid
        positions = [spec["xy_mm"] for spec in sources_mm.values()]
        x_positions = sorted(set(p[0] for p in positions))
        y_positions = sorted(set(p[1] for p in positions))

        assert len(x_positions) == 2  # 2 columns
        assert len(y_positions) == 2  # 2 rows


class TestSolveLayout:
    """Tests for the layout dispatcher."""

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create source image files."""
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        img_path = tmp_path / "img.png"
        img.save(img_path)
        return [str(img_path)]

    def test_dispatch_horizontal(self, source_images):
        """solve_layout dispatches to horizontal solver."""
        sources_mm, _ = solve_layout(source_images, "horizontal", 5.0, 300)
        assert len(sources_mm) == 1

    def test_dispatch_vertical(self, source_images):
        """solve_layout dispatches to vertical solver."""
        sources_mm, _ = solve_layout(source_images, "vertical", 5.0, 300)
        assert len(sources_mm) == 1

    def test_dispatch_grid(self, source_images):
        """solve_layout dispatches to grid solver."""
        sources_mm, _ = solve_layout(source_images, "grid", 5.0, 300)
        assert len(sources_mm) == 1

    def test_unknown_layout_raises(self, source_images):
        """Unknown layout raises ValueError."""
        with pytest.raises(ValueError, match="Unknown layout"):
            solve_layout(source_images, "unknown", 5.0, 300)

    def test_solver_registry(self):
        """LAYOUT_SOLVERS contains expected layouts."""
        assert "horizontal" in LAYOUT_SOLVERS
        assert "vertical" in LAYOUT_SOLVERS
        assert "grid" in LAYOUT_SOLVERS
