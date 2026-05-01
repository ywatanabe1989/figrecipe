#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for savefig() consistency with fr.save() (Issue #42).

Tests that fig.savefig() and fr.save() produce consistent outputs,
both going through the same save pipeline with auto-crop and finalization.
"""

import pytest


@pytest.fixture
def fig_ax():
    """Create a simple figure with SCITEX style."""
    import figrecipe as fr

    fr.load_style("SCITEX")
    fig, ax = fr.subplots()
    ax.plot([1, 2, 3], [1, 2, 3], id="test")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    yield fig, ax
    import matplotlib.pyplot as plt

    plt.close(fig.fig)


class TestSavefigConsistency:
    """Tests that savefig() delegates to save_figure()."""

    def test_savefig_creates_yaml(self, fig_ax, tmp_path):
        """savefig() should create a YAML recipe by default."""
        fig, ax = fig_ax
        output = tmp_path / "test.png"

        result = fig.savefig(output, verbose=False)

        # Should return (image_path, yaml_path, validation_result) tuple
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0].exists()
        assert result[1].exists()
        assert result[1].suffix == ".yaml"

    def test_savefig_no_recipe(self, fig_ax, tmp_path):
        """savefig(save_recipe=False) should only save the image."""
        fig, ax = fig_ax
        output = tmp_path / "test.png"

        result = fig.savefig(output, save_recipe=False, verbose=False)

        # Should return (image_path, None, None) tuple
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0].exists()
        assert result[1] is None
        assert result[2] is None
        # YAML should NOT be created
        assert not (tmp_path / "test.yaml").exists()

    def test_savefig_same_as_fr_save(self, fig_ax, tmp_path):
        """savefig() output should match fr.save() output dimensions."""
        from PIL import Image

        import figrecipe as fr

        fig1, ax1 = fig_ax

        # Save with savefig()
        savefig_path = tmp_path / "savefig.png"
        fig1.savefig(savefig_path, verbose=False, validate=False)

        # Create second figure for fr.save()
        fr.load_style("SCITEX")
        fig2, ax2 = fr.subplots()
        ax2.plot([1, 2, 3], [1, 2, 3], id="test")
        ax2.set_xlabel("X axis")
        ax2.set_ylabel("Y axis")

        frsave_path = tmp_path / "frsave.png"
        fr.save(fig2, frsave_path, verbose=False, validate=False)

        # Compare image dimensions (should be identical)
        with Image.open(savefig_path) as img1, Image.open(frsave_path) as img2:
            assert (
                img1.size == img2.size
            ), f"savefig() produced {img1.size}, fr.save() produced {img2.size}"

        import matplotlib.pyplot as plt

        plt.close(fig2.fig)

    def test_savefig_applies_autocrop(self, tmp_path):
        """savefig() should apply auto-crop from mm_layout."""
        from PIL import Image

        import figrecipe as fr

        fr.load_style("SCITEX")
        fig, ax = fr.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])

        output = tmp_path / "test.png"
        fig.savefig(output, verbose=False, validate=False)

        # Check that image was created and has reasonable dimensions
        # (auto-crop should make it smaller than the uncropped figure)
        with Image.open(output) as img:
            # With SCITEX style at 300 DPI, cropped figure should be
            # roughly 40mm wide * 300/25.4 ≈ 472px, plus margins
            # Just check it's not too large (uncropped would be ~2k px)
            assert img.width < 1000, f"Image seems uncropped: {img.width}px wide"
            assert img.height < 800, f"Image seems uncropped: {img.height}px tall"

        import matplotlib.pyplot as plt

        plt.close(fig.fig)

    def test_savefig_respects_dpi_kwarg(self, fig_ax, tmp_path):
        """savefig() should respect the dpi keyword argument."""
        from PIL import Image

        fig, ax = fig_ax

        # Save at different DPIs
        output_300 = tmp_path / "dpi300.png"
        output_150 = tmp_path / "dpi150.png"

        fig.savefig(output_300, dpi=300, verbose=False, validate=False)

        # Create new figure for 150 DPI test
        import figrecipe as fr

        fr.load_style("SCITEX")
        fig2, ax2 = fr.subplots()
        ax2.plot([1, 2, 3], [1, 2, 3], id="test")
        ax2.set_xlabel("X axis")
        ax2.set_ylabel("Y axis")
        fig2.savefig(output_150, dpi=150, verbose=False, validate=False)

        with Image.open(output_300) as img300, Image.open(output_150) as img150:
            # 300 DPI should be roughly 2x the size of 150 DPI
            ratio = img300.width / img150.width
            assert 1.8 < ratio < 2.2, f"DPI ratio unexpected: {ratio}"

        import matplotlib.pyplot as plt

        plt.close(fig2.fig)


class TestSavefigRecording:
    """Tests that savefig() properly records calls for reproduction."""

    def test_savefig_recipe_contains_plot(self, fig_ax, tmp_path):
        """Recipe from savefig() should contain the plot call."""
        from ruamel.yaml import YAML

        fig, ax = fig_ax
        output = tmp_path / "test.png"

        fig.savefig(output, verbose=False, validate=False)

        # Read the recipe
        yaml_path = tmp_path / "test.yaml"
        yaml_loader = YAML(typ="safe")
        with open(yaml_path) as f:
            recipe = yaml_loader.load(f)

        # Should contain axes with a plot call
        assert "axes" in recipe
        ax_key = list(recipe["axes"].keys())[0]
        assert "calls" in recipe["axes"][ax_key]
        assert len(recipe["axes"][ax_key]["calls"]) > 0

        # Verify the plot call is recorded correctly
        calls = recipe["axes"][ax_key]["calls"]
        plot_calls = [c for c in calls if c["function"] == "plot"]
        assert len(plot_calls) == 1
