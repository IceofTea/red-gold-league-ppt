# -*- coding: utf-8 -*-
"""Generate the four abstract backgrounds used by the deck.

Everything is drawn from scratch with Pillow, so the output can be
released under CC0 together with this repository.  No third-party
textures or photographs are involved.

Usage:
    python scripts/make_backgrounds.py [output_dir]
"""
from __future__ import annotations

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 1920, 1080


def _gradient(inner: tuple[int, int, int], outer: tuple[int, int, int],
              cx: float = 0.5, cy: float = 0.45) -> Image.Image:
    """Radial gradient: ``inner`` in the centre, ``outer`` at the edges."""
    g = Image.radial_gradient("L").resize((W, H), Image.BICUBIC)
    g = ImageOps.invert(g)
    return ImageOps.colorize(g, black=outer, white=inner).convert("RGB")


def _grain(img: Image.Image, sigma: float = 6.0, opacity: float = 0.045) -> Image.Image:
    noise = Image.effect_noise((W, H), sigma).convert("L")
    noise = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise, opacity)


def _vignette(img: Image.Image, strength: float = 0.45) -> Image.Image:
    mask = Image.radial_gradient("L").resize((W, H), Image.BICUBIC)
    mask = ImageOps.invert(mask)  # bright centre, dark edges
    mask = mask.point(lambda v: int(255 - (255 - v) * strength))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, black, mask)


def _hairlines(img: Image.Image, ys: list[float], color=(200, 164, 93),
               alpha: int = 40, width: int = 2) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in ys:
        d.line([(0, int(H * y)), (W, int(H * y))], fill=(*color, alpha), width=width)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(layer, (0, 0), layer)


def _mountains(img: Image.Image, base_y: float = 0.72, color=(120, 24, 20),
               alpha: int = 60) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k, (amp, off, a) in enumerate([(70, 0.0, alpha), (40, 0.12, alpha // 2)]):
        pts = [(0, H)]
        for x in range(0, W + 1, 24):
            t = x / W
            y = H * base_y + off * H - amp * math.sin(t * math.pi * 2.2 + k * 1.7) \
                - amp * 0.4 * math.sin(t * math.pi * 7 + k)
            pts.append((x, int(y)))
        pts.append((W, H))
        d.polygon(pts, fill=(*color, a))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(layer, (0, 0), layer)


def make_cover() -> Image.Image:
    img = _gradient((126, 22, 20), (48, 3, 5))
    _hairlines(img, [0.795, 0.835], alpha=50)
    img = _grain(img, 8.0, 0.055)
    return _vignette(img, 0.32)


def make_paper() -> Image.Image:
    img = _gradient((252, 249, 241), (228, 218, 200), cx=0.55, cy=0.42)
    img = _grain(img, 9.0, 0.07)
    # A few faint paper fibres.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(20261025)
    for _ in range(120):
        x, y = rnd.randrange(W), rnd.randrange(H)
        ln = rnd.randrange(20, 160)
        d.line([(x, y), (x + ln, y + rnd.randrange(-3, 4))],
               fill=(170, 150, 120, rnd.randrange(6, 18)), width=1)
    img.paste(layer, (0, 0), layer)
    return _vignette(img, 0.18)


def make_chapter() -> Image.Image:
    img = _gradient((146, 28, 24), (58, 5, 7))
    img = _grain(img, 8.0, 0.05)
    return _vignette(img, 0.40)


def make_dark() -> Image.Image:
    img = _gradient((104, 18, 18), (40, 3, 4))
    img = _grain(img, 8.0, 0.05)
    return _vignette(img, 0.42)


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for name, fn in [
        ("cover_bg.jpg", make_cover),
        ("paper_bg.jpg", make_paper),
        ("chapter_bg.jpg", make_chapter),
        ("dark_bg.jpg", make_dark),
    ]:
        path = os.path.join(out_dir, name)
        fn().save(path, "JPEG", quality=92, optimize=True)
        print(path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "red_gold_deck/assets/bg")
