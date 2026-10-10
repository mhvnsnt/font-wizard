# Free Font API Guide

Font Wizard federates open-licensed fonts as bases and references. All of
these are free, no API key required.

## Google Fonts (keyless via CSS2 API)
- The `webfonts/v1` metadata API now requires a free API key — so this repo
  uses the **keyless CSS2 API** instead: `fonts.googleapis.com/css2?family=…`
  returns direct gstatic file URLs with no key. A plain UA gets TTF, a
  browser UA gets WOFF2.
- ~1,700 open-licensed families (mostly OFL).
- `api/google_fonts.py`: `search()`, `file_urls(family, weights, fmt)`,
  `download(family, dest, weights, fmt)`.
- License check: every family page lists its license — most are SIL OFL
  (free for commercial use; you can't sell OFL font files standalone, but
  you MAY sell products that use them and packs where the font is a
  component of a larger work — read the OFL FAQ).

## Fontsource (CDN)
- npm-mirrored open fonts over jsDelivr CDN, no key.
- `api/fontsource.py`: `search()`, `download(family_id, dest, ...)`.
- Good for woff2-first web workflows.

## federate.py — one command
```sh
python api/federate.py "Space Grotesk"
# -> fonts/_federated/space-grotesk/ + FEDERATED.json (source + license)
```
Use a federated font as:
- a **base**: start a new family from its metrics/skeleton, redraw the style;
- a **reference**: side-by-side while drawing custom glyphs;
- a **fallback**: bundle for characters your custom set doesn't cover yet.

## License rules (don't skip this)
- OFL fonts: free to use, modify, embed, and bundle. You may NOT sell the
  font files by themselves; you MAY sell products that use them and packs
  where the font is a component of a larger work — read the OFL FAQ.
- Custom families built in this repo (Trippy Drippy Wizard etc.) are the
  owner's IP — their sale terms live in each family's README.
- When in doubt, keep the FEDERATED.json manifest so the provenance is
  always traceable.
