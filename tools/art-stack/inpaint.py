#!/usr/bin/env python3
"""Object removal / occlusion erasing (fence wires, watermarks, etc.).

Free, local. Uses OpenCV inpainting. Hook for LaMa (SOTA) when installed.

Usage:
    inpaint.py in.jpg mask.png out.jpg [--method telea|ns] [--radius 3]

The mask is a grayscale image: WHITE pixels = area to erase and fill.
Make the mask with any editor, or generate one (e.g. thin vertical bars).

LaMa upgrade path (optional, heavier):
    pip install torch  # then clone https://github.com/advimman/lama
    and point --lama-ckpt at big-lama.pt. This script auto-uses LaMa
    when --lama-ckpt is given and torch is importable.

Example (erase fence wires crossing sign letters):
    inpaint.py sign.jpg wire_mask.png sign_clean.jpg --radius 5
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("mask", help="grayscale mask, white = erase")
    ap.add_argument("dst")
    ap.add_argument("--method", default="telea", choices=["telea", "ns"])
    ap.add_argument("--radius", type=float, default=3.0)
    ap.add_argument("--lama-ckpt", default=None,
                    help="path to big-lama.pt for SOTA inpainting")
    args = ap.parse_args()

    import cv2
    img = cv2.imread(args.src)
    m = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"cannot read {args.src}")
    if m is None:
        raise SystemExit(f"cannot read mask {args.mask}")
    if m.shape[:2] != img.shape[:2]:
        m = cv2.resize(m, (img.shape[1], img.shape[0]))
    _, m = cv2.threshold(m, 127, 255, cv2.THRESH_BINARY)

    if args.lama_ckpt:
        try:
            out = lama_inpaint(args.src, args.mask, args.lama_ckpt)
            cv2.imwrite(args.dst, out)
            print(f"saved {args.dst} (LaMa)")
            return
        except ImportError:
            print("torch/lama unavailable, falling back to OpenCV", file=sys.stderr)

    flag = cv2.INPAINT_TELEA if args.method == "telea" else cv2.INPAINT_NS
    out = cv2.inpaint(img, m, args.radius, flag)
    cv2.imwrite(args.dst, out)
    print(f"saved {args.dst} ({args.method}, r={args.radius})")

def lama_inpaint(src, mask, ckpt):
    """SOTA inpainting via LaMa. Requires torch + lama repo on sys.path."""
    import sys, torch
    sys.path.insert(0, str(Path(__file__).parent / "lama"))
    from saicinpainting.evaluation.utils import move_to_device
    from saicinpainting.training.trainers import load_checkpoint
    import cv2
    model = load_checkpoint(ckpt, strict=False, map_location="cpu")
    model = move_to_device(model, "cpu").eval()
    img = cv2.imread(src)
    m = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
    img_t = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).permute(2, 0, 1).unsqueeze(0).float() / 255
    m_t = torch.from_numpy(m).unsqueeze(0).unsqueeze(0).float() / 255
    with torch.no_grad():
        res = model({"image": img_t, "mask": m_t})["inpainted"][0]
    out = (res.permute(1, 2, 0).numpy() * 255).astype("uint8")
    return cv2.cvtColor(out, cv2.COLOR_RGB2BGR)

import sys
if __name__ == "__main__":
    main()
