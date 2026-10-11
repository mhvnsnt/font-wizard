#!/usr/bin/env python3
"""Pillow compositing: bg + text + overlays. Free, local.

Usage:
    composite.py --bg card.png --text "STAY TRIPPEDD" --font F.ttf
                 --size 120 --fill white --stroke 4 --out final.png
                 [--pos center|top|bottom|x,y] [--overlay logo.png --overlay-pos 40,40]

Multi-line: separate lines with \\n in --text.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

def parse_pos(s, W, H, tw, th):
    if s == "center": return ((W - tw) // 2, (H - th) // 2)
    if s == "top":    return ((W - tw) // 2, int(H * 0.08))
    if s == "bottom": return ((W - tw) // 2, int(H * 0.84) - th)
    x, y = s.split(","); return (int(x), int(y))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--text", default="")
    ap.add_argument("--font", default=None)
    ap.add_argument("--size", type=int, default=96)
    ap.add_argument("--fill", default="white")
    ap.add_argument("--stroke", type=int, default=0)
    ap.add_argument("--stroke-fill", default="black")
    ap.add_argument("--pos", default="center")
    ap.add_argument("--overlay", default=None)
    ap.add_argument("--overlay-pos", default="0,0")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base = Image.open(args.bg).convert("RGBA")
    W, H = base.size

    if args.overlay:
        ov = Image.open(args.overlay).convert("RGBA")
        ox, oy = map(int, args.overlay_pos.split(","))
        base.alpha_composite(ov, (ox, oy))

    if args.text:
        font = ImageFont.truetype(args.font, args.size) if args.font \
            else ImageFont.load_default()
        d = ImageDraw.Draw(base)
        lines = args.text.replace("\\n", "\n").split("\n")
        boxes = [d.textbbox((0, 0), ln, font=font, stroke_width=args.stroke)
                 for ln in lines]
        tw = max(b[2] - b[0] for b in boxes)
        th = sum(b[3] - b[1] for b in boxes)
        x, y = parse_pos(args.pos, W, H, tw, th)
        for ln, b in zip(lines, boxes):
            d.text((x, y), ln, font=font, fill=args.fill,
                   stroke_width=args.stroke, stroke_fill=args.stroke_fill)
            y += b[3] - b[1]

    base.convert("RGB").save(args.out)
    print(f"saved {args.out} {base.size}")

if __name__ == "__main__":
    main()
