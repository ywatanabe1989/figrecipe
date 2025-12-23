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
