#!/usr/bin/env python3
"""
build_tdw.py — assemble Block Burner TTF from glyph bitmaps.

Uses OpenCV findContours (RETR_TREE) on white-on-black bitmaps so holes
(counters, doodle knockouts) get correct alternating winding. Contours are
simplified with approxPolyDP and emitted as TrueType line segments.

Usage:
  python build_tdw.py --glyphs work/trippy-drippy-wizard/glyphs \
      --out fonts/trippy-drippy-wizard/BlockBurner-Regular.ttf
"""
import argparse, json, os
import numpy as np
import cv2
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM = 1000
LETTER_H = 760        # normalized total ink height for letters/digits
SB = 70               # side bearing (units)
TRACE_H = 1200        # trace resolution (px tall)
EPS = 1.6             # approxPolyDP epsilon at TRACE_H

# char -> (target_height_units, anchor, anchor_value)
# anchor 'top': bbox top -> value ; 'bottom': bbox bottom -> value ; 'center'
TREAT = {
    '.': (250, 'bottom', 0),
    ',': (380, 'bottom', -80),
    "'": (380, 'top', 760),
    '-': (300, 'center', 330),
}
DEFAULT_TREAT = (LETTER_H, 'top', 760)


def load_bitmap(glyph_png):
    """Stored glyphs are black-on-white; return white-on-black float array at TRACE_H."""
    img = np.array(Image.open(glyph_png).convert('L'))
    img = 255 - img  # -> white on black
    h, w = img.shape
    s = TRACE_H / h
    img = cv2.resize(img, (int(w * s), TRACE_H), interpolation=cv2.INTER_LANCZOS4)
    _, bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    return bw


def trace_glyph(bw):
    """Return list of (points[N,2], depth) with points in image coords (y down)."""
    contours, hierarchy = cv2.findContours(bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if hierarchy is None:
        return []
    hierarchy = hierarchy[0]
    out = []
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < 8:
            continue
        approx = cv2.approxPolyDP(cnt, EPS, True).reshape(-1, 2)
        if len(approx) < 3:
            continue
        # nesting depth
        depth, p = 0, hierarchy[i][3]
        while p != -1:
            depth += 1
            p = hierarchy[p][3]
        out.append((approx.astype(float), depth))
    return out


def signed_area(pts):
    x = pts[:, 0]; y = pts[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def build_glyph(glyph_png, treat):
    bw = load_bitmap(glyph_png)
    H, W = bw.shape
    traced = trace_glyph(bw)
    if not traced:
        return None, 0
    # union bbox in image coords
    allpts = np.vstack([p for p, _ in traced])
    x0, y0 = allpts.min(axis=0)
    x1, y1 = allpts.max(axis=0)
    ink_w, ink_h = x1 - x0, y1 - y0
    th, anchor, aval = treat
    scale = th / ink_h if ink_h else 1.0

    pen = TTGlyphPen(None)
    for pts, depth in traced:
        # to font coords: flip y, scale, translate
        fx = (pts[:, 0] - x0) * scale
        fy = (H - pts[:, 1]) * scale  # y-up, top of ink at ink_h*scale
        if anchor == 'top':
            dy = aval - ink_h * scale
        elif anchor == 'bottom':
            dy = aval - 0
        else:  # center
            dy = aval - ink_h * scale / 2
        fy = fy + dy
        fpts = np.stack([fx, fy], axis=1)
        # winding: even depth -> CW (neg area in y-up), odd -> CCW
        area = signed_area(fpts)
        want_ccw = (depth % 2 == 1)
        if (area > 0) != want_ccw:
            fpts = fpts[::-1]
        pen.moveTo(tuple(fpts[0]))
        for pt in fpts[1:]:
            pen.lineTo(tuple(pt))
        pen.closePath()
    adv = int(ink_w * scale + 2 * SB)
    return pen.glyph(), adv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glyphs', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--name', default='BlockBurner')
    ap.add_argument('--version', default='1.0')
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(args.glyphs, 'glyphs.json')))
    glyph_order = ['.notdef', 'space'] + [g['char'] for g in manifest]
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)

    cmap = {}
    for g in manifest:
        cmap[ord(g['char'])] = g['char']
    for g in manifest:
        if g['char'].isupper():
            cmap[ord(g['char'].lower())] = g['char']
    fb.setupCharacterMap(cmap)

    fb.setupNameTable({
        'familyName': 'Block Burner',
        'styleName': 'Regular',
        'uniqueFontIdentifier': f'{args.name}-Regular-{args.version}',
        'fullName': 'Block Burner Regular',
        'psName': f'{args.name}-Regular',
        'version': f'Version {args.version}',
    })

    glyphs, metrics = {}, {}
    glyphs['.notdef'] = TTGlyphPen(None).glyph()
    metrics['.notdef'] = (600, 0)
    glyphs['space'] = TTGlyphPen(None).glyph()
    metrics['space'] = (350, 0)

    for g in manifest:
        ch = g['char']
        src = os.path.join(args.glyphs, g['file'])
        gl, adv = build_glyph(src, TREAT.get(ch, DEFAULT_TREAT))
        if gl is None:
            print(f'WARN: no contours in {ch}')
            continue
        glyphs[ch] = gl
        metrics[ch] = (adv, SB)
        print(f'{ch}: adv={adv}')

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-400)
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-400,
                usWinAscent=950, usWinDescent=450, usWeightClass=400)
    fb.setupPost()
    fb.setupMaxp()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fb.save(args.out)
    print(f'TTF -> {args.out}')


if __name__ == '__main__':
    main()
