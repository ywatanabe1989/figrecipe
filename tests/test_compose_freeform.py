#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for mm-based free-form positioning in compose_figures().

Issue #74: Add mm-based free-form positioning to figrecipe.compose()
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import pytest
from PIL import Image

import figrecipe as fr
from figrecipe._api._compose import compose_figures


class TestComposeFreefrom:
    """Tests for mm-based free-form positioning."""

    @pytest.fixture
    def source_recipes(self, tmp_path):
        """Create source recipe files for testing."""
        # Create first figure
        fig1, ax1 = fr.subplots()
        ax1.plot([1, 2, 3], [1, 4, 9], id="line1")
        ax1.set_xlabel("X1")
        recipe1 = tmp_path / "panel_a.yaml"
        fr.save(fig1, recipe1, validate=False, verbose=False)

        # Create second figure
        fig2, ax2 = fr.subplots()
        ax2.bar([1, 2, 3], [3, 1, 4], id="bar1")
        ax2.set_ylabel("Y2")
        recipe2 = tmp_path / "panel_b.yaml"
        fr.save(fig2, recipe2, validate=False, verbose=False)

        # Create third figure
        fig3, ax3 = fr.subplots()
        ax3.scatter([1, 2, 3], [2, 3, 1], id="scatter1")
        recipe3 = tmp_path / "panel_c.yaml"
        fr.save(fig3, recipe3, validate=False, verbose=False)

        return recipe1, recipe2, recipe3

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create source image files for testing."""
        # Create simple test images
        img1 = Image.new("RGBA", (200, 150), (255, 0, 0, 255))
        img1_path = tmp_path / "panel_a.png"
        img1.save(img1_path)

        img2 = Image.new("RGBA", (200, 150), (0, 255, 0, 255))
        img2_path = tmp_path / "panel_b.png"
        img2.save(img2_path)

        img3 = Image.new("RGBA", (300, 100), (0, 0, 255, 255))
        img3_path = tmp_path / "panel_c.png"
        img3.save(img3_path)

        return img1_path, img2_path, img3_path

    def test_freeform_basic(self, source_images, tmp_path):
        """Basic free-form composition with mm positioning."""
        img1, img2, img3 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            canvas_size_mm=(180, 120),
            sources={
                str(img1): {"xy_mm": (0, 0), "size_mm": (80, 50)},
                str(img2): {"xy_mm": (90, 0), "size_mm": (80, 50)},
                str(img3): {"xy_mm": (0, 60), "size_mm": (170, 50)},
            },
            output_path=str(output_path),
            panel_labels=False,
        )

        assert result["success"] is True
        assert output_path.exists()

        # Check output image dimensions (180mm x 120mm at 300 DPI)
        output_img = Image.open(output_path)
        expected_w = int(180 * 300 / 25.4)
        expected_h = int(120 * 300 / 25.4)
        assert output_img.width == expected_w
        assert output_img.height == expected_h

    def test_freeform_with_recipes(self, source_recipes, tmp_path):
        """Free-form composition with recipe files."""
        recipe1, recipe2, recipe3 = source_recipes
        output_path = tmp_path / "output.png"

        result = compose_figures(
            canvas_size_mm=(180, 120),
            sources={
                str(recipe1): {"xy_mm": (0, 0), "size_mm": (80, 50)},
                str(recipe2): {"xy_mm": (90, 0), "size_mm": (80, 50)},
                str(recipe3): {"xy_mm": (0, 60), "size_mm": (170, 50)},
            },
            output_path=str(output_path),
            panel_labels=True,
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_freeform_auto_canvas_size(self, source_images, tmp_path):
        """Free-form composition with auto-calculated canvas size."""
        img1, img2, _ = source_images
        output_path = tmp_path / "output.png"

        # Don't specify canvas_size_mm, let it auto-calculate
        result = compose_figures(
            sources={
                str(img1): {"xy_mm": (0, 0), "size_mm": (50, 40)},
                str(img2): {"xy_mm": (60, 0), "size_mm": (50, 40)},
            },
            output_path=str(output_path),
            panel_labels=False,
        )

        assert result["success"] is True

        # Canvas should be auto-sized to fit all panels
        output_img = Image.open(output_path)
        # Expected: 60 + 50 = 110mm width, 40mm height
        expected_w = int(110 * 300 / 25.4)
        expected_h = int(40 * 300 / 25.4)
        assert output_img.width == expected_w
        assert output_img.height == expected_h

    def test_freeform_with_panel_labels(self, source_images, tmp_path):
        """Free-form composition with panel labels."""
        img1, img2, _ = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            canvas_size_mm=(120, 50),
            sources={
                str(img1): {"xy_mm": (0, 0), "size_mm": (50, 40)},
                str(img2): {"xy_mm": (60, 0), "size_mm": (50, 40)},
            },
            output_path=str(output_path),
            panel_labels=True,
            label_style="uppercase",
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_freeform_missing_xy_mm_raises(self, source_images, tmp_path):
        """Missing xy_mm in source spec raises ValueError."""
        img1, _, _ = source_images
        output_path = tmp_path / "output.png"

        with pytest.raises(ValueError, match="missing required"):
            compose_figures(
                canvas_size_mm=(100, 100),
                sources={
                    str(img1): {"size_mm": (50, 40)},  # Missing xy_mm
                },
                output_path=str(output_path),
            )

    def test_freeform_missing_size_mm_raises(self, source_images, tmp_path):
        """Missing size_mm in source spec raises ValueError."""
        img1, _, _ = source_images
        output_path = tmp_path / "output.png"

        with pytest.raises(ValueError, match="missing required"):
            compose_figures(
                canvas_size_mm=(100, 100),
                sources={
                    str(img1): {"xy_mm": (0, 0)},  # Missing size_mm
                },
                output_path=str(output_path),
            )

    def test_freeform_invalid_spec_raises(self, source_images, tmp_path):
        """Invalid source spec (not a dict) raises ValueError."""
        img1, _, _ = source_images
        output_path = tmp_path / "output.png"

        with pytest.raises(ValueError, match="must be a dict"):
            compose_figures(
                canvas_size_mm=(100, 100),
                sources={
                    str(img1): "invalid",  # Should be dict
                },
                output_path=str(output_path),
            )

    def test_freeform_empty_sources_raises(self, tmp_path):
        """Empty sources dict raises ValueError."""
        output_path = tmp_path / "output.png"

        with pytest.raises(ValueError, match="No sources"):
            compose_figures(
                canvas_size_mm=(100, 100),
                sources={},
                output_path=str(output_path),
            )

    def test_freeform_with_symlinks(self, source_images, tmp_path):
        """Free-form composition creates source symlinks."""
        img1, img2, _ = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            canvas_size_mm=(120, 50),
            sources={
                str(img1): {"xy_mm": (0, 0), "size_mm": (50, 40)},
                str(img2): {"xy_mm": (60, 0), "size_mm": (50, 40)},
            },
            output_path=str(output_path),
            create_symlinks=True,
        )

        assert result["success"] is True
        assert "sources_dir" in result
        sources_dir = Path(result["sources_dir"])
        assert sources_dir.exists()

    def test_freeform_without_symlinks(self, source_images, tmp_path):
        """Free-form composition without symlinks."""
        img1, _, _ = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            canvas_size_mm=(60, 50),
            sources={
                str(img1): {"xy_mm": (0, 0), "size_mm": (50, 40)},
            },
            output_path=str(output_path),
            create_symlinks=False,
        )

        assert result["success"] is True
        assert "sources_dir" not in result


class TestComposeBackwardCompatibility:
    """Tests ensuring backward compatibility with grid-based layout."""

    @pytest.fixture
    def source_images(self, tmp_path):
        """Create source image files for testing."""
        img1 = Image.new("RGBA", (200, 150), (255, 0, 0, 255))
        img1_path = tmp_path / "img1.png"
        img1.save(img1_path)

        img2 = Image.new("RGBA", (200, 150), (0, 255, 0, 255))
        img2_path = tmp_path / "img2.png"
        img2.save(img2_path)

        return img1_path, img2_path

    def test_list_sources_horizontal(self, source_images, tmp_path):
        """List-based sources with horizontal layout still works."""
        img1, img2 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            sources=[str(img1), str(img2)],
            output_path=str(output_path),
            layout="horizontal",
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_list_sources_vertical(self, source_images, tmp_path):
        """List-based sources with vertical layout still works."""
        img1, img2 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            sources=[str(img1), str(img2)],
            output_path=str(output_path),
            layout="vertical",
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_list_sources_grid(self, source_images, tmp_path):
        """List-based sources with grid layout still works."""
        img1, img2 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            sources=[str(img1), str(img2)],
            output_path=str(output_path),
            layout="grid",
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_list_sources_with_gap(self, source_images, tmp_path):
        """List-based sources with custom gap still works."""
        img1, img2 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            sources=[str(img1), str(img2)],
            output_path=str(output_path),
            layout="horizontal",
            gap_mm=10.0,
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_list_sources_with_labels(self, source_images, tmp_path):
        """List-based sources with panel labels still works."""
        img1, img2 = source_images
        output_path = tmp_path / "output.png"

        result = compose_figures(
            sources=[str(img1), str(img2)],
            output_path=str(output_path),
            panel_labels=True,
            label_style="lowercase",
        )

        assert result["success"] is True
        assert output_path.exists()

    def test_list_sources_empty_raises(self, tmp_path):
        """Empty list of sources raises ValueError."""
        output_path = tmp_path / "output.png"

        with pytest.raises(ValueError, match="No valid source"):
            compose_figures(
                sources=[],
                output_path=str(output_path),
            )
