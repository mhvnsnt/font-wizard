#!/usr/bin/env python3
"""Thin ffmpeg wrapper for common promo jobs. Free, local (system ffmpeg).

Usage:
    vid.py trim in.mp4 3 12 out.mp4            # cut 3s..12s
    vid.py vertical in.mp4 out.mp4             # 16:9 -> 9:16 center crop
    vid.py captions in.mp4 subs.srt out.mp4   # burn subtitles
    vid.py gif in.mp4 out.gif --fps 12 --w 480
    vid.py thumbs in.mp4 outdir --n 8          # extract N evenly spaced frames

Pass-through: anything unrecognized is forwarded to ffmpeg after 'vid.py --'.
"""
import subprocess, sys, shutil

def need_ffmpeg():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not installed")

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    need_ffmpeg()
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--":                       # raw passthrough
        run(["ffmpeg"] + a[1:]); return
    op = a[0]
    if op == "trim":
        _, src, start, end, dst = a
        run(["ffmpeg", "-y", "-ss", start, "-to", end, "-i", src,
             "-c", "copy", dst])
    elif op == "vertical":
        _, src, dst = a
        run(["ffmpeg", "-y", "-i", src, "-vf",
             "crop=ih*9/16:ih,scale=1080:1920", "-c:a", "copy", dst])
    elif op == "captions":
        _, src, srt, dst = a
        run(["ffmpeg", "-y", "-i", src, "-vf", f"subtitles={srt}", dst])
    elif op == "gif":
        src, dst = a[1], a[2]
        fps = "12"; w = "480"
        for i, x in enumerate(a):
            if x == "--fps": fps = a[i+1]
            if x == "--w": w = a[i+1]
        run(["ffmpeg", "-y", "-i", src, "-vf",
             f"fps={fps},scale={w}:-1:flags=lanczos", dst])
    elif op == "thumbs":
        src, outdir = a[1], a[2]
        n = "8"
        for i, x in enumerate(a):
            if x == "--n": n = a[i+1]
        import os
        os.makedirs(outdir, exist_ok=True)
        run(["ffmpeg", "-y", "-i", src, "-vf", f"fps=1/{n},scale=640:-1",
             f"{outdir}/thumb_%02d.jpg"])
    else:
        sys.exit(f"unknown op {op}\n" + __doc__)

if __name__ == "__main__":
    main()
