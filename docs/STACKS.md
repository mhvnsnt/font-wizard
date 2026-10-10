# Open-Source Stacks

Everything Font Wizard runs on is free and open-source. Pull these in as
needed.

## In requirements.txt (pip)
| Tool | What it does |
|---|---|
| fontTools | Read/write/merge/subset TTF, OTF, WOFF, WOFF2. The backbone. |
| Pillow | Glyph raster work, PNG export, specimen rendering. |
| numpy | Array ops for cleanup, recolor, masking. |
| pypotrace | Python bindings for potrace (needs system libpotrace). |
| brotli | WOFF2 compression. |
| requests | Free API federation. |

## System / documented (not in requirements.txt)
### potrace (C, GPL)
Bitmap → vector tracer. The vectorize step. Install: `apt install potrace`
/ `brew install potrace`. Peter Selinger's classic — still the best free
tracer for clean glyph outlines.

### FontForge (GPL)
Full font editor with Python scripting. Use it when a family needs manual
refinement: kerning, hinting, glyph surgery. Scripting:
```python
import fontforge
font = fontforge.open("Family.ttf")
# ... adjust, then font.generate("Family-Fixed.ttf")
```
Docs: fontforge.org. Big, old, irreplaceable.

### gftools (Apache 2.0)
Google Fonts' own toolchain: QA (`gftools qa`), fixes, family upgrades,
push pipeline. If a family ever targets Google Fonts submission, this is
the gate. `pip install gftools`.

### nanoemoji (Apache 2.0)
Color font builder (COLRv0/COLRv1, CBDT, sbix). For when a family wants
gradient/glow color baked into the font itself — e.g. a gold+purple
Trippy Drippy Wizard color variant. `pip install nanoemoji`.

## Free font sources (no key)
- Google Fonts API — `api/google_fonts.py`
- Fontsource CDN — `api/fontsource.py`
- fonts.cdnfonts.com / Open Font Library — grab direct TTF/OTF links when
  the license is open; record provenance in FEDERATED.json.
