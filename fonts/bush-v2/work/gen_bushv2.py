#!/usr/bin/env python3
"""Bush V2 generator — genuinely crude hand-drawn fat-marker glyphs.

Each glyph is defined as hand-authored stroke polylines (centerlines).
Rendering lays down overlapping jittered marker "dabs" along each stroke:
positional jitter, varying pressure (dab radius), per-vertex lump noise,
dry-brush skips, ink speckle, per-glyph baseline shift + rotation.

Vector outlines are built directly with fontTools (each dab = one polygonal
contour; overlapping same-winding contours fill as a union). No tracing step.
"""

import math, os, random, hashlib, sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPM = 1000
CAP = 700          # cap height in font units
BASE = 150         # baseline offset in font units
S = CAP / 100.0    # glyph-space (0..100) -> font units

# ---------------------------------------------------------------- strokes
# y-up, x 0..100, baseline y=0, cap y=100. Each glyph: list of strokes,
# each stroke: list of (x, y). Dots are single-point strokes.
STROKES = {
 'A': [[(10,0),(50,100),(90,0)], [(28,35),(72,35)]],
 'B': [[(15,0),(15,100)], [(15,100),(55,100),(70,85),(70,65),(55,52),(15,52)],
       [(15,52),(60,52),(78,35),(78,15),(60,0),(15,0)]],
 'C': [[(85,80),(60,95),(35,95),(15,75),(15,25),(35,5),(60,5),(85,20)]],
 'D': [[(15,0),(15,100)], [(15,100),(55,100),(80,75),(80,25),(55,0),(15,0)]],
 'E': [[(80,100),(15,100),(15,0),(80,0)], [(15,50),(65,50)]],
 'F': [[(80,100),(15,100),(15,0)], [(15,52),(65,52)]],
 'G': [[(85,80),(60,95),(35,95),(15,75),(15,25),(35,5),(60,5),(85,20),(85,45),(55,45)]],
 'H': [[(15,0),(15,100)], [(85,0),(85,100)], [(15,50),(85,50)]],
 'I': [[(50,0),(50,100)], [(25,100),(75,100)], [(25,0),(75,0)]],
 'J': [[(85,100),(85,25),(65,5),(40,5),(25,20)]],
 'K': [[(15,0),(15,100)], [(80,100),(15,45)], [(35,60),(80,0)]],
 'L': [[(15,100),(15,0),(80,0)]],
 'M': [[(10,0),(10,100),(50,40),(90,100),(90,0)]],
 'N': [[(15,0),(15,100),(85,0),(85,100)]],
 'O': [[(50,100),(75,95),(90,75),(90,25),(75,5),(50,0),(25,5),(10,25),(10,75),(25,95),(50,100)]],
 'P': [[(15,0),(15,100),(60,100),(78,85),(78,60),(60,48),(15,48)]],
 'Q': [[(50,100),(75,95),(90,75),(90,25),(75,5),(50,0),(25,5),(10,25),(10,75),(25,95),(50,100)],
       [(68,22),(90,-8)]],
 'R': [[(15,0),(15,100),(60,100),(78,85),(78,60),(60,48),(15,48)], [(50,48),(80,0)]],
 'S': [[(80,85),(60,98),(35,98),(18,85),(18,68),(35,55),(65,45),(82,32),(82,15),(65,2),(40,2),(20,12)]],
 'T': [[(50,0),(50,100)], [(15,100),(85,100)]],
 'U': [[(15,100),(15,30),(30,8),(50,0),(70,8),(85,30),(85,100)]],
 'V': [[(10,100),(50,0),(90,100)]],
 'W': [[(5,100),(25,0),(50,60),(75,0),(95,100)]],
 'X': [[(15,0),(85,100)], [(15,100),(85,0)]],
 'Y': [[(10,100),(50,50),(90,100)], [(50,50),(50,0)]],
 'Z': [[(15,100),(85,100),(15,0),(85,0)]],
 '0': [[(50,100),(72,95),(85,75),(85,25),(72,5),(50,0),(28,5),(15,25),(15,75),(28,95),(50,100)]],
 '1': [[(30,80),(55,100),(55,0)], [(30,0),(80,0)]],
 '2': [[(20,78),(38,95),(62,92),(74,75),(60,55),(22,22),(20,0),(80,0)]],
 '3': [[(20,85),(45,98),(65,90),(70,75),(55,62),(35,58)],
       [(35,58),(60,55),(72,40),(65,22),(45,12),(25,15)]],
 '4': [[(58,100),(14,32),(82,32),(82,0)]],
 '5': [[(75,100),(35,100),(28,60),(55,62),(70,50),(70,30),(55,15),(30,12),(20,20)]],
 '6': [[(70,85),(50,98),(30,90),(18,70),(15,40),(25,15),(45,5),(60,12),(68,30),(60,48),(40,52),(25,45)]],
 '7': [[(15,100),(85,100),(40,0)]],
 '8': [[(50,100),(68,95),(75,80),(68,66),(50,60),(32,66),(25,80),(32,95),(50,100)],
       [(50,60),(72,55),(82,35),(72,12),(50,5),(28,12),(18,35),(28,55),(50,60)]],
 '9': [[(30,15),(50,2),(70,10),(82,30),(85,60),(75,85),(55,95),(40,88),(32,70),(40,52),(60,48),(75,55)]],
 '!': [[(50,100),(50,35)], [(50,12)]],
 '?': [[(25,80),(40,95),(60,92),(68,75),(55,60),(45,52),(45,35)], [(45,10)]],
 '.': [[(50,8)]],
 ',': [[(55,10),(45,-12)]],
 "'": [[(55,100),(45,75)]],
 '-': [[(20,45),(80,45)]],
 '&': [[(75,30),(58,48),(30,54),(20,70),(30,86),(50,86),(60,74),(38,42),(56,16),(74,12),(82,26),(72,42)]],
}

GLYPH_NAMES = {
 'A':'A','B':'B','C':'C','D':'D','E':'E','F':'F','G':'G','H':'H','I':'I',
 'J':'J','K':'K','L':'L','M':'M','N':'N','O':'O','P':'P','Q':'Q','R':'R',
 'S':'S','T':'T','U':'U','V':'V','W':'W','X':'X','Y':'Y','Z':'Z',
 '0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six',
 '7':'seven','8':'eight','9':'nine',
 '!':'exclam','?':'question','.':'period',',':'comma',"'":'quotesingle',
 '-':'hyphen','&':'ampersand',
}

# ---------------------------------------------------------------- render
def seed_for(ch):
    return int(hashlib.md5(ch.encode()).hexdigest()[:8], 16)

def subdivide(pts, step=2.5):
    """Resample polyline to ~step-spaced points."""
    out = []
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append(pts[-1])
    return out

def dab_poly(cx, cy, r, rng, n=10):
    pts = []
    a0 = rng.uniform(0, 2 * math.pi)
    for i in range(n):
        a = a0 + 2 * math.pi * i / n + rng.uniform(-0.15, 0.15)
        rr = r * (1 + rng.uniform(-0.32, 0.32))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def render_glyph(ch):
    rng = random.Random(seed_for(ch))
    strokes = STROKES[ch]
    # per-glyph personality
    dy = rng.uniform(-8, 8)                    # baseline shift (±8% of height)
    rot = math.radians(rng.uniform(-4, 4))    # slight rotation
    lean = rng.uniform(-0.06, 0.06)           # horizontal shear
    cosr, sinr = math.cos(rot), math.sin(rot)

    def xform(x, y):
        x = x + lean * y
        x, y = x - 50, y - 50
        x, y = x * cosr - y * sinr, x * sinr + y * cosr
        return x + 50, y + 50 + dy

    contours = []  # in glyph space (0..100)
    for stroke in strokes:
        if len(stroke) == 1:
            # dot: one lumpy blob
            x, y = xform(*stroke[0])
            x += rng.uniform(-2, 2); y += rng.uniform(-2, 2)
            contours.append(dab_poly(x, y, rng.uniform(9, 12), rng))
            continue
        pts = [xform(x, y) for x, y in stroke]
        smp = subdivide(pts)
        phase = rng.uniform(0, 2 * math.pi)
        freq = rng.uniform(0.5, 1.1)
        skip_streak = 0
        for i, (x, y) in enumerate(smp):
            t = i / max(1, len(smp) - 1)
            # unsteady-hand drift, perpendicular-ish wobble
            x += rng.uniform(-2.4, 2.4) + 2.0 * math.sin(t * 9 + phase)
            y += rng.uniform(-2.4, 2.4) + 2.0 * math.cos(t * 7 + phase * 1.7)
            # marker pressure -> dab radius
            r = 8.5 * (0.72 + 0.55 * abs(math.sin(t * math.pi * freq + phase))
                       + rng.uniform(-0.18, 0.18))
            r = max(3.5, r)
            # dry-brush skip (never two in a row -> no broken strokes)
            if rng.random() < 0.055 and skip_streak == 0 and 0 < i < len(smp) - 1:
                skip_streak = 1
                continue
            skip_streak = 0
            contours.append(dab_poly(x, y, r, rng))
        # ink speckle near the stroke
        for _ in range(rng.randint(8, 16)):
            sx, sy = rng.choice(smp)
            contours.append(dab_poly(sx + rng.uniform(-6, 6),
                                     sy + rng.uniform(-6, 6),
                                     rng.uniform(1.2, 3.0), rng, n=7))

    # to font units
    fu = []
    for poly in contours:
        fu.append([(round((x * S) + 60), round(y * S + BASE)) for x, y in poly])
    xs = [p[0] for poly in fu for p in poly]
    adv = max(300, (max(xs) - min(xs)) + 130)
    return fu, adv

# ---------------------------------------------------------------- TTF
def build_ttf(path):
    fb = FontBuilder(UPM, isTTF=True)
    order = ['.notdef', 'space']
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + ['!', '?', '.', ',', "'", '-', '&']
    for c in chars:
        order.append(GLYPH_NAMES[c])
    fb.setupGlyphOrder(order)

    glyphs, metrics = {}, {}
    # .notdef
    pen = TTGlyphPen(None)
    pen.moveTo((60, 0)); pen.lineTo((540, 0)); pen.lineTo((540, 700)); pen.lineTo((60, 700))
    pen.closePath()
    glyphs['.notdef'] = pen.glyph()
    metrics['.notdef'] = (600, 60)

    glyphs['space'] = TTGlyphPen(None).glyph()
    metrics['space'] = (400, 0)

    for c in chars:
        contours, adv = render_glyph(c)
        pen = TTGlyphPen(None)
        for poly in contours:
            pen.moveTo(poly[0])
            for pt in poly[1:]:
                pen.lineTo(pt)
            pen.closePath()
        name = GLYPH_NAMES[c]
        glyphs[name] = pen.glyph()
        metrics[name] = (int(adv), 60)

    cmap_dict = {ord(c): GLYPH_NAMES[c] for c in chars}
    cmap_dict[ord(' ')] = 'space'
    fb.setupCharacterMap(cmap_dict)
    # lowercase -> caps
    cmap = fb.font['cmap'].tables[0].cmap
    for lc, uc in zip('abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        cmap[ord(lc)] = GLYPH_NAMES[uc]

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=850, descent=-200)
    fb.setupNameTable({'familyName': 'Bush V2', 'styleName': 'Regular',
                       'fullName': 'Bush V2 Regular',
                       'psName': 'BushV2-Regular',
                       'typographicFamily': 'Bush V2',
                       'typographicSubfamily': 'Regular'})
    fb.setupOS2()
    fb.setupPost()
    fb.save(path)
    print('TTF:', path)

# ---------------------------------------------------------------- PNG pack
def rasterize(contours, adv, px=2000, ink=(0, 0, 0)):
    sc = px / UPM
    xs = [p[0] for poly in contours for p in poly]
    minx, maxx = min(xs), max(xs)
    img = Image.new('RGBA', (int((maxx - minx) * sc) + 16, px + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for poly in contours:
        d.polygon([((x - minx) * sc + 8, px + 4 - y * sc) for x, y in poly],
                  fill=ink + (255,))
    return img

def build_pngs(ttf_path):
    from fontTools.ttLib import TTFont
    f = TTFont(ttf_path)
    glyf = f['glyf']
    hmtx = f['hmtx']
    pngdir = os.path.join(OUT, 'png')
    os.makedirs(pngdir, exist_ok=True)
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + ['!', '?', '.', ',', "'", '-', '&']
    for c in chars:
        contours, adv = render_glyph(c)
        img = rasterize(contours, adv)
        fn = 'quotesingle.png' if c == "'" else ('hyphen.png' if c == '-' else
              ('ampersand.png' if c == '&' else ('exclam.png' if c == '!' else
              ('question.png' if c == '?' else ('period.png' if c == '.' else
              ('comma.png' if c == ',' else c + '.png'))))))
        img.save(os.path.join(pngdir, fn))
    print('PNGs:', len(chars))

# ---------------------------------------------------------------- specimen
def build_specimen(ttf_path):
    Wp, Hp = 1600, 2000
    img = Image.new('RGB', (Wp, Hp), (255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        bush = ImageFont.truetype(ttf_path, 120)
        bush_sm = ImageFont.truetype(ttf_path, 72)
        clean = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
        clean_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
    except OSError:
        bush = ImageFont.load_default(); bush_sm = bush; clean = bush; clean_sm = bush
    d.text((60, 40), 'BUSH V2', font=bush, fill=(0, 0, 0))
    d.text((60, 190), 'crude hand-marker font — 43 glyphs', font=clean_sm, fill=(80, 80, 80))
    y = 300
    for line in ['ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ', '0123456789', '! ? . , \' - &']:
        d.text((60, y), line, font=bush_sm, fill=(0, 0, 0))
        y += 130
    d.text((60, y + 20), 'A kid drew this with a fat marker. On purpose.',
           font=clean_sm, fill=(80, 80, 80))
    d.text((60, y + 70), 'TAP TO TYPE — install the TTF, pick BUSH V2.',
           font=clean_sm, fill=(80, 80, 80))
    p = os.path.join(OUT, 'SPECIMEN.png')
    img.save(p)
    print('SPECIMEN:', p)

if __name__ == '__main__':
    ttf = os.path.join(OUT, 'BushV2-Regular.ttf')
    build_ttf(ttf)
    build_pngs(ttf)
    build_specimen(ttf)
