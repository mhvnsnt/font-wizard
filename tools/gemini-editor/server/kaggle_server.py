#!/usr/bin/env python3
"""Gemini-Editor GPU server — runs on Kaggle T4 (or any CUDA box).

Exposes a single HTTP endpoint the agent calls instead of running diffusion locally:

    POST /edit  {"image": "<base64>", "instruction": "..."} -> {"image": "<base64>", "model": ...}
    POST /generate {"prompt": "..."} -> {"image": "<base64>"}
    GET  /health -> {"ok": true, "models": [...]}

PIPELINE (mirrors Gemini's native editing):
  1. UNDERSTAND (agent-side, already done): the agent read the image with vision
     and produced a text instruction like "make the background black".
  2. ROUTE (here): instruction -> model
       - "make X Y" / "change ... to ..." / "fix ..." -> InstructPix2Pix
       - "remove ..." (needs mask)                   -> SAM auto-mask + SD inpaint
       - pure generation                             -> SDXL
  3. EDIT: run diffusion, return PNG bytes.
  4. VERIFY (agent-side): the agent reads the result and loops if wrong.

SETUP (Kaggle notebook, GPU T4 x2):
  1. New notebook at kaggle.com, accelerator = GPU T4 x2, internet ON.
  2. Paste the contents of kaggle_notebook_setup.py into a code cell and run.
     It installs: diffusers, transformers, segment-anything, fastapi, uvicorn,
     downloads: InstructPix2Pix (timbrooks/instruct-pix2pix),
                 SDXL inpainting, SAM ViT-H.
  3. Run this file:  !python kaggle_server.py  (or: uvicorn kaggle_server:app --port 8000)
  4. Expose it: use the public URL from the KAGGLE_SETUP.md ngrok/cloudflare
     instructions, then set GEMINI_EDITOR_GPU_URL on the agent VM.

VRAM: InstructPix2Pix ~7GB, SDXL inpaint ~8GB, SAM ~2.5GB.
T4 x2 (2x16GB) fits all three at once. Single T4 (16GB): load one at a time.

Cost: $0 — Kaggle free tier, 30 GPU-hrs/week.
"""
import base64
import io
import os
import re

MODEL_DIR = os.environ.get("GEMINI_EDITOR_MODELS", "/kaggle/input/models")

# Lazy-loaded globals (so --help / import doesn't need torch)
_ip2p = None
_sdxl_inpaint = None
_sam = None
_device = "cuda"


def _lazy_imports():
    global _torch, _diffusers_pipe
    import torch  # noqa
    return torch


def load_instruct_pix2pix():
    """timbrooks/instruct-pix2pix — instruction-based editing.

    The closest free equivalent to Gemini's "make the background black".
    Prompt format: the raw instruction, e.g. "make the background black".
    """
    global _ip2p
    if _ip2p is None:
        import torch
        from diffusers import StableDiffusionInstructPix2PixPipeline
        _ip2p = StableDiffusionInstructPix2PixPipeline.from_pretrained(
            "timbrooks/instruct-pix2pix",
            torch_dtype=torch.float16,
            safety_checker=None,
        ).to(_device)
    return _ip2p


def load_sdxl_inpaint():
    """SDXL inpainting for masked edits (SAM generates the mask)."""
    global _sdxl_inpaint
    if _sdxl_inpaint is None:
        import torch
        from diffusers import StableDiffusionXLInpaintPipeline
        _sdxl_inpaint = StableDiffusionXLInpaintPipeline.from_pretrained(
            "diffusers/stable-diffusion-xl-1.0-inpainting-0.1",
            torch_dtype=torch.float16,
            variant="fp16",
        ).to(_device)
    return _sdxl_inpaint


def load_sam():
    """Segment Anything (ViT-H) — auto-mask from text/box prompt."""
    global _sam
    if _sam is None:
        from segment_anything import sam_model_registry, SamPredictor
        ckpt = os.path.join(MODEL_DIR, "sam_vit_h_4b8939.pth")
        _sam = SamPredictor(sam_model_registry["vit_h"](checkpoint=ckpt).to(_device))
    return _sam


def route_instruction(instruction):
    ins = instruction.lower()
    if re.search(r"\b(remove|erase|delete|cut out)\b", ins):
        return "sam_inpaint"
    return "instruct_pix2pix"


def edit_instruct_pix2pix(image, instruction, steps=30, guidance=7.5, image_guidance=1.5):
    from PIL import Image as PILImage
    pipe = load_instruct_pix2pix()
    if isinstance(image, bytes):
        image = PILImage.open(io.BytesIO(image)).convert("RGB")
    out = pipe(
        instruction,
        image=image,
        num_inference_steps=steps,
        guidance_scale=guidance,
        image_guidance_scale=image_guidance,
    ).images[0]
    return out


def edit_sam_inpaint(image, instruction, prompt_fill="background"):
    """SAM auto-masks the named object, SDXL inpaints it away."""
    import numpy as np
    import torch
    from PIL import Image as PILImage
    if isinstance(image, bytes):
        image = PILImage.open(io.BytesIO(image)).convert("RGB")
    sam = load_sam()
    sam.set_image(np.array(image))
    # NOTE: full text-prompted SAM needs GroundingDINO; this path uses a
    # center-box heuristic. For precise masks the agent should send a box.
    h, w = image.size[1], image.size[0]
    box = np.array([w * 0.2, h * 0.2, w * 0.8, h * 0.8])
    masks, _, _ = sam.predict(box=box, multimask_output=False)
    mask = PILImage.fromarray((masks[0] * 255).astype("uint8"))
    pipe = load_sdxl_inpaint()
    out = pipe(prompt=prompt_fill, image=image, mask_image=mask).images[0]
    return out


# ---- HTTP API ----
try:
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(title="gemini-editor-gpu")

    class EditReq(BaseModel):
        image: str  # base64 PNG/JPG
        instruction: str

    class GenReq(BaseModel):
        prompt: str

    @app.get("/health")
    def health():
        import torch
        return {"ok": True, "cuda": torch.cuda.is_available(),
                "models": ["instruct-pix2pix", "sdxl-inpaint", "sam-vit-h"]}

    @app.post("/edit")
    def edit(req: EditReq):
        img = base64.b64decode(req.image)
        kind = route_instruction(req.instruction)
        if kind == "sam_inpaint":
            out = edit_sam_inpaint(img, req.instruction)
        else:
            out = edit_instruct_pix2pix(img, req.instruction)
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return {"image": base64.b64encode(buf.getvalue()).decode(), "model": kind}

    @app.post("/generate")
    def generate(req: GenReq):
        import torch
        from diffusers import StableDiffusionXLPipeline
        pipe = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16, variant="fp16").to(_device)
        out = pipe(req.prompt).images[0]
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return {"image": base64.b64encode(buf.getvalue()).decode(), "model": "sdxl"}

except ImportError:
    app = None  # fastapi not installed; run pip install fastapi uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
