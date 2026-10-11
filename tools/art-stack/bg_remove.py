#!/usr/bin/env python3
"""AI background removal / cutouts. Free, local, no API key.

Usage:
    bg_remove.py in.jpg out.png [--model MODEL] [--alpha-matting] [--batch DIR]

Models (rembg sessions):
    u2net              fast default (~170MB, good enough for most cutouts)
    isnet-general-use  better edges (~170MB)
    birefnet-general   SOTA matting (~900MB, best hair/fine detail)
    rmbg               balanced alternative

Examples:
    bg_remove.py photo.jpg cutout.png
    bg_remove.py --model birefnet-general photo.jpg cutout.png
    bg_remove.py --batch intake/ --model isnet-general-use   # writes *_cutout.png
"""
import argparse, sys
from pathlib import Path
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="input image (omit with --batch)")
    ap.add_argument("dst", nargs="?", help="output PNG")
    ap.add_argument("--model", default="u2net",
                    choices=["u2net", "isnet-general-use", "birefnet-general", "rmbg"])
    ap.add_argument("--batch", help="process every image in DIR, write *_cutout.png")
    ap.add_argument("--alpha-matting", action="store_true",
                    help="extra edge refinement (slower)")
    args = ap.parse_args()

    from rembg import new_session, remove
    session = new_session(args.model)
    kwargs = {}
    if args.alpha_matting:
        kwargs = {"alpha_matting": True, "alpha_matting_foreground_threshold": 240,
                  "alpha_matting_background_threshold": 10}

    def cut(src: Path, dst: Path):
        out = remove(Image.open(src), session=session, **kwargs)
        out.save(dst)
        print(f"saved {dst} {out.size} {out.mode}")

    if args.batch:
        d = Path(args.batch)
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                cut(f, f.with_name(f.stem + "_cutout.png"))
    else:
        if not args.src or not args.dst:
            ap.error("need src and dst (or --batch)")
        cut(Path(args.src), Path(args.dst))

if __name__ == "__main__":
    main()
