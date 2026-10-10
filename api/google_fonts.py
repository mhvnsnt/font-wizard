"""
google_fonts.py — free Google Fonts client, NO API KEY.

Uses the keyless CSS2 API (fonts.googleapis.com/css2), which returns direct
gstatic font-file URLs. A plain UA gets TTF; a browser UA gets WOFF2.

NOTE: the webfonts metadata API (googleapis.com/webfonts/v1) now requires a
free API key — this module deliberately avoids it so federation stays
keyless.

- search(query): match against a cached family list (from the Fontsource
  index, which mirrors Google Fonts coverage)
- download(family, dest, weights): fetch TTF files via css2
"""
import os
import re
import requests

CSS2 = "https://fonts.googleapis.com/css2"
_TTF_UA = "curl/font-wizard"          # non-browser UA -> truetype URLs
_WOFF2_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")


def _css(family, weights, ua):
    params = {"family": f"{family}:wght@{';'.join(map(str, weights))}",
              "display": "swap"}
    r = requests.get(CSS2, params=params,
                     headers={"User-Agent": ua}, timeout=30)
    r.raise_for_status()
    if "font-family" not in r.text:
        raise ValueError(f"family not found via css2: {family}")
    return r.text


def file_urls(family, weights=(400,), fmt="ttf"):
    """Direct gstatic URLs for a family. fmt: 'ttf' or 'woff2'."""
    ua = _TTF_UA if fmt == "ttf" else _WOFF2_UA
    css = _css(family, weights, ua)
    urls = re.findall(r"url\((https://[^)]+)\)", css)
    # css2 returns one block per weight/subset; keep latin (last block per weight)
    return urls


def search(query, limit=20):
    """Client-side search over the Fontsource index (mirrors GF coverage)."""
    import fontsource
    return [f for f in fontsource.search(query, limit=limit)]


def download(family, dest, weights=(400,), fmt="ttf"):
    """Download font files for a family. Returns saved paths."""
    os.makedirs(dest, exist_ok=True)
    saved = []
    for i, url in enumerate(file_urls(family, weights, fmt)):
        w = weights[i] if i < len(weights) else weights[0]
        path = os.path.join(
            dest, f"{family.replace(' ', '')}-{w}.{fmt}")
        with requests.get(url, timeout=60, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 16):
                    fh.write(chunk)
        saved.append(path)
        print(f"{family} [{w}/{fmt}] -> {path}")
    return saved


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: google_fonts.py <search|download> ...")
        sys.exit(1)
    if sys.argv[1] == "search":
        for f in search(sys.argv[2])[:20]:
            print(f"{f['id']}  ({f.get('category')})")
    elif sys.argv[1] == "download":
        weights = tuple(map(int, sys.argv[4].split(","))) if len(sys.argv) > 4 else (400,)
        download(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "dl",
                 weights)
