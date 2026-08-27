# Gotchas

## Font loading race condition
Chromium can screenshot before a linked or `@font-face` font has actually
finished loading, silently baking a fallback-font layout into the PNG
(wrong widths, wrong line breaks). `render.py` already calls
`page.evaluate("document.fonts.ready")` before capturing — don't skip this
if writing a one-off render script instead of using it.

## Google Fonts / web fonts won't load in this container
The container's network egress is restricted to a specific allowlist (pip/
npm/GitHub package registries — see the network configuration). It does
**not** include `fonts.googleapis.com` or `fonts.gstatic.com`, so a
`<link>` to Google Fonts will silently fail and fall back to a system font
regardless of the font-loading wait above. Default to system fonts that
are already installed and render reliably: **Segoe UI** or **Arial** for
body text, **Consolas** for anything code/monospace. If a specific brand
or display font is genuinely required, it needs to be embedded as a
base64 `@font-face` from a font file already on disk — don't assume a web
font link will work.

## Verify before showing the user, don't just eyeball it
A broken render (missing font, a CSS property that silently didn't apply,
a page that screenshotted mid-load) often still *looks* plausible at a
glance. Two checks, in order:
1. Run `verify_render.py` — catches the extreme cases (blank/flat colour,
   tiny file size).
2. For anything with a gradient, chart, or colour-coded element, sample
   the actual pixels with PIL rather than assuming the CSS did what it was
   supposed to:
   ```python
   from PIL import Image
   img = Image.open("output.png").convert("RGB")
   img.getpixel((x, y))  # sample specific coordinates
   ```
   e.g. sampling several x-positions along a gradient confirms real colour
   variation is present, and sampling a bar-chart region confirms bars
   rendered at different heights rather than a flexbox layout collapsing
   to a flat row.

## Transparent backgrounds
Pass `--transparent` to `render.py` (maps to `omit_background=True`) when
the graphic needs to sit on a coloured surface — e.g. a SharePoint tile or
a dark Teams theme — rather than assuming a white background is fine.

## Avoid stray scrollbars in the screenshot
Set `overflow: hidden` on `html, body` and size them exactly to the target
canvas. Without this, a fixed-viewport screenshot can pick up scrollbar
artifacts if any child content overflows even by a pixel.

## Viewport vs full-page capture
Default to a fixed-viewport screenshot (`render.py`'s default) for graphics
built to an exact canvas size — this is nearly all of them (banners, cards,
diagrams). Only use `--full-page` if the content is genuinely meant to
scroll/overflow and all of it should be captured, which is rare for a
single static graphic.

## Old wkhtmltoimage workarounds no longer apply
If an old draft or reference conversation mentions wrangling flexbox,
gradient syntax, or CSS Grid to work around rendering quirks — that was
compensating for wkhtmltoimage's old QtWebKit engine and doesn't apply
here. Real Chromium handles modern CSS correctly; don't pre-emptively
simplify layout to dodge a problem this engine doesn't have.
