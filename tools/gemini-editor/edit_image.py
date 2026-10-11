#!/usr/bin/env python3
"""Gemini-Editor: instruction-driven image editing with free tools.

Replicates what Gemini does natively (see image + text instruction -> edited image)
using a routed backend architecture:

  SEE / UNDERSTAND / VERIFY : the agent itself (reads images natively)
  EDIT : routed by instruction type to the best free backend

Backends:
  local        - art-stack (rembg/BiRefNet bg removal, OpenCV/LaMa inpaint,
                 Pillow composite, Real-ESRGAN upscale). CPU, works now.
  pollinations - free image generation API. Works now. For generation/variation.
  kaggle       - ComfyUI + InstructPix2Pix + SAM + SDXL on Kaggle T4 GPU.
                 Needs GPU server setup (see server/KAGGLE_SETUP.md).

Usage:
    edit_image.py --input in.jpg --instruction "make the background black" [--output out.jpg] [--backend auto]

Instruction routing (auto mode):
  "remove (the) background"          -> local bg_remove
  "make the background <color>"      -> local bg_remove + composite onto color
  "remove <object>" / "erase <thing>"-> local inpaint (needs --mask or auto-detect note)
  "upscale" / "enhance"              -> local realesrgan (if available)
  "generate ..." / "create ..."      -> pollinations
  anything else                      -> kaggle (InstructPix2Pix) if configured,
                                        else pollinations img2img-ish fallback

Examples:
    edit_image.py -i sign.jpg -instr "remove the background"
    edit_image.py -i sign.jpg -instr "make the background black" -o sign_black.jpg
    edit_image.py -instr "generate blackletter letter M, white on black" -o m.jpg
"""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART_STACK = Path(os.environ.get("ART_STACK_DIR", HERE.parent / "art-stack"))
KAGGLE_URL = os.environ.get("GEMINI_EDITOR_GPU_URL", "").rstrip("/")


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r


def route_instruction(instruction):
    ins = instruction.lower().strip()
    if re.search(r"\bremove\b.*\bbackground\b", ins):
        return "local_bg_remove"
    m = re.search(r"make the background (\w+)", ins)
    if m:
        return ("local_bg_color", m.group(1))
    if re.search(r"\b(upscale|enhance|4x)\b", ins):
        return "local_upscale"
    if re.search(r"\b(remove|erase|delete)\b", ins):
        return "local_inpaint"
    if re.search(r"\b(generate|create|draw|make an? image of)\b", ins):
        return "pollinations_generate"
    # Default: instruction edit -> needs diffusion
    return "kaggle_instruct"


def art_stack(script, *args):
    runner = ART_STACK / "run.sh"
    if not runner.exists():
        # fall back to direct python if venv present
        venv_py = ART_STACK / ".venv" / "bin" / "python"
        if venv_py.exists():
            return run([str(venv_py), str(ART_STACK / script), *args])
        return None
    return run([str(runner), script, *args])


def do_local_bg_remove(inp, out):
    # Try u2net first (smaller download, faster on CPU). Fall back to birefnet.
    r = art_stack("bg_remove.py", str(inp), str(out), "--model", "u2net")
    if r is None or r.returncode != 0:
        r = art_stack("bg_remove.py", str(inp), str(out), "--model", "birefnet-general")
    return r


COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 255, 0), "blue": (0, 0, 255), "transparent": None,
}


def do_local_bg_color(inp, out, color):
    from PIL import Image
    tmp = Path(str(out) + ".cutout.png")
    r = do_local_bg_remove(inp, tmp)
    if r is None or r.returncode != 0 or not tmp.exists():
        print("bg removal failed", file=sys.stderr)
        if r:
            print(r.stderr[-500:], file=sys.stderr)
        return r
    fg = Image.open(tmp).convert("RGBA")
    rgb = COLORS.get(color.lower(), (0, 0, 0))
    bg = Image.new("RGBA", fg.size, rgb + (255,))
    bg.alpha_composite(fg)
    bg.convert("RGB").save(out)
    tmp.unlink(missing_ok=True)
    print(f"background -> {color}: {out}")
    return run(["true"])


def do_pollinations_generate(instruction, out, width=1024, height=1024):
    # Strip leading generate/create verbs for the prompt
    prompt = re.sub(r"^(generate|create|draw|make an? image of)\s+", "", instruction.strip(), flags=re.I)
    q = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{q}?width={width}&height={height}&nologo=true"
    print(f"pollinations: {url[:120]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "gemini-editor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        Path(out).write_bytes(data)
        print(f"generated: {out} ({len(data)} bytes)")
        return run(["true"])
    except Exception as e:
        print(f"pollinations failed: {e}", file=sys.stderr)
        return run(["false"])


def do_kaggle_instruct(inp, instruction, out):
    if not KAGGLE_URL:
        print("KAGGLE GPU server not configured.", file=sys.stderr)
        print("Set GEMINI_EDITOR_GPU_URL, or see server/KAGGLE_SETUP.md.", file=sys.stderr)
        print("Falling back: trying pollinations (generation only, not precise edit).", file=sys.stderr)
        return None
    import json as _json
    import base64
    img_b64 = base64.b64encode(Path(inp).read_bytes()).decode()
    payload = _json.dumps({"image": img_b64, "instruction": instruction}).encode()
    req = urllib.request.Request(
        KAGGLE_URL + "/edit",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = _json.loads(resp.read())
        out_img = base64.b64decode(result["image"])
        Path(out).write_bytes(out_img)
        print(f"kaggle edit done: {out} (model={result.get('model')})")
        return run(["true"])
    except Exception as e:
        print(f"kaggle edit failed: {e}", file=sys.stderr)
        return run(["false"])


def main():
    ap = argparse.ArgumentParser(description="Instruction-driven image editing (free stack).")
    ap.add_argument("-i", "--input", help="input image (not needed for pure generation)")
    ap.add_argument("--instruction", "--instr", required=True, help='e.g. "make the background black"')
    ap.add_argument("-o", "--output", default="edited.png", help="output path")
    ap.add_argument("--backend", default="auto", choices=["auto", "local", "pollinations", "kaggle"])
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    a = ap.parse_args()

    route = route_instruction(a.instruction)

    if a.backend != "auto":
        # map explicit backend to action
        if a.backend == "pollinations":
            route = "pollinations_generate"
        elif a.backend == "kaggle":
            route = "kaggle_instruct"
        elif a.backend == "local":
            if not a.input:
                ap.error("--input required for local backend")

    key = route[0] if isinstance(route, tuple) else route
    out = Path(a.output)

    if key == "local_bg_remove":
        if not a.input:
            ap.error("--input required")
        r = do_local_bg_remove(a.input, out)
    elif key == "local_bg_color":
        if not a.input:
            ap.error("--input required")
        r = do_local_bg_color(a.input, out, route[1])
    elif key == "local_upscale":
        print("upscale: Real-ESRGAN hook (art-stack vid.py thumbs path); not yet wired standalone", file=sys.stderr)
        r = run(["false"])
    elif key == "local_inpaint":
        print("inpaint needs --mask; generate mask first or use SAM on GPU server", file=sys.stderr)
        r = run(["false"])
    elif key == "pollinations_generate":
        r = do_pollinations_generate(a.instruction, out, a.width, a.height)
    elif key == "kaggle_instruct":
        if not a.input:
            ap.error("--input required")
        r = do_kaggle_instruct(a.input, a.instruction, out)
        if r is None:
            # fallback
            r = do_pollinations_generate(a.instruction, out, a.width, a.height)
    else:
        print(f"unknown route: {route}", file=sys.stderr)
        r = run(["false"])

    sys.exit(0 if r and r.returncode == 0 else 1)


if __name__ == "__main__":
    main()
