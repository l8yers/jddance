#!/usr/bin/env python3
"""Regenerate committed web assets. Requires ImageMagick and FFmpeg locally."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
OUT = ASSETS / 'optimized'
OUT.mkdir(exist_ok=True)
manifest = {}
for source in sorted(ASSETS.iterdir()):
    if source.suffix.lower() not in {'.jpeg', '.jpg', '.png'}:
        continue
    width, height = map(int, subprocess.check_output(
        ['magick', 'identify', '-format', '%w %h', str(source)], text=True).split())
    sizes = sorted({min(width, size) for size in ([128, 256, 640] if source.stem == 'logo' else [320, 640, 1200])})
    variants = []
    for size in sizes:
        target = OUT / f'{source.stem}-{size}.webp'
        subprocess.run(['magick', str(source), '-auto-orient', '-resize', f'{size}x>',
                        '-strip', '-quality', '80', str(target)], check=True)
        w, h = map(int, subprocess.check_output(
            ['magick', 'identify', '-format', '%w %h', str(target)], text=True).split())
        variants.append({'src': target.relative_to(ROOT).as_posix(), 'width': w, 'height': h})
    manifest[source.name] = variants
subprocess.run(['ffmpeg', '-y', '-i', str(ASSETS / 'jddance.mp4'), '-an',
                '-vf', 'scale=640:640,fps=24', '-c:v', 'libx264', '-crf', '29',
                '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(OUT / 'hero.mp4')], check=True)
(ROOT / 'data/media.json').write_text(json.dumps(manifest, indent=2) + '\n')
