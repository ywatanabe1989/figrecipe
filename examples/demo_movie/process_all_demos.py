#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-27 01:50:03 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_movie/process_all_demos.py

"""Process all demo videos with TTS, BGM, and timing from recorded metadata.

This script reads timing.json files generated during recording to:
- Trim videos from title_screen_start to closing_screen_end + 1s
- Sync TTS narration with actual caption timestamps
- Add background music with fade in/out

Usage:
    python process_all_demos.py              # Process all demos (2 workers)
    python process_all_demos.py --demo 01    # Process specific demo
    python process_all_demos.py --workers 4  # Use 4 parallel workers
    python process_all_demos.py --sequential # Run sequentially (no parallelism)
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser._audio import generate_tts_segments, mix_narration_with_bgm

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "examples/demo_movie/outputs"
BGM_PATH = PROJECT_ROOT / "docs/bgm/smile.mp3"
TTS_CACHE = PROJECT_ROOT / "examples/demo_movie/tts_cache"


def find_demo_files(demo_id: str) -> tuple:
    """Find video and timing files for a demo.

    Parameters
    ----------
    demo_id : str
        Demo ID (e.g., "01", "02").

    Returns
    -------
    tuple
        (video_path, timing_path) or (None, None) if not found.
    """
    for timing_file in OUTPUT_DIR.glob(f"{demo_id}_*.timing.json"):
        video_file = timing_file.with_suffix("").with_suffix(".mp4")
        if video_file.exists():
            return video_file, timing_file
    return None, None


def process_demo(demo_id: str) -> dict:
    """Process a single demo using recorded timing metadata.

    Parameters
    ----------
    demo_id : str
        Demo ID (e.g., "01").

    Returns
    -------
    dict
        Result with keys: success, demo_id, duration, error.
    """
    video_path, timing_path = find_demo_files(demo_id)

    if not video_path:
        return {
            "success": False,
            "demo_id": demo_id,
            "error": "Video not found",
        }
    if not timing_path:
        return {
            "success": False,
            "demo_id": demo_id,
            "error": "Timing file not found",
        }

    try:
        # Load timing
        timing = json.loads(timing_path.read_text())
        events = {e["type"]: e for e in timing["events"]}

        title_start = events["title_screen_start"]["time"]
        closing_end = events["closing_screen_end"]["time"]
        recording_end = events["recording_end"]["time"]
        captions = [e for e in timing["events"] if e["type"] == "caption"]

        # Calculate trim points (keep 1s after closing for branding visibility)
        trim_start = title_start
        trim_end = min(closing_end + 1.0, recording_end)
        final_duration = trim_end - trim_start

        # Build narrations from timing data
        narrations = [("title", f"{timing['title']} Demo")]
        narration_times = [0.5]  # Title at start

        for i, c in enumerate(captions):
            adjusted_time = c["time"] - trim_start
            narrations.append((f"caption_{i}", c["text"]))
            narration_times.append(adjusted_time)

        # Generate TTS
        TTS_CACHE.mkdir(parents=True, exist_ok=True)
        narration_files = generate_tts_segments(narrations, TTS_CACHE)

        # Mix audio
        mixed_audio = Path(f"/tmp/demo_{demo_id}_mixed.mp3")
        mix_narration_with_bgm(
            narration_files=narration_files,
            narration_times=narration_times,
            bgm_path=BGM_PATH,
            output_path=mixed_audio,
            duration=final_duration,
            bgm_volume=0.10,
            narration_delay=0.3,
            fade_in_duration=0.5,
            fade_out_duration=1.0,
        )

        # Create final video
        final_path = video_path.with_name(video_path.stem + "_FINAL.mp4")

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(trim_start),
                "-to",
                str(trim_end),
                "-i",
                str(video_path),
                "-i",
                str(mixed_audio),
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                str(final_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "demo_id": demo_id,
                "error": result.stderr[:200],
            }

        # Cleanup
        mixed_audio.unlink(missing_ok=True)

        # Get final duration
        dur = (
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(final_path),
                ]
            )
            .decode()
            .strip()
        )

        return {
            "success": True,
            "demo_id": demo_id,
            "duration": float(dur),
            "output": str(final_path),
        }

    except Exception as e:
        return {"success": False, "demo_id": demo_id, "error": str(e)}


def main():
    """Process all demos with optional parallelism."""
    parser = argparse.ArgumentParser(description="Process demo videos with TTS and BGM")
    parser.add_argument("--demo", type=str, help="Process specific demo by ID")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of parallel workers (default: 2)",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run sequentially (no parallelism)",
    )
    args = parser.parse_args()

    # Find all demos
    demo_ids = []
    if args.demo:
        demo_ids = [args.demo]
    else:
        for timing_file in sorted(OUTPUT_DIR.glob("*.timing.json")):
            demo_id = timing_file.name.split("_")[0]
            if demo_id not in demo_ids:
                demo_ids.append(demo_id)

    if not demo_ids:
        print("No demos found to process")
        return

    print(f"Processing {len(demo_ids)} demos...")
    print(f"Workers: {'sequential' if args.sequential else args.workers}")
    print()

    results = []

    if args.sequential or len(demo_ids) == 1:
        # Sequential processing
        for demo_id in demo_ids:
            print(f"Processing demo {demo_id}...")
            result = process_demo(demo_id)
            results.append(result)
            status = "✅" if result["success"] else "❌"
            dur = f"{result.get('duration', 0):.2f}s" if result["success"] else ""
            print(f"  {status} Demo {demo_id} {dur}")
            if not result["success"]:
                print(f"     Error: {result.get('error', 'Unknown')}")
    else:
        # Parallel processing
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_demo, did): did for did in demo_ids}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                status = "✅" if result["success"] else "❌"
                dur = f"{result.get('duration', 0):.2f}s" if result["success"] else ""
                print(f"{status} Demo {result['demo_id']} {dur}")
                if not result["success"]:
                    print(f"   Error: {result.get('error', 'Unknown')}")

    # Summary
    success_count = sum(1 for r in results if r["success"])
    print()
    print(f"Completed: {success_count}/{len(demo_ids)} demos")


if __name__ == "__main__":
    main()

# EOF
