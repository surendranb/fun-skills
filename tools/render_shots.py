#!/usr/bin/env python3
"""
render_shots.py - Headless Chrome Screenshot Renderer for SVG Scenes & Progression Shots

Takes an SVG file or a directory of SVGs and captures pixel-perfect PNG screenshots via Headless Chrome.

Usage:
    python3 tools/render_shots.py <path_to_svg_or_dir> [--width 1200] [--height 800]
"""

import sys
import os
import subprocess
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def render_svg_to_png(file_path: Path, output_png_path: Path, width=1200, height=800):
    abs_path = file_path.resolve()
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--screenshot={output_png_path.resolve()}",
        f"file://{abs_path}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=15)
        if output_png_path.exists():
            print(f"  📸 Rendered: {output_png_path.name} ({output_png_path.stat().st_size} bytes)")
        else:
            print(f"  ❌ Failed: {res.stderr.decode()[:200]}")
    except Exception as e:
        print(f"  ❌ Exception rendering {file_path.name}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/render_shots.py <path_to_svg_or_dir> [--width 1200] [--height 800]")
        sys.exit(1)

    target = Path(sys.argv[1])
    width = 1200
    height = 800
    
    if "--width" in sys.argv:
        idx = sys.argv.index("--width")
        width = int(sys.argv[idx + 1])
    if "--height" in sys.argv:
        idx = sys.argv.index("--height")
        height = int(sys.argv[idx + 1])

    if target.is_file():
        out_png = target.with_suffix(".png")
        render_svg_to_png(target, out_png, width, height)
    elif target.is_dir():
        files = sorted(list(target.glob("*.svg")) + list(target.glob("*.html")))
        print(f"Found {len(files)} files in {target.name} to render:")
        for f in files:
            out_png = f.with_suffix(".png")
            render_svg_to_png(f, out_png, width, height)

if __name__ == "__main__":
    main()
