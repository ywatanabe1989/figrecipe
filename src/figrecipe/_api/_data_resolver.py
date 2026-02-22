#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data resolution utilities for declarative plot creation."""

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

# Cache for loaded CSV files
_csv_cache: Dict[str, Any] = {}


def resolve_data(
    data: Any,
    data_file: Optional[str] = None,
) -> Any:
    """Resolve data - could be inline list, column name (with data_file), or file path.

    Parameters
    ----------
    data : Any
        Data specification. Can be:
        - List/tuple: converted to numpy array
        - String: if data_file is provided, treated as column name
                  otherwise, treated as file path (.npy, .csv, .npz)
        - Other: returned as-is
    data_file : str, optional
        Path to CSV file. If provided, string `data` is treated as column name.

    Returns
    -------
    Any
        Resolved data (typically numpy array).

    Examples
    --------
    # Direct data
    >>> resolve_data([1, 2, 3])
    array([1, 2, 3])

    # CSV column
    >>> resolve_data("temperature", data_file="experiment.csv")
    array([20.5, 21.0, ...])  # from temperature column
    """
    if data is None:
        return None

    if isinstance(data, (list, tuple)):
        # Handle inhomogeneous arrays (e.g., boxplot data with different group sizes)
        try:
            return np.array(data)
        except ValueError:
            # Fallback for inhomogeneous shapes - return as list for boxplot/violin
            return list(data)

    if isinstance(data, str):
        # If data_file provided, treat string as column name
        if data_file is not None:
            return _load_csv_column(data_file, data)

        # Otherwise, treat as file path
        path = Path(data)
        if path.exists():
            if path.suffix == ".npy":
                return np.load(path)
            elif path.suffix == ".csv":
                return np.loadtxt(path, delimiter=",")
            elif path.suffix == ".npz":
                return np.load(path)

    return data


def _load_csv_column(csv_path: str, column_name: str) -> np.ndarray:
    """Load a specific column from a CSV file.

    Uses pandas if available (handles headers better), falls back to numpy.
    """
    global _csv_cache

    csv_path = str(Path(csv_path).resolve())

    # Check cache
    if csv_path not in _csv_cache:
        try:
            import pandas as pd

            _csv_cache[csv_path] = pd.read_csv(csv_path)
        except ImportError:
            # Fallback to numpy with header detection
            with open(csv_path, "r") as f:
                header = f.readline().strip().split(",")
            data = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
            _csv_cache[csv_path] = {"header": header, "data": data}

    cached = _csv_cache[csv_path]

    # Extract column
    try:
        import pandas as pd

        if isinstance(cached, pd.DataFrame):
            if column_name not in cached.columns:
                raise ValueError(
                    f"Column '{column_name}' not found. "
                    f"Available: {list(cached.columns)}"
                )
            return cached[column_name].values
    except ImportError:
        pass

    # Numpy fallback
    if isinstance(cached, dict):
        header = cached["header"]
        data = cached["data"]
        if column_name not in header:
            raise ValueError(f"Column '{column_name}' not found. Available: {header}")
        col_idx = header.index(column_name)
        return data[:, col_idx] if data.ndim > 1 else np.array([data[col_idx]])

    raise ValueError(f"Cannot extract column from cached data type: {type(cached)}")


def clear_csv_cache() -> None:
    """Clear the CSV file cache."""
    global _csv_cache
    _csv_cache.clear()


# EOF
