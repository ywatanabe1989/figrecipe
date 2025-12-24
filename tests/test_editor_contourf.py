#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for contourf element detection and properties in the editor."""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


class TestContourHitmapDetection:
    """Test contourf detection in hitmap system."""

    def test_contourf_detected_in_hitmap(self):
        """Test that contourf is detected in hitmap with correct call_id."""
        import figrecipe as fr
        from figrecipe._editor._hitmap import generate_hitmap

        fig, ax = fr.subplots()
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        ax.contourf(X, Y, Z, levels=10, id="test_contourf")

        hitmap_img, color_map = generate_hitmap(fig)

        # Find contour entry in color_map
        contour_entries = [
            (k, v) for k, v in color_map.items() if "contour" in k.lower()
        ]

        assert len(contour_entries) > 0, "No contour entry found in color_map"

        key, entry = contour_entries[0]
        assert (
            entry.get("call_id") == "test_contourf"
        ), f"call_id mismatch: expected 'test_contourf', got '{entry.get('call_id')}'"
        assert (
            entry.get("type") == "contour"
        ), f"type should be 'contour', got '{entry.get('type')}'"

    def test_contourf_recorded_in_calls(self):
        """Test that contourf call is recorded and accessible."""
        import figrecipe as fr
        from figrecipe._editor._helpers import to_json_serializable
        from figrecipe._signatures import get_signature

        fig, ax = fr.subplots()
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        ax.contourf(X, Y, Z, levels=10, id="test_contourf")

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

        assert (
            "test_contourf" in calls_data
        ), f"test_contourf not in calls_data. Keys: {list(calls_data.keys())}"

        call_info = calls_data["test_contourf"]
        assert call_info["function"] == "contourf"
        assert len(call_info["signature"]["kwargs"]) > 0

    def test_contourf_hitmap_and_calls_match(self):
        """Test that hitmap call_id matches calls data key."""
        import figrecipe as fr
        from figrecipe._editor._hitmap import generate_hitmap

        fig, ax = fr.subplots()
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.exp(-(X**2 + Y**2))
        ax.contourf(X, Y, Z, id="my_contourf")

        # Get hitmap
        hitmap_img, color_map = generate_hitmap(fig)

        # Get calls data
        calls_data = {}
        if hasattr(fig, "record"):
            for ax_key, ax_record in fig.record.axes.items():
                for call in ax_record.calls:
                    calls_data[call.id] = {"function": call.function}

        # Find contour entry
        contour_entry = None
        for k, v in color_map.items():
            if "contour" in k.lower():
                contour_entry = v
                break

        assert contour_entry is not None, "No contour in color_map"

        call_id = contour_entry.get("call_id")
        assert call_id is not None, "call_id missing from hitmap contour entry"
        assert call_id in calls_data, (
            f"Hitmap call_id '{call_id}' not found in calls_data. "
            f"Available: {list(calls_data.keys())}"
        )

    def test_contour_detected_separately(self):
        """Test that contour (unfilled) is also detected."""
        import figrecipe as fr
        from figrecipe._editor._hitmap import generate_hitmap

        fig, ax = fr.subplots()
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        ax.contour(X, Y, Z, levels=10, id="test_contour")

        hitmap_img, color_map = generate_hitmap(fig)

        contour_entries = [
            (k, v) for k, v in color_map.items() if "contour" in k.lower()
        ]

        assert len(contour_entries) > 0
        key, entry = contour_entries[0]
        assert entry.get("call_id") == "test_contour"


class TestAllPlotsContourf:
    """Test contourf in the all-plots demo figure."""

    def test_all_plots_contourf_recorded(self):
        """Test that contourf is properly recorded in all-plots figure."""
        import figrecipe as fr
        from figrecipe._dev.demo_plotters import create_all_plots_figure

        fig, axes, results = create_all_plots_figure(fr)

        # Check contourf was successful
        assert results.get("contourf", {}).get(
            "success", False
        ), f"contourf failed in demo: {results.get('contourf')}"

        # Check it's recorded
        found = False
        if hasattr(fig, "record"):
            for ax_key, ax_record in fig.record.axes.items():
                for call in ax_record.calls:
                    if call.function == "contourf":
                        found = True
                        assert call.id is not None, "contourf call has no id"
                        break

        assert found, "contourf call not found in all-plots figure record"

    def test_all_plots_contourf_hitmap(self):
        """Test that contourf is detected in hitmap for all-plots figure."""
        import figrecipe as fr
        from figrecipe._dev.demo_plotters import create_all_plots_figure
        from figrecipe._editor._hitmap import generate_hitmap

        fig, axes, results = create_all_plots_figure(fr)

        hitmap_img, color_map = generate_hitmap(fig)

        contourf_entries = [
            (k, v) for k, v in color_map.items() if v.get("call_id") == "contourf"
        ]

        assert (
            len(contourf_entries) > 0
        ), "contourf not found in hitmap color_map by call_id"


class TestContourTabSwitching:
    """Test that contour element types are mapped to Element tab."""

    def test_contour_in_element_types(self):
        """Test that 'contour' is in ELEMENT_TYPES for tab switching."""
        from figrecipe._editor._templates._scripts._tabs import SCRIPTS_TABS

        # Check that ELEMENT_TYPES includes 'contour'
        assert (
            "'contour'" in SCRIPTS_TABS
        ), "'contour' not found in ELEMENT_TYPES in _tabs.py"

    def test_specgram_in_element_types(self):
        """Test that 'specgram' is in ELEMENT_TYPES for tab switching."""
        from figrecipe._editor._templates._scripts._tabs import SCRIPTS_TABS

        # Check that ELEMENT_TYPES includes 'specgram'
        assert (
            "'specgram'" in SCRIPTS_TABS
        ), "'specgram' not found in ELEMENT_TYPES in _tabs.py"

    def test_element_types_includes_all_plot_types(self):
        """Test that all major plot element types are included."""
        from figrecipe._editor._templates._scripts._tabs import SCRIPTS_TABS

        required_types = [
            "line",
            "scatter",
            "bar",
            "hist",
            "contour",
            "image",
            "pie",
            "quiver",
        ]

        for plot_type in required_types:
            assert (
                f"'{plot_type}'" in SCRIPTS_TABS
            ), f"'{plot_type}' not found in ELEMENT_TYPES"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
