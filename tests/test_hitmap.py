#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for hitmap visualization functionality."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from figrecipe._utils._hitmap import create_hitmap, generate_hitmap_report


@pytest.fixture
def identical_images():
    """Create two identical test images."""
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[20:80, 20:80] = [255, 0, 0]  # Red square
    return arr, arr.copy()


@pytest.fixture
def different_images():
    """Create two different test images."""
    arr1 = np.zeros((100, 100, 3), dtype=np.uint8)
    arr1[20:80, 20:80] = [255, 0, 0]  # Red square

    arr2 = np.zeros((100, 100, 3), dtype=np.uint8)
    arr2[30:90, 30:90] = [0, 0, 255]  # Blue square, offset

    return arr1, arr2


class TestCreateHitmap:
    """Tests for create_hitmap function."""

    def test_identical_images_match(self, identical_images):
        """Identical images should have 100% match ratio."""
        img1, img2 = identical_images
        hitmap, stats = create_hitmap(img1, img2)

        assert stats["match_ratio"] == 1.0
        assert stats["mismatch_ratio"] == 0.0
        assert stats["mismatch_pixels"] == 0
        assert stats["max_diff"] == 0.0
        assert stats["mean_diff"] == 0.0

    def test_different_images_mismatch(self, different_images):
        """Different images should have mismatch."""
        img1, img2 = different_images
        hitmap, stats = create_hitmap(img1, img2)

        assert stats["match_ratio"] < 1.0
        assert stats["mismatch_ratio"] > 0.0
        assert stats["mismatch_pixels"] > 0
        assert stats["max_diff"] > 0

    def test_hitmap_shape(self, identical_images):
        """Hitmap should have same shape as input images."""
        img1, img2 = identical_images
        hitmap, _ = create_hitmap(img1, img2)

        assert hitmap.shape == img1.shape

    def test_output_path(self, identical_images, tmp_path):
        """Hitmap should be saved to output path."""
        img1, img2 = identical_images
        output_path = tmp_path / "hitmap.png"

        create_hitmap(img1, img2, output_path=output_path)

        assert output_path.exists()

    def test_threshold_affects_match(self, different_images):
        """Higher threshold should increase match ratio."""
        img1, img2 = different_images

        _, stats_strict = create_hitmap(img1, img2, threshold=0)
        _, stats_lenient = create_hitmap(img1, img2, threshold=50)

        assert stats_lenient["match_ratio"] >= stats_strict["match_ratio"]

    def test_binary_mode(self, different_images):
        """Binary mode should produce green/red hitmap."""
        img1, img2 = different_images
        hitmap, _ = create_hitmap(img1, img2, mode="binary")

        # Check that hitmap contains green and/or red
        has_green = np.any(hitmap[:, :, 1] > 0)
        has_red = np.any(hitmap[:, :, 0] > 0)

        assert has_green or has_red

    def test_diff_mode(self, different_images):
        """Diff mode should show difference magnitude in red channel."""
        img1, img2 = different_images
        hitmap, _ = create_hitmap(img1, img2, mode="diff")

        # Diff areas should have red intensity
        assert np.any(hitmap[:, :, 0] > 0)

    def test_heatmap_mode(self, different_images):
        """Heatmap mode should produce colormap output."""
        img1, img2 = different_images
        hitmap, _ = create_hitmap(img1, img2, mode="heatmap")

        # Heatmap should have various color values
        assert hitmap.dtype == np.uint8
        assert hitmap.shape[-1] == 3

    def test_regions_detected(self, different_images):
        """Difference regions should be detected."""
        img1, img2 = different_images
        _, stats = create_hitmap(img1, img2, show_bbox=True, min_region_area=5)

        assert "regions" in stats
        assert "num_regions" in stats

    def test_from_file_paths(self, identical_images, tmp_path):
        """Should accept file paths as input."""
        img1, img2 = identical_images

        path1 = tmp_path / "img1.png"
        path2 = tmp_path / "img2.png"

        Image.fromarray(img1).save(path1)
        Image.fromarray(img2).save(path2)

        hitmap, stats = create_hitmap(path1, path2)

        assert stats["match_ratio"] == 1.0


class TestGenerateHitmapReport:
    """Tests for generate_hitmap_report function."""

    def test_report_generation(self, identical_images, tmp_path):
        """Report should contain expected fields."""
        img1, img2 = identical_images

        orig_path = tmp_path / "original.png"
        repro_path = tmp_path / "reproduced.png"

        Image.fromarray(img1).save(orig_path)
        Image.fromarray(img2).save(repro_path)

        report = generate_hitmap_report(orig_path, repro_path, output_dir=tmp_path)

        assert "original" in report
        assert "reproduced" in report
        assert "hitmap" in report
        assert "is_pixel_perfect" in report
        assert "stats" in report
        assert report["is_pixel_perfect"] is True

    def test_report_hitmap_created(self, different_images, tmp_path):
        """Report should create hitmap file."""
        img1, img2 = different_images

        orig_path = tmp_path / "original.png"
        repro_path = tmp_path / "reproduced.png"

        Image.fromarray(img1).save(orig_path)
        Image.fromarray(img2).save(repro_path)

        report = generate_hitmap_report(orig_path, repro_path, output_dir=tmp_path)

        assert Path(report["hitmap"]).exists()
        assert report["is_pixel_perfect"] is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_different_sizes(self):
        """Images of different sizes should be handled."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((102, 98, 3), dtype=np.uint8)

        # Should not raise, should crop to common area
        hitmap, stats = create_hitmap(img1, img2)

        assert hitmap is not None
        assert "match_ratio" in stats

    def test_empty_diff_no_bbox(self, identical_images):
        """No regions should be detected for identical images."""
        img1, img2 = identical_images
        _, stats = create_hitmap(img1, img2, show_bbox=True)

        assert stats["num_regions"] == 0
        assert stats["regions"] == []
