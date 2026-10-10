#!/usr/bin/env python3
"""
build_ttf.py — assemble a TTF from SVG glyph outlines via fontTools.

Takes svg/ dir + glyphs.json (from vectorize.py), converts each SVG path to
a TrueType glyph outline, assigns metrics, and writes a working .ttf.

Also builds .woff and .woff2 alongside (needs brotli for woff2).

Usage:
  python build_ttf.py --glyphs glyphs/ --name "TrippyDrippyWizard" \\
      --out fonts/TrippyDrippyWizard-Regular.ttf [--units 2048] [--weight 400]
"""
import argparse, json, os, re
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.tuPen import TTGlyphPen


def svg_to_glyph(svg_text: str, units: int, advance: int):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    vw, vh = float(m.group(1)), float(m.group(2))
    d = re.search(r'<path d="([^"]+)"', svg_text).group(1)
    scale = units / max(vw, vh)
    pen = TTGlyphPen(None)
    spen = SVGPathPen(pen)
    # flip Y (SVG origin top-left -> font origin bottom-left) and scale
    spen = _FlipPen(spen, vh, scale)
    spen.addPath(d) if hasattr(spen, "addPath") else _draw(spen, d)
    return pen.glyph()


class _FlipPen:
    """Wrap a pen: scale + flip Y around the viewBox height."""
    def __init__(self, out, vh, scale):
        self._out, self._vh, self._s = out, vh, scale
    def _p(self, x, y):
        return (x * self._s, (self._vh - y) * self._s)
    def moveTo(self, p): self._out.moveTo(self._p(*p))
    def lineTo(self, p): self._out.lineTo(self._p(*p))
    def curveTo(self, *ps): self._out.curveTo(*[self._p(*p) for p in ps])
    def qCurveTo(self, *ps): self._out.qCurveTo(*[self._p(*p) for p in ps])
    def closePath(self): self._out.closePath()
    def endPath(self): self._out.endPath()
    def addComponent(self, *a, **k): self._out.addComponent(*a, **k)


def _draw(spen, d):
    # fallback: let SVGPathPen parse directly (it handles the d string)
    spen._commands = None
    from fontTools.pens.svgPathPen import parse_path
    parse_path(d, spen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glyphs", required=True)
    ap.add_argument("--svg-dir", default=None)
    ap.add_argument("--name", required=True, help="family name, e.g. TrippyDrippyWizard")
    ap.add_argument("--out", required=True)
    ap.add_argument("--units", type=int, default=2048)
    ap.add_argument("--weight", type=int, default=400)
    ap.add_argument("--version", default="1.0")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(args.glyphs, "glyphs.json")))
    svg_dir = args.svg_dir or os.path.join(args.glyphs, "..", "svg")

    glyph_order = [".notdef", "space"] + [g["char"] for g in manifest]
    fb = FontBuilder(args.units, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({ord(g["char"]): g["char"] for g in manifest})
    fb.setupNameTable({
        "familyName": args.name.replace("-", " "),
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{args.name}-Regular-{args.version}",
        "fullName": f"{args.name} Regular",
        "psName": f"{args.name}-Regular",
        "version": f"Version {args.version}",
    })

    glyphs, metrics = {}, {}
    glyphs[".notdef"] = TTGlyphPen(None).glyph()
    metrics[".notdef"] = (args.units // 2, 0)
    glyphs["space"] = TTGlyphPen(None).glyph()
    metrics["space"] = (args.units // 3, 0)

    for g in manifest:
        svg_text = open(os.path.join(svg_dir, g["svg"])).read()
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
        vw = float(m.group(1))
        adv = int(vw * (args.units / max(vw, float(m.group(2)))) * 1.12)
        glyphs[g["char"]] = svg_to_glyph(svg_text, args.units, adv)
        metrics[g["char"]] = (adv, 0)
        print(f"{g['char']}: advance {adv}")

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=int(args.units * 0.9),
                             descent=int(args.units * 0.25))
    fb.setupNameTable  # noqa
    fb.setupOS2(sTypoAscender=int(args.units * 0.9),
                sTypoDescender=-int(args.units * 0.25),
                usWinAscent=int(args.units * 0.95),
                usWinDescent=int(args.units * 0.3),
                usWeightClass=args.weight)
    fb.setupPost()
    fb.setupMaxp()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    fb.save(args.out)
    print(f"TTF -> {args.out}")

    # WOFF / WOFF2 siblings
    base = os.path.splitext(args.out)[0]
    for flavor, ext in (("woff", ".woff"), ("woff2", ".woff2")):
        try:
            f2 = FontBuilder(args.units, isTTF=True)
            from fontTools.ttLib import TTFont
            t = TTFont(args.out)
            t.flavor = flavor
            t.save(base + ext)
            print(f"{flavor} -> {base + ext}")
        except Exception as e:
            print(f"skip {flavor}: {e}")


if __name__ == "__main__":
    main()
