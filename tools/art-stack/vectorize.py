#!/usr/bin/env python3
"""Raster glyph/logo -> SVG outlines. Free, local.

Backend chain: potrace CLI (best) -> vtracer (pip, no system deps).
Install: tools/art-stack/install.sh (or pip install vtracer).

Usage:
    vectorize.py in.png out.svg [--threshold 128] [--turdsize 2]

Input should be a clean black-on-white bitmap (use bg_remove.py + threshold
first). For font glyph pipelines, font-wizard's pipeline/vectorize.py
(pypotrace) is the richer path — this is the quick wrapper for logos/cards.

Example:
    vectorize.py glyph_M.png glyph_M.svg --turdsize 4
"""
import argparse, subprocess, shutil, sys
from pathlib import Path
from PIL import Image
import numpy as np

def via_potrace(bw: np.ndarray, dst: str, turdsize: int, alphamax: float):
    tmp = Path(dst).with_suffix(".pbm")
    Image.fromarray((bw * 255).astype("uint8")).save(tmp)
    subprocess.run([
        "potrace", str(tmp), "-s", "-o", dst,
        "--turdsize", str(turdsize), "--alphamax", str(alphamax),
    ], check=True)
    tmp.unlink()

def via_vtracer(bw: np.ndarray, dst: str):
    import vtracer
    # vtracer wants RGBA pixels; black = foreground
    h, w = bw.shape
    rgba = np.zeros((h, w, 4), dtype="uint8")
    rgba[..., :3] = (bw * 255)[..., None]
    rgba[..., 3] = 255
    flat = rgba.reshape(-1, 4)
    pixels = tuple(tuple(int(c) for c in px) for px in flat)
    svg = vtracer.convert_pixels_to_svg(
        pixels, (w, h),
        colormode="binary",
        hierarchical="stacked",
        mode="spline",
    )
    Path(dst).write_text(svg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--threshold", type=int, default=128)
    ap.add_argument("--turdsize", type=int, default=2)
    ap.add_argument("--alphamax", type=float, default=1.0)
    args = ap.parse_args()

    img = Image.open(args.src).convert("L")
    bw = (np.array(img) < args.threshold).astype("uint8")  # 1 = ink

    if shutil.which("potrace"):
        via_potrace(bw, args.dst, args.turdsize, args.alphamax)
        print(f"saved {args.dst} (potrace)")
    else:
        try:
            via_vtracer(bw, args.dst)
            print(f"saved {args.dst} (vtracer)")
        except ImportError:
            sys.exit("no vectorizer available — pip install vtracer "
                     "or apt install potrace")

if __name__ == "__main__":
    main()
