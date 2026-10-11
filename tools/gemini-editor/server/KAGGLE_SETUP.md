# Gemini-Editor GPU Server — Kaggle Setup

**Goal:** a free GPU box that runs diffusion models behind an HTTP API, so the
agent never runs diffusion locally. This is the "EDIT" half of the
see → understand → edit → verify loop. (See/understand/verify = the agent's own
vision; edit = this server.)

**Cost:** $0. Kaggle free tier = 30 GPU-hours/week (T4 x2).

## Prerequisites (one-time, ~10 min, needs the owner on his phone)

1. **Kaggle account verified for GPU.** Account: `MarsFMMG`
   (`fmmg.mars@gmail.com`). As of 2026-10-10 the account shows GPU T4 x2
   selectable in notebooks, but phone/Persona verification was never confirmed
   complete and no API token exists on the VM. If GPU is disabled in a new
   notebook: finish verification at kaggle.com/settings (phone → possible
   Persona ID check), then continue.
2. **kaggle.json API token** (for pushing the notebook from CLI later):
   kaggle.com → Settings → API → Create New Token. Save as `~/.kaggle/kaggle.json`
   (`chmod 600`). NOT YET DONE as of 2026-10-10.

## Setup (per session — Kaggle kills idle notebooks)

### Option A: notebook UI (simplest, no token needed)

1. Go to kaggle.com/code → New Notebook.
2. Settings (right panel): Accelerator = **GPU T4 x2**, Internet = **ON**.
3. Paste this into the first cell and run:

```python
# ---- gemini-editor GPU bootstrap ----
!pip -q install diffusers transformers accelerate safetensors segment-anything fastapi "uvicorn[standard]" pillow numpy
!mkdir -p /kaggle/working/models /kaggle/working/server
!wget -q -O /kaggle/working/models/sam_vit_h_4b8939.pth \
  https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
# copy kaggle_server.py into /kaggle/working/server/ (upload via notebook file panel,
# or: !wget <raw-github-url-when-merged>)
print("bootstrap done — now run the server cell")
```

4. Second cell — download models once (cached in /kaggle/working for the session):

```python
import torch
from diffusers import StableDiffusionInstructPix2PixPipeline
p = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    "timbrooks/instruct-pix2pix", torch_dtype=torch.float16, safety_checker=None)
p.save_pretrained("/kaggle/working/models/ip2p")
print("ip2p cached")
```

5. Third cell — start the server (blocks the cell; that's fine):

```python
!cd /kaggle/working/server && python kaggle_server.py
# server on :8000 — expose it (next step) or use Kaggle's proxy
```

### Exposing the server to the agent VM

Kaggle notebooks have no public inbound port. Two free options:

**Option 1 — cloudflared tunnel (recommended):**
```python
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /tmp/cf
!chmod +x /tmp/cf
!/tmp/cf tunnel --url http://localhost:8000 &
# copy the https://*.trycloudflare.com URL from output
```

**Option 2 — ngrok** (needs free authtoken):
```python
!pip -q install pyngrok
from pyngrok import ngrok
print(ngrok.connect(8000).public_url)
```

### Point the agent at it

On the agent VM:
```bash
export GEMINI_EDITOR_GPU_URL="https://<your-tunnel-url>"
```

Then:
```bash
tools/gemini-editor/edit_image.py -i photo.jpg --instr "make the background black"
```

### Option B: persistent-ish (advanced)

Kaggle notebooks die when idle ~1h and have a 9h max. For longer runs, re-run
the bootstrap (models re-download each session unless attached as a Kaggle
Dataset — recommended: save /kaggle/working/models as a private dataset once,
attach it to skip downloads).

## VRAM map (T4 x2 = 2 × 16 GB)

| Model | VRAM | Fits |
|---|---|---|
| InstructPix2Pix (fp16) | ~7 GB | single T4 OK |
| SDXL inpaint (fp16) | ~8 GB | single T4 OK |
| SAM ViT-H | ~2.5 GB | anywhere |
| All three | ~17 GB | T4 x2 only |

Single-T4 fallback: the server lazy-loads; request one model family at a time.

## Verify it's working

```bash
curl -s "$GEMINI_EDITOR_GPU_URL/health"
# {"ok": true, "cuda": true, "models": [...]}
```

Then the loop test:
```bash
edit_image.py -i sign.jpg --instr "make the background black" -o sign_black.jpg
# agent reads sign_black.jpg with vision -> verifies -> done or retries
```

## Troubleshooting

- **GPU disabled in notebook:** verification incomplete — see Prerequisites.
- **OOM:** use one model at a time; add `--lowvram` not needed (diffusers handles it).
- **Tunnel dies:** cloudflared trycloudflare URLs expire with the notebook — expected.
  Re-run setup per session (~5 min after first bootstrap).
- **Slow first edit:** model load ~60-90s on first request; subsequent edits fast.
