---
name: html-graphics
description: Use this skill whenever creating a visual graphic as a PNG image — banners, cards, diagrams, infographics, section headers, Teams/SharePoint announcement images, social graphics, or any standalone visual asset that isn't a full slide deck (use pptx skill) or document (use docx skill). Trigger on requests like "make a banner", "create a graphic/card", "Teams announcement image", "diagram/infographic as an image", or "render this as a PNG". Always use this skill instead of wkhtmltoimage or ad-hoc rendering — it documents the correct Playwright/Chromium-based approach and the gotchas that cause silent, broken, or blank renders if skipped.
---

# HTML Graphics (Playwright render)

Build the graphic as an HTML/CSS file, then render it to PNG with a real
Chromium browser via Playwright. This container already has Playwright
installed with a cached Chromium build at `/opt/pw-browsers` — no download
needed.

Do **not** use wkhtmltoimage. It's abandonware (unmaintained since 2023) and
runs on a patched QtWebKit engine roughly equivalent to 2013-era Safari —
shaky flexbox, no CSS Grid, and it can silently mangle modern gradient
syntax. Reserve `cairosvg` only for pure-SVG-only graphics with no HTML/CSS
layout (icons, simple vector diagrams) — it has no layout engine, so it's
the wrong tool for anything built with flexbox, grid, or CSS positioning.

## Workflow

1. **Confirm the brief before building.** Get the target use (Teams banner,
   SharePoint card, diagram, etc.), dimensions if known, and whether CCG
   brand colours/fonts apply — see `references/ccg-brand.md`. If dimensions
   aren't specified, check `references/common-sizes.md` for the standard
   size for that use case.
2. **Build the HTML/CSS** at the exact target pixel dimensions (set
   `html, body { width: Wpx; height: Hpx; margin: 0; overflow: hidden; }`
   on the canvas element). Use system fonts (Segoe UI, Arial, Calibri,
   Consolas) — see the font-loading note in `references/gotchas.md` before
   reaching for a web font.
3. **Render with `scripts/render.py`**:
   ```
   python3 scripts/render.py input.html output.png --width 1696 --height 488
   ```
   Add `--scale 2` for a higher-DPI export without touching the CSS (e.g.
   build at 848×244 and export at 1696×488 by passing `--scale 2` instead
   of doubling every value by hand). Add `--transparent` if the graphic
   needs to sit on a coloured surface (e.g. a SharePoint tile) rather than
   white. See `references/gotchas.md` for when each of these matters.
4. **Verify before showing the user.** Run
   `python3 scripts/verify_render.py output.png` as a first-pass sanity
   check (catches blank/flat-colour renders), then actually view the image
   yourself — sample specific pixel regions with PIL if there's a
   gradient, chart, or colour-coded element you need to confirm rendered
   correctly, the way you'd check a data table's values before reporting
   them.
5. **Copy to `/mnt/user-data/outputs`** and present with `present_files`.

## Reference files

- `references/common-sizes.md` — standard target dimensions (Teams banner,
  SharePoint hero, LinkedIn, social square, etc.). Check here first if the
  user hasn't specified a size.
- `references/gotchas.md` — font-loading race conditions, why Google Fonts
  won't work in this container, transparent backgrounds, avoiding stray
  scrollbars, viewport vs full-page capture.
- `references/ccg-brand.md` — when the official CCG brand guide (colours,
  Novel Pro/Sofia Pro) applies vs when a freer palette is appropriate, and
  the practical font fallback for HTML rendering.
