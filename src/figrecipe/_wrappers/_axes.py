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
        """Create a wrapper function that records the call.

        Parameters
        ----------
        method_name : str
            Name of the method.
        method : callable
            The original method.

        Returns
        -------
        callable
            Wrapped method that records calls.
        """

        def wrapper(*args, id: Optional[str] = None, track: bool = True, **kwargs):
            # Call the original method first (without our custom kwargs)
            result = method(*args, **kwargs)

            # Record the call if tracking is enabled
            if self._track and track:
                # Capture actual colors from result for plotting methods
                # that use matplotlib's color cycle
                recorded_kwargs = kwargs.copy()
                if method_name in (
                    "plot",
                    "scatter",
                    "bar",
                    "barh",
                    "step",
                    "fill_between",
                ):
                    # Check if fmt string already specifies color (e.g., "b-", "r--")
                    has_fmt_color = self._args_have_fmt_color(args)
                    if (
                        "color" not in recorded_kwargs
                        and "c" not in recorded_kwargs
                        and not has_fmt_color
                    ):
                        actual_color = self._extract_color_from_result(
                            method_name, result
                        )
                        if actual_color is not None:
                            recorded_kwargs["color"] = actual_color

                # Process args to detect result references (e.g., clabel's ContourSet)
                processed_args = self._process_result_refs_in_args(args, method_name)

                call_record = self._recorder.record_call(
                    ax_position=self._position,
                    method_name=method_name,
                    args=processed_args,
                    kwargs=recorded_kwargs,
                    call_id=id,
                )

                # Store result reference for methods whose results can be used later
                if method_name in self.RESULT_REFERENCEABLE_METHODS:
                    import builtins

                    self._result_refs[builtins.id(result)] = call_record.id

            return result

        return wrapper

    def _process_result_refs_in_args(self, args: tuple, method_name: str) -> tuple:
        """Process args to replace matplotlib objects with references.

        For methods like clabel that take a ContourSet as argument,
        replace the object with a reference to the original call_id.

        Parameters
        ----------
        args : tuple
            Original arguments.
        method_name : str
            Name of the method.

        Returns
        -------
        tuple
            Processed args with references.
        """
        if method_name not in self.RESULT_REFERENCING_METHODS:
            return args

        import builtins

        processed = []
        for i, arg in enumerate(args):
            obj_id = builtins.id(arg)
            if obj_id in self._result_refs:
                # This arg is a reference to a previous call's result
                processed.append({"__ref__": self._result_refs[obj_id]})
            else:
                processed.append(arg)
        return tuple(processed)

    def _args_have_fmt_color(self, args: tuple) -> bool:
        """Check if args contain a matplotlib fmt string with color specifier.

        Fmt strings like "b-", "r--", "go" contain color codes (b,g,r,c,m,y,k,w).

        Parameters
        ----------
        args : tuple
            Arguments passed to plot method.

        Returns
        -------
        bool
            True if a fmt string with color is found.
        """
        color_codes = set("bgrcmykw")
        for arg in args:
            if isinstance(arg, str) and len(arg) >= 1 and len(arg) <= 4:
                # Fmt strings are short (e.g., "b-", "r--", "go", "k:")
                if arg[0] in color_codes:
                    return True
        return False

    def _extract_color_from_result(self, method_name: str, result) -> Optional[str]:
        """Extract actual color used from plot result.

        Parameters
        ----------
        method_name : str
            Name of the plotting method.
        result : Any
            Return value from the plotting method.

        Returns
        -------
        str or None
            The color used, or None if not extractable.
        """
        try:
            if method_name == "plot":
                # plot() returns list of Line2D
                if result and hasattr(result[0], "get_color"):
                    return result[0].get_color()
            elif method_name == "scatter":
                # scatter() returns PathCollection
                if hasattr(result, "get_facecolor"):
                    fc = result.get_facecolor()
                    if len(fc) > 0:
                        # Convert RGBA to hex
                        import matplotlib.colors as mcolors

                        return mcolors.to_hex(fc[0])
            elif method_name in ("bar", "barh"):
                # bar() returns BarContainer
                if hasattr(result, "patches") and result.patches:
                    fc = result.patches[0].get_facecolor()
                    import matplotlib.colors as mcolors

                    return mcolors.to_hex(fc)
            elif method_name == "step":
                # step() returns list of Line2D
                if result and hasattr(result[0], "get_color"):
                    return result[0].get_color()
            elif method_name == "fill_between":
                # fill_between() returns PolyCollection
                if hasattr(result, "get_facecolor"):
                    fc = result.get_facecolor()
                    if len(fc) > 0:
                        import matplotlib.colors as mcolors

                        return mcolors.to_hex(fc[0])
        except Exception:
            pass
        return None

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
        """Record a seaborn plotting call.

        Parameters
        ----------
        func_name : str
            Name of the seaborn function (e.g., 'scatterplot').
        args : tuple
            Processed positional arguments.
        kwargs : dict
            Processed keyword arguments.
        data_arrays : dict
            Dictionary of array data extracted from DataFrame/arrays.
        call_id : str, optional
            Custom ID for this call.
        """
        if not self._track:
            return

        from .._utils._numpy_io import should_store_inline, to_serializable

        # Generate call ID if not provided
        if call_id is None:
            call_id = self._recorder._generate_call_id(f"sns_{func_name}")

        # Process data arrays into args format
        processed_args = []
        for i, arg in enumerate(args):
            if arg == "__ARRAY__":
                key = f"_arg_{i}"
                if key in data_arrays:
                    arr = data_arrays[key]
                    if should_store_inline(arr):
                        processed_args.append(
                            {
                                "name": f"arg{i}",
                                "data": to_serializable(arr),
                                "dtype": str(arr.dtype),
                            }
                        )
                    else:
                        processed_args.append(
                            {
                                "name": f"arg{i}",
                                "data": "__FILE__",
                                "dtype": str(arr.dtype),
                                "_array": arr,
                            }
                        )
            else:
                processed_args.append(
                    {
                        "name": f"arg{i}",
                        "data": arg,
                    }
                )

        # Process DataFrame column data
        for key, arr in data_arrays.items():
            if key.startswith("_col_"):
                param_name = key[5:]  # Remove "_col_" prefix
                col_name = data_arrays.get(f"_colname_{param_name}", param_name)
                if should_store_inline(arr):
                    processed_args.append(
                        {
                            "name": col_name,
                            "param": param_name,
                            "data": to_serializable(arr),
                            "dtype": str(arr.dtype),
                        }
                    )
                else:
                    processed_args.append(
                        {
                            "name": col_name,
                            "param": param_name,
                            "data": "__FILE__",
                            "dtype": str(arr.dtype),
                            "_array": arr,
                        }
                    )

        # Process kwarg arrays
        processed_kwargs = dict(kwargs)
        for key, value in kwargs.items():
            if value == "__ARRAY__":
                arr_key = f"_kwarg_{key}"
                if arr_key in data_arrays:
                    arr = data_arrays[arr_key]
                    if should_store_inline(arr):
                        processed_kwargs[key] = to_serializable(arr)
                    else:
                        # Mark for file storage
                        processed_kwargs[key] = "__FILE__"
                        processed_kwargs[f"_array_{key}"] = arr

        # Create call record
        from .._recorder import CallRecord

        record = CallRecord(
            id=call_id,
            function=f"sns.{func_name}",
            args=processed_args,
            kwargs=processed_kwargs,
            ax_position=self._position,
        )

        # Add to axes record
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.add_call(record)

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
        """Pie chart with automatic SCITEX styling.

        Parameters
        ----------
        x : array-like
            Wedge sizes.
        id : str, optional
            Custom ID for this call.
        track : bool, optional
            Whether to record this call (default: True).
        **kwargs
            Additional arguments passed to matplotlib's pie.

        Returns
        -------
        tuple
            (patches, texts) or (patches, texts, autotexts) if autopct is set.
        """
        from ..styles import get_style
        from ..styles._style_applier import check_font

        # Call matplotlib's pie
        result = self._ax.pie(x, **kwargs)

        # Get style settings
        style = get_style()
        if style:
            pie_style = style.get("pie", {})
            text_pt = pie_style.get("text_pt", 6)
            show_axes = pie_style.get("show_axes", False)
            font_family = check_font(style.get("fonts", {}).get("family", "Arial"))

            # Apply text size to all pie text elements (labels and percentages)
            for text in self._ax.texts:
                text.set_fontsize(text_pt)
                text.set_fontfamily(font_family)

            # Hide axes if configured (default: hide for pie charts)
            if not show_axes:
                self._ax.set_xticks([])
                self._ax.set_yticks([])
                self._ax.set_xticklabels([])
                self._ax.set_yticklabels([])
                # Hide spines
                for spine in self._ax.spines.values():
                    spine.set_visible(False)

        # Record the call if tracking is enabled
        if self._track and track:
            self._recorder.record_call(
                ax_position=self._position,
                method_name="pie",
                args=(x,),
                kwargs=kwargs,
                call_id=id,
            )

        return result

    def imshow(
        self,
        X,
        *,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Display image with automatic SCITEX styling.

        Parameters
        ----------
        X : array-like
            Image data.
        id : str, optional
            Custom ID for this call.
        track : bool, optional
            Whether to record this call (default: True).
        **kwargs
            Additional arguments passed to matplotlib's imshow.

        Returns
        -------
        AxesImage
            The created image.
        """
        from ..styles import get_style

        # Call matplotlib's imshow
        result = self._ax.imshow(X, **kwargs)

        # Get style settings
        style = get_style()
        if style:
            imshow_style = style.get("imshow", {})
            show_axes = imshow_style.get("show_axes", True)
            show_labels = imshow_style.get("show_labels", True)

            # Hide axes if configured
            if not show_axes:
                self._ax.set_xticks([])
                self._ax.set_yticks([])
                self._ax.set_xticklabels([])
                self._ax.set_yticklabels([])
                # Hide spines
                for spine in self._ax.spines.values():
                    spine.set_visible(False)

            if not show_labels:
                self._ax.set_xlabel("")
                self._ax.set_ylabel("")

        # Record the call if tracking is enabled
        if self._track and track:
            self._recorder.record_call(
                ax_position=self._position,
                method_name="imshow",
                args=(X,),
                kwargs=kwargs,
                call_id=id,
            )

        return result

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
        """Violin plot with support for inner display options.

        Parameters
        ----------
        dataset : array-like
            Data to plot.
        positions : array-like, optional
            Position of each violin on x-axis.
        id : str, optional
            Custom ID for this call.
        track : bool, optional
            Whether to record this call (default: True).
        inner : str, optional
            Inner display type: "box", "quartile", "stick", "point", "swarm", or None.
            Default is from style config (SCITEX default: "box").
        **kwargs
            Additional arguments passed to matplotlib's violinplot.

        Returns
        -------
        dict
            Dictionary with violin parts (bodies, cbars, cmins, cmaxes, cmeans, cmedians).
        """
        from ..styles import get_style

        # Get style settings
        style = get_style()
        violin_style = style.get("violinplot", {}) if style else {}

        # Determine inner type (user kwarg > style config > default)
        if inner is None:
            inner = violin_style.get("inner", "box")

        # Get violin display options from style
        showmeans = kwargs.pop("showmeans", violin_style.get("showmeans", False))
        showmedians = kwargs.pop("showmedians", violin_style.get("showmedians", True))
        showextrema = kwargs.pop("showextrema", violin_style.get("showextrema", False))

        # Call matplotlib's violinplot
        result = self._ax.violinplot(
            dataset,
            positions=positions,
            showmeans=showmeans,
            showmedians=showmedians if inner not in ("box", "swarm") else False,
            showextrema=showextrema if inner not in ("box", "swarm") else False,
            **kwargs,
        )

        # Apply alpha from style to violin bodies
        alpha = violin_style.get("alpha", 0.7)
        if "bodies" in result:
            for body in result["bodies"]:
                body.set_alpha(alpha)

        # Overlay inner elements based on inner type
        if positions is None:
            positions = list(range(1, len(dataset) + 1))

        if inner == "box":
            self._add_violin_inner_box(dataset, positions, violin_style)
        elif inner == "swarm":
            self._add_violin_inner_swarm(dataset, positions, violin_style)
        elif inner == "quartile":
            # quartile lines are handled by showmedians + showextrema
            pass
        elif inner == "stick":
            self._add_violin_inner_stick(dataset, positions, violin_style)
        elif inner == "point":
            self._add_violin_inner_point(dataset, positions, violin_style)

        # Record the call if tracking is enabled
        if self._track and track:
            recorded_kwargs = kwargs.copy()
            recorded_kwargs["inner"] = inner
            recorded_kwargs["showmeans"] = showmeans
            recorded_kwargs["showmedians"] = showmedians
            recorded_kwargs["showextrema"] = showextrema

            self._recorder.record_call(
                ax_position=self._position,
                method_name="violinplot",
                args=(dataset,),
                kwargs=recorded_kwargs,
                call_id=id,
            )

        return result

    def _add_violin_inner_box(self, dataset, positions, style: Dict[str, Any]) -> None:
        """Add box plot inside violin.

        Parameters
        ----------
        dataset : array-like
            Data arrays for each violin.
        positions : array-like
            X positions of violins.
        style : dict
            Violin style configuration.
        """
        from ..styles._style_applier import mm_to_pt

        whisker_lw = mm_to_pt(style.get("whisker_mm", 0.2))
        median_size = mm_to_pt(style.get("median_mm", 0.8))

        for i, (data, pos) in enumerate(zip(dataset, positions)):
            data = np.asarray(data)
            q1, median, q3 = np.percentile(data, [25, 50, 75])
            iqr = q3 - q1
            whisker_low = max(data.min(), q1 - 1.5 * iqr)
            whisker_high = min(data.max(), q3 + 1.5 * iqr)

            # Draw box (Q1 to Q3)
            self._ax.vlines(
                pos, q1, q3, colors="black", linewidths=whisker_lw, zorder=3
            )
            # Draw whiskers
            self._ax.vlines(
                pos,
                whisker_low,
                q1,
                colors="black",
                linewidths=whisker_lw * 0.5,
                zorder=3,
            )
            self._ax.vlines(
                pos,
                q3,
                whisker_high,
                colors="black",
                linewidths=whisker_lw * 0.5,
                zorder=3,
            )
            # Draw median as a white dot with black edge
            self._ax.scatter(
                [pos],
                [median],
                s=median_size**2,
                c="white",
                edgecolors="black",
                linewidths=whisker_lw,
                zorder=4,
            )

    def _add_violin_inner_swarm(
        self, dataset, positions, style: Dict[str, Any]
    ) -> None:
        """Add swarm points inside violin.

        Parameters
        ----------
        dataset : array-like
            Data arrays for each violin.
        positions : array-like
            X positions of violins.
        style : dict
            Violin style configuration.
        """
        from ..styles._style_applier import mm_to_pt

        point_size = mm_to_pt(style.get("median_mm", 0.8))

        for data, pos in zip(dataset, positions):
            data = np.asarray(data)
            n = len(data)

            # Simple swarm: jitter x positions
            # More sophisticated swarm would avoid overlaps
            jitter = np.random.default_rng(42).uniform(-0.15, 0.15, n)
            x_positions = pos + jitter

            self._ax.scatter(
                x_positions, data, s=point_size**2, c="black", alpha=0.5, zorder=3
            )

    def _add_violin_inner_stick(
        self, dataset, positions, style: Dict[str, Any]
    ) -> None:
        """Add stick (line) markers inside violin for each data point.

        Parameters
        ----------
        dataset : array-like
            Data arrays for each violin.
        positions : array-like
            X positions of violins.
        style : dict
            Violin style configuration.
        """
        from ..styles._style_applier import mm_to_pt

        lw = mm_to_pt(style.get("whisker_mm", 0.2))

        for data, pos in zip(dataset, positions):
            data = np.asarray(data)
            # Draw short horizontal lines at each data point
            for val in data:
                self._ax.hlines(
                    val,
                    pos - 0.05,
                    pos + 0.05,
                    colors="black",
                    linewidths=lw * 0.5,
                    alpha=0.3,
                    zorder=3,
                )

    def _add_violin_inner_point(
        self, dataset, positions, style: Dict[str, Any]
    ) -> None:
        """Add point markers inside violin for each data point.

        Parameters
        ----------
        dataset : array-like
            Data arrays for each violin.
        positions : array-like
            X positions of violins.
        style : dict
            Violin style configuration.
        """
        from ..styles._style_applier import mm_to_pt

        point_size = mm_to_pt(style.get("median_mm", 0.8)) * 0.5

        for data, pos in zip(dataset, positions):
            data = np.asarray(data)
            x_positions = np.full_like(data, pos)
            self._ax.scatter(
                x_positions, data, s=point_size**2, c="black", alpha=0.3, zorder=3
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
        """Create a joyplot (ridgeline plot) for distribution comparison.

        Parameters
        ----------
        arrays : list of array-like or dict
            List of 1D arrays for each ridge. If dict, uses values.
        overlap : float, default 0.5
            Amount of overlap between ridges (0 = no overlap, 1 = full overlap).
        fill_alpha : float, default 0.7
            Alpha for the filled KDE area.
        line_alpha : float, default 1.0
            Alpha for the KDE line.
        colors : list, optional
            Colors for each ridge. If None, uses color cycle.
        labels : list of str, optional
            Labels for each ridge (for y-axis).
        id : str, optional
            Custom ID for this call.
        track : bool, optional
            Whether to record this call (default: True).
        **kwargs
            Additional arguments.

        Returns
        -------
        RecordingAxes
            Self for method chaining.

        Examples
        --------
        >>> ax.joyplot([data1, data2, data3], overlap=0.5)
        >>> ax.joyplot({"A": arr_a, "B": arr_b}, labels=["A", "B"])
        """
        from scipy import stats

        from .._utils._units import mm_to_pt
        from ..styles import get_style

        # Convert dict to list of arrays
        if isinstance(arrays, dict):
            if labels is None:
                labels = list(arrays.keys())
            arrays = list(arrays.values())

        n_ridges = len(arrays)

        # Get colors from style or use default cycle
        if colors is None:
            style = get_style()
            if style and "colors" in style and "palette" in style.colors:
                palette = list(style.colors.palette)
                # Normalize RGB 0-255 to 0-1
                colors = []
                for c in palette:
                    if isinstance(c, (list, tuple)) and len(c) >= 3:
                        if all(v <= 1.0 for v in c):
                            colors.append(tuple(c))
                        else:
                            colors.append(tuple(v / 255.0 for v in c))
                    else:
                        colors.append(c)
            else:
                # Matplotlib default color cycle
                import matplotlib.pyplot as plt

                colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

        # Calculate global x range
        all_data = np.concatenate([np.asarray(arr) for arr in arrays])
        x_min, x_max = np.min(all_data), np.max(all_data)
        x_range = x_max - x_min
        x_padding = x_range * 0.1
        x = np.linspace(x_min - x_padding, x_max + x_padding, 200)

        # Calculate KDEs and find max density for scaling
        kdes = []
        max_density = 0
        for arr in arrays:
            arr = np.asarray(arr)
            if len(arr) > 1:
                kde = stats.gaussian_kde(arr)
                density = kde(x)
                kdes.append(density)
                max_density = max(max_density, np.max(density))
            else:
                kdes.append(np.zeros_like(x))

        # Scale factor for ridge height
        ridge_height = 1.0 / (1.0 - overlap * 0.5) if overlap < 1 else 2.0

        # Get line width from style
        style = get_style()
        lw = mm_to_pt(0.2)  # Default
        if style and "lines" in style:
            lw = mm_to_pt(style.lines.get("trace_mm", 0.2))

        # Plot each ridge from back to front
        for i in range(n_ridges - 1, -1, -1):
            color = colors[i % len(colors)]
            baseline = i * (1.0 - overlap)

            # Scale density to fit nicely
            scaled_density = (
                kdes[i] / max_density * ridge_height if max_density > 0 else kdes[i]
            )

            # Fill
            self._ax.fill_between(
                x,
                baseline,
                baseline + scaled_density,
                facecolor=color,
                edgecolor="none",
                alpha=fill_alpha,
            )
            # Line on top
            self._ax.plot(
                x,
                baseline + scaled_density,
                color=color,
                alpha=line_alpha,
                linewidth=lw,
            )

        # Set y limits
        self._ax.set_ylim(-0.1, n_ridges * (1.0 - overlap) + ridge_height)

        # Set y-axis labels if provided
        if labels:
            y_positions = [(i * (1.0 - overlap)) + 0.3 for i in range(n_ridges)]
            self._ax.set_yticks(y_positions)
            self._ax.set_yticklabels(labels)
        else:
            # Hide y-axis ticks for cleaner look
            self._ax.set_yticks([])

        # Record the call if tracking is enabled
        if self._track and track:
            self._recorder.record_call(
                ax_position=self._position,
                method_name="joyplot",
                args=(arrays,),
                kwargs={
                    "overlap": overlap,
                    "fill_alpha": fill_alpha,
                    "line_alpha": line_alpha,
                    "labels": labels,
                },
                call_id=id,
            )

        return self

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
        """Create a swarm plot (beeswarm plot) showing individual data points.

        Parameters
        ----------
        data : list of array-like
            List of 1D arrays to plot.
        positions : array-like, optional
            X positions for each swarm. Default is 1, 2, 3, ...
        size : float, optional
            Marker size in mm. Default from style config.
        color : color or list of colors, optional
            Colors for each swarm.
        alpha : float, default 0.7
            Transparency of markers.
        jitter : float, default 0.3
            Width of jitter spread (in data units).
        id : str, optional
            Custom ID for this call.
        track : bool, optional
            Whether to record this call (default: True).
        **kwargs
            Additional arguments passed to scatter.

        Returns
        -------
        list
            List of PathCollection objects.

        Examples
        --------
        >>> ax.swarmplot([data1, data2, data3])
        >>> ax.swarmplot([arr1, arr2], positions=[0, 1], color=['red', 'blue'])
        """
        from .._utils._units import mm_to_pt
        from ..styles import get_style

        # Get style
        style = get_style()

        # Default marker size from style
        if size is None:
            if style and "markers" in style:
                size = style.markers.get("scatter_mm", 0.8)
            else:
                size = 0.8
        size_pt = mm_to_pt(size) ** 2  # matplotlib uses area

        # Get colors
        if color is None:
            if style and "colors" in style and "palette" in style.colors:
                palette = list(style.colors.palette)
                colors = []
                for c in palette:
                    if isinstance(c, (list, tuple)) and len(c) >= 3:
                        if all(v <= 1.0 for v in c):
                            colors.append(tuple(c))
                        else:
                            colors.append(tuple(v / 255.0 for v in c))
                    else:
                        colors.append(c)
            else:
                import matplotlib.pyplot as plt

                colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
        elif isinstance(color, list):
            colors = color
        else:
            colors = [color] * len(data)

        # Default positions
        if positions is None:
            positions = list(range(1, len(data) + 1))

        # Random generator for reproducible jitter
        rng = np.random.default_rng(42)

        results = []
        for i, (arr, pos) in enumerate(zip(data, positions)):
            arr = np.asarray(arr)

            # Create jittered x positions using beeswarm algorithm (simplified)
            x_jitter = self._beeswarm_positions(arr, jitter, rng)
            x_positions = pos + x_jitter

            c = colors[i % len(colors)]
            result = self._ax.scatter(
                x_positions, arr, s=size_pt, c=[c], alpha=alpha, **kwargs
            )
            results.append(result)

        # Record the call if tracking is enabled
        if self._track and track:
            self._recorder.record_call(
                ax_position=self._position,
                method_name="swarmplot",
                args=(data,),
                kwargs={
                    "positions": positions,
                    "size": size,
                    "alpha": alpha,
                    "jitter": jitter,
                },
                call_id=id,
            )

        return results

    def _beeswarm_positions(
        self,
        data: np.ndarray,
        width: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Calculate beeswarm-style x positions to minimize overlap.

        This is a simplified beeswarm that uses binning and jittering.
        For a true beeswarm, we'd need to iteratively place points.

        Parameters
        ----------
        data : array
            Y values of points.
        width : float
            Maximum jitter width.
        rng : Generator
            Random number generator.

        Returns
        -------
        array
            X offsets for each point.
        """
        n = len(data)
        if n == 0:
            return np.array([])

        # Sort data and get order
        order = np.argsort(data)
        sorted_data = data[order]

        # Group nearby points and offset them
        x_offsets = np.zeros(n)

        # Simple approach: bin by quantiles and spread within each bin
        n_bins = max(1, int(np.sqrt(n)))
        bin_edges = np.percentile(sorted_data, np.linspace(0, 100, n_bins + 1))

        for i in range(n_bins):
            mask = (sorted_data >= bin_edges[i]) & (sorted_data <= bin_edges[i + 1])
            n_in_bin = mask.sum()
            if n_in_bin > 0:
                # Spread points evenly within bin width
                offsets = np.linspace(-width / 2, width / 2, n_in_bin)
                # Add small random noise
                offsets += rng.uniform(-width * 0.1, width * 0.1, n_in_bin)
                x_offsets[mask] = offsets

        # Restore original order
        result = np.zeros(n)
        result[order] = x_offsets
        return result


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
