#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for demo video processing.

Provides video format conversion (MP4 to GIF) and
video concatenation using ffmpeg.
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available.

    Returns
    -------
    bool
        True if ffmpeg is available.
    """
    return shutil.which("ffmpeg") is not None


def convert_to_gif(
    input_path: Path,
    output_path: Optional[Path] = None,
    fps: int = 10,
    width: int = 800,
    optimize: bool = True,
) -> Path:
    """Convert MP4 video to GIF.

    Parameters
    ----------
    input_path : Path
        Path to input MP4 file.
    output_path : Path, optional
        Path for output GIF. If None, uses input path with .gif extension.
    fps : int, optional
        Frame rate for GIF (default: 10).
    width : int, optional
        Width of output GIF in pixels (default: 800).
    optimize : bool, optional
        Whether to optimize GIF palette (default: True).

    Returns
    -------
    Path
        Path to output GIF file.

    Raises
    ------
    RuntimeError
        If ffmpeg is not available or conversion fails.
    """
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg is not installed or not in PATH")

    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".gif")
    output_path = Path(output_path)

    if optimize:
        # Two-pass conversion for better quality
        palette_path = input_path.parent / f"{input_path.stem}_palette.png"

        # Generate palette
        palette_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=diff",
            str(palette_path),
        ]
        subprocess.run(palette_cmd, capture_output=True, check=True)

        # Generate GIF using palette
        gif_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-i",
            str(palette_path),
            "-lavfi",
            f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
            str(output_path),
        ]
        subprocess.run(gif_cmd, capture_output=True, check=True)

        # Clean up palette
        palette_path.unlink(missing_ok=True)
    else:
        # Simple single-pass conversion
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"fps={fps},scale={width}:-1:flags=lanczos",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    return output_path


def concatenate_videos(
    input_paths: List[Path],
    output_path: Path,
    transition_frames: int = 0,
) -> Path:
    """Concatenate multiple videos into one.

    Parameters
    ----------
    input_paths : List[Path]
        List of paths to input video files.
    output_path : Path
        Path for output concatenated video.
    transition_frames : int, optional
        Number of black frames between videos (default: 0).

    Returns
    -------
    Path
        Path to output video file.

    Raises
    ------
    RuntimeError
        If ffmpeg is not available or concatenation fails.
    """
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg is not installed or not in PATH")

    if not input_paths:
        raise ValueError("No input paths provided")

    output_path = Path(output_path)

    # Create concat file list
    concat_list = output_path.parent / "concat_list.txt"
    with open(concat_list, "w") as f:
        for path in input_paths:
            f.write(f"file '{Path(path).resolve()}'\n")

    # Concatenate videos
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    # Clean up
    concat_list.unlink(missing_ok=True)

    return output_path


__all__ = ["convert_to_gif", "concatenate_videos", "check_ffmpeg"]

# EOF
