"""Assemble Magnolia Rune full-charset TTF.
Usage: python3 rune_build.py
Reads ../MagnoliaRune-Regular.ttf, adds all new glyphs, writes back.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import rune_glyphs as RG
from rune_lib import distress

SRC = os.path.join(os.path.dirname(__file__), '..', 'MagnoliaRune-Regular.ttf')

def poly_to_contours(polys):
    """Shapely polygons -> list of contours (each a list of (x,y) int tuples)."""
    contours = []
    for p in polys:
        p = orient(p, sign=-1.0)  # exterior CW (y-up)
        ext = [(int(round(x)), int(round(y))) for x, y in list(p.exterior.coords)[:-1]]
        if len(ext) >= 3:
            contours.append(ext)
        for ring in p.interiors:
            hole = [(int(round(x)), int(round(y))) for x, y in list(ring.coords)[:-1]]
            if len(hole) >= 3:
                contours.append(hole)
    return contours

def contours_to_glyph(contours):
    g = Glyph()
    coords, endpts, flags = [], [], []
    for c in contours:
        for (x, y) in c:
            coords.append((x, y))
            flags.append(1)
        endpts.append(len(coords) - 1)
    g.coordinates = GlyphCoordinates(coords)
    g.endPtsOfContours = endpts
    g.flags = bytearray(flags)
    g.numberOfContours = len(contours)
    g.program = Program()
    g.program.fromBytecode(b'')
    return g

def build_one(name, fn, seed):
    rng = random.Random(seed)
    clean = fn()
    polys = []
    # glyphs where a fragmentation band would destroy legibility
    nofrag = {'ampersand'}
    for p in clean:
        polys.extend(distress(p, rng, frag=(name not in nofrag)))
    polys = [p for p in polys if p.area > 500]
    if not polys:
        polys = clean
    return polys

def main():
    f = TTFont(SRC)
    glyf = f['glyf']
    hmtx = f['hmtx']
    cmap = f.getBestCmap()
    order = f.getGlyphOrder()

    new_glyphs = []  # (name, codepoint or None)
    # uppercase
    for name, fn in RG.UPPER.items():
        new_glyphs.append((name, ord(name)))
    # lowercase
    for name, fn in RG.LOWER.items():
        new_glyphs.append((name, ord(name)))
    # digits
    for name, fn in RG.DIGITS.items():
        new_glyphs.append((name, RG.DIGIT_CODEPOINTS[name]))
    # punctuation
    for name, fn in RG.PUNCT.items():
        new_glyphs.append((name, RG.PUNCT_CODEPOINTS[name]))
    # symbols
    for name, fn in RG.SYMBOLS.items():
        new_glyphs.append((name, RG.SYMBOL_CODEPOINTS[name]))

    fn_map = {}
    fn_map.update(RG.UPPER); fn_map.update(RG.LOWER)
    fn_map.update(RG.DIGITS); fn_map.update(RG.PUNCT); fn_map.update(RG.SYMBOLS)

    for idx, (name, cp) in enumerate(new_glyphs):
        polys = build_one(name, fn_map[name], seed=1000 + idx)
        contours = poly_to_contours(polys)
        if not contours:
            print('WARN: empty glyph', name)
            continue
        g = contours_to_glyph(contours)
        glyf[name] = g
        # metrics from bounds
        allx = [x for c in contours for x, y in c]
        minx, maxx = min(allx), max(allx)
        width = maxx - minx
        adv = int(math.ceil(width + 150))
        # shift glyph so lsb = 70
        shift = 70 - minx
        if shift != 0:
            g.coordinates = GlyphCoordinates([(x + shift, y) for x, y in g.coordinates])
        hmtx[name] = (adv, 70)
        # NOTE: glyf[name] = g above already appended to glyph order via __setitem__
        if cp is not None:
            # add to all cmap subtables
            for table in f['cmap'].tables:
                if table.isUnicode():
                    table.cmap[cp] = name

    f.setGlyphOrder(order)
    f['glyf'].glyphOrder = order
    # maxp
    f['maxp'].numGlyphs = len(order)
    # hhea numOfLongHorMetrics: set to len (simple)
    try:
        f['hhea'].numberOfHMetrics = len(order)
    except Exception:
        pass
    # post: rebuild as format 2.0 with names
    post = f['post']
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = order
    # OS/2: set xHeight/capHeight, unicode ranges for new blocks
    os2 = f['OS/2']
    os2.sxHeight = 470
    os2.sCapHeight = 761
    # set unicode range bits: bit0 latin, bit1 latin-1 suppl (copyright etc), bit57 general punct? keep simple
    try:
        r = list(os2.ulUnicodeRange)
        while len(r) < 4:
            r.append(0)
        r[0] = r[0] | 0x00000001 | 0x00000002  # basic latin + latin-1 supplement
        os2.ulUnicodeRange = r
    except Exception as e:
        print('os2 range note:', e)
    # name: bump version
    name_tab = f['name']
    for rec in name_tab.names:
        try:
            s = rec.toUnicode()
        except Exception:
            continue
        if rec.nameID in (3, 5):
            ns = s.replace('1.0', '2.0')
            if ns != s:
                rec.string = ns.encode('utf-16-be') if rec.platformID == 3 else ns.encode('mac_roman', errors='replace')

    f.save(SRC)
    print('saved', SRC, 'glyphs:', len(order))

if __name__ == '__main__':
    main()
