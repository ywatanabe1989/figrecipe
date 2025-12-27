#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Marker detection using spatiotemporal analysis.

- Temporal: Peak detection finds dark marker frames
- Spatial: OCR extracts text at fixed positions
"""

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


def extract_frames(video_path: Path, fps: int = 5) -> List[Tuple[float, np.ndarray]]:
    """Extract frames from video with timestamps."""
    frames = []

    with tempfile.TemporaryDirectory() as tmpdir:
        frame_pattern = Path(tmpdir) / "frame_%06d.png"
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps}",
            "-f",
            "image2",
            str(frame_pattern),
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        for i, frame_file in enumerate(sorted(Path(tmpdir).glob("frame_*.png"))):
            timestamp = i / fps
            try:
                from PIL import Image

                img = Image.open(frame_file)
                frame = np.array(img)[:, :, :3]
            except ImportError:
                import imageio

                frame = imageio.imread(frame_file)[:, :, :3]
            frames.append((timestamp, frame))

    return frames


def frame_brightness(frame: np.ndarray) -> float:
    """Calculate mean brightness (0-255)."""
    return float(np.mean(frame))


def is_dark_frame(frame: np.ndarray, threshold: float = 30) -> bool:
    """Check if frame is dark (marker candidate)."""
    return frame_brightness(frame) < threshold


def detect_dark_frames(
    frames: List[Tuple[float, np.ndarray]],
) -> List[float]:
    """Find timestamps of dark frames using peak detection."""
    if len(frames) < 3:
        return []

    brightnesses = np.array([frame_brightness(f[1]) for f in frames])
    dark_timestamps = []

    for i in range(len(brightnesses)):
        if brightnesses[i] < 40:  # Dark threshold
            dark_timestamps.append(frames[i][0])

    return dark_timestamps


def ocr_frame(frame: np.ndarray) -> str:
    """Extract text from frame using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image

        img = Image.fromarray(frame)
        text = pytesseract.image_to_string(
            img,
            config="--psm 6",
        )
        return text.strip()
    except ImportError:
        return ""
    except Exception:
        return ""


def extract_marker_metadata(frame: np.ndarray) -> Optional[Dict]:
    """Extract metadata from marker frame via OCR.

    Detection strategy (OCR is unreliable, so be lenient):
    1. Accept frames with version string (vX.Y.Z or X.Y.Z pattern)
    2. OR accept frames with marker keywords (TRIM, START, END)
    3. Caller determines type by position (first=start, last=end)
    """
    text = ocr_frame(frame)
    if not text:
        return None

    metadata = {}
    text_upper = text.upper()

    # Accept if has version string OR marker keywords
    has_version = bool(re.search(r"\d+\.\d+\.\d+", text))
    has_keywords = any(kw in text_upper for kw in ["TRIM", "START", "END"])

    if not (has_version or has_keywords):
        return None

    # Try to detect type from text, but this is optional
    if "START" in text_upper:
        metadata["marker_type"] = "start"
    elif "END" in text_upper:
        metadata["marker_type"] = "end"
    else:
        # Type will be determined by caller based on position
        metadata["marker_type"] = "marker"

    # Extract version (vX.Y.Z pattern)
    version_match = re.search(r"v?(\d+\.\d+\.\d+)", text)
    if version_match:
        metadata["version"] = version_match.group(1)

    # Extract timestamp (YYYY-MM-DD HH:MM pattern)
    ts_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", text)
    if ts_match:
        metadata["timestamp"] = ts_match.group(1)

    return metadata


def detect_markers(
    video_path: Path,
    fps: int = 5,  # Lower fps for faster processing (500ms markers = 2.5 frames)
) -> Tuple[Optional[float], Optional[float], Dict]:
    """Detect start/end markers using spatiotemporal analysis.

    Strategy:
    1. Find dark frames (brightness < 40)
    2. OCR each to find version string (marker identifier)
    3. First marker = START, last marker = END

    Returns (start_time, end_time, metadata).
    """
    frames = extract_frames(video_path, fps=fps)
    if not frames:
        return None, None, {}

    # Stage 1: Find dark frame candidates
    dark_timestamps = detect_dark_frames(frames)

    # Stage 2: Collect marker groups (consecutive frames = same marker)
    # Group frames that are within 1 second of each other
    marker_groups = []  # List of (first_timestamp, last_timestamp, metadata)
    current_group = None

    for timestamp in dark_timestamps:
        frame_idx = int(timestamp * fps)
        if 0 <= frame_idx < len(frames):
            frame = frames[frame_idx][1]
            marker_meta = extract_marker_metadata(frame)

            if marker_meta:
                if current_group is None:
                    # Start new group
                    current_group = [timestamp, timestamp, marker_meta]
                elif timestamp - current_group[1] < 1.0:
                    # Extend current group
                    current_group[1] = timestamp
                else:
                    # Save current group and start new one
                    marker_groups.append(tuple(current_group))
                    current_group = [timestamp, timestamp, marker_meta]

    if current_group:
        marker_groups.append(tuple(current_group))

    # Stage 3: Determine start/end by position
    start_time = None
    end_time = None
    metadata = {}

    if marker_groups:
        # First group is START (use first frame of group)
        start_time = marker_groups[0][0]
        metadata["start"] = marker_groups[0][2]
        metadata["start"]["marker_type"] = "start"

        # Last group is END (use first frame of group, if different from first group)
        if len(marker_groups) > 1:
            end_time = marker_groups[-1][0]
            metadata["end"] = marker_groups[-1][2]
            metadata["end"]["marker_type"] = "end"

    # Trim margins: drop first 1.5s after start marker, drop last 1s before end marker
    if start_time is not None:
        start_time += 1.5  # Drop first 1.5 seconds
    if end_time is not None:
        end_time -= 1.0  # Drop last 1 second

    return start_time, end_time, metadata


__all__ = [
    "extract_frames",
    "frame_brightness",
    "is_dark_frame",
    "detect_dark_frames",
    "ocr_frame",
    "extract_marker_metadata",
    "detect_markers",
]

# EOF
