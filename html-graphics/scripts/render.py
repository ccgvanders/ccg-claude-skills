#!/usr/bin/env python3
"""
Render an HTML file to a PNG using Playwright + real Chromium.

Usage:
    python3 render.py input.html output.png --width 1696 --height 488 \
        [--scale 2] [--transparent] [--full-page]

Notes:
    - Waits for document.fonts.ready before capturing, to avoid a
      fallback-font flash being baked into the screenshot.
    - Defaults to a fixed-viewport screenshot (not full-page) since most
      graphics are built to an exact canvas size. Use --full-page only if
      content genuinely overflows and should all be captured.
    - --scale is a device scale factor, not a resize: --width 848 --height 244
      --scale 2 renders a 1696x488 PNG of the same 848x244 layout, useful
      for a crisp export without doubling every CSS value by hand.
"""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def render(input_html: str, output_png: str, width: int, height: int,
           scale: float = 1.0, transparent: bool = False, full_page: bool = False):
    input_path = Path(input_html).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input HTML not found: {input_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page.goto(f"file://{input_path}")
        # Wait for web fonts to finish loading before capturing.
        page.evaluate("document.fonts.ready")
        page.screenshot(path=output_png, full_page=full_page, omit_background=transparent)
        browser.close()

    print(f"Rendered {output_png} ({int(width*scale)}x{int(height*scale)} px)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render HTML to PNG via Playwright/Chromium")
    parser.add_argument("input_html")
    parser.add_argument("output_png")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--scale", type=float, default=1.0, help="device scale factor (2 = retina/higher-DPI export)")
    parser.add_argument("--transparent", action="store_true", help="omit background for a transparent PNG")
    parser.add_argument("--full-page", action="store_true", help="capture full scrollable page instead of fixed viewport")
    args = parser.parse_args()

    render(args.input_html, args.output_png, args.width, args.height,
           scale=args.scale, transparent=args.transparent, full_page=args.full_page)
