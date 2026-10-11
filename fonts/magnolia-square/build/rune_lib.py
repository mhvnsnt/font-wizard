"""Magnolia Rune glyph construction library.
Builds blackletter glyphs in the rough/fragmented 'rune' style, then
distresses them to match the traced v1 glyphs (fence-gap fragmentation,
jagged edges, bites, detached chips).
"""
import math, random
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import translate

# ---- metrics (font units, y-up) ----
BASE = 1
CAP = 761
XH = 470          # x-height for lowercase
ASC = 700         # lowercase ascender (b d f h k l)
DESC = -180       # descender (g j p q y)
LSB = 70
STEMW = 140       # main vertical stroke width
BARH = 120        # horizontal bar thickness

def P(pts):
    """Polygon from point list (auto-fixed)."""
    p = Polygon(pts)
    if not p.is_valid:
        p = p.buffer(0)
    return p

def rect(x0, y0, x1, y1):
    return P([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])

def U(*geoms):
    """Union of geometries; returns list of Polygons. Flattens nested lists."""
    flat = []
    for g in geoms:
        if isinstance(g, (list, tuple)):
            flat.extend(g)
        else:
            flat.append(g)
    u = unary_union(flat)
    if u.is_empty:
        return []
    if isinstance(u, Polygon):
        return [u]
    return [g for g in u.geoms if isinstance(g, Polygon)]

def octagon(cx, cy, rx, ry, rot=0.0):
    pts = []
    for k in range(8):
        a = math.pi/4*k + rot
        pts.append((cx + rx*math.cos(a), cy + ry*math.sin(a)))
    return P(pts)

def ring(cx, cy, rx, ry, t):
    """Octagonal ring (bowl)."""
    outer = octagon(cx, cy, rx, ry)
    inner = octagon(cx, cy, max(rx-t,1), max(ry-t,1))
    d = outer.difference(inner)
    if isinstance(d, Polygon):
        return [d]
    return [g for g in d.geoms if isinstance(g, Polygon)]

def stem(x, w=STEMW, y0=BASE, y1=CAP, serif=55, flare=42):
    """Vertical stem with flared slab serifs top/bottom."""
    parts = [rect(x, y0, x+w, y1)]
    # top serif
    parts.append(P([
        (x-flare, y1-serif), (x+w+flare, y1-serif),
        (x+w+flare-18, y1), (x-flare+18, y1)]))
    parts.append(rect(x-flare, y1-serif, x+w+flare, y1-18))
    # bottom serif
    parts.append(P([
        (x-flare, y0+serif), (x+w+flare, y0+serif),
        (x+w+flare-18, y0), (x-flare+18, y0)]))
    parts.append(rect(x-flare, y0+18, x+w+flare, y0+serif))
    return U(*parts)

def hbar(x0, x1, y, h=BARH, chamfer=30):
    """Horizontal bar with 45-degree chamfered ends."""
    return [P([
        (x0+chamfer, y), (x1-chamfer, y),
        (x1, y+chamfer), (x1, y+h-chamfer),
        (x1-chamfer, y+h), (x0+chamfer, y+h),
        (x0, y+h-chamfer), (x0, y+chamfer)])]

def diag(x0, y0, x1, y1, w=STEMW):
    """Thick diagonal bar from (x0,y0) to (x1,y1)."""
    dx, dy = x1-x0, y1-y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy/L*w/2, dx/L*w/2
    return [P([(x0+nx,y0+ny),(x1+nx,y1+ny),(x1-nx,y1-ny),(x0-nx,y0-ny)])]

def diamond(cx, cy, r):
    return [P([(cx,cy+r),(cx+r,cy),(cx,cy-r),(cx-r,cy)])]

def stroke(pts, w):
    """Thick stroked path -> polygon(s). pts = [(x,y),...]."""
    from shapely.geometry import LineString
    ls = LineString(pts)
    p = ls.buffer(w/2, cap_style='flat', join_style='mitre')
    if isinstance(p, Polygon):
        return [p]
    return [g for g in p.geoms if isinstance(g, Polygon)]

# ---------------- distress ----------------
def _jitter_ring(coords, rng, amp):
    pts = list(coords)[:-1]  # drop closing dup
    out = []
    n = len(pts)
    for i,(x,y) in enumerate(pts):
        x2,y2 = pts[(i+1)%n]
        dx, dy = x2-x, y2-y
        L = math.hypot(dx,dy) or 1
        nx, ny = -dy/L, dx/L
        steps = max(1, int(L/20))
        for s in range(steps):
            t = s/steps
            j = rng.uniform(-amp, amp)
            j2 = rng.uniform(-amp*0.4, amp*0.4)
            out.append((x+dx*t+nx*j+dx/L*j2, y+dy*t+ny*j+dy/L*j2))
    return out

def distress(poly, rng, jag_amp=8, bites=2, frag=True):
    """Apply rune distress to a shapely Polygon. Returns list of Polygons."""
    # 1. jagged edges
    ext = _jitter_ring(list(poly.exterior.coords), rng, jag_amp)
    holes = [_jitter_ring(list(r.coords), rng, jag_amp*0.8) for r in poly.interiors]
    holes = [h for h in holes if len(h) >= 3]
    if len(ext) < 3:
        return []
    try:
        p = Polygon(ext, holes)
        if not p.is_valid:
            p = p.buffer(0)
    except Exception:
        p = poly
    if p.is_empty:
        return []
    polys = [p] if isinstance(p, Polygon) else [g for g in p.geoms if isinstance(g, Polygon)]
    out = []
    minx, miny, maxx, maxy = poly.bounds
    for p in polys:
        # 2. bites: subtract small notched rects at random edge spots
        for _ in range(bites):
            bx = rng.uniform(minx, maxx)
            by = rng.uniform(miny, maxy)
            bw = rng.uniform(15, 38)
            bh = rng.uniform(10, 26)
            ang = rng.uniform(0, math.pi)
            bite = rect(-bw/2, -bh/2, bw/2, bh/2)
            # rotate+translate: manual
            c, s = math.cos(ang), math.sin(ang)
            pts = [(bx + x*c - y*s, by + x*s + y*c) for x,y in [(-bw/2,-bh/2),(bw/2,-bh/2),(bw/2,bh/2),(-bw/2,bh/2)]]
            p = p.difference(P(pts))
            if p.is_empty:
                break
        if p.is_empty:
            continue
        # 3. fence-gap fragmentation: subtract 1 horizontal band
        if frag and rng.random() < 0.45 and (maxy-miny) > 260:
            band_y = rng.uniform(miny+90, maxy-150)
            band_h = rng.uniform(55, 110)
            band = rect(minx-50, band_y, maxx+50, band_y+band_h)
            p = p.difference(band)
            if p.is_empty:
                continue
        if isinstance(p, Polygon):
            out.append(p)
        else:
            out.extend(g for g in p.geoms if isinstance(g, Polygon))
    # 4. detached chip (like A's floating piece)
    if rng.random() < 0.15:
        cw, chh = rng.uniform(50,110), rng.uniform(35,70)
        cxp = rng.uniform(minx, maxx)
        cyp = miny - rng.uniform(40, 95)
        chip = rect(cxp-cw/2, cyp-chh/2, cxp+cw/2, cyp+chh/2)
        chip = distress_chip(chip, rng)
        out.append(chip)
    return [g for g in out if g.area > 400]

def jitterv(rng, a):
    return rng.uniform(-a, a)

def distress_chip(chip, rng):
    ext = _jitter_ring(list(chip.exterior.coords), rng, 12)
    p = Polygon(ext)
    return p if p.is_valid else chip

def finalize(polys):
    """Orient for TrueType: exterior CW (neg area y-up), holes CCW."""
    from shapely.geometry.polygon import orient
    out = []
    for p in polys:
        p = orient(p, sign=-1.0)
        out.append(p)
    return out
