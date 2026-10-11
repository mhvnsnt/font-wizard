# TOOLS.md — font-wizard

Free art/editing stack. Everything here is open-source, runs local, costs
nothing. No paid APIs, no subscriptions, no keys.

## Home: tools/art-stack/

The shared toolkit lives here. Other repos (media-pipeline, trippedd-studio)
wire into it — see their TOOLS.md.

**First-time setup:** `bash tools/art-stack/install.sh`
(Python lives in `tools/art-stack/.venv/` — system pip is debian-managed.)

**Run anything:** `tools/art-stack/run.sh <script> <args...>`

### bg_remove.py — AI background removal / cutouts

```bash
tools/art-stack/run.sh bg_remove.py photo.jpg cutout.png
tools/art-stack/run.sh bg_remove.py --model birefnet-general photo.jpg cutout.png
tools/art-stack/run.sh bg_remove.py --batch intake/
```

Models: `u2net` (fast default), `isnet-general-use` (better edges),
`birefnet-general` (SOTA — best hair/fine detail, ~900MB download),
`rmbg` (balanced). `--alpha-matting` refines edges further.

Use for: character cutouts, isolating sign lettering, product shots.

### inpaint.py — object removal (fence wires, watermarks, photobombers)

```bash
tools/art-stack/run.sh inpaint.py sign.jpg wire_mask.png sign_clean.jpg --radius 5
```

Mask = grayscale PNG, white pixels = area to erase. OpenCV Telea/NS
inpainting built in; pass `--lama-ckpt big-lama.pt` for SOTA LaMa inpainting
(requires torch + the lama repo — heavier, optional).

Use for: erasing fence bars crossing the Magnolia sign letters, removing
unwanted objects before tracing.

### vectorize.py — raster → SVG outlines

```bash
tools/art-stack/run.sh vectorize.py glyph_M.png glyph_M.svg --turdsize 4
```

Needs `potrace` (install.sh handles it). Input should be clean
black-on-white. For font glyph pipelines, `pipeline/vectorize.py`
(pypotrace) is the richer path — this is the quick wrapper for logos/cards.

### composite.py — text + image compositing

```bash
tools/art-stack/run.sh composite.py --bg card.png --text "STAY TRIPPEDD" \
  --font fonts/bush-v2/Bush-Regular.ttf --size 120 --fill white \
  --stroke 4 --pos center --out card_final.png
```

`--pos`: center | top | bottom | x,y. `--text` supports `\n` multi-line.
`--overlay logo.png --overlay-pos 40,40` layers an image.

Use for: network cards, bumpers, thumbnails, promo art.

### vid.py — ffmpeg shortcuts

```bash
tools/art-stack/run.sh vid.py trim in.mp4 3 12 out.mp4
tools/art-stack/run.sh vid.py vertical in.mp4 out.mp4      # 16:9 -> 9:16
tools/art-stack/run.sh vid.py captions in.mp4 subs.srt out.mp4
tools/art-stack/run.sh vid.py gif in.mp4 out.gif --fps 12 --w 480
tools/art-stack/run.sh vid.py -- -i in.mp4 ...             # raw passthrough
```

Use for: Shorts cuts, caption burns, preview GIFs.

## Existing pipeline/ tools (font-specific)

- `pipeline/build_font.py`, `build_ttf.py` — TTF assembly (fontTools)
- `pipeline/extract_glyphs.py` — glyph extraction from renders
- `pipeline/vectorize.py` — pypotrace glyph vectorization
- `pipeline/render_specimen.py` — specimen sheets
- `pipeline/make_commercial.py` — font commercial videos

## Provenance

Free Art Stack wired 2026-10-10 (owner directive: "wire up all that's free").
Branch `feature/free-art-stack`.
