#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the recorder module."""

import numpy as np

from figrecipe._recorder import CallRecord, FigureRecord, Recorder


class TestCallRecord:
    """Tests for CallRecord dataclass."""

    def test_create_call_record(self):
        """Test creating a call record."""
        record = CallRecord(
            id="plot_001",
            function="plot",
            args=[{"name": "x", "data": [1, 2, 3]}],
            kwargs={"color": "red"},
        )
        assert record.id == "plot_001"
        assert record.function == "plot"
        assert len(record.args) == 1
        assert record.kwargs["color"] == "red"

    def test_to_dict(self):
        """Test converting to dictionary."""
        record = CallRecord(
            id="scatter_001",
            function="scatter",
            args=[],
            kwargs={"s": 10},
        )
        d = record.to_dict()
        assert d["id"] == "scatter_001"
        assert d["function"] == "scatter"
        assert d["kwargs"]["s"] == 10

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "hist_001",
            "function": "hist",
            "args": [{"name": "x", "data": [1, 2, 3]}],
            "kwargs": {"bins": 10},
        }
        record = CallRecord.from_dict(data)
        assert record.id == "hist_001"
        assert record.function == "hist"
        assert record.kwargs["bins"] == 10


class TestFigureRecord:
    """Tests for FigureRecord dataclass."""

    def test_create_figure_record(self):
        """Test creating a figure record."""
        record = FigureRecord(figsize=(10, 6), dpi=100)
        assert record.figsize == (10, 6)
        assert record.dpi == 100
        assert len(record.axes) == 0

    def test_get_or_create_axes(self):
        """Test getting or creating axes."""
        record = FigureRecord()
        ax = record.get_or_create_axes(0, 0)
        assert ax.position == (0, 0)
        assert "ax_0_0" in record.axes

        # Getting same axes again should return same object
        ax2 = record.get_or_create_axes(0, 0)
        assert ax is ax2

    def test_to_dict_and_from_dict(self):
        """Test round-trip serialization."""
        record = FigureRecord(figsize=(8, 6), dpi=150)
        ax = record.get_or_create_axes(0, 0)
        ax.add_call(
            CallRecord(
                id="plot_001",
                function="plot",
                args=[],
                kwargs={"color": "blue"},
            )
        )

        # Convert to dict and back
        d = record.to_dict()
        restored = FigureRecord.from_dict(d)

        assert restored.figsize == (8, 6)
        assert restored.dpi == 150
        assert "ax_0_0" in restored.axes
        assert len(restored.axes["ax_0_0"].calls) == 1


class TestRecorder:
    """Tests for Recorder class."""

    def test_start_figure(self):
        """Test starting a new figure."""
        recorder = Recorder()
        record = recorder.start_figure(figsize=(12, 8), dpi=200)
        assert record.figsize == (12, 8)
        assert record.dpi == 200

    def test_record_call(self):
        """Test recording a call."""
        recorder = Recorder()
        recorder.start_figure()

        call = recorder.record_call(
            ax_position=(0, 0),
            method_name="plot",
            args=(np.array([1, 2, 3]), np.array([4, 5, 6])),
            kwargs={"color": "red"},
        )

        assert call.id == "plot_000"
        assert call.function == "plot"
        assert call.kwargs["color"] == "red"

    def test_record_call_with_custom_id(self):
        """Test recording a call with custom ID."""
        recorder = Recorder()
        recorder.start_figure()

        call = recorder.record_call(
            ax_position=(0, 0),
            method_name="scatter",
            args=(),
            kwargs={},
            call_id="my_scatter",
        )

        assert call.id == "my_scatter"

    def test_auto_increment_ids(self):
        """Test that IDs auto-increment."""
        recorder = Recorder()
        recorder.start_figure()

        call1 = recorder.record_call((0, 0), "plot", (), {})
        call2 = recorder.record_call((0, 0), "plot", (), {})
        call3 = recorder.record_call((0, 0), "scatter", (), {})

        assert call1.id == "plot_000"
        assert call2.id == "plot_001"
        assert call3.id == "scatter_000"

    def test_record_to_correct_axes(self):
        """Test that calls are recorded to correct axes."""
        recorder = Recorder()
        recorder.start_figure()

        recorder.record_call((0, 0), "plot", (), {})
        recorder.record_call((0, 1), "scatter", (), {})
        recorder.record_call((1, 0), "bar", (), {})

        record = recorder.figure_record
        assert len(record.axes["ax_0_0"].calls) == 1
        assert len(record.axes["ax_0_1"].calls) == 1
        assert len(record.axes["ax_1_0"].calls) == 1
