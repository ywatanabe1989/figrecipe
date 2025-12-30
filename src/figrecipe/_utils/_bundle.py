#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bundle and path resolution utilities for figrecipe.

This module provides utilities for resolving recipe paths from:
- Direct YAML files (.yaml, .yml)
- Image files (.png, .jpg, etc.) with associated YAML
- Bundle directories containing recipe.yaml
- ZIP files containing recipe.yaml

This enables integration with FTS (Figure Transfer Specification) bundles.
"""

import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Union

# Standard recipe filename in bundles
RECIPE_FILENAME = "recipe.yaml"
RECIPE_FILENAME_ALT = "recipe.yml"


def resolve_recipe_path(
    path: Union[str, Path],
    extract_dir: Optional[Path] = None,
) -> Tuple[Path, Optional[Path]]:
    """Resolve a path to a recipe YAML file.

    Handles multiple input formats:
    - Direct YAML file: Returns as-is
    - Image file (.png, etc.): Finds associated .yaml
    - Directory: Looks for recipe.yaml inside
    - ZIP file: Extracts and finds recipe.yaml

    Parameters
    ----------
    path : str or Path
        Input path - can be YAML, image, directory, or ZIP.
    extract_dir : Path, optional
        Directory to extract ZIP contents to. If None, uses a temp directory.

    Returns
    -------
    tuple
        (recipe_path, temp_dir) where temp_dir is set if extraction occurred
        and the caller should clean it up, or None if no cleanup needed.

    Raises
    ------
    FileNotFoundError
        If path doesn't exist or recipe.yaml not found.
    ValueError
        If path type is not supported.

    Examples
    --------
    >>> recipe_path, temp = resolve_recipe_path("figure.yaml")
    >>> recipe_path, temp = resolve_recipe_path("figure/")
    >>> recipe_path, temp = resolve_recipe_path("figure.zip")
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    # Case 1: Direct YAML file
    if path.suffix.lower() in (".yaml", ".yml"):
        return path, None

    # Case 2: Image file - find associated YAML
    if path.suffix.lower() in (
        ".png",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".svg",
        ".tif",
        ".tiff",
    ):
        return _resolve_from_image(path), None

    # Case 3: Directory - look for recipe.yaml
    if path.is_dir():
        return _resolve_from_directory(path), None

    # Case 4: ZIP file - extract and find recipe.yaml
    if path.suffix.lower() == ".zip":
        return _resolve_from_zip(path, extract_dir)

    raise ValueError(
        f"Unsupported path type: {path.suffix}. "
        f"Expected .yaml, .yml, .png, .zip, or directory."
    )


def _resolve_from_image(path: Path) -> Path:
    """Find YAML recipe associated with an image file."""
    yaml_path = path.with_suffix(".yaml")
    if yaml_path.exists():
        return yaml_path

    yml_path = path.with_suffix(".yml")
    if yml_path.exists():
        return yml_path

    raise FileNotFoundError(
        f"Recipe file not found for {path.name}. "
        f"Expected {yaml_path.name} or {yml_path.name}"
    )


def _resolve_from_directory(path: Path) -> Path:
    """Find recipe.yaml inside a directory (FTS bundle)."""
    recipe_path = path / RECIPE_FILENAME
    if recipe_path.exists():
        return recipe_path

    recipe_alt = path / RECIPE_FILENAME_ALT
    if recipe_alt.exists():
        return recipe_alt

    # Also check for any .yaml file as fallback
    yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
    if len(yaml_files) == 1:
        return yaml_files[0]

    if yaml_files:
        raise FileNotFoundError(
            f"Multiple YAML files found in {path}. "
            f"Expected {RECIPE_FILENAME} or a single .yaml file."
        )

    raise FileNotFoundError(
        f"No recipe found in directory {path}. "
        f"Expected {RECIPE_FILENAME} or a .yaml file."
    )


def _resolve_from_zip(
    path: Path,
    extract_dir: Optional[Path] = None,
) -> Tuple[Path, Path]:
    """Extract ZIP and find recipe.yaml inside."""
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Not a valid ZIP file: {path}")

    # Create extraction directory
    if extract_dir is None:
        extract_dir = Path(tempfile.mkdtemp(prefix="figrecipe_bundle_"))

    with zipfile.ZipFile(path, "r") as zf:
        # Find recipe.yaml in the ZIP
        recipe_name = None
        for name in zf.namelist():
            basename = Path(name).name
            if basename in (RECIPE_FILENAME, RECIPE_FILENAME_ALT):
                recipe_name = name
                break

        if recipe_name is None:
            # Try to find any yaml file
            yaml_files = [n for n in zf.namelist() if n.endswith((".yaml", ".yml"))]
            if len(yaml_files) == 1:
                recipe_name = yaml_files[0]
            elif yaml_files:
                raise FileNotFoundError(
                    f"Multiple YAML files found in {path}. Expected {RECIPE_FILENAME}."
                )
            else:
                raise FileNotFoundError(
                    f"No recipe found in ZIP {path}. Expected {RECIPE_FILENAME}."
                )

        # Extract all files (needed for data files referenced by recipe)
        zf.extractall(extract_dir)

    recipe_path = extract_dir / recipe_name
    return recipe_path, extract_dir


def is_bundle_path(path: Union[str, Path]) -> bool:
    """Check if path is a bundle directory or ZIP.

    Parameters
    ----------
    path : str or Path
        Path to check.

    Returns
    -------
    bool
        True if path is a directory or ZIP file.
    """
    path = Path(path)
    if not path.exists():
        return False
    return path.is_dir() or path.suffix.lower() == ".zip"


__all__ = [
    "resolve_recipe_path",
    "is_bundle_path",
    "RECIPE_FILENAME",
]
