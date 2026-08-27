#!/usr/bin/env python3
"""
Quick sanity check for a rendered PNG before showing it to the user.
Catches the most common silent-failure modes: a blank/flat-colour render
(usually a sign a font failed to load, CSS didn't apply, or the page
screenshotted before it finished loading) or a suspiciously tiny file.

This is a first-pass automated check, not a substitute for actually
viewing the image — always view it yourself afterwards, and for anything
with a gradient, chart, or colour-coded element, sample the specific
pixels that matter (see the gradient/bar-chart example in
references/gotchas.md).

Usage:
    python3 verify_render.py output.png
"""
import sys
from pathlib import Path
from PIL import Image


def verify(png_path: str) -> bool:
    path = Path(png_path)
    if not path.exists():
        print(f"FAIL: {png_path} does not exist")
        return False

    img = Image.open(path).convert("RGB")
    w, h = img.size
    size_kb = path.stat().st_size / 1024

    samples = []
    for fx in (0.05, 0.25, 0.5, 0.75, 0.95):
        for fy in (0.2, 0.5, 0.8):
            samples.append(img.getpixel((int(w * fx), int(h * fy))))

    unique_colours = len(set(samples))
    print(f"Size: {w}x{h}, {size_kb:.0f} KB, {unique_colours}/{len(samples)} unique sample colours")

    ok = True
    if unique_colours <= 1:
        print("WARNING: image appears to be a single flat colour — likely a broken/blank render")
        ok = False
    if size_kb < 5:
        print("WARNING: file size is suspiciously small for a graphic this size")
        ok = False

    if ok:
        print("OK: looks like a real render — still view it visually before sharing")
    return ok


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 verify_render.py output.png")
        sys.exit(2)
    sys.exit(0 if verify(sys.argv[1]) else 1)
