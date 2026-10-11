# Gemini-Editor Pipeline

**What:** instruction-driven image editing with free tools — the open replication
of what Gemini does natively ("remove the background", "make it black", "fix the E").

**The loop:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. SEE         agent reads the input image (native vision) │
│ 2. UNDERSTAND  agent parses the instruction into an edit plan │
│ 3. EDIT        routed to the best free backend (below)      │
│ 4. VERIFY      agent reads the output, compares to intent   │
│                └─ mismatch? adjust instruction, loop back to 3 │
└─────────────────────────────────────────────────────────┘
```

Steps 1, 2, 4 are the agent itself — no separate vision model needed.
Step 3 is this toolkit.

## Backends

| Backend | What it runs | Needs | Status |
|---|---|---|---|
| `local` | art-stack: rembg/BiRefNet cutout, OpenCV/LaMa inpaint, Pillow composite, Real-ESRGAN | CPU | **works now** |
| `pollinations` | free image-gen API (`image.pollinations.ai`) | internet | **works now** |
| `kaggle` | InstructPix2Pix + SDXL-inpaint + SAM on T4 GPU via HTTP | GPU server | needs setup (see `server/KAGGLE_SETUP.md`) |

## Instruction routing

`edit_image.py` routes automatically:

| Instruction pattern | Backend | How |
|---|---|---|
| "remove the background" | local | BiRefNet cutout → transparent PNG |
| "make the background black/white/…" | local | cutout + composite onto solid color |
| "remove X" / "erase X" (+ mask) | local | OpenCV inpaint (LaMa hook for quality) |
| "upscale" | local | Real-ESRGAN (if installed) |
| "generate …" / "create …" | pollinations | text-to-image API |
| anything else ("fix the E", "make it pop") | kaggle | InstructPix2Pix (instruction-tuned diffusion) |

Explicit override: `--backend local|pollinations|kaggle`.

## Why not ComfyUI?

The research recommended ComfyUI headless. We chose **diffusers-direct in FastAPI**
instead: same models (IP2P, SDXL), fewer moving parts, one Python file, no
node-graph JSON to maintain. If ComfyUI-specific nodes are ever needed
(ControlNet poses, AnimateDiff), the server can grow a `/comfy` route later.

## Why no separate vision model?

Qwen2-VL / LLaVA were in the original plan for understand+verify. They're
redundant: the agent calling this tool already has native vision. Adding a
local VLM would burn VRAM for zero gain. The agent IS the vision model.

## Usage

```bash
# background removal (local, CPU)
edit_image.py -i sign.jpg --instr "remove the background" -o sign_cut.png

# background swap (local, CPU)
edit_image.py -i sign.jpg --instr "make the background black" -o sign_black.jpg

# generation (pollinations, free API)
edit_image.py --instr "generate blackletter letter M, white on black" -o m.jpg

# instruction edit (needs GPU server)
export GEMINI_EDITOR_GPU_URL="https://xxx.trycloudflare.com"
edit_image.py -i photo.jpg --instr "fix the rust on the E" -o fixed.jpg
```

## The verify loop (agent-side pattern)

```python
# pseudo — the agent does this, not the tool
for attempt in range(3):
    run edit_image.py --input in --instruction "..."
    read output image with vision
    if matches intent: break
    else: refine instruction ("the E is still rusty, only fix the E's color")
```

## Wiring

Each repo gets a shim that calls the home-base client:

- `font-wizard/tools/gemini-editor/` — home base (this dir)
- `media-pipeline/tools/gemini-editor/` → shim → `../../font-wizard/tools/gemini-editor/edit_image.py`
- `trippedd-studio/tools/gemini-editor/` → shim (donor-first, no duplication)
- `bannon-video-pipe/tools/gemini-editor/` → shim

Environment:
- `ART_STACK_DIR` — override art-stack location (default: `../art-stack`)
- `GEMINI_EDITOR_GPU_URL` — Kaggle server URL when available

## What this doesn't do (honest)

- **One-shot perfection.** Gemini nails "fix the E" first try; this may take 2-3
  verify-loop iterations. The loop is the feature that closes the gap.
- **No GPU = no instruction editing.** Local CPU covers cutout/composite/inpaint;
  true "edit this part per my words" needs the Kaggle server.
- **Pollinations is generation-only.** It can't edit your photo; it makes new ones.
