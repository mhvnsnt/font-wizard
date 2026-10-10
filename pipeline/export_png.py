#!/usr/bin/env python3
"""
export_png.py — transparent-background PNG glyph pack for designers.

Takes the cleaned glyph bitmaps (glyphs/ dir) and exports each as a tall
transparent PNG (default 2000px), ink colorized (default white; --ink RRGGBB
to bake a brand color). Manifest updated with png paths.

Usage:
  python export_png.py --glyphs glyphs/ --out png/ [--height 2000] [--ink FFFFFF]
"""
import argparse, json, os
from PIL import Image
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glyphs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=int, default=2000)
    ap.add_argument("--ink", default="FFFFFF")
    args = ap.parse_args()

    ink = tuple(int(args.ink[i:i + 2], 16) for i in (0, 2, 4))
    os.makedirs(args.out, exist_ok=True)
    manifest = json.load(open(os.path.join(args.glyphs, "glyphs.json")))

    for g in manifest:
        src = Image.open(os.path.join(args.glyphs, g["file"])).convert("L")
        scale = args.height / src.height
        big = src.resize((max(1, int(src.width * scale)), args.height),
                         Image.LANCZOS)
        a = np.array(big).astype(np.float32)
        alpha = np.clip((160 - a) / 160, 0, 1) * 255   # dark ink -> opaque
        rgba = np.zeros((big.height, big.width, 4), dtype=np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = ink
        rgba[..., 3] = alpha.astype(np.uint8)
        out = os.path.join(args.out, f"{g['codepoint']}_{g['char']}.png")
        Image.fromarray(rgba).save(out)
        g["png"] = os.path.basename(out)
        print(f"{g['char']} -> {out}")

    json.dump(manifest, open(os.path.join(args.glyphs, "glyphs.json"), "w"),
              indent=1)
    print(f"exported {len(manifest)} PNGs")


if __name__ == "__main__":
    main()
