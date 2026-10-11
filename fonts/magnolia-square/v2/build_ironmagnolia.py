#!/usr/bin/env python3
"""Build IronMagnolia-Regular.ttf v2 from SVG glyphs. Standalone, no potrace."""
import json, os, re
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UNITS = 2048

def parse_svg_path(d, pen, scale, vh):
    """Parse M/L/Z-only SVG path. SVG is already y-up; just scale."""
    tokens = re.findall(r'[MLZ]|[-+]?\d*\.?\d+', d)
    i = 0
    while i < len(tokens):
        cmd = tokens[i]; i += 1
        if cmd == 'M':
            x, y = float(tokens[i])*scale, float(tokens[i+1])*scale; i += 2
            pen.moveTo((x, y))
        elif cmd == 'L':
            x, y = float(tokens[i])*scale, float(tokens[i+1])*scale; i += 2
            pen.lineTo((x, y))
        elif cmd == 'Z':
            pen.closePath()

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    gdir = os.path.join(base, 'glyphs_final')
    svgdir = os.path.join(base, 'svg_v2')
    manifest = json.load(open(os.path.join(gdir, 'glyphs.json')))

    glyph_order = ['.notdef', 'space'] + [g['char'] for g in manifest]
    fb = FontBuilder(UNITS, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({ord(g['char']): g['char'] for g in manifest})
    fb.setupNameTable({
        'familyName': 'Iron Magnolia',
        'styleName': 'Regular',
        'uniqueFontIdentifier': 'IronMagnolia-Regular-2.0',
        'fullName': 'Iron Magnolia Regular',
        'psName': 'IronMagnolia-Regular',
        'version': 'Version 2.0',
    })
    glyphs, metrics = {}, {}
    glyphs['.notdef'] = TTGlyphPen(None).glyph()
    metrics['.notdef'] = (UNITS//2, 0)
    glyphs['space'] = TTGlyphPen(None).glyph()
    metrics['space'] = (UNITS//3, 0)

    for g in manifest:
        svg = open(os.path.join(svgdir, g['svg'])).read()
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
        vw, vh = float(m.group(1)), float(m.group(2))
        d = re.search(r'<path d="([^"]+)"', svg).group(1)
        scale = UNITS / max(vw, vh)
        pen = TTGlyphPen(None)
        parse_svg_path(d, pen, scale, vh)
        glyphs[g['char']] = pen.glyph()
        adv = int(vw * scale * 1.12)
        metrics[g['char']] = (adv, 0)
        print(f'{g["char"]}: advance {adv}')

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=int(UNITS*0.9), descent=int(UNITS*0.25))
    fb.setupOS2(sTypoAscender=int(UNITS*0.9), sTypoDescender=-int(UNITS*0.25),
                usWinAscent=int(UNITS*0.95), usWinDescent=int(UNITS*0.3),
                usWeightClass=400)
    fb.setupPost()
    fb.setupMaxp()
    out = os.path.join(base, '..', 'IronMagnolia-Regular.ttf')
    fb.save(out)
    print(f'TTF -> {out}')

if __name__ == '__main__':
    main()
