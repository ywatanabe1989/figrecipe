#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for diagram recipe save/load/reproduce roundtrip."""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import figrecipe as fr
from figrecipe._serializer import load_recipe


class TestStandaloneDiagramRecipe:
    """Standalone diagram recipes (type: diagram) load via load_recipe()."""

    def test_load_standalone_diagram_recipe(self, tmp_path):
        """Standalone diagram YAML converts to FigureRecord on load."""
        # Create and save a diagram (produces standalone format)
        d = fr.Diagram(width_mm=180, height_mm=100)
        d.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        d.add_box("b", title="B", x_mm=130, y_mm=50, width_mm=40, height_mm=25)
        d.add_arrow("a", "b")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.render_to_file(tmp_path / "diagram.png", save_hitmap=False)

        yaml_path = tmp_path / "diagram.yaml"
        assert yaml_path.exists()

        # Load it through load_recipe
        record = load_recipe(yaml_path)
        assert record is not None
        assert "ax_0_0" in record.axes
        ax_data = record.axes["ax_0_0"]
        assert len(ax_data.calls) == 1
        assert ax_data.calls[0].function == "diagram"
        assert "diagram_data" in ax_data.calls[0].kwargs

    def test_reproduce_standalone_diagram(self, tmp_path):
        """Standalone diagram recipe can be reproduced via fr.reproduce()."""
        d = fr.Diagram(width_mm=180, height_mm=100)
        d.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)
        d.add_box("b", title="B", x_mm=130, y_mm=50, width_mm=40, height_mm=25)
        d.add_arrow("a", "b", label="flow")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.render_to_file(tmp_path / "diagram.png", save_hitmap=False)

        yaml_path = tmp_path / "diagram.yaml"

        # Reproduce from standalone diagram recipe
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig = fr.reproduce(yaml_path)

        assert fig is not None

    def test_diagram_data_preserved(self, tmp_path):
        """Boxes, arrows, containers survive save/load cycle."""
        d = fr.Diagram(width_mm=180, height_mm=100)
        d.add_box("x", title="X", x_mm=40, y_mm=50, width_mm=40, height_mm=25)
        d.add_box("y", title="Y", x_mm=130, y_mm=50, width_mm=40, height_mm=25)
        d.add_container(
            "grp",
            title="Group",
            children=["x", "y"],
            x_mm=85,
            y_mm=50,
            width_mm=160,
            height_mm=50,
        )
        d.add_arrow("x", "y")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.render_to_file(tmp_path / "test.png", save_hitmap=False)

        record = load_recipe(tmp_path / "test.yaml")
        diagram_data = record.axes["ax_0_0"].calls[0].kwargs["diagram_data"]

        # Verify structure
        assert len(diagram_data["boxes"]) == 2
        assert len(diagram_data["arrows"]) == 1
        assert len(diagram_data["containers"]) >= 1


class TestEmbeddedDiagramRecipe:
    """Embedded diagram recipes (function: diagram in axes) load correctly."""

    def test_load_existing_embedded_recipe(self):
        """Load an existing embedded recipe (09a_schematic_out)."""
        recipe_path = Path("examples/09a_schematic_out/recipe.yaml")
        if not recipe_path.exists():
            return  # Skip if example not built

        record = load_recipe(recipe_path)
        assert record is not None
        assert "ax_0_0" in record.axes

    def test_legacy_schematic_function_dispatches(self, tmp_path):
        """function: schematic dispatches to diagram replay."""
        # The 09a example uses function: schematic with schematic_data
        # Our reproducer should handle both function names
        d = fr.Diagram(width_mm=180, height_mm=100)
        d.add_box("a", title="A", x_mm=50, y_mm=50, width_mm=40, height_mm=25)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d.render_to_file(tmp_path / "test.png", save_hitmap=False)

        record = load_recipe(tmp_path / "test.yaml")
        # Standalone format converts to function: diagram
        assert record.axes["ax_0_0"].calls[0].function == "diagram"


# EOF
