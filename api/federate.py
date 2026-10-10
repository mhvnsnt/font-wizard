#!/usr/bin/env python3
"""
federate.py — pull a free font by name and drop it into the Font Wizard pipeline.

Searches Google Fonts first, falls back to Fontsource, downloads the files
into fonts/_federated/<family>/ with a manifest recording source + license.

This is the "federation" step: any open-licensed font becomes a base or
reference for a new Font Wizard family.

Usage:
  python federate.py "Rubik Mono One"            # google fonts -> fonts/_federated/
  python federate.py --source fontsource "Space Grotesk" --dest fonts/_ref/
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import google_fonts, fontsource


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("family")
    ap.add_argument("--source", choices=["google", "fontsource", "auto"],
                    default="auto")
    ap.add_argument("--dest", default="fonts/_federated")
    args = ap.parse_args()

    fam_dir = os.path.join(args.dest,
                           args.family.replace(" ", "-").lower())
    os.makedirs(fam_dir, exist_ok=True)
    saved, provenance = [], {}

    if args.source in ("google", "auto"):
        try:
            saved = google_fonts.download(args.family, fam_dir)
            provenance = {"source": "google-fonts",
                          "license": "OFL (see family page)"}
        except ValueError:
            if args.source == "google":
                raise
    if not saved:
        hits = fontsource.search(args.family, limit=5)
        if not hits:
            raise SystemExit(f"not found on google fonts or fontsource: {args.family}")
        fid = hits[0]["id"]
        saved = fontsource.download(fid, fam_dir)
        provenance = {"source": "fontsource", "fontsource_id": fid}

    manifest = {"family": args.family, "files": [os.path.basename(p) for p in saved],
                **provenance,
                "note": "federated base/reference — check license before sale"}
    json.dump(manifest, open(os.path.join(fam_dir, "FEDERATED.json"), "w"), indent=1)
    print(f"federated {args.family}: {len(saved)} files -> {fam_dir}")


if __name__ == "__main__":
    main()
