#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NumPy array I/O utilities for figrecipe."""

import csv
from pathlib import Path
from typing import Literal, Union

import numpy as np

# Threshold for inline vs file storage (in elements)
INLINE_THRESHOLD = 100

# Data format type
DataFormat = Literal["csv", "npz", "inline"]

# CSV format type: single file with all columns vs separate files per variable
CsvFormat = Literal["single", "separate"]


def should_store_inline(data: np.ndarray) -> bool:
    """Determine if array should be stored inline or as file.

    Parameters
    ----------
    data : np.ndarray
        Array to check.

    Returns
    -------
    bool
        True if array is small enough for inline storage.
    """
    return data.size <= INLINE_THRESHOLD


def save_array(
    data: np.ndarray,
    path: Union[str, Path],
    data_format: DataFormat = "csv",
) -> Path:
    """Save numpy array to file.

    Parameters
    ----------
    data : np.ndarray
        Array to save.
    path : str or Path
        Output file path (extension will be set based on format).
    data_format : str
        Format to use: 'csv' (default), 'npz', or 'inline'.

    Returns
    -------
    Path
        Path to saved file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if data_format == "csv":
        path = path.with_suffix(".csv")
        save_array_csv(data, path)
    elif data_format == "npz":
        path = path.with_suffix(".npz")
        np.savez_compressed(path, data=data)
    else:
        path = path.with_suffix(".npy")
        np.save(path, data)

    return path


def save_array_csv(data: np.ndarray, path: Union[str, Path]) -> Path:
    """Save numpy array to CSV file with dtype header.

    Parameters
    ----------
    data : np.ndarray
        Array to save.
    path : str or Path
        Output CSV file path.

    Returns
    -------
    Path
        Path to saved file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        # Write header with dtype info
        writer.writerow([f"# dtype: {data.dtype}"])
        # Write data
        if data.ndim == 1:
            for val in data:
                writer.writerow([val])
        else:
            for row in data:
                writer.writerow(row if hasattr(row, "__iter__") else [row])

    return path


def load_array_csv(path: Union[str, Path]) -> np.ndarray:
    """Load numpy array from CSV file.

    Parameters
    ----------
    path : str or Path
        Path to CSV file.

    Returns
    -------
    np.ndarray
        Loaded array.
    """
    path = Path(path)
    dtype = None
    data_rows = []

    with open(path, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].startswith("# dtype:"):
                dtype_str = row[0].replace("# dtype:", "").strip()
                dtype = np.dtype(dtype_str)
            else:
                data_rows.append(row)

    # Parse data
    if not data_rows:
        return np.array([], dtype=dtype)

    # Check if 1D (single column)
    if all(len(row) == 1 for row in data_rows):
        data = [row[0] for row in data_rows]
    else:
        data = data_rows

    return np.array(data, dtype=dtype)


def load_array(path: Union[str, Path]) -> np.ndarray:
    """Load numpy array from file.

    Parameters
    ----------
    path : str or Path
        Path to .npy, .npz, or .csv file.

    Returns
    -------
    np.ndarray
        Loaded array.
    """
    path = Path(path)

    if path.suffix == ".npz":
        with np.load(path) as f:
            return f["data"]
    elif path.suffix == ".csv":
        return load_array_csv(path)
    else:
        return np.load(path)


def to_serializable(data) -> Union[list, dict]:
    """Convert numpy array to serializable format for inline storage.

    Parameters
    ----------
    data : array-like
        Data to convert.

    Returns
    -------
    list or dict
        Serializable representation.
    """
    if hasattr(data, "tolist"):
        return data.tolist()
    elif hasattr(data, "values"):  # pandas
        return data.values.tolist()
    else:
        return list(data)


def from_serializable(data, dtype=None) -> np.ndarray:
    """Convert serializable format back to numpy array.

    Parameters
    ----------
    data : list
        Serializable data.
    dtype : dtype, optional
        Target dtype.

    Returns
    -------
    np.ndarray
        Numpy array.
    """
    return np.array(data, dtype=dtype)


def _sanitize_trace_id(trace_id: str) -> str:
    """Sanitize trace ID for use in CSV column names.

    Parameters
    ----------
    trace_id : str
        Raw trace identifier.

    Returns
    -------
    str
        Sanitized trace ID safe for CSV column names.
    """
    if not trace_id:
        return "unnamed"

    sanitized = str(trace_id).lower()
    result = []
    for char in sanitized:
        if char.isalnum():
            result.append(char)
        elif char in (" ", "_", "(", ")", "[", "]", "{", "}", "/", "\\", ".", "-"):
            result.append("-")

    sanitized = "".join(result)
    while "--" in sanitized:
        sanitized = sanitized.replace("--", "-")
    return sanitized.strip("-") or "unnamed"


def _get_csv_column_name(
    variable: str,
    ax_row: int = 0,
    ax_col: int = 0,
    trace_id: str = None,
) -> str:
    """Get CSV column name in scitex-compatible format.

    Format: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}

    Parameters
    ----------
    variable : str
        Variable name (e.g., "x", "y").
    ax_row : int
        Row position of axes in grid.
    ax_col : int
        Column position of axes in grid.
    trace_id : str, optional
        Trace identifier.

    Returns
    -------
    str
        Full column name.
    """
    safe_id = _sanitize_trace_id(trace_id) if trace_id else "0"
    return (
        f"ax-row-{ax_row}-col-{ax_col}_trace-id-{safe_id}_variable-{variable.lower()}"
    )


def save_arrays_single_csv(
    arrays_by_trace: dict,
    path: Union[str, Path],
) -> Path:
    """Save all arrays to single wide CSV file (scitex/SigmaPlot-compatible).

    Parameters
    ----------
    arrays_by_trace : dict
        Nested dict: {ax_key: {trace_id: {"x": arr, "y": arr, ...}, ...}, ...}
        Where ax_key is like "ax_0_0" (row_col format).
    path : str or Path
        Output CSV file path.

    Returns
    -------
    Path
        Path to saved file.
    """
    import pandas as pd

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Collect all columns
    columns = {}
    max_len = 0

    for ax_key, traces in arrays_by_trace.items():
        # Parse ax_key like "ax_0_0" to get row, col
        parts = ax_key.split("_")
        ax_row = int(parts[1]) if len(parts) > 1 else 0
        ax_col = int(parts[2]) if len(parts) > 2 else 0

        for trace_id, variables in traces.items():
            for var_name, arr in variables.items():
                if arr is None:
                    continue
                arr = np.asarray(arr).flatten()
                col_name = _get_csv_column_name(var_name, ax_row, ax_col, trace_id)
                columns[col_name] = arr
                max_len = max(max_len, len(arr))

    if not columns:
        # No data to save
        return path

    # Pad shorter arrays with NaN
    for col_name, arr in columns.items():
        if len(arr) < max_len:
            padded = np.full(max_len, np.nan)
            padded[: len(arr)] = arr
            columns[col_name] = padded

    # Create DataFrame and save
    df = pd.DataFrame(columns)
    df.to_csv(path, index=False)

    return path


def load_single_csv(path: Union[str, Path]) -> dict:
    """Load arrays from single wide CSV file.

    Parameters
    ----------
    path : str or Path
        Path to CSV file.

    Returns
    -------
    dict
        Nested dict: {ax_key: {trace_id: {"x": arr, "y": arr, ...}, ...}, ...}
    """
    import pandas as pd

    path = Path(path)
    df = pd.read_csv(path)

    result = {}
    for col_name in df.columns:
        # Parse column name: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}
        if not col_name.startswith("ax-row-"):
            continue

        try:
            parts = col_name.split("_")
            # parts[0] = "ax-row-0-col-0", parts[1] = "trace-id-xxx", parts[2] = "variable-yyy"
            ax_part = parts[0]  # "ax-row-0-col-0"
            trace_part = parts[1]  # "trace-id-xxx"
            var_part = parts[2]  # "variable-yyy"

            # Extract values
            ax_rest = ax_part[7:]  # Remove "ax-row-"
            row_str, col_str = ax_rest.split("-col-")
            ax_row, ax_col = int(row_str), int(col_str)

            trace_id = trace_part[9:]  # Remove "trace-id-"
            variable = var_part[9:]  # Remove "variable-"

            ax_key = f"ax_{ax_row}_{ax_col}"

            if ax_key not in result:
                result[ax_key] = {}
            if trace_id not in result[ax_key]:
                result[ax_key][trace_id] = {}

            # Get array, dropping NaN values
            arr = df[col_name].dropna().values
            result[ax_key][trace_id][variable] = arr

        except (ValueError, IndexError):
            continue

    return result
