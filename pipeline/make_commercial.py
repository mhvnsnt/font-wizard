#!/usr/bin/env python3
"""Font commercial generator — LAYOUT v2 (owner 2026-10-10).
Usage: make_commercial.py <font_name> <ttf_path> <output_mp4> [cta] [tagline]
Rotation lists live in commercial_rotation.json next to this script.

LAYOUT v2:
- 0-3s  FONT TITLE types out BIG (~200-220px) within 5% broadcast safe-action
         inset, vertically centered. The hero — details clearly visible.
- 3-4s  CTA small (~72px) in the font, lower-third margin, black on white.
- 4-5s  Rotating 3-word TAGLINE small (~72px) in the font, lower-third margin,
         black on white.
- 5-7s  CTA small (~72px) white on black, wavy trippy, lower-third margin.
- 7-10s END CARD: font name BIG gold in the font, then itch.io URL and
         "FONT PACK — INSTALL ON ANY DEVICE" smaller below, wavy trippy.
"""
import json, os, sys, random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROT = json.load(open(os.path.join(HERE, 'commercial_rotation.json')))

W, H, FPS = 1920, 1080, 30
SAFE = 0.05                    # 5% broadcast safe-action inset
SAFE_W = int(W * (1 - 2 * SAFE))
SAFE_X0 = int(W * SAFE)

TITLE_MAX = 220               # hero title size
MARGIN_SIZE = 72              # tagline / CTA margin size
MARGIN_Y = 840                # lower-third margin baseline area

def center_x(d, text, font):
    bb = d.textbbox((0, 0), text, font=font)
    return (W - (bb[2] - bb[0])) // 2

def fit_font(ttf, text, max_size, max_width):
    """Largest font size <= max_size whose text fits max_width."""
    size = max_size
    while size > 10:
        f = ImageFont.truetype(ttf, size)
        tmp = Image.new('RGB', (W, H))
        d = ImageDraw.Draw(tmp)
        bb = d.textbbox((0, 0), text, font=f)
        if (bb[2] - bb[0]) <= max_width:
            return f
        size -= 10
    return ImageFont.truetype(ttf, 10)

def vcenter_y(d, text, font):
    bb = d.textbbox((0, 0), text, font=font)
    return (H - (bb[3] - bb[1])) // 2

def wavy(img, t):
    arr = np.array(img)
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (20 * np.sin(yy / 60 + t * 4) + 12 * np.sin(yy / 23 - t * 7)).astype(int)
    return Image.fromarray(arr[yy, np.clip(xx + dx, 0, W - 1)])

def main():
    font_name, ttf, out = sys.argv[1], sys.argv[2], sys.argv[3]
    cta = sys.argv[4] if len(sys.argv) > 4 else random.choice(ROT['ctas'])
    tag = sys.argv[5] if len(sys.argv) > 5 else random.choice(ROT['taglines'])
    print(f'Commercial v2: {font_name} | CTA: "{cta}" | tagline: "{tag}"')

    title_font = fit_font(ttf, font_name, TITLE_MAX, SAFE_W)
    margin_font = ImageFont.truetype(ttf, MARGIN_SIZE)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    frames_dir = os.path.join(os.path.dirname(out), '_frames')
    os.makedirs(frames_dir, exist_ok=True)

    fn = 0
    def save(img):
        nonlocal fn
        img.save(f'{frames_dir}/f{fn:04d}.png')
        fn += 1

    # 0-3s: font name types out BIG, black on white, centered in safe area
    n = len(font_name)
    for i in range(3 * FPS):
        img = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        t = font_name[:int(n * (i + 1) / (3 * FPS)) + 1]
        d.text((center_x(d, t, title_font), vcenter_y(d, t, title_font)), t,
               font=title_font, fill=(0, 0, 0))
        save(img)

    # 3-4s: CTA small in margin, black on white
    for _ in range(1 * FPS):
        img = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((center_x(d, cta, margin_font), vcenter_y(d, cta, margin_font)), cta,
               font=margin_font, fill=(0, 0, 0))
        save(img)

    # 4-5s: tagline small in margin, black on white
    for _ in range(1 * FPS):
        img = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((center_x(d, tag, margin_font), vcenter_y(d, tag, margin_font)), tag,
               font=margin_font, fill=(0, 0, 0))
        save(img)

    # 5-7s: CTA small in margin, white on black, wavy
    for i in range(2 * FPS):
        img = Image.new('RGB', (W, H), (0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((center_x(d, cta, margin_font), vcenter_y(d, cta, margin_font)), cta,
               font=margin_font, fill=(255, 255, 255))
        save(wavy(img, i / FPS))

    # 7-10s: end card — font name BIG gold, URL + install line smaller below
    try:
        clean = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    except OSError:
        clean = ImageFont.load_default()
    for i in range(3 * FPS):
        img = Image.new('RGB', (W, H), (10, 5, 15))
        d = ImageDraw.Draw(img)
        t = font_name
        d.text((center_x(d, t, title_font), 330), t, font=title_font, fill=(247, 190, 30))
        d.text((center_x(d, "mhvnsnt.itch.io", clean), 640), "mhvnsnt.itch.io",
               font=clean, fill=(255, 255, 255))
        sub = "FONT PACK \u2014 INSTALL ON ANY DEVICE"
        d.text((center_x(d, sub, clean), 730), sub, font=clean, fill=(180, 130, 255))
        save(wavy(img, i / FPS + 10))

    os.system(f"ffmpeg -y -v error -framerate 30 -i {frames_dir}/f%04d.png "
              f"-c:v libx264 -pix_fmt yuv420p -crf 18 {out}")
    print(f'Done: {out} ({fn} frames)')

if __name__ == '__main__':
    main()
