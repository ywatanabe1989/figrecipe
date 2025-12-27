#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add TTS narration and BGM to demo videos.

Extracts caption texts from demo scripts and generates narrated videos
using the figrecipe._dev.browser module.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from figrecipe._dev.browser import add_narration_to_video, extract_captions_from_script

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "examples/demo_movie/outputs"
DEMO_DIR = PROJECT_ROOT / "examples/demo_movie"
BGM_PATH = PROJECT_ROOT / "docs/bgm/smile.mp3"
TTS_CACHE = PROJECT_ROOT / "examples/demo_movie/tts_cache"

# Demo script registry
DEMO_SCRIPTS = {
    "01": "01_enable_dark_mode.py",
    "02": "02_change_color.py",
    "03": "03_datatable_import.py",
    "04": "04_image_drop.py",
    "05": "05_panel_drag.py",
    "06": "06_file_browser.py",
}


def find_demo_pairs() -> List[Tuple[str, Path, Path]]:
    """Find matching demo script and video pairs."""
    pairs = []
    for demo_id, script_name in DEMO_SCRIPTS.items():
        script_path = DEMO_DIR / script_name
        if not script_path.exists():
            continue
        for video_path in OUTPUT_DIR.glob(f"{demo_id}_*.mp4"):
            if "_with_bgm" in video_path.name or "_FINAL" in video_path.name:
                continue
            pairs.append((demo_id, script_path, video_path))
            break
    return pairs


def main():
    """Process all demos to add narration and BGM."""
    import argparse

    parser = argparse.ArgumentParser(description="Add TTS narration to demo videos")
    parser.add_argument("--demo", type=str, help="Process specific demo by ID")
    args = parser.parse_args()

    if not BGM_PATH.exists():
        print(f"BGM not found: {BGM_PATH}")
        return

    pairs = find_demo_pairs()
    if args.demo:
        pairs = [(d, s, v) for d, s, v in pairs if d == args.demo]

    if not pairs:
        print("No demos found to process")
        return

    print(f"Processing {len(pairs)} demos with TTS narration and BGM\n")

    results = []
    for demo_id, script_path, video_path in pairs:
        print(f"Demo {demo_id}: {video_path.name}")

        # Extract captions from script
        captions = extract_captions_from_script(script_path)
        print(f"  Found {len(captions)} captions")

        # Generate title text from script name (remove leading number prefix)
        import re

        title_base = script_path.stem
        # Remove leading "01_", "02_", etc.
        title_base = re.sub(r"^\d+_", "", title_base)
        title_text = title_base.replace("_", " ").title() + " Demo"

        # Create output path
        output_path = video_path.with_name(video_path.stem + "_FINAL.mp4")

        # Add narration
        success, info = add_narration_to_video(
            video_path=video_path,
            captions=captions,
            output_path=output_path,
            bgm_path=BGM_PATH,
            tts_cache_dir=TTS_CACHE,
            title_text=title_text,
        )

        results.append((demo_id, success, info))

        if success:
            print(f"  Done! {info['captions']} narrations, {info['duration']:.1f}s\n")
        else:
            print(f"  FAILED: {info.get('error', 'Unknown')}\n")

    success_count = sum(1 for _, s, _ in results if s)
    print(f"\nCompleted: {success_count}/{len(pairs)} demos")

    if success_count > 0:
        print("\nFinal videos:")
        for demo_id, success, info in results:
            if success:
                print(f"  {info['output']}")


if __name__ == "__main__":
    main()
