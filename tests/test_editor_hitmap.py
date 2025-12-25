#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for hitmap call_id assignment across all plot types.

These tests verify that all plot types correctly receive call_ids
in the hitmap color_map, which is essential for the editor to
display properties for selected elements.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from figrecipe._params import PLOTTING_METHODS

# Test data generators for each plotting method
PLOT_TEST_DATA = {
    "plot": lambda ax: ax.plot([1, 2, 3], [1, 4, 9]),
    "scatter": lambda ax: ax.scatter([1, 2, 3], [1, 4, 9]),
    "bar": lambda ax: ax.bar(["A", "B"], [3, 5]),
    "barh": lambda ax: ax.barh(["A", "B"], [3, 5]),
    "hist": lambda ax: ax.hist(np.random.randn(100), bins=10),
    "hist2d": lambda ax: ax.hist2d(np.random.randn(100), np.random.randn(100), bins=10),
    "boxplot": lambda ax: ax.boxplot([[1, 2, 3], [2, 3, 4]]),
    "violinplot": lambda ax: ax.violinplot([[1, 2, 3], [2, 3, 4]]),
    "pie": lambda ax: ax.pie([30, 40, 30]),
    "errorbar": lambda ax: ax.errorbar([1, 2, 3], [1, 4, 9], yerr=[0.5, 0.5, 0.5]),
    "fill": lambda ax: ax.fill([0, 1, 1, 0], [0, 0, 1, 1]),
    "fill_between": lambda ax: ax.fill_between([1, 2, 3], [0, 0, 0], [1, 4, 9]),
    "fill_betweenx": lambda ax: ax.fill_betweenx([1, 2, 3], [0, 0, 0], [1, 4, 9]),
    "stackplot": lambda ax: ax.stackplot([1, 2, 3], [1, 2, 3], [2, 3, 4]),
    "stem": lambda ax: ax.stem([1, 2, 3], [1, 4, 9]),
    "step": lambda ax: ax.step([1, 2, 3], [1, 4, 9]),
    "imshow": lambda ax: ax.imshow(np.random.rand(10, 10)),
    "pcolor": lambda ax: ax.pcolor(np.random.rand(5, 5)),
    "pcolormesh": lambda ax: ax.pcolormesh(np.random.rand(5, 5)),
    "contour": lambda ax: ax.contour(
        *np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20)),
        np.random.rand(20, 20),
    ),
    "contourf": lambda ax: ax.contourf(
        *np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20)),
        np.random.rand(20, 20),
    ),
    "quiver": lambda ax: ax.quiver([0, 1], [0, 1], [1, 1], [1, 0]),
    "barbs": lambda ax: ax.barbs([0, 1], [0, 1], [10, 20], [5, 10]),
    "streamplot": lambda ax: ax.streamplot(
        np.linspace(-2, 2, 10),
        np.linspace(-2, 2, 10),
        np.ones((10, 10)),
        np.ones((10, 10)),
    ),
    "hexbin": lambda ax: ax.hexbin(
        np.random.randn(100), np.random.randn(100), gridsize=5
    ),
    "tripcolor": lambda ax: ax.tripcolor([0, 1, 0.5], [0, 0, 1], [1, 2, 3]),
    "triplot": lambda ax: ax.triplot([0, 1, 0.5], [0, 0, 1]),
    "tricontour": lambda ax: ax.tricontour(
        [0, 1, 0.5, 0.5], [0, 0, 1, 0.5], [1, 2, 3, 2]
    ),
    "tricontourf": lambda ax: ax.tricontourf(
        [0, 1, 0.5, 0.5], [0, 0, 1, 0.5], [1, 2, 3, 2]
    ),
    "eventplot": lambda ax: ax.eventplot([[1, 2, 3], [2, 3, 4]]),
    "stairs": lambda ax: ax.stairs([1, 4, 9], [0, 1, 2, 3]),
    "ecdf": lambda ax: ax.ecdf(np.random.randn(100)),
    "matshow": lambda ax: ax.matshow(np.random.rand(5, 5)),
    "spy": lambda ax: ax.spy(np.eye(5)),
    "loglog": lambda ax: ax.loglog([1, 10, 100], [1, 100, 10000]),
    "semilogx": lambda ax: ax.semilogx([1, 10, 100], [1, 2, 3]),
    "semilogy": lambda ax: ax.semilogy([1, 2, 3], [1, 10, 100]),
    "acorr": lambda ax: ax.acorr(np.random.randn(100)),
    "xcorr": lambda ax: ax.xcorr(np.random.randn(100), np.random.randn(100)),
    "specgram": lambda ax: ax.specgram(np.random.randn(1000), Fs=1000, NFFT=256),
    "psd": lambda ax: ax.psd(np.random.randn(1000), Fs=1000, NFFT=256),
    "csd": lambda ax: ax.csd(
        np.random.randn(1000), np.random.randn(1000), Fs=1000, NFFT=256
    ),
    "cohere": lambda ax: ax.cohere(
        np.random.randn(1000), np.random.randn(1000), Fs=1000, NFFT=256
    ),
    "angle_spectrum": lambda ax: ax.angle_spectrum(np.random.randn(256)),
    "magnitude_spectrum": lambda ax: ax.magnitude_spectrum(np.random.randn(256)),
    "phase_spectrum": lambda ax: ax.phase_spectrum(np.random.randn(256)),
}

# Plot types that don't yet have hitmap element detection
HITMAP_NOT_IMPLEMENTED = {
    "barbs",
    "ecdf",
    "fill_betweenx",
    "hexbin",
    "loglog",
    "pcolor",
    "semilogx",
    "semilogy",
    "stackplot",
    "stairs",
    "step",
    "tricontour",
    "tricontourf",
    "tripcolor",
    "triplot",
}


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


def _generate_hitmap(fig):
    """Helper to generate hitmap and return color_map."""
    from figrecipe._editor._hitmap_main import generate_hitmap

    _, color_map = generate_hitmap(fig)
    return color_map


def _get_call_ids_by_type(color_map):
    """Extract call_ids grouped by element type."""
    by_type = {}
    for key, val in color_map.items():
        t = val.get("type", "unknown")
        cid = val.get("call_id")
        if t not in by_type:
            by_type[t] = set()
        if cid:
            by_type[t].add(cid)
    return by_type


class TestHitmapSpecialCases:
    """Test special hitmap behaviors."""

    def test_custom_id_preserved(self):
        """Test that custom id is preserved."""
        import figrecipe as fr

        fig, ax = fr.subplots(1, 1)
        ax.plot([1, 2, 3], [1, 4, 9], id="my_custom_plot")

        color_map = _generate_hitmap(fig)
        call_ids = _get_call_ids_by_type(color_map)

        assert "line" in call_ids
        assert "my_custom_plot" in call_ids["line"]

    def test_pie_wedges_share_call_id(self):
        """Test that all pie wedges share same call_id."""
        import figrecipe as fr

        fig, ax = fr.subplots(1, 1)
        ax.pie([30, 40, 30])

        color_map = _generate_hitmap(fig)
        pie_elements = [v for v in color_map.values() if v.get("type") == "pie"]

        assert len(pie_elements) == 3
        call_ids_set = {e.get("call_id") for e in pie_elements}
        assert len(call_ids_set) == 1

    def test_multipanel_grid_call_ids(self):
        """Test that 3x3 grid correctly maps call_ids to ax_idx."""
        import figrecipe as fr

        fig, axes = fr.subplots(3, 3, figsize=(10, 10))

        axes[0, 0].plot([1, 2, 3], [1, 4, 9])
        axes[0, 1].scatter([1, 2, 3], [1, 4, 9])
        axes[0, 2].bar(["A", "B"], [3, 5])
        axes[1, 0].hist(np.random.randn(50), bins=10)
        axes[1, 1].imshow(np.random.rand(5, 5))
        X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))
        axes[1, 2].contourf(X, Y, X**2 + Y**2)
        axes[2, 0].specgram(np.random.randn(1000), Fs=1000, NFFT=256)
        axes[2, 1].quiver([0, 1], [0, 1], [1, 1], [1, 0])
        axes[2, 2].pie([30, 40, 30])

        color_map = _generate_hitmap(fig)
        call_ids = _get_call_ids_by_type(color_map)

        expected = {
            "line": "plot_000",
            "scatter": "scatter_000",
            "bar": "bar_000",
            "hist": "hist_000",
            "image": {"imshow_000", "specgram_000"},
            "contour": "contourf_000",
            "quiver": "quiver_000",
            "pie": "pie_000",
        }

        for plot_type, expected_id in expected.items():
            assert plot_type in call_ids
            if isinstance(expected_id, set):
                assert expected_id.issubset(call_ids[plot_type])
            else:
                assert expected_id in call_ids[plot_type]

    def test_ax_idx_mapping_correctness(self):
        """Test ax_idx is correctly computed from row,col format."""
        from figrecipe._editor._hitmap._detect import detect_plot_types

        class MockCall:
            def __init__(self, func, id):
                self.function = func
                self.id = id

        class MockAxRecord:
            def __init__(self, calls):
                self.calls = calls

        class MockRecord:
            def __init__(self):
                self.axes = {
                    f"ax_{r}_{c}": MockAxRecord(
                        [MockCall(f"plot{r}{c}", f"plot{r}{c}_000")]
                    )
                    for r in range(3)
                    for c in range(3)
                }

        class MockAx:
            def __init__(self):
                pass

            def get_position(self):
                class Pos:
                    x0 = 0
                    y0 = 0
                    width = 0.3
                    height = 0.3

                return Pos()

        class MockFig:
            def __init__(self):
                self.record = MockRecord()
                self._axes = [MockAx() for _ in range(9)]
                self.fig = self  # detect_plot_types checks for fig.fig

            def get_axes(self):
                return self._axes

        fig = MockFig()
        result = detect_plot_types(fig)

        # 3x3 grid should have ax_idx 0-8
        for ax_idx in range(9):
            assert ax_idx in result, f"ax_idx {ax_idx} not found"


class TestAllPlottingMethodsRecording:
    """Systematic test for ALL registered plotting methods."""

    @pytest.mark.parametrize("method_name", sorted(PLOT_TEST_DATA.keys()))
    def test_method_is_recorded(self, method_name):
        """Test that method call is recorded with correct call_id."""
        import figrecipe as fr

        fig, ax = fr.subplots(1, 1)
        PLOT_TEST_DATA[method_name](ax)

        calls = list(fig.record.axes.values())[0].calls
        recorded_funcs = [c.function for c in calls]
        assert method_name in recorded_funcs

        call = next(c for c in calls if c.function == method_name)
        assert call.id.startswith(f"{method_name}_")

    @pytest.mark.parametrize("method_name", sorted(PLOT_TEST_DATA.keys()))
    def test_method_generates_hitmap_elements(self, method_name):
        """Test that method generates hitmap elements."""
        import figrecipe as fr

        if method_name in HITMAP_NOT_IMPLEMENTED:
            pytest.skip(f"Hitmap not implemented for {method_name}")

        fig, ax = fr.subplots(1, 1)
        PLOT_TEST_DATA[method_name](ax)

        color_map = _generate_hitmap(fig)
        assert len(color_map) > 0, f"{method_name} generated no hitmap elements"

    def test_all_plotting_methods_covered(self):
        """Verify PLOT_TEST_DATA covers all PLOTTING_METHODS."""
        missing = PLOTTING_METHODS - set(PLOT_TEST_DATA.keys())
        assert not missing, f"Missing test data for: {missing}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
