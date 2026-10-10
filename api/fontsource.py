"""
fontsource.py — free Fontsource CDN client (no key, open-licensed fonts).

Fontsource mirrors Google Fonts (+ more) as npm packages served over CDN:
  https://cdn.jsdelivr.net/fontsource/fonts/{id}:vf@latest/{subset}-{weight}-{style}.woff2

- search(query): client-side filter over the full font index
- download(family_id, dest): fetch woff2/woff/ttf files

Docs: https://fontsource.org/docs
"""
import os
import requests

API = "https://api.fontsource.org/v1/fonts"
CDN = "https://cdn.jsdelivr.net/fontsource/fonts"
_INDEX = None


def index():
    global _INDEX
    if _INDEX is None:
        r = requests.get(API, timeout=60)
        r.raise_for_status()
        _INDEX = r.json()
    return _INDEX


def search(query, limit=20):
    def norm(s):
        return s.lower().replace(" ", "").replace("-", "")
    q = norm(query)
    hits = [f for f in index()
            if q in norm(f["id"]) or q in norm(f.get("family", ""))]
    return hits[:limit]


def download(family_id, dest, subsets=("latin",), weights=(400,),
             styles=("normal",), fmt="woff2"):
    """Download font files from the Fontsource CDN. Returns saved paths."""
    os.makedirs(dest, exist_ok=True)
    saved = []
    for subset in subsets:
        for weight in weights:
            for style in styles:
                url = (f"{CDN}/{family_id}:vf@latest/"
                       f"{subset}-{weight}-{style}.{fmt}")
                path = os.path.join(
                    dest, f"{family_id}-{subset}-{weight}-{style}.{fmt}")
                r = requests.get(url, timeout=60)
                if r.status_code != 200:
                    print(f"skip {url} ({r.status_code})")
                    continue
                open(path, "wb").write(r.content)
                saved.append(path)
                print(f"{family_id} -> {path}")
    return saved


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: fontsource.py <search|download> ...")
        sys.exit(1)
    if sys.argv[1] == "search":
        for f in search(sys.argv[2]):
            print(f"{f['id']}  ({f.get('category')})")
    elif sys.argv[1] == "download":
        download(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "dl")
