# fetch / store — Zero-Disk Retrieval Layer

The disk stays clean. Everything lives in permanent storage (GitHub / Google Drive).
These tools move things between cold storage and local disk.

## fetch — pull something back to disk

```bash
./fetch <name>              # restore by manifest name
./fetch --list              # show everything in cold storage
./fetch --search <term>     # find by keyword
```

## store — push something to cold storage

```bash
./store <path> --to drive --name "ep01-master"    # upload to Drive, update manifest
./store <path> --to github --repo mhvnsnt/xyz    # (repos are pushed via git directly)
```

## Manifest

`~/workspace/agent-ops/STORAGE-MANIFEST.json` maps every off-disk item to its
location. `fetch` reads it. `store` updates it. Never edit by hand.
