#!/usr/bin/env python3
"""
extract_glyphs.py — pull individual glyph bitmaps out of artwork.

Two modes:
  1. --grid: source image is a grid of glyphs (rows x cols), e.g. a font-pack
     card or specimen sheet. Crops each cell.
  2. --boxes: explicit JSON list of {char, x, y, w, h} boxes (from a manual
     pass or a segmentation tool).

Every glyph is cleaned: thresholded to pure black-on-white, despeckled,
tight-cropped to its ink bounding box, and padded. Output: PNGs named
U+XXXX.png in --out dir, plus glyphs.json manifest.

Usage:
  python extract_glyphs.py --src card.png --grid 9 4 --chars "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" --out glyphs/
  python extract_glyphs.py --src artwork.png --boxes boxes.json --out glyphs/
"""
import argparse, json, os
from PIL import Image, ImageFilter, ImageOps
import numpy as np


def clean(gray: Image.Image, thresh: int = 160) -> Image.Image:
    g = np.array(gray.convert("L")).astype(np.int16)
    bw = (g < thresh).astype(np.uint8) * 255          # ink = white
    img = Image.fromarray(255 - bw)                   # back to black ink on white
    img = img.filter(ImageFilter.MedianFilter(3))     # despeckle
    return img


def tight_crop(img: Image.Image, pad: int = 12) -> Image.Image:
    inv = np.array(ImageOps.invert(img.convert("L")))
    ys, xs = np.where(inv > 30)
    if len(xs) == 0:
        return img
    x0, x1 = max(0, xs.min() - pad), min(img.width, xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(img.height, ys.max() + pad)
    return img.crop((x0, y0, x1, y1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--grid", nargs=2, type=int, metavar=("COLS", "ROWS"))
    ap.add_argument("--chars", default="")
    ap.add_argument("--boxes")
    ap.add_argument("--thresh", type=int, default=160)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    src = Image.open(args.src).convert("RGB")
    manifest = []

    jobs = []
    if args.grid:
        cols, rows = args.grid
        chars = args.chars or "".join(chr(c) for c in range(0x41, 0x5B))
        cw, chh = src.width / cols, src.height / rows
        for i, ch in enumerate(chars):
            r, c = divmod(i, cols)
            jobs.append((ch, (int(c * cw), int(r * chh),
                              int((c + 1) * cw), int((r + 1) * chh))))
    elif args.boxes:
        for b in json.load(open(args.boxes)):
            jobs.append((b["char"], (b["x"], b["y"],
                                     b["x"] + b["w"], b["y"] + b["h"])))
    else:
        ap.error("need --grid or --boxes")

    for ch, box in jobs:
        glyph = tight_crop(clean(src.crop(box).convert("L"), args.thresh))
        code = f"U+{ord(ch):04X}"
        path = os.path.join(args.out, f"{code}.png")
        glyph.save(path)
        manifest.append({"char": ch, "codepoint": code,
                         "file": os.path.basename(path),
                         "size": glyph.size})
        print(f"{ch} ({code}) -> {path} {glyph.size}")

    json.dump(manifest, open(os.path.join(args.out, "glyphs.json"), "w"), indent=1)
    print(f"wrote {len(manifest)} glyphs + glyphs.json")


if __name__ == "__main__":
    main()
