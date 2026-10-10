# 🧙 Font Wizard

A free, open-source custom font foundry. Build, federate, and ship font
packs with free tools and free APIs — no paid software, no licenses to buy.

This is the canonical home for all Font Wizard font-pack product work.

## What it does
- **Build custom fonts** from artwork: extract glyphs → generate the missing
  ones in-style → vectorize → assemble a real TTF/WOFF/WOFF2.
- **Federate free fonts**: pull any open-licensed font from Google Fonts or
  Fontsource by name and drop it into the pipeline as a base or reference.
- **Ship product**: every family lands with installable fonts, a transparent
  PNG glyph pack for designers, and a specimen sales card.

## Quick start
```sh
pip install -r requirements.txt   # fontTools, pillow, numpy, pypotrace, brotli, requests
# system: potrace  (apt install potrace / brew install potrace)

# Federate a free font as a base/reference:
python api/federate.py "Space Grotesk"

# Build a family (see docs/FONT-PACK-PIPELINE.md):
python pipeline/extract_glyphs.py --src card.png --grid 9 4 \
    --chars "ABC..." --out work/myfamily/glyphs/
python pipeline/vectorize.py --glyphs work/myfamily/glyphs/ --out-svg work/myfamily/svg/
python pipeline/build_ttf.py --glyphs work/myfamily/glyphs/ \
    --name MyFamily --out fonts/myfamily/MyFamily-Regular.ttf
python pipeline/export_png.py --glyphs work/myfamily/glyphs/ --out fonts/myfamily/png/
python pipeline/render_specimen.py --ttf fonts/myfamily/MyFamily-Regular.ttf \
    --out fonts/myfamily/SPECIMEN.png --title "My Family"
```

## Layout
```
pipeline/     # the foundry: extract, vectorize, build, export, specimen
api/          # free font APIs: google_fonts, fontsource, federate
fonts/        # shipped product — one dir per family
  trippy-drippy-wizard/   # first family (build in progress)
docs/         # pipeline doc, API guide, stacks, contributing
```

## Free stacks inside
fontTools · potrace · FontForge (scripting) · nanoemoji (color fonts) ·
gftools (Google Fonts QA) — documented in `docs/STACKS.md`.

Free APIs: Google Fonts (no key), Fontsource CDN — `docs/API-GUIDE.md`.

## Families
| Family | Style | Status |
|---|---|---|
| Trippy Drippy Wizard | drippy psychedelic bubble (Wizard Gang) | building |

## Contributing
See `docs/CONTRIBUTING.md`. Branch → PR → merge; no open PRs.

## License
MIT — see LICENSE. (Individual font families may carry their own terms;
see each family's README.)
