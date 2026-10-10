#!/usr/bin/env python3
"""
render_specimen.py — sales/display card for a font pack.

Renders the built TTF into a specimen poster: family name, full character
set, sample words, sizes. This is the card used on itch.io / Gumroad /
Creative Market listings.

Usage:
  python render_specimen.py --ttf fonts/Family-Regular.ttf --out SPECIMEN.png \\
      --title "Trippy Drippy Wizard" [--bg 14101E] [--ink F5B301]
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ttf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Font Pack")
    ap.add_argument("--bg", default="14101E")
    ap.add_argument("--ink", default="F5B301")
    ap.add_argument("--width", type=int, default=1600)
    args = ap.parse_args()

    bg = tuple(int(args.bg[i:i + 2], 16) for i in (0, 2, 4))
    ink = tuple(int(args.ink[i:i + 2], 16) for i in (0, 2, 4))
    W = args.width
    img = Image.new("RGB", (W, 2200), bg)
    d = ImageDraw.Draw(img)
    y = 80

    def text(s, size, yy, color=ink):
        nonlocal y
        f = ImageFont.truetype(args.ttf, size)
        bb = d.textbbox((0, 0), s, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, yy), s, font=f, fill=color)
        return yy + (bb[3] - bb[1]) + 40

    y = text(args.title.upper(), 120, y)
    y = text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 90, y)
    y = text("abcdefghijklmnopqrstuvwxyz", 90, y)
    y = text("0123456789  !?.,'\"-_:;()", 80, y)
    for line, size in [("TRIPPEDD NETWORK", 110), ("WIZARD GANG", 110),
                       ("The quick brown fox", 80),
                       ("GAMES • SHOWS • VLOGS", 70)]:
        y = text(line, size, y)
    y = text("free / open-source — built with Font Wizard", 44, y,
             color=(150, 150, 160))

    img = img.crop((0, 0, W, y + 60))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.save(args.out)
    print(f"specimen -> {args.out}")


if __name__ == "__main__":
    main()
