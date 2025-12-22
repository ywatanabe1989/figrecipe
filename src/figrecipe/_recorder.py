#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core recording functionality for figrecipe."""

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid

import matplotlib
import numpy as np


@dataclass
class CallRecord:
    """Record of a single plotting call."""

    id: str
    function: str
    args: List[Dict[str, Any]]
    kwargs: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ax_position: Tuple[int, int] = (0, 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "function": self.function,
            "args": self.args,
            "kwargs": self.kwargs,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], ax_position: Tuple[int, int] = (0, 0)) -> "CallRecord":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            function=data["function"],
            args=data["args"],
            kwargs=data["kwargs"],
            timestamp=data.get("timestamp", ""),
            ax_position=ax_position,
        )


@dataclass
class AxesRecord:
    """Record of all calls on a single axes."""

    position: Tuple[int, int]
    calls: List[CallRecord] = field(default_factory=list)
    decorations: List[CallRecord] = field(default_factory=list)

    def add_call(self, record: CallRecord) -> None:
        """Add a plotting call record."""
        self.calls.append(record)

    def add_decoration(self, record: CallRecord) -> None:
        """Add a decoration call (set_xlabel, etc.)."""
        self.decorations.append(record)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "calls": [c.to_dict() for c in self.calls],
            "decorations": [d.to_dict() for d in self.decorations],
        }


@dataclass
class FigureRecord:
    """Record of an entire figure."""

    id: str = field(default_factory=lambda: f"fig_{uuid.uuid4().hex[:8]}")
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    matplotlib_version: str = field(default_factory=lambda: matplotlib.__version__)
    figsize: Tuple[float, float] = (6.4, 4.8)
    dpi: int = 300
    axes: Dict[str, AxesRecord] = field(default_factory=dict)
    # Layout parameters (subplots_adjust)
    layout: Optional[Dict[str, float]] = None
    # Style parameters
    style: Optional[Dict[str, Any]] = None
    # Constrained layout flag
    constrained_layout: bool = False

    def get_axes_key(self, row: int, col: int) -> str:
        """Get dictionary key for axes at position."""
        return f"ax_{row}_{col}"

    def get_or_create_axes(self, row: int, col: int) -> AxesRecord:
        """Get or create axes record at position."""
        key = self.get_axes_key(row, col)
        if key not in self.axes:
            self.axes[key] = AxesRecord(position=(row, col))
        return self.axes[key]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "figrecipe": "1.0",
            "id": self.id,
            "created": self.created,
            "matplotlib_version": self.matplotlib_version,
            "figure": {
                "figsize": list(self.figsize),
                "dpi": self.dpi,
            },
            "axes": {k: v.to_dict() for k, v in self.axes.items()},
        }
        # Add layout if set
        if self.layout is not None:
            result["figure"]["layout"] = self.layout
        # Add style if set
        if self.style is not None:
            result["figure"]["style"] = self.style
        # Add constrained_layout if True
        if self.constrained_layout:
            result["figure"]["constrained_layout"] = True
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FigureRecord":
        """Create from dictionary."""
        fig_data = data.get("figure", {})
        record = cls(
            id=data.get("id", f"fig_{uuid.uuid4().hex[:8]}"),
            created=data.get("created", ""),
            matplotlib_version=data.get("matplotlib_version", ""),
            figsize=tuple(fig_data.get("figsize", [6.4, 4.8])),
            dpi=fig_data.get("dpi", 300),
            layout=fig_data.get("layout"),
            style=fig_data.get("style"),
            constrained_layout=fig_data.get("constrained_layout", False),
        )

        # Reconstruct axes
        for ax_key, ax_data in data.get("axes", {}).items():
            # Parse position from key like "ax_0_1"
            parts = ax_key.split("_")
            if len(parts) >= 3:
                row, col = int(parts[1]), int(parts[2])
            else:
                row, col = 0, 0

            ax_record = AxesRecord(position=(row, col))
            for call_data in ax_data.get("calls", []):
                ax_record.calls.append(CallRecord.from_dict(call_data, (row, col)))
            for dec_data in ax_data.get("decorations", []):
                ax_record.decorations.append(CallRecord.from_dict(dec_data, (row, col)))

            record.axes[ax_key] = ax_record

        return record


class Recorder:
    """Central recorder for tracking matplotlib calls."""

    # Plotting methods that create artists
    PLOTTING_METHODS = {
        "plot", "scatter", "bar", "barh", "hist", "hist2d",
        "boxplot", "violinplot", "pie", "errorbar", "fill",
        "fill_between", "fill_betweenx", "stackplot", "stem",
        "step", "imshow", "pcolor", "pcolormesh", "contour",
        "contourf", "quiver", "barbs", "streamplot", "hexbin",
        "tripcolor", "triplot", "tricontour", "tricontourf",
        "eventplot", "stairs", "ecdf", "matshow", "spy",
        "loglog", "semilogx", "semilogy", "acorr", "xcorr",
        "specgram", "psd", "csd", "cohere", "angle_spectrum",
        "magnitude_spectrum", "phase_spectrum",
    }

    # Decoration methods
    DECORATION_METHODS = {
        "set_xlabel", "set_ylabel", "set_title", "set_xlim",
        "set_ylim", "legend", "grid", "axhline", "axvline",
        "axhspan", "axvspan", "text", "annotate",
    }

    def __init__(self):
        self._figure_record: Optional[FigureRecord] = None
        self._method_counters: Dict[str, int] = {}

    def start_figure(
        self,
        figsize: Tuple[float, float] = (6.4, 4.8),
        dpi: int = 300,
    ) -> FigureRecord:
        """Start recording a new figure."""
        self._figure_record = FigureRecord(figsize=figsize, dpi=dpi)
        self._method_counters = {}
        return self._figure_record

    @property
    def figure_record(self) -> Optional[FigureRecord]:
        """Get current figure record."""
        return self._figure_record

    def _generate_call_id(self, method_name: str) -> str:
        """Generate unique call ID."""
        counter = self._method_counters.get(method_name, 0)
        self._method_counters[method_name] = counter + 1
        return f"{method_name}_{counter:03d}"

    def record_call(
        self,
        ax_position: Tuple[int, int],
        method_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        call_id: Optional[str] = None,
    ) -> CallRecord:
        """Record a plotting call.

        Parameters
        ----------
        ax_position : tuple
            (row, col) position of axes.
        method_name : str
            Name of the method called.
        args : tuple
            Positional arguments.
        kwargs : dict
            Keyword arguments.
        call_id : str, optional
            Custom ID for this call.

        Returns
        -------
        CallRecord
            The recorded call.
        """
        if self._figure_record is None:
            self.start_figure()

        # Generate ID if not provided
        if call_id is None:
            call_id = self._generate_call_id(method_name)

        # Process args into serializable format
        processed_args = self._process_args(args, method_name)

        # Filter kwargs to non-default only (if signature available)
        processed_kwargs = self._process_kwargs(kwargs, method_name)

        record = CallRecord(
            id=call_id,
            function=method_name,
            args=processed_args,
            kwargs=processed_kwargs,
            ax_position=ax_position,
        )

        # Add to appropriate axes
        ax_record = self._figure_record.get_or_create_axes(*ax_position)

        if method_name in self.DECORATION_METHODS:
            ax_record.add_decoration(record)
        else:
            ax_record.add_call(record)

        return record

    def _process_args(
        self,
        args: tuple,
        method_name: str,
    ) -> List[Dict[str, Any]]:
        """Process positional arguments for storage.

        Parameters
        ----------
        args : tuple
            Raw positional arguments.
        method_name : str
            Name of the method.

        Returns
        -------
        list
            Processed args with name and data.
        """
        from ._utils._numpy_io import should_store_inline, to_serializable

        processed = []
        # Simple arg names based on common patterns
        arg_names = self._get_arg_names(method_name, len(args))

        for i, (name, value) in enumerate(zip(arg_names, args)):
            if isinstance(value, np.ndarray):
                if should_store_inline(value):
                    processed.append({
                        "name": name,
                        "data": to_serializable(value),
                        "dtype": str(value.dtype),
                    })
                else:
                    # Mark for file storage (will be handled by serializer)
                    processed.append({
                        "name": name,
                        "data": "__FILE__",
                        "dtype": str(value.dtype),
                        "_array": value,  # Temporary, removed during serialization
                    })
            elif hasattr(value, "values"):  # pandas
                arr = np.asarray(value)
                if should_store_inline(arr):
                    processed.append({
                        "name": name,
                        "data": to_serializable(arr),
                        "dtype": str(arr.dtype),
                    })
                else:
                    processed.append({
                        "name": name,
                        "data": "__FILE__",
                        "dtype": str(arr.dtype),
                        "_array": arr,
                    })
            else:
                # Scalar or other serializable value
                try:
                    processed.append({
                        "name": name,
                        "data": value if self._is_serializable(value) else str(value),
                    })
                except (TypeError, ValueError):
                    processed.append({
                        "name": name,
                        "data": str(value),
                    })

        return processed

    def _get_arg_names(self, method_name: str, n_args: int) -> List[str]:
        """Get argument names for a method.

        Parameters
        ----------
        method_name : str
            Name of the method.
        n_args : int
            Number of arguments.

        Returns
        -------
        list
            List of argument names.
        """
        # Common patterns
        patterns = {
            "plot": ["x", "y", "fmt"],
            "scatter": ["x", "y", "s", "c"],
            "bar": ["x", "height", "width", "bottom"],
            "barh": ["y", "width", "height", "left"],
            "hist": ["x", "bins"],
            "imshow": ["X"],
            "contour": ["X", "Y", "Z", "levels"],
            "contourf": ["X", "Y", "Z", "levels"],
            "fill_between": ["x", "y1", "y2"],
            "errorbar": ["x", "y", "yerr", "xerr"],
            "text": ["x", "y", "s"],
            "annotate": ["text", "xy", "xytext"],
        }

        if method_name in patterns:
            names = patterns[method_name][:n_args]
            # Pad with generic names if needed
            while len(names) < n_args:
                names.append(f"arg{len(names)}")
            return names

        # Default generic names
        return [f"arg{i}" for i in range(n_args)]

    def _process_kwargs(
        self,
        kwargs: Dict[str, Any],
        method_name: str,
    ) -> Dict[str, Any]:
        """Process keyword arguments for storage.

        Parameters
        ----------
        kwargs : dict
            Raw keyword arguments.
        method_name : str
            Name of the method.

        Returns
        -------
        dict
            Processed kwargs (non-default only).
        """
        # Remove internal keys
        skip_keys = {"id", "track", "_array"}
        processed = {}

        for key, value in kwargs.items():
            if key in skip_keys:
                continue

            if self._is_serializable(value):
                processed[key] = value
            elif isinstance(value, np.ndarray):
                processed[key] = value.tolist()
            elif hasattr(value, "values"):
                processed[key] = np.asarray(value).tolist()
            else:
                # Try to convert to string
                try:
                    processed[key] = str(value)
                except Exception:
                    pass

        return processed

    def _is_serializable(self, value: Any) -> bool:
        """Check if value is directly serializable to YAML."""
        if value is None:
            return True
        if isinstance(value, (bool, int, float, str)):
            return True
        if isinstance(value, (list, tuple)):
            return all(self._is_serializable(v) for v in value)
        if isinstance(value, dict):
            return all(
                isinstance(k, str) and self._is_serializable(v)
                for k, v in value.items()
            )
        return False
