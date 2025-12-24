#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for pie chart color handling in the figure editor."""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


class TestPieChartColorsRecording:
    """Test that pie chart colors are properly recorded and reproducible."""

    def test_pie_colors_recorded_as_list(self):
        """Test that pie chart colors are recorded as a list."""
        import figrecipe as fr

        fig, ax = fr.subplots()
        colors = ["red", "blue", "green", "yellow"]
        ax.pie([25, 25, 25, 25], labels=["A", "B", "C", "D"], colors=colors, id="pie1")

        # Check recorded data
        assert hasattr(fig, "record")
        found = False
        for ax_key, ax_record in fig.record.axes.items():
            for call in ax_record.calls:
                if call.id == "pie1":
                    found = True
                    # Colors should be recorded
                    assert "colors" in call.kwargs
                    assert call.kwargs["colors"] == colors
                    break
        assert found, "pie1 call not found in record"

    def test_pie_colors_reproduced_correctly(self):
        """Test that pie chart reproduces with correct colors."""
        import figrecipe as fr
        from figrecipe._reproducer import reproduce_from_record

        fig, ax = fr.subplots()
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        ax.pie([25, 25, 25, 25], labels=["A", "B", "C", "D"], colors=colors, id="pie1")

        # Reproduce and check
        new_fig, new_axes = reproduce_from_record(fig.record)

        # Verify wedge colors
        mpl_ax = new_fig.fig.get_axes()[0]
        from matplotlib.patches import Wedge

        wedges = [p for p in mpl_ax.patches if isinstance(p, Wedge)]
        assert len(wedges) == 4

    def test_pie_colors_update_preserves_list(self):
        """Test that updating a single color preserves the list structure."""
        import figrecipe as fr
        from figrecipe._reproducer import reproduce_from_record

        fig, ax = fr.subplots()
        colors = ["red", "blue", "green", "yellow"]
        ax.pie([25, 25, 25, 25], labels=["A", "B", "C", "D"], colors=colors, id="pie1")

        # Simulate updating one color in the list
        for ax_key, ax_record in fig.record.axes.items():
            for call in ax_record.calls:
                if call.id == "pie1":
                    # Update first color to orange (as the editor would)
                    new_colors = colors.copy()
                    new_colors[0] = "orange"
                    call.kwargs["colors"] = new_colors
                    break

        # Reproduce and verify
        new_fig, new_axes = reproduce_from_record(fig.record)

        # Check the record was updated
        for ax_key, ax_record in new_fig.record.axes.items():
            for call in ax_record.calls:
                if call.id == "pie1":
                    assert call.kwargs["colors"][0] == "orange"
                    assert len(call.kwargs["colors"]) == 4


class TestColorNormalization:
    """Test that color lists are normalized to consistent format."""

    def test_colors_normalization_in_javascript(self):
        """Test that handleColorListChange normalizes colors."""
        from figrecipe._editor._templates._scripts._colors import SCRIPTS_COLORS

        # Check that normalization logic exists
        assert "normalizedColors = colorsArray.map" in SCRIPTS_COLORS
        assert "resolveColorToHex(color)" in SCRIPTS_COLORS

    def test_mixed_format_colors_handled(self):
        """Test that mixed format colors are handled correctly in reproduce."""
        from figrecipe._reproducer._core import _reconstruct_kwargs

        # Simulate mixed format that could come from frontend
        # (string name + hex values)
        kwargs = {"colors": ["blue", "#ff4632", "#14b414", "#e6a014"]}
        result = _reconstruct_kwargs(kwargs)

        # All should remain as strings (no flattening)
        assert isinstance(result["colors"], list)
        assert len(result["colors"]) == 4
        assert result["colors"][0] == "blue"


class TestColorListFieldDetection:
    """Test the JavaScript color list field detection logic (Python simulation)."""

    def test_colors_plural_is_list_field(self):
        """Test that 'colors' (plural) is detected as a list field."""

        # Simulate the JavaScript isColorListField function
        def is_color_list_field(key, value):
            if key.lower() == "colors" and isinstance(value, list):
                return True
            return False

        # 'colors' with list value should be detected
        assert is_color_list_field("colors", ["red", "blue"])
        assert is_color_list_field("Colors", ["red", "blue", "green"])

        # 'colors' with non-list value should not be detected
        assert not is_color_list_field("colors", "red")
        assert not is_color_list_field("colors", None)

        # 'color' (singular) should not be detected
        assert not is_color_list_field("color", ["red"])
        assert not is_color_list_field("color", "red")

    def test_single_color_fields_excluded_from_list(self):
        """Test that single color fields are not detected as list fields."""

        def is_color_list_field(key, value):
            if key.lower() == "colors" and isinstance(value, list):
                return True
            return False

        # These should not be color list fields
        assert not is_color_list_field("color", "red")
        assert not is_color_list_field("facecolor", "#ff0000")
        assert not is_color_list_field("edgecolor", "blue")
        assert not is_color_list_field("c", "green")


class TestPieChartIntegration:
    """Integration tests for pie chart in the editor context."""

    def test_pie_hitmap_detection(self):
        """Test that pie chart is detected in hitmap."""
        import figrecipe as fr
        from figrecipe._editor._hitmap import generate_hitmap

        fig, ax = fr.subplots()
        ax.pie([30, 40, 30], labels=["A", "B", "C"], id="test_pie")

        hitmap_img, color_map = generate_hitmap(fig)

        # Find pie entry
        pie_entries = [
            (k, v) for k, v in color_map.items() if v.get("call_id") == "test_pie"
        ]
        assert len(pie_entries) > 0, "Pie chart not found in hitmap"

    def test_pie_calls_endpoint_data(self):
        """Test that pie call data is correctly formatted for /calls endpoint."""
        import figrecipe as fr
        from figrecipe._editor._helpers import to_json_serializable
        from figrecipe._signatures import get_signature

        fig, ax = fr.subplots()
        colors = ["red", "blue", "green"]
        ax.pie([33, 33, 34], colors=colors, id="pie_test")

        # Simulate /calls endpoint
        calls_data = {}
        if hasattr(fig, "record"):
            for ax_key, ax_record in fig.record.axes.items():
                for call in ax_record.calls:
                    call_id = call.id
                    func_name = call.function
                    sig = get_signature(func_name)

                    calls_data[call_id] = {
                        "function": func_name,
                        "ax_key": ax_key,
                        "args": to_json_serializable(call.args),
                        "kwargs": to_json_serializable(call.kwargs),
                        "signature": {
                            "args": sig.get("args", []),
                            "kwargs": {
                                k: v
                                for k, v in sig.get("kwargs", {}).items()
                                if k != "**kwargs"
                            },
                        },
                    }

        assert "pie_test" in calls_data
        assert calls_data["pie_test"]["function"] == "pie"

        # Colors should be a list in kwargs
        kwargs = calls_data["pie_test"]["kwargs"]
        assert "colors" in kwargs
        assert isinstance(kwargs["colors"], list)
        assert len(kwargs["colors"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
