#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle path utilities and constants."""

import zipfile
from pathlib import Path
from typing import Dict, Union

# Bundle file names
SPEC_FILENAME = "spec.json"
STYLE_FILENAME = "style.json"
DATA_FILENAME = "data.csv"
EXPORTS_DIR = "exports"
CACHE_DIR = "cache"


def is_bundle_path(path: Union[str, Path]) -> bool:
    """Check if path represents a bundle.

    Parameters
    ----------
    path : str or Path
        Path to check.

    Returns
    -------
    bool
        True if path is a ZIP bundle or directory with spec.json.
    """
    path = Path(path)

    # ZIP file
    if path.suffix.lower() == ".zip":
        if path.exists():
            try:
                with zipfile.ZipFile(path, "r") as zf:
                    return SPEC_FILENAME in zf.namelist()
            except zipfile.BadZipFile:
                return False
        return True  # Assume valid if doesn't exist yet

    # Directory with spec.json
    if path.is_dir() and (path / SPEC_FILENAME).exists():
        return True

    return False


def bundle_exists(path: Union[str, Path]) -> bool:
    """Check if a valid bundle exists at path.

    Parameters
    ----------
    path : str or Path
        Path to bundle.

    Returns
    -------
    bool
        True if bundle exists with spec.json.
    """
    path = Path(path)

    if not path.exists():
        return False

    # ZIP file
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                return SPEC_FILENAME in zf.namelist()
        except zipfile.BadZipFile:
            return False

    # Directory
    if path.is_dir():
        return (path / SPEC_FILENAME).exists()

    return False


def get_bundle_paths(bundle_path: Union[str, Path]) -> Dict[str, Path]:
    """Get paths to bundle components (for directory bundles).

    Parameters
    ----------
    bundle_path : str or Path
        Path to bundle directory.

    Returns
    -------
    dict
        Dictionary with keys: 'root', 'spec', 'style', 'data', 'exports', 'cache'
    """
    root = Path(bundle_path)
    return {
        "root": root,
        "spec": root / SPEC_FILENAME,
        "style": root / STYLE_FILENAME,
        "data": root / DATA_FILENAME,
        "exports": root / EXPORTS_DIR,
        "cache": root / CACHE_DIR,
    }


def create_bundle_structure(bundle_path: Union[str, Path]) -> Dict[str, Path]:
    """Create bundle directory structure (for directory bundles).

    Parameters
    ----------
    bundle_path : str or Path
        Path to bundle directory.

    Returns
    -------
    dict
        Dictionary with paths to created directories.
    """
    paths = get_bundle_paths(bundle_path)

    # Create directories
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["exports"].mkdir(exist_ok=True)
    paths["cache"].mkdir(exist_ok=True)

    return paths
