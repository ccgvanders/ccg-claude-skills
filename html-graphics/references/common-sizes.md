# Common target sizes

Build the HTML at the exact target dimensions below, then render at that
size (or use `--scale 2` on `render.py` for a crisper export without
changing the CSS).

| Use case | Dimensions | Notes |
|---|---|---|
| Teams announcement / channel banner | 848×244 px minimum | Build at 1696×488 (2x) or use `--scale 2` for a crisp result. Teams overlays white title/subheading text, typically left-of-centre — keep that zone visually calmer than the rest (see the contrast-pocket technique in gotchas). |
| SharePoint page hero / banner web part | ~1200×300 px | Varies slightly by web part template — check the actual placeholder in the page editor if precision matters. |
| LinkedIn banner | 1584×396 px | |
| Social square (Instagram-style) | 1080×1080 px | |
| Section/title card (standalone image, not a slide) | 1600×900 or 1920×1080 | Use the pptx skill instead if it needs to live inside an actual slide deck. |
| A4 print header/letterhead graphic | Use the docx or pdf skill instead | This skill is for standalone PNGs; print-accurate letterhead work belongs in the document skills, which handle page geometry and DPI properly. |

If a use case isn't listed here and the user hasn't given dimensions, ask
rather than guessing — the aspect ratio matters more than the absolute
size for how "busy" the design can be.
