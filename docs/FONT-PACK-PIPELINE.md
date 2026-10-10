# Font-Pack Pipeline — the repeatable process

This is how every Font Wizard family gets built, from artwork to a shippable
product. Follow it top to bottom for a new family; the Trippy Drippy Wizard
build was the reference implementation.

## 0. Source art
- Start with the style reference: a title card, logo, or lettering sample.
- You need at least a few real glyphs to anchor the style. Everything else
  gets generated or drawn to match.

## 1. Glyph inventory (`pipeline/extract_glyphs.py`)
- Crop each glyph from the artwork (`--boxes` with a JSON box list, or
  `--grid` for a specimen card).
- Script cleans (threshold + despeckle), tight-crops, pads.
- Output: `work/<family>/glyphs/` — `U+XXXX.png` files + `glyphs.json`.

## 2. Fill the gaps
- List what's missing for A–Z, 0–9, basic punctuation.
- Generate missing glyphs in-style (image model with the source art as
  style reference, one glyph per image, white on black).
- **Inspect every glyph with your own eyes before accepting it.** A bad
  glyph in the set poisons the whole font.

## 3. Vectorize (`pipeline/vectorize.py`)
- potrace each bitmap to SVG outlines.
- Tune `--turdsize` (speckle killer) and `--alphamax` (smoothness).
- Output: `work/<family>/svg/` — one SVG per glyph.

## 4. Build the TTF (`pipeline/build_ttf.py`)
- fontTools assembles outlines + metrics into a real `.ttf`.
- Generates `.woff` / `.woff2` siblings automatically.
- Output: `fonts/<family-slug>/Family-Regular.ttf` (+ woff/woff2).

## 5. PNG glyph pack (`pipeline/export_png.py`)
- Transparent-background PNGs, 2000px tall, in brand ink color.
- For designers who want the artwork directly, no font install.
- Output: `fonts/<family-slug>/png/`.

## 6. Specimen card (`pipeline/render_specimen.py`)
- Renders the TTF into a sales poster: alphabet, numerals, sample words.
- This is the listing image for itch.io / Gumroad / Creative Market.
- Output: `fonts/<family-slug>/SPECIMEN.png`.

## 7. Ship
- Family README (license, install, preview).
- Commit to `fonts/<family-slug>/`, PR, merge.
- Publish: free pack on itch.io, paid pack on Gumroad — the pipeline
  outputs serve both.

## Directory contract
```
work/<family>/glyphs/    # cleaned bitmaps + glyphs.json (build scratch)
work/<family>/svg/       # vectorized outlines (build scratch)
fonts/<family-slug>/     # SHIPPED product
  Family-Regular.ttf / .woff / .woff2
  png/                   # transparent glyph PNGs
  SPECIMEN.png
  README.md
```
`work/` is scratch (gitignored). `fonts/` is the product — never commit
half-built fonts there.
