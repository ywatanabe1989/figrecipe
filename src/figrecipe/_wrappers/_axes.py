#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Axes that records all plotting calls."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

if TYPE_CHECKING:
    from .._recorder import Recorder


class RecordingAxes:
    """Wrapper around matplotlib Axes that records all calls.

    This wrapper intercepts calls to plotting methods and records them
    for later reproduction.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The underlying matplotlib axes.
    recorder : Recorder
        The recorder instance to log calls to.
    position : tuple
        (row, col) position in the figure grid.

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6], color='red', id='my_line')
    >>> # The call is recorded automatically
    """

    # Methods whose results can be referenced by other methods (e.g., clabel needs ContourSet)
    RESULT_REFERENCEABLE_METHODS = {"contour", "contourf"}
    # Methods that take results from other methods as arguments
    RESULT_REFERENCING_METHODS = {"clabel"}

    def __init__(
        self,
        ax: Axes,
        recorder: "Recorder",
        position: Tuple[int, int] = (0, 0),
    ):
        self._ax = ax
        self._recorder = recorder
        self._position = position
        self._track = True
        # Map matplotlib result objects (by id) to their source call_id
        self._result_refs: Dict[int, str] = {}

    @property
    def ax(self) -> Axes:
        """Get the underlying matplotlib axes."""
        return self._ax

    @property
    def position(self) -> Tuple[int, int]:
        """Get axes position in grid."""
        return self._position

    def __getattr__(self, name: str) -> Any:
        """Intercept attribute access to wrap methods.

        This is the core mechanism for recording calls.
        """
        attr = getattr(self._ax, name)

        # If it's a plotting or decoration method, wrap it
        if callable(attr) and name in (
            self._recorder.PLOTTING_METHODS | self._recorder.DECORATION_METHODS
        ):
            return self._create_recording_wrapper(name, attr)

        # For other methods/attributes, return as-is
        return attr

    def _create_recording_wrapper(self, method_name: str, method: callable):
        """Create a wrapper function that records the call."""
        from ._axes_helpers import record_call_with_color_capture

        def wrapper(
            *args,
            id: Optional[str] = None,
            track: bool = True,
            stats: Optional[Dict[str, Any]] = None,
            **kwargs,
        ):
            # Call matplotlib method (without stats - it's metadata only)
            result = method(*args, **kwargs)
            if self._track and track:
                # Re-add stats to kwargs for recording
                record_kwargs = kwargs.copy()
                if stats is not None:
                    record_kwargs["stats"] = stats
                record_call_with_color_capture(
                    self._recorder,
                    self._position,
                    method_name,
                    args,
                    record_kwargs,
                    result,
                    id,
                    self._result_refs,
                    self.RESULT_REFERENCING_METHODS,
                    self.RESULT_REFERENCEABLE_METHODS,
                )
            return result

        return wrapper

    def set_caption(self, caption: str) -> "RecordingAxes":
        """Set panel caption metadata (not rendered, stored in recipe).

        This is for storing a description for this panel/axis,
        typically used in multi-panel scientific figures
        (e.g., "(A) Control group measurements").

        Parameters
        ----------
        caption : str
            The panel caption text.

        Returns
        -------
        RecordingAxes
            Self for method chaining.

        Examples
        --------
        >>> fig, axes = fr.subplots(1, 2)
        >>> axes[0].set_caption("(A) Control group")
        >>> axes[1].set_caption("(B) Treatment group")
        """
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.caption = caption
        return self

    @property
    def panel_caption(self) -> Optional[str]:
        """Get the panel caption metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.caption

    def set_stats(self, stats: Dict[str, Any]) -> "RecordingAxes":
        """Set panel-level statistics metadata (not rendered, stored in recipe).

        This is for storing statistical summary or comparison results
        for this panel/axis, such as group means, sample sizes, or
        comparison p-values.

        Parameters
        ----------
        stats : dict
            Statistics dictionary. Common keys include:
            - n: sample size
            - mean: mean value
            - std: standard deviation
            - sem: standard error of the mean
            - comparisons: list of comparison results

        Returns
        -------
        RecordingAxes
            Self for method chaining.

        Examples
        --------
        >>> fig, axes = fr.subplots(1, 2)
        >>> axes[0].set_stats({"n": 50, "mean": 3.2, "std": 1.1})
        >>> axes[1].set_stats({
        ...     "n": 48,
        ...     "mean": 5.1,
        ...     "comparisons": [{"vs": "control", "p_value": 0.003}]
        ... })
        """
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.stats = stats
        return self

    @property
    def stats(self) -> Optional[Dict[str, Any]]:
        """Get the panel-level statistics metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.stats

    def no_record(self):
        """Context manager to temporarily disable recording.

        Examples
        --------
        >>> with ax.no_record():
        ...     ax.plot([1, 2, 3], [4, 5, 6])  # Not recorded
        """
        return _NoRecordContext(self)

    def record_seaborn_call(
        self,
        func_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        data_arrays: Dict[str, np.ndarray],
        call_id: Optional[str] = None,
    ) -> None:
        """Record a seaborn plotting call."""
        if not self._track:
            return

        from ._axes_seaborn import record_seaborn_call

        record_seaborn_call(
            self._recorder,
            self._position,
            func_name,
            args,
            kwargs,
            data_arrays,
            call_id,
        )

    # Expose common properties directly
    @property
    def figure(self):
        return self._ax.figure

    @property
    def xaxis(self):
        return self._ax.xaxis

    @property
    def yaxis(self):
        return self._ax.yaxis

    def pie(
        self,
        x,
        *,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Pie chart with automatic SCITEX styling."""
        from ._axes_plots import pie_plot

        return pie_plot(
            self._ax,
            x,
            self._recorder,
            self._position,
            self._track and track,
            id,
            **kwargs,
        )

    def imshow(
        self,
        X,
        *,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Display image with automatic SCITEX styling."""
        from ._axes_plots import imshow_plot

        return imshow_plot(
            self._ax,
            X,
            self._recorder,
            self._position,
            self._track and track,
            id,
            **kwargs,
        )

    def violinplot(
        self,
        dataset,
        positions=None,
        *,
        id: Optional[str] = None,
        track: bool = True,
        inner: Optional[str] = None,
        **kwargs,
    ):
        """Violin plot with support for inner display options."""
        from ._axes_plots import violinplot_plot

        return violinplot_plot(
            self._ax,
            dataset,
            positions,
            self._recorder,
            self._position,
            self._track and track,
            id,
            inner,
            **kwargs,
        )

    # Methods that should not be recorded
    def get_xlim(self):
        return self._ax.get_xlim()

    def get_ylim(self):
        return self._ax.get_ylim()

    def get_xlabel(self):
        return self._ax.get_xlabel()

    def get_ylabel(self):
        return self._ax.get_ylabel()

    def get_title(self):
        return self._ax.get_title()

    def graph(
        self,
        G,
        *,
        preset: Optional[str] = None,
        layout: Optional[str] = None,
        pos=None,
        seed: int = 42,
        # Node styling
        node_size=None,
        node_color=None,
        node_alpha: Optional[float] = None,
        node_shape: Optional[str] = None,
        node_edgecolors: Optional[str] = None,
        node_linewidths: Optional[float] = None,
        # Edge styling
        edge_width=None,
        edge_color=None,
        edge_alpha: Optional[float] = None,
        edge_style: Optional[str] = None,
        arrows=None,
        arrowsize: Optional[float] = None,
        arrowstyle: Optional[str] = None,
        connectionstyle: Optional[str] = None,
        # Labels
        labels=None,
        font_size: Optional[float] = None,
        font_color: Optional[str] = None,
        font_weight: Optional[str] = None,
        font_family: Optional[str] = None,
        # Colormap
        colormap: Optional[str] = None,
        vmin=None,
        vmax=None,
        # Recording
        id: Optional[str] = None,
        track: bool = True,
        **layout_kwargs,
    ):
        """Draw a NetworkX graph with publication-quality styling.

        Parameters
        ----------
        G : networkx.Graph or networkx.DiGraph
            The graph to draw.
        layout : str
            Layout algorithm: 'spring', 'circular', 'kamada_kawai', 'shell',
            'spectral', 'random', 'planar', 'spiral', 'hierarchical'.
        pos : dict, optional
            Pre-computed node positions {node: (x, y)}.
        seed : int
            Random seed for layout reproducibility.
        node_size : str, callable, or float
            Node sizes. Can be attribute name ('degree'), callable, or scalar.
        node_color : str, callable, or any
            Node colors. Can be attribute name, callable, color name, or array.
        node_alpha : float
            Node transparency (default 0.8).
        edge_width : str, callable, or float
            Edge widths. Can be attribute name ('weight'), callable, or scalar.
        edge_color : str, callable, or any
            Edge colors.
        edge_alpha : float
            Edge transparency (default 0.4).
        arrows : bool, optional
            Draw arrows for directed graphs. Auto-detected if None.
        arrowsize : float
            Arrow head size for directed edges.
        labels : bool, dict, or str
            Node labels. True for node IDs, dict for custom, str for attribute.
        font_size : float
            Label font size (default 6pt for scitex).
        colormap : str
            Matplotlib colormap for numeric node colors.
        preset : str, optional
            Built-in preset: 'default', 'minimal', 'citation', 'dependency'.
        id : str, optional
            Unique identifier for this plot call.
        track : bool
            Whether to record this call for reproducibility.
        **layout_kwargs
            Additional kwargs passed to layout algorithm.

        Returns
        -------
        dict
            Dictionary with 'pos', 'node_collection', 'edge_collection'.

        Examples
        --------
        >>> import networkx as nx
        >>> import figrecipe as fr
        >>> G = nx.karate_club_graph()
        >>> fig, ax = fr.subplots()
        >>> ax.graph(G, node_color='club', node_size='degree')
        >>> fr.save(fig, 'network.png')
        """
        try:
            from .._graph import draw_graph, graph_to_record
            from .._graph_presets import get_preset
        except ImportError as e:
            if "networkx" in str(e):
                raise ImportError(
                    "Graph visualization requires networkx. Install with:\n"
                    "  pip install figrecipe[graph]\n"
                    "or:\n"
                    "  pip install networkx"
                ) from None
            raise

        # Default values
        defaults = {
            "layout": "spring",
            "node_size": 100,
            "node_color": "#3498db",
            "node_alpha": 0.8,
            "node_shape": "o",
            "node_edgecolors": "white",
            "node_linewidths": 0.5,
            "edge_width": 1.0,
            "edge_color": "gray",
            "edge_alpha": 0.4,
            "edge_style": "solid",
            "arrowsize": 10,
            "arrowstyle": "-|>",
            "connectionstyle": "arc3,rad=0.0",
            "labels": False,
            "font_size": 6,
            "font_color": "black",
            "font_weight": "normal",
            "font_family": "sans-serif",
            "colormap": "viridis",
        }

        # Start with defaults
        kwargs = defaults.copy()

        # Overlay preset values
        if preset:
            preset_kwargs = get_preset(preset)
            kwargs.update(preset_kwargs)

        # Overlay explicit args (only if not None)
        explicit = {
            "layout": layout,
            "node_size": node_size,
            "node_color": node_color,
            "node_alpha": node_alpha,
            "node_shape": node_shape,
            "node_edgecolors": node_edgecolors,
            "node_linewidths": node_linewidths,
            "edge_width": edge_width,
            "edge_color": edge_color,
            "edge_alpha": edge_alpha,
            "edge_style": edge_style,
            "arrows": arrows,
            "arrowsize": arrowsize,
            "arrowstyle": arrowstyle,
            "connectionstyle": connectionstyle,
            "labels": labels,
            "font_size": font_size,
            "font_color": font_color,
            "font_weight": font_weight,
            "font_family": font_family,
            "colormap": colormap,
            "vmin": vmin,
            "vmax": vmax,
        }
        for key, value in explicit.items():
            if value is not None:
                kwargs[key] = value

        # Draw the graph
        result = draw_graph(
            self._ax,
            G,
            pos=pos,
            seed=seed,
            **kwargs,
            **layout_kwargs,
        )

        # Record for reproducibility
        if self._track and track:
            call_id = id if id else self._recorder._generate_call_id("graph")

            # Build style kwargs for recording (replace callables with marker)
            record_style = kwargs.copy()
            record_style["seed"] = seed
            record_style["preset"] = preset
            for key in ["node_size", "node_color", "edge_width", "edge_color"]:
                if callable(record_style.get(key)):
                    record_style[key] = "custom"

            # Serialize graph data for recipe
            graph_record = graph_to_record(G, pos=result["pos"], **record_style)

            from .._recorder import CallRecord

            record = CallRecord(
                id=call_id,
                function="graph",
                args=[],
                kwargs={"graph_data": graph_record},
                ax_position=self._position,
            )
            ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
            ax_record.add_call(record)

        return result

    def joyplot(
        self,
        arrays,
        *,
        overlap: float = 0.5,
        fill_alpha: float = 0.7,
        line_alpha: float = 1.0,
        colors=None,
        labels=None,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Create a joyplot (ridgeline plot) for distribution comparison."""
        from ._axes_plots import joyplot_plot

        return joyplot_plot(
            self._ax,
            self,
            arrays,
            self._recorder,
            self._position,
            self._track and track,
            id,
            overlap,
            fill_alpha,
            line_alpha,
            colors,
            labels,
            **kwargs,
        )

    def swarmplot(
        self,
        data,
        positions=None,
        *,
        size: float = None,
        color=None,
        alpha: float = 0.7,
        jitter: float = 0.3,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Create a swarm plot (beeswarm plot) showing individual data points."""
        from ._axes_plots import swarmplot_plot

        return swarmplot_plot(
            self._ax,
            data,
            positions,
            self._recorder,
            self._position,
            self._track and track,
            id,
            size,
            color,
            alpha,
            jitter,
            **kwargs,
        )

    @property
    def caption(self) -> Optional[str]:
        """Get the panel caption metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.caption

    def generate_panel_caption(
        self, label: Optional[str] = None, style: str = "publication"
    ) -> str:
        """Generate a caption for this panel from stats metadata."""
        from ._caption_generator import generate_panel_caption

        return generate_panel_caption(label=label, stats=self.stats, style=style)

    def add_stat_annotation(
        self,
        x1: float,
        x2: float,
        p_value: Optional[float] = None,
        text: Optional[str] = None,
        y: Optional[float] = None,
        style: str = "stars",
        bracket_height: Optional[float] = None,
        text_offset: Optional[float] = None,
        color: Optional[str] = None,
        linewidth: Optional[float] = None,
        fontsize: Optional[float] = None,
        fontweight: Optional[str] = None,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Add a statistical comparison annotation (bracket with stars/p-value).

        Parameters
        ----------
        x1, x2 : float
            X positions of the two groups being compared.
        p_value : float, optional
            P-value for automatic star conversion.
        text : str, optional
            Custom text (overrides p_value formatting).
        y : float, optional
            Y position for bracket (auto-calculated if None).
        style : str
            "stars", "p_value", "both", or "bracket_only".
        """
        from ._stat_annotation import draw_stat_annotation

        # Draw the annotation
        artists = draw_stat_annotation(
            self._ax,
            x1,
            x2,
            y=y,
            text=text,
            p_value=p_value,
            style=style,
            bracket_height=bracket_height,
            text_offset=text_offset,
            color=color,
            linewidth=linewidth,
            fontsize=fontsize,
            fontweight=fontweight,
            **kwargs,
        )

        # Record if tracking
        if self._track and track:
            call_id = id if id else self._recorder._generate_call_id("stat_annotation")
            record_kwargs = {
                "x1": x1,
                "x2": x2,
                "p_value": p_value,
                "text": text,
                "y": y,
                "style": style,
                "bracket_height": bracket_height,
                "text_offset": text_offset,
                "color": color,
                "linewidth": linewidth,
                "fontsize": fontsize,
            }
            record_kwargs.update(kwargs)
            # Remove None values
            record_kwargs = {k: v for k, v in record_kwargs.items() if v is not None}

            from .._recorder import CallRecord

            record = CallRecord(
                id=call_id,
                function="stat_annotation",
                args=[],
                kwargs=record_kwargs,
                ax_position=self._position,
            )
            ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
            ax_record.add_decoration(record)

        return artists


class _NoRecordContext:
    """Context manager to temporarily disable recording."""

    def __init__(self, axes: RecordingAxes):
        self._axes = axes
        self._original_track = axes._track

    def __enter__(self):
        self._axes._track = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._axes._track = self._original_track
        return False
