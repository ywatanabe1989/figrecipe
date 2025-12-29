#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for figrecipe CLI commands."""

import json

import pytest
from click.testing import CliRunner

from figrecipe._cli import main


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_recipe(tmp_path):
    """Create a sample recipe file for testing."""
    import figrecipe as fr

    # Create a simple figure
    fig, axes = fr.subplots(1, 1)
    axes.plot([1, 2, 3], [1, 4, 9], label="test")
    axes.set_xlabel("X")
    axes.set_ylabel("Y")

    # Save as recipe using RecordingFigure's save_recipe method
    recipe_path = tmp_path / "test_figure.yaml"
    fig.save_recipe(recipe_path)

    return recipe_path


class TestMainCommand:
    """Test main CLI group."""

    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "figrecipe" in result.output
        assert "reproduce" in result.output

    def test_version_flag(self, runner):
        """Test -V flag shows version."""
        result = runner.invoke(main, ["-V"])
        assert result.exit_code == 0
        assert "figrecipe" in result.output

    def test_no_command_shows_help(self, runner):
        """Test that no command shows help."""
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert "Commands:" in result.output


class TestVersionCommand:
    """Test version command."""

    def test_version(self, runner):
        """Test version command shows version."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "figrecipe" in result.output

    def test_version_full(self, runner):
        """Test version --full shows dependencies."""
        result = runner.invoke(main, ["version", "--full"])
        assert result.exit_code == 0
        assert "matplotlib" in result.output
        assert "numpy" in result.output
        assert "Python" in result.output


class TestInfoCommand:
    """Test info command."""

    def test_info_requires_source(self, runner):
        """Test info requires source argument."""
        result = runner.invoke(main, ["info"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_info_basic(self, runner, sample_recipe):
        """Test basic info output."""
        result = runner.invoke(main, ["info", str(sample_recipe)])
        assert result.exit_code == 0
        assert "Recipe Version" in result.output
        assert "Figure ID" in result.output

    def test_info_json(self, runner, sample_recipe):
        """Test info --json outputs valid JSON."""
        result = runner.invoke(main, ["info", "--json", str(sample_recipe)])
        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert "figrecipe_version" in data or "id" in data

    def test_info_verbose(self, runner, sample_recipe):
        """Test info -v shows detailed info."""
        result = runner.invoke(main, ["info", "-v", str(sample_recipe)])
        assert result.exit_code == 0
        # Verbose mode should at least show basic info
        assert "Figure ID" in result.output or "Matplotlib" in result.output


class TestReproduceCommand:
    """Test reproduce command."""

    def test_reproduce_requires_source(self, runner):
        """Test reproduce requires source argument."""
        result = runner.invoke(main, ["reproduce"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_reproduce_basic(self, runner, sample_recipe, tmp_path):
        """Test basic reproduce."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            main, ["reproduce", str(sample_recipe), "-o", str(output_path)]
        )
        assert result.exit_code == 0
        assert output_path.exists()
        assert "Saved" in result.output

    def test_reproduce_formats(self, runner, sample_recipe, tmp_path):
        """Test reproduce with different formats."""
        for fmt in ["png", "pdf", "svg"]:
            output_path = tmp_path / f"output.{fmt}"
            result = runner.invoke(
                main,
                ["reproduce", str(sample_recipe), "-o", str(output_path), "-f", fmt],
            )
            assert result.exit_code == 0
            assert output_path.exists()

    def test_reproduce_help(self, runner):
        """Test reproduce --help."""
        result = runner.invoke(main, ["reproduce", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output
        assert "--format" in result.output
        assert "--dpi" in result.output


class TestValidateCommand:
    """Test validate command."""

    def test_validate_requires_source(self, runner):
        """Test validate requires source argument."""
        result = runner.invoke(main, ["validate"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_validate_help(self, runner):
        """Test validate --help."""
        result = runner.invoke(main, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--threshold" in result.output
        assert "--strict" in result.output
        assert "--quiet" in result.output


class TestFontsCommand:
    """Test fonts command."""

    def test_fonts_list(self, runner):
        """Test fonts command lists fonts."""
        result = runner.invoke(main, ["fonts"])
        assert result.exit_code == 0
        assert "fonts" in result.output.lower()

    def test_fonts_search(self, runner):
        """Test fonts --search."""
        result = runner.invoke(main, ["fonts", "--search", "sans"])
        assert result.exit_code == 0
        assert "matching" in result.output.lower()

    def test_fonts_check_available(self, runner):
        """Test fonts --check with common font."""
        # DejaVu Sans is typically available
        result = runner.invoke(main, ["fonts", "--check", "DejaVu Sans"])
        # May or may not be available, just check it runs
        assert result.exit_code in [0, 1]

    def test_fonts_help(self, runner):
        """Test fonts --help."""
        result = runner.invoke(main, ["fonts", "--help"])
        assert result.exit_code == 0
        assert "--check" in result.output
        assert "--search" in result.output


class TestEditCommand:
    """Test edit command."""

    def test_edit_help(self, runner):
        """Test edit --help."""
        result = runner.invoke(main, ["edit", "--help"])
        assert result.exit_code == 0
        assert "SOURCE" in result.output or "source" in result.output.lower()


class TestCropCommand:
    """Test crop command."""

    def test_crop_help(self, runner):
        """Test crop --help."""
        result = runner.invoke(main, ["crop", "--help"])
        assert result.exit_code == 0
        assert "IMAGE" in result.output or "image" in result.output.lower()


class TestComposeCommand:
    """Test compose command."""

    def test_compose_help(self, runner):
        """Test compose --help."""
        result = runner.invoke(main, ["compose", "--help"])
        assert result.exit_code == 0


class TestStyleCommand:
    """Test style command."""

    def test_style_help(self, runner):
        """Test style --help."""
        result = runner.invoke(main, ["style", "--help"])
        assert result.exit_code == 0


class TestConvertCommand:
    """Test convert command."""

    def test_convert_help(self, runner):
        """Test convert --help."""
        result = runner.invoke(main, ["convert", "--help"])
        assert result.exit_code == 0
        assert "--format" in result.output or "format" in result.output.lower()


class TestExtractCommand:
    """Test extract command."""

    def test_extract_help(self, runner):
        """Test extract --help."""
        result = runner.invoke(main, ["extract", "--help"])
        assert result.exit_code == 0

    def test_extract_requires_source(self, runner):
        """Test extract requires source argument."""
        result = runner.invoke(main, ["extract"])
        assert result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_module_invocation(self):
        """Test python -m figrecipe works."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "figrecipe", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "figrecipe" in result.stdout

    def test_full_workflow(self, runner, tmp_path):
        """Test full workflow: create -> info -> reproduce -> validate."""
        import figrecipe as fr

        # Create figure
        fig, axes = fr.subplots(1, 1)
        axes.plot([1, 2, 3], [1, 4, 9])
        recipe_path = tmp_path / "workflow_test.yaml"
        fig.save_recipe(recipe_path)

        # Info
        result = runner.invoke(main, ["info", str(recipe_path)])
        assert result.exit_code == 0

        # Reproduce
        output_path = tmp_path / "reproduced.png"
        result = runner.invoke(
            main, ["reproduce", str(recipe_path), "-o", str(output_path)]
        )
        assert result.exit_code == 0
        assert output_path.exists()
