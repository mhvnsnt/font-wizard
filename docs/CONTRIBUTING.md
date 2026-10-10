# Contributing to Font Wizard

## Adding a new family
1. Open an issue or pick a style direction: name the family, link the style
   reference art.
2. Create `work/<family-slug>/`, follow `docs/FONT-PACK-PIPELINE.md`
   steps 0–6.
3. Ship to `fonts/<family-slug>/` with TTF + WOFF/WOFF2 + PNG pack +
   SPECIMEN.png + README.
4. Branch `fonts/<family-slug>` → PR → merge. No open PRs.

## Rules
- Every glyph gets human eyes before it ships. No exceptions.
- `work/` is scratch and gitignored. Only finished product lands in `fonts/`.
- Record provenance: federated bases keep their FEDERATED.json; custom art
  notes its source in the family README.
- License headers: custom families are owner IP unless the family README
  says otherwise. Don't relicense federated OFL fonts.

## Code style
- Pipeline scripts are CLIs with `--help`. Keep them dependency-light.
- API clients live in `api/`, one module per source, plus `federate.py`.
