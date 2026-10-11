# Free Art Stack — home base

100% free, open-source art + editing toolkit. No paid APIs, no subscriptions,
no API keys. Everything runs local on the VM.

## Tools

| Script | What it does | Backend |
|---|---|---|
| `bg_remove.py` | AI background removal / cutouts | rembg: `u2net` (fast), `isnet-general-use` (quality), `birefnet-general` (SOTA) |
| `inpaint.py` | Object removal / fence-wire erasing | OpenCV Telea/NS inpainting (LaMa-ready hook) |
| `vectorize.py` | Raster glyph/logo → SVG outlines | potrace (via pypotrace or CLI) |
| `composite.py` | Layer compositing, text overlay, color ops | Pillow |
| `vid.py` | Thin ffmpeg wrapper: trim, crop, vertical cut, captions burn | ffmpeg (system) |

## Install

```bash
bash tools/art-stack/install.sh
```

Installs: `rembg`, `opencv-python-headless` (pip), `potrace`,
`imagemagick` (apt). Downloads rembg models on first run (~170MB for u2net,
cached in `~/.u2net`).

## Quick examples

```bash
# Cut out a character from a photo (SOTA matting)
python3 tools/art-stack/bg_remove.py --model birefnet-general in.jpg out.png

# Erase fence wires crossing the sign letters (mask = white where the wires are)
python3 tools/art-stack/inpaint.py --method telea sign.jpg wire_mask.png clean.png

# Vectorize a traced glyph to SVG for font building
python3 tools/art-stack/vectorize.py glyph.png glyph.svg

# Composite text onto a card background
python3 tools/art-stack/composite.py --bg card.png --text "STAY TRIPPEDD" \
    --font fonts/bush-v2/Bush-Regular.ttf --size 120 --out card_final.png
```

## Wired repos

- **font-wizard** (this repo) — home base. `pipeline/vectorize.py` already
  exists; `tools/art-stack/vectorize.py` wraps potrace CLI for non-glyph use.
- **media-pipeline** — `scripts/bg_remove.py` upgraded to call this stack
  (model-selectable). See that repo's TOOLS.md.
- **trippedd-studio** — `tools/art-stack/` shim points here. See that repo's
  TOOLS.md.
