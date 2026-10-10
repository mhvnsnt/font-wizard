# Font 03 — UNNAMED (awaiting owner naming)

A crude lo-fi handmade marker font — wobbly, bouncy, rough dry-brush edges.
Anchored on the **In the Bushes** locked art style (kid-drawing, handmade
deadpan). The playful counterpoint to Trippy Drippy Wizard's psychedelic
drips and Block Burner's hard street tags.

**Status:** Built 2026-10-10. NAME PENDING — the owner picks the name.

## What's inside
- `UnnamedFont03-Regular.ttf` — the typing font (A–Z, 0–9, `! ? . , ' - &`;
  lowercase auto-maps to caps)
- `png/` — 43 transparent-background glyphs at 2000px tall (white ink)
- `SPECIMEN.png` — sales/type specimen card
- `font03-commercial.mp4` — 10-second commercial (layout v2)

## Install
- **Android:** zFont 3 → install the TTF
- **Windows/Mac/Linux:** double-click the TTF → Install
- **Design apps:** drop the TTF in, or use the PNG pack directly

## License
Free for personal and commercial use. Do not resell or redistribute the
font files themselves. Built with Font Wizard (fontTools + OpenCV pipeline).

## Build
Glyphs generated procedurally (`work/font-03-unnamed/gen_kid_glyphs.py`):
DejaVu Sans Bold skeleton → elastic wobble → dry-marker texture → kid
retrace ghost → OpenCV findContours → fontTools TTF. Fully repeatable.
