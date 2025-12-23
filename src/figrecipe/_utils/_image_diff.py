#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image comparison utilities for roundtrip testing."""

from pathlib import Path
from typing import Tuple, Union

import numpy as np


def load_image(path: Union[str, Path]) -> np.ndarray:
    """Load image as numpy array.

    Parameters
    ----------
    path : str or Path
        Path to image file.

    Returns
    -------
    np.ndarray
        Image as (H, W, C) array with values 0-255.
    """
    from PIL import Image

    img = Image.open(path).convert("RGB")
    return np.array(img)


def compute_diff(
    img1: np.ndarray,
    img2: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """Compute pixel-level difference between two images.

    Parameters
    ----------
    img1 : np.ndarray
        First image (H, W, C).
    img2 : np.ndarray
        Second image (H, W, C).

    Returns
    -------
    mse : float
        Mean squared error (0 = identical).
    diff_img : np.ndarray
        Difference image (absolute difference).
    """
    # Ensure same shape
    if img1.shape != img2.shape:
        raise ValueError(f"Image shapes differ: {img1.shape} vs {img2.shape}")

    # Compute difference
    diff = np.abs(img1.astype(float) - img2.astype(float))
    mse = np.mean(diff**2)

    # Normalize diff for visualization
    diff_img = (
        (diff / diff.max() * 255).astype(np.uint8)
        if diff.max() > 0
        else diff.astype(np.uint8)
    )

    return mse, diff_img


def compare_images(
    path1: Union[str, Path],
    path2: Union[str, Path],
    diff_path: Union[str, Path] = None,
) -> dict:
    """Compare two image files.

    Parameters
    ----------
    path1 : str or Path
        Path to first image.
    path2 : str or Path
        Path to second image.
    diff_path : str or Path, optional
        If provided, save difference image here.

    Returns
    -------
    dict
        Comparison results:
        - identical: bool (True if MSE == 0)
        - mse: float (mean squared error)
        - psnr: float (peak signal-to-noise ratio, inf if identical)
        - max_diff: float (maximum pixel difference)
        - size1: tuple (H, W) of first image
        - size2: tuple (H, W) of second image
        - same_size: bool (True if dimensions match)
        - file_size1: int (file size in bytes)
        - file_size2: int (file size in bytes)
    """
    import os

    img1 = load_image(path1)
    img2 = load_image(path2)

    # File sizes
    file_size1 = os.path.getsize(path1)
    file_size2 = os.path.getsize(path2)

    # Check if same size
    same_size = img1.shape == img2.shape

    if same_size:
        mse, diff_img = compute_diff(img1, img2)
    else:
        # Can't compute pixel diff for different sizes
        mse = float("nan")
        diff_img = None

    # Peak signal-to-noise ratio
    if mse == 0:
        psnr = float("inf")
    elif np.isnan(mse):
        psnr = float("nan")
    else:
        psnr = 10 * np.log10(255**2 / mse)

    # Max difference
    if same_size:
        max_diff = np.max(np.abs(img1.astype(float) - img2.astype(float)))
    else:
        max_diff = float("nan")

    # Save diff image if requested
    if diff_path is not None and diff_img is not None:
        from PIL import Image

        Image.fromarray(diff_img).save(diff_path)

    return {
        "identical": mse == 0,
        "mse": float(mse),
        "psnr": float(psnr),
        "max_diff": float(max_diff),
        "size1": (img1.shape[0], img1.shape[1]),
        "size2": (img2.shape[0], img2.shape[1]),
        "same_size": img1.shape == img2.shape,
        "file_size1": file_size1,
        "file_size2": file_size2,
    }


def create_comparison_figure(
    original_path: Union[str, Path],
    reproduced_path: Union[str, Path],
    output_path: Union[str, Path],
    title: str = "Roundtrip Comparison",
):
    """Create a side-by-side comparison figure.

    Parameters
    ----------
    original_path : str or Path
        Path to original image.
    reproduced_path : str or Path
        Path to reproduced image.
    output_path : str or Path
        Path to save comparison figure.
    title : str
        Title for the comparison.
    """
    import matplotlib.pyplot as plt

    img1 = load_image(original_path)
    img2 = load_image(reproduced_path)

    try:
        mse, diff_img = compute_diff(img1, img2)
    except ValueError:
        # Different sizes, just show side by side
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].imshow(img1)
        axes[0].set_title("Original")
        axes[0].axis("off")
        axes[1].imshow(img2)
        axes[1].set_title("Reproduced")
        axes[1].axis("off")
        fig.suptitle(f"{title}\n(Different sizes)", fontsize=14)
        fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img1)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(img2)
    axes[1].set_title("Reproduced")
    axes[1].axis("off")

    axes[2].imshow(diff_img)
    axes[2].set_title(f"Difference (MSE: {mse:.2f})")
    axes[2].axis("off")

    status = "IDENTICAL" if mse == 0 else f"MSE: {mse:.2f}"
    fig.suptitle(f"{title}\n{status}", fontsize=14, fontweight="bold")

    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
