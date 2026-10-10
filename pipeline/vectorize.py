#!/usr/bin/env python3
"""
vectorize.py — bitmap glyphs -> SVG outlines via potrace.

Reads glyphs/ dir (PNGs + glyphs.json from extract_glyphs.py), traces each
glyph with potrace, writes SVGs to --out-svg/ and updates the manifest with
path data.

Needs: libpotrace installed (apt: potrace / brew: potrace), pypotrace (pip).

Usage:
  python vectorize.py --glyphs glyphs/ --out-svg svg/ [--turdsize 2] [--alphamax 1]
"""
import argparse, json, os
import numpy as np
from PIL import Image

try:
    import potrace
except ImportError:
    raise SystemExit("pypotrace not installed: pip install pypotrace (needs libpotrace)")


def trace(png_path: str, turdsize: int, alphamax: float) -> str:
    img = Image.open(png_path).convert("L")
    arr = np.array(img)
    bmp = potrace.Bitmap((arr < 160).astype(np.uint32))
    path = bmp.trace(turdsize=turdsize, alphamax=alphamax)
    w, h = img.size
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<path d="']
    for curve in path.curves:
        sx, sy = curve.start_point
        parts.append(f"M{sx.x:.1f},{h - sy.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                parts.append(f"L{seg.c.x:.1f},{h - seg.c.y:.1f}"
                             f"L{seg.end_point.x:.1f},{h - seg.end_point.y:.1f}")
            else:
                parts.append(
                    f"C{seg.c1.x:.1f},{h - seg.c1.y:.1f} "
                    f"{seg.c2.x:.1f},{h - seg.c2.y:.1f} "
                    f"{seg.end_point.x:.1f},{h - seg.end_point.y:.1f}")
        parts.append("Z")
    parts.append('" fill="black"/></svg>')
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glyphs", required=True)
    ap.add_argument("--out-svg", required=True)
    ap.add_argument("--turdsize", type=int, default=2,
                    help="drop speckles smaller than this (px)")
    ap.add_argument("--alphamax", type=float, default=1.0,
                    help="corner threshold; 0=polygons, higher=smoother")
    args = ap.parse_args()

    os.makedirs(args.out_svg, exist_ok=True)
    manifest_path = os.path.join(args.glyphs, "glyphs.json")
    manifest = json.load(open(manifest_path))
    for g in manifest:
        src = os.path.join(args.glyphs, g["file"])
        svg = trace(src, args.turdsize, args.alphamax)
        out = os.path.join(args.out_svg, g["codepoint"] + ".svg")
        open(out, "w").write(svg)
        g["svg"] = os.path.basename(out)
        print(f"{g['char']} -> {out}")
    json.dump(manifest, open(manifest_path, "w"), indent=1)
    print(f"traced {len(manifest)} glyphs")


if __name__ == "__main__":
    main()
