#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for hitmap call_id matching with recorded calls.

These tests verify that hitmap elements have call_ids that match
actual recorded calls, which is essential for the editor's property
panel to display correct data.
"""

import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import figrecipe as fr


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


def get_hitmap_and_calls(fig):
    """Generate hitmap and get recorded calls."""
    from figrecipe._editor._hitmap_main import generate_hitmap

    _, color_map = generate_hitmap(fig)

    # Get recorded call IDs
    recorded_call_ids = set()
    if hasattr(fig, "record"):
        for ax_key, ax_record in fig.record.axes.items():
            for call in ax_record.calls:
                recorded_call_ids.add(call.id)

    return color_map, recorded_call_ids


def check_call_ids_match(color_map, recorded_call_ids, allow_fallback=False):
    """Check that hitmap call_ids match recorded calls.

    Returns list of mismatches.
    """
    mismatches = []
    for key, info in color_map.items():
        call_id = info.get("call_id")
        elem_type = info.get("type", "unknown")

        # Skip elements that don't need call_id matching
        if elem_type in (
            "axes",
            "spine",
            "xticks",
            "yticks",
            "title",
            "xlabel",
            "ylabel",
            "legend",
            "text",
            "panel_label",
        ):
            continue

        if call_id is None:
            mismatches.append(
                {
                    "key": key,
                    "type": elem_type,
                    "call_id": None,
                    "reason": "No call_id assigned",
                }
            )
        elif call_id not in recorded_call_ids:
            # Check if it's a fallback ID (like line_0_1, bar_2, etc.)
            is_fallback = (
                any(
                    call_id.startswith(p)
                    for p in ["line_", "bar_", "scatter_", "fill_", "stairs_", "step_"]
                )
                and "_" in call_id
                and call_id.split("_")[-1].isdigit()
            )

            if not allow_fallback or not is_fallback:
                mismatches.append(
                    {
                        "key": key,
                        "type": elem_type,
                        "call_id": call_id,
                        "reason": f"call_id '{call_id}' not in recorded calls",
                        "recorded": list(recorded_call_ids),
                    }
                )

    return mismatches


class TestSinglePanelCallIdMatching:
    """Test call_id matching for single-panel figures."""

    def test_plot_call_id_matches(self):
        """Test that plot elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.plot([1, 2, 3], [1, 4, 9], id="my_plot")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_plot" in recorded

    def test_scatter_call_id_matches(self):
        """Test that scatter elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.scatter([1, 2, 3], [1, 4, 9], id="my_scatter")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_scatter" in recorded

    def test_bar_call_id_matches(self):
        """Test that bar elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.bar(["A", "B", "C"], [1, 4, 9], id="my_bar")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_bar" in recorded

    def test_errorbar_call_id_matches(self):
        """Test that errorbar elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.errorbar([1, 2, 3], [1, 4, 9], yerr=[0.5, 0.5, 0.5], id="my_errorbar")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_errorbar" in recorded

    def test_fill_between_call_id_matches(self):
        """Test that fill_between elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.fill_between([1, 2, 3], [0, 0, 0], [1, 4, 9], id="my_fill")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_fill" in recorded

    def test_hist_call_id_matches(self):
        """Test that hist elements have matching call_ids."""
        rng = np.random.default_rng(42)
        fig, ax = fr.subplots(1, 1)
        ax.hist(rng.standard_normal(100), bins=10, id="my_hist")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_hist" in recorded

    def test_pie_call_id_matches(self):
        """Test that pie elements have matching call_ids."""
        fig, ax = fr.subplots(1, 1)
        ax.pie([30, 40, 30], id="my_pie")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_pie" in recorded

    def test_imshow_call_id_matches(self):
        """Test that imshow elements have matching call_ids."""
        rng = np.random.default_rng(42)
        fig, ax = fr.subplots(1, 1)
        ax.imshow(rng.random((10, 10)), id="my_image")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"
        assert "my_image" in recorded


class TestMultiPanelCallIdMatching:
    """Test call_id matching for multi-panel figures."""

    def test_3x3_grid_call_ids_match(self):
        """Test that 3x3 grid correctly maps call_ids."""
        fig, axes = fr.subplots(3, 3)

        # Each panel has a different plot type with custom id
        axes[0, 0].plot([1, 2, 3], [1, 4, 9], id="plot_0_0")
        axes[0, 1].scatter([1, 2, 3], [1, 4, 9], id="scatter_0_1")
        axes[0, 2].bar(["A", "B"], [3, 5], id="bar_0_2")
        axes[1, 0].fill([0, 1, 1, 0], [0, 0, 1, 1], id="fill_1_0")
        axes[1, 1].errorbar([1, 2], [1, 4], yerr=[0.5, 0.5], id="errorbar_1_1")
        axes[1, 2].fill_between([1, 2, 3], [0, 0, 0], [1, 4, 9], id="fillbetween_1_2")
        axes[2, 0].pie([30, 40, 30], id="pie_2_0")
        rng = np.random.default_rng(42)
        axes[2, 1].hist(rng.standard_normal(50), bins=5, id="hist_2_1")
        axes[2, 2].imshow(rng.random((5, 5)), id="imshow_2_2")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"

        # Verify all custom ids are recorded
        expected_ids = [
            "plot_0_0",
            "scatter_0_1",
            "bar_0_2",
            "fill_1_0",
            "errorbar_1_1",
            "fillbetween_1_2",
            "pie_2_0",
            "hist_2_1",
            "imshow_2_2",
        ]
        for expected_id in expected_ids:
            assert expected_id in recorded, f"{expected_id} not in recorded calls"

    def test_16_panel_grid_call_ids_match(self):
        """Test that 4x4 grid (16 panels) correctly maps call_ids.

        This tests the natural sorting fix for ax_10_0 vs ax_1_0.
        """
        fig, axes = fr.subplots(4, 4)

        # Plot in each panel with custom id encoding position
        for i in range(4):
            for j in range(4):
                axes[i, j].plot([1, 2], [1, 2], id=f"plot_{i}_{j}")

        color_map, recorded = get_hitmap_and_calls(fig)
        mismatches = check_call_ids_match(color_map, recorded)

        assert not mismatches, f"Mismatches: {mismatches}"

        # Verify all 16 plots are recorded with correct ids
        for i in range(4):
            for j in range(4):
                expected_id = f"plot_{i}_{j}"
                assert expected_id in recorded, f"{expected_id} not in recorded calls"


class TestReproducedFigureCallIdMatching:
    """Test call_id matching after save/reproduce cycle."""

    def test_reproduced_single_panel_call_ids_match(self):
        """Test call_ids match after save/reproduce for single panel."""
        fig, ax = fr.subplots(1, 1)
        ax.plot([1, 2, 3], [1, 4, 9], id="my_plot")
        ax.scatter([1, 2, 3], [9, 4, 1], id="my_scatter")

        # Save and reproduce
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.png"
            fr.save(fig, output, validate_error_level="warning")
            fig2, _ = fr.reproduce(output)

            color_map, recorded = get_hitmap_and_calls(fig2)
            mismatches = check_call_ids_match(color_map, recorded)

            assert not mismatches, f"Mismatches: {mismatches}"
            assert "my_plot" in recorded
            assert "my_scatter" in recorded

    def test_reproduced_multipanel_call_ids_match(self):
        """Test call_ids match after save/reproduce for multi-panel."""
        fig, axes = fr.subplots(3, 3)

        axes[0, 0].plot([1, 2], [1, 2], id="plot_a")
        axes[0, 1].scatter([1, 2], [1, 2], id="scatter_b")
        axes[0, 2].bar(["X", "Y"], [1, 2], id="bar_c")
        axes[1, 0].fill([0, 1, 1], [0, 0, 1], id="fill_d")
        axes[1, 1].errorbar([1, 2], [1, 2], yerr=[0.1, 0.1], id="errorbar_e")
        axes[1, 2].pie([50, 50], id="pie_f")
        rng = np.random.default_rng(42)
        axes[2, 0].hist(rng.random(50), id="hist_g")
        axes[2, 1].imshow(rng.random((5, 5)), id="imshow_h")
        axes[2, 2].fill_between([1, 2], [0, 0], [1, 1], id="fillbetween_i")

        # Save and reproduce
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.png"
            fr.save(fig, output, validate_error_level="warning")
            fig2, _ = fr.reproduce(output)

            color_map, recorded = get_hitmap_and_calls(fig2)
            mismatches = check_call_ids_match(color_map, recorded)

            assert not mismatches, f"Mismatches: {mismatches}"


class TestMultiLayerElements:
    """Test multi-layer elements like stackplot."""

    def test_stackplot_layers_have_layer_index(self):
        """Test that stackplot layers get layer_index for individual editing."""
        fig, ax = fr.subplots(1, 1)
        ax.stackplot([1, 2, 3], [1, 2, 3], [2, 3, 4], [3, 4, 5], id="my_stack")

        color_map, recorded = get_hitmap_and_calls(fig)

        # Check that stackplot layers have layer_index
        stack_elements = [
            (k, v) for k, v in color_map.items() if v.get("type") == "stackplot"
        ]
        assert (
            len(stack_elements) == 3
        ), f"Expected 3 stackplot layers, got {len(stack_elements)}"

        # Each layer should have a unique layer_index
        layer_indices = [v.get("layer_index") for _, v in stack_elements]
        assert set(layer_indices) == {
            0,
            1,
            2,
        }, f"Expected layer_indices 0,1,2, got {layer_indices}"

        # All layers should share the same call_id
        call_ids = [v.get("call_id") for _, v in stack_elements]
        assert all(
            cid == "my_stack" for cid in call_ids
        ), "All layers should have call_id 'my_stack'"


class TestNaturalSortingFix:
    """Test that natural sorting works for ax_key ordering."""

    def test_natural_sort_key(self):
        """Test natural sort function."""
        import re

        def natural_sort_key(s):
            return [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", s)]

        keys = ["ax_0_0", "ax_0_1", "ax_1_0", "ax_10_0", "ax_2_0", "ax_9_0"]
        sorted_keys = sorted(keys, key=natural_sort_key)

        expected = ["ax_0_0", "ax_0_1", "ax_1_0", "ax_2_0", "ax_9_0", "ax_10_0"]
        assert sorted_keys == expected, f"Got {sorted_keys}, expected {expected}"

    def test_detect_plot_types_uses_natural_sort(self):
        """Test that detect_plot_types uses natural sorting."""
        from figrecipe._editor._hitmap._detect import detect_plot_types

        # Create a figure with enough panels to trigger sorting issues
        fig, axes = fr.subplots(4, 4)  # 16 panels

        # Plot in each with distinct id
        for i in range(4):
            for j in range(4):
                axes[i, j].plot([1, 2], [1, 2], id=f"p{i}{j}")

        result = detect_plot_types(fig)

        # ax_idx 0-15 should all be present
        for ax_idx in range(16):
            assert ax_idx in result, f"ax_idx {ax_idx} not found in result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
