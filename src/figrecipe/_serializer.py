#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serialization for recipe files (YAML + data files)."""

from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
from ruamel.yaml import YAML

from ._recorder import FigureRecord
from ._utils._numpy_io import (
    CsvFormat,
    DataFormat,
    load_array,
    save_array,
    save_arrays_single_csv,
)


def _convert_numpy_types(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types.

    Parameters
    ----------
    obj : Any
        Object to convert.

    Returns
    -------
    Any
        Object with numpy types converted to native Python types.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: _convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        converted = [_convert_numpy_types(item) for item in obj]
        return type(obj)(converted) if isinstance(obj, tuple) else converted
    else:
        return obj


def save_recipe(
    record: FigureRecord,
    path: Union[str, Path],
    include_data: bool = True,
    data_format: DataFormat = "csv",
    csv_format: CsvFormat = "separate",
) -> Path:
    """Save a figure record to YAML file.

    Parameters
    ----------
    record : FigureRecord
        The figure record to save.
    path : str or Path
        Output path (.yaml).
    include_data : bool
        If True, save large arrays to separate files.
    data_format : str
        Format for data files: 'csv' (default), 'npz', or 'inline'.
        - 'csv': Human-readable CSV files with dtype header
        - 'npz': Compressed numpy binary format
        - 'inline': Store all data directly in YAML (may be large)
    csv_format : str
        CSV file structure: 'separate' (default) or 'single'.
        - 'separate': One CSV file per variable (current behavior)
        - 'single': Single CSV with all columns (scitex/SigmaPlot-compatible)
        Only applies when data_format='csv'.

    Returns
    -------
    Path
        Path to saved YAML file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create data directory for large arrays (only for separate format)
    data_dir = path.parent / f"{path.stem}_data"

    # Convert record to dict
    data = record.to_dict()

    # Process arrays: save large ones to files, update references
    if include_data and data_format != "inline":
        if data_format == "csv" and csv_format == "single":
            # Save all arrays to single CSV file
            csv_path = path.with_suffix(".csv")
            data = _process_arrays_for_single_csv(data, csv_path)
        else:
            # Save to separate files (original behavior)
            data = _process_arrays_for_save(data, data_dir, record.id, data_format)

    # Convert numpy types to native Python types
    data = _convert_numpy_types(data)

    # Save YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(path, "w") as f:
        yaml.dump(data, f)

    return path


def _process_arrays_for_save(
    data: Dict[str, Any],
    data_dir: Path,
    fig_id: str,
    data_format: DataFormat = "csv",
) -> Dict[str, Any]:
    """Process arrays in data dict, saving large ones to files.

    Parameters
    ----------
    data : dict
        Data dictionary to process.
    data_dir : Path
        Directory for array files.
    fig_id : str
        Figure ID for naming files.
    data_format : str
        Format for data files: 'csv', 'npz', or 'inline'.

    Returns
    -------
    dict
        Processed data with file references.
    """
    data_dir_created = False

    for ax_key, ax_data in data.get("axes", {}).items():
        for call_list in [ax_data.get("calls", []), ax_data.get("decorations", [])]:
            for call in call_list:
                call_id = call.get("id", "unknown")

                # Process args
                for i, arg in enumerate(call.get("args", [])):
                    if "_array" in arg:
                        # Large array - save to file
                        if not data_dir_created:
                            data_dir.mkdir(parents=True, exist_ok=True)
                            data_dir_created = True

                        arr = arg.pop("_array")
                        filename = f"{call_id}_{arg.get('name', f'arg{i}')}"
                        file_path = save_array(arr, data_dir / filename, data_format)
                        arg["data"] = str(file_path.relative_to(data_dir.parent))

    return data


def _process_arrays_for_single_csv(
    data: Dict[str, Any],
    csv_path: Path,
) -> Dict[str, Any]:
    """Process arrays in data dict, saving all to single CSV file.

    Parameters
    ----------
    data : dict
        Data dictionary to process.
    csv_path : Path
        Path for the single CSV file.

    Returns
    -------
    dict
        Processed data with CSV file reference.
    """
    # Collect all arrays by trace
    arrays_by_trace = {}

    for ax_key, ax_data in data.get("axes", {}).items():
        arrays_by_trace[ax_key] = {}

        for call_list in [ax_data.get("calls", []), ax_data.get("decorations", [])]:
            for call in call_list:
                call_id = call.get("id", "unknown")

                # Collect arrays from args
                trace_arrays = {}
                for arg in call.get("args", []):
                    if "_array" in arg:
                        arr = arg.pop("_array")
                        var_name = arg.get("name", "data")
                        trace_arrays[var_name] = arr
                        # Update reference to point to CSV file
                        arg["data"] = str(csv_path.name)

                if trace_arrays:
                    arrays_by_trace[ax_key][call_id] = trace_arrays

    # Save all arrays to single CSV
    if any(traces for traces in arrays_by_trace.values()):
        save_arrays_single_csv(arrays_by_trace, csv_path)

        # Add data reference to the recipe
        data["data"] = {
            "csv_path": str(csv_path.name),
            "csv_format": "single",
        }

    return data


def load_recipe(path: Union[str, Path]) -> FigureRecord:
    """Load a figure record from YAML file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    FigureRecord
        Loaded figure record.
    """
    path = Path(path)

    yaml = YAML()
    with open(path) as f:
        data = yaml.load(f)

    # Resolve data file references
    data = _resolve_data_references(data, path.parent)

    return FigureRecord.from_dict(data)


def _resolve_data_references(
    data: Dict[str, Any],
    base_dir: Path,
) -> Dict[str, Any]:
    """Resolve file references to actual array data.

    Parameters
    ----------
    data : dict
        Data dictionary with file references.
    base_dir : Path
        Base directory for resolving relative paths.

    Returns
    -------
    dict
        Data with arrays loaded.
    """
    for ax_key, ax_data in data.get("axes", {}).items():
        for call_list in [ax_data.get("calls", []), ax_data.get("decorations", [])]:
            for call in call_list:
                for arg in call.get("args", []):
                    data_ref = arg.get("data")

                    # Check if it's a file reference
                    if isinstance(data_ref, str) and (
                        data_ref.endswith(".npy")
                        or data_ref.endswith(".npz")
                        or data_ref.endswith(".csv")
                    ):
                        file_path = base_dir / data_ref
                        if file_path.exists():
                            arr = load_array(file_path)
                            arg["data"] = arr.tolist()
                            arg["_loaded_array"] = arr

    return data


def recipe_to_dict(path: Union[str, Path]) -> Dict[str, Any]:
    """Load recipe as raw dictionary (for inspection).

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Raw recipe data.
    """
    path = Path(path)

    yaml = YAML()
    with open(path) as f:
        return dict(yaml.load(f))
