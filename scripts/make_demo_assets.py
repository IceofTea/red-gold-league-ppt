# -*- coding: utf-8 -*-
"""Generate the CC0 demo images used by ``examples/demo.py``.

Every picture is drawn from scratch with Pillow: gradients, layered ridges,
water reflections, clouds, stars, skylines, fields and a road.  No photo,
texture or third-party asset is involved, so the whole set can be shipped with
the repository under CC0.

Usage::

    python scripts/make_demo_assets.py [output_dir]

The default output directory is ``examples/assets``.  Images are 1600x1000,
which is large enough for a 13.33x7.5 inch slide at ~120 dpi.
"""
from __future__ import annotations

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 1600, 1000


# --------------------------------------------------------------------------
# small toolkit
# --------------------------------------------------------------------------
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(top, bottom, gamma=1.0):
    """Vertical gradient built on a 1-pixel strip, then resized."""
    strip = Image.new("RGB", (1, H))
    px = strip.load()
    for y in range(H):
        t = (y / (H - 1)) ** gamma
        px[0, y] = lerp(top, bottom, t)
    return strip.resize((W, H), Image.BICUBIC)


_MASK_CACHE: dict[int, Image.Image] = {}


def _radial_mask(size: int) -> Image.Image:
    """A circular falloff mask (Pillow's radial_gradient is off-centre)."""
    if size in _MASK_CACHE:
        return _MASK_CACHE[size]
    mask = Image.new("L", (size, size), 0)
    px = mask.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            if d < 1:
                px[x, y] = int(255 * (1 - d) ** 1.7)
    _MASK_CACHE[size] = mask
    return mask


def glow(img, cx, cy, radius, color, strength=0.9):
    size = max(4, int(radius * 2))
    mask = _radial_mask(size).point(lambda v: int(v * strength))
    layer = Image.new("RGB", (size, size), color)
    img.paste(layer, (int(cx - radius), int(cy - radius)), mask)


def disc(img, cx, cy, r, color, blur=2.0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.paste(layer, (0, 0), layer)


def clouds(img, y, n=8, color=(255, 224, 198), alpha=80, seed=1,
           size=1.0, blur=9.0):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        cx = rnd.uniform(-0.05, 1.05) * W
        cy = H * y + rnd.uniform(-0.05, 0.05) * H
        w = rnd.uniform(0.10, 0.30) * W * size
        h = w * rnd.uniform(0.16, 0.30)
        for _ in range(rnd.randint(3, 7)):
            dx = rnd.uniform(-0.55, 0.55) * w
            dy = rnd.uniform(-0.35, 0.35) * h
            ew = w * rnd.uniform(0.30, 0.55)
            eh = h * rnd.uniform(0.45, 0.85)
            d.ellipse([cx + dx - ew, cy + dy - eh,
                       cx + dx + ew, cy + dy + eh], fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.paste(layer, (0, 0), layer)


def ridge(img, base, amp, color, seed=1, blur=1.2, alpha=255,
          freqs=(1.15, 3.1, 7.3)):
    rnd = random.Random(seed)
    phase = rnd.random() * math.tau
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [(0, H)]
    for x in range(0, W + 1, 12):
        t = x / W
        y = H * base - amp * (
            0.55 * math.sin(t * math.tau * freqs[0] + phase)
            + 0.28 * math.sin(t * math.tau * freqs[1] + phase * 1.7)
            + 0.17 * math.sin(t * math.tau * freqs[2] + phase * 0.6))
        pts.append((x, int(y)))
    pts.append((W, H))
    d.polygon(pts, fill=(*color[:3], alpha))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.paste(layer, (0, 0), layer)


def mist(img, y, height, color=(255, 214, 170), alpha=80, blur=30):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([0, int(H * y), W, int(H * (y + height))],
                fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.paste(layer, (0, 0), layer)


def grain(img, sigma=7.0, opacity=0.035):
    noise = Image.effect_noise((W, H), sigma).convert("L")
    noise = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise, opacity)


def stars(img, bottom=0.65, count=800, seed=3, bright=230):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x, y = rnd.randrange(W), int(rnd.uniform(0, bottom) * H)
        r = rnd.choice([0.8, 1.0, 1.0, 1.4, 2.0])
        a = rnd.randint(40, bright)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 246, 224, a))
    img.paste(layer, (0, 0), layer)


def milky_way(img, cx=0.35, cy=0.30, length=1.3, seed=11):
    """A soft diagonal band of tiny stars."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(2200):
        t = rnd.uniform(-0.5, 0.5)
        spread = rnd.gauss(0, 0.05)
        x = (cx + t * length * 0.9 + spread * 0.55) * W
        y = (cy + t * 0.55 + spread) * H
        r = rnd.uniform(0.5, 1.6)
        a = rnd.randint(20, 110)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(226, 220, 255, a))
    layer = layer.filter(ImageFilter.GaussianBlur(1.4))
    img.paste(layer, (0, 0), layer)


def add_water(img, horizon, darken=0.55, blur=7.0, glitter=True,
              glitter_x=0.5):
    """Mirror the sky into the lower part and add horizontal shimmer."""
    sky = img.crop((0, max(0, horizon - 260), W, horizon))
    sky = sky.transpose(Image.FLIP_TOP_BOTTOM)
    sky = sky.resize((W, H - horizon), Image.BICUBIC)
    sky = sky.filter(ImageFilter.GaussianBlur(blur))
    water = Image.blend(sky, Image.new("RGB", sky.size, (8, 6, 16)), darken)
    img.paste(water, (0, horizon))

    layer = Image.new("RGBA", (W, H - horizon), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(5)
    for _ in range(260):
        t = rnd.random()
        y = int((H - horizon) * (t ** 1.6))
        x = rnd.randrange(W)
        ln = rnd.randint(10, 90) * (0.3 + t)
        a = rnd.randint(8, 34)
        d.line([(x, y), (x + ln, y)], fill=(255, 220, 180, a),
               width=max(1, int(1 + 2 * t)))
    if glitter:
        gx = int(W * glitter_x)
        for _ in range(220):
            t = rnd.random() ** 1.5
            y = int((H - horizon) * t)
            x = gx + rnd.gauss(0, 30 + 180 * t)
            ln = rnd.randint(4, 40) * (0.4 + t)
            d.line([(x, y), (x + ln, y)],
                   fill=(255, 226, 170, rnd.randint(30, 120)),
                   width=max(1, int(1 + 2 * t)))
    layer = layer.filter(ImageFilter.GaussianBlur(0.7))
    img.paste(layer, (0, horizon), layer)


def tree_line(img, base, color, seed=1, height=0.10, density=1.0):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = -20
    while x < W + 20:
        h = H * height * rnd.uniform(0.55, 1.25)
        w = h * rnd.uniform(0.22, 0.38)
        y = H * base
        d.polygon([(x, y), (x + w / 2, y - h), (x + w, y)],
                  fill=(*color[:3], 255))
        x += w * rnd.uniform(0.5, 1.1) / max(density, 0.1)
    img.paste(layer, (0, 0), layer)


def skyline(img, base=0.74, color=(20, 9, 16), seed=7,
            lit=(255, 186, 110), max_h=0.28):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = -10
    while x < W:
        bw = rnd.randint(36, 110)
        bh = rnd.randint(50, int(H * max_h))
        y = H * base - bh
        d.rectangle([x, y, x + bw, H * base], fill=(*color, 255))
        for wy in range(int(y) + 9, int(H * base) - 8, 13):
            for wx in range(x + 6, x + bw - 6, 11):
                if rnd.random() < 0.30:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(*lit, rnd.randint(90, 230)))
        if rnd.random() < 0.3:  # antenna
            ax = x + bw // 2
            d.line([(ax, y), (ax, y - rnd.randint(10, 40))],
                   fill=(*color, 255), width=2)
        x += bw + rnd.randint(3, 14)
    img.paste(layer, (0, 0), layer)


# --------------------------------------------------------------------------
# the twelve scenes
# --------------------------------------------------------------------------
def mountain_dawn():
    img = vgrad((38, 8, 22), (206, 96, 52), gamma=1.5)
    glow(img, W * 0.62, H * 0.46, 340, (255, 168, 96), 0.55)
    disc(img, W * 0.62, H * 0.46, 58, (255, 224, 168, 245), 3)
    clouds(img, 0.28, n=7, color=(255, 186, 140), alpha=55, seed=2, size=1.2)
    mist(img, 0.50, 0.10, alpha=75)
    ridge(img, 0.58, 130, (128, 40, 34), 11, blur=2.2, alpha=210)
    mist(img, 0.60, 0.08, alpha=90)
    ridge(img, 0.69, 100, (92, 24, 26), 22, blur=1.4, alpha=235)
    mist(img, 0.72, 0.07, alpha=70)
    ridge(img, 0.80, 85, (58, 13, 18), 33, blur=0.8)
    ridge(img, 0.92, 60, (30, 6, 10), 44, blur=0.4)
    return grain(img, 7, 0.03)


def sea_dusk():
    img = vgrad((32, 6, 24), (232, 118, 66), gamma=1.7)
    glow(img, W * 0.52, H * 0.62, 300, (255, 172, 100), 0.5)
    disc(img, W * 0.52, H * 0.62, 46, (255, 214, 152, 240), 2)
    clouds(img, 0.30, n=6, color=(255, 170, 130), alpha=50, seed=6, size=1.4)
    add_water(img, int(H * 0.63), darken=0.52, blur=6, glitter_x=0.52)
    # dark foreground cliff
    ridge(img, 0.94, 55, (18, 5, 9), 9, blur=0.6)
    return grain(img, 6, 0.03)


def city_night():
    img = vgrad((6, 8, 26), (58, 12, 26), gamma=1.4)
    stars(img, bottom=0.55, count=500, seed=21)
    glow(img, W * 0.72, H * 0.66, 300, (255, 120, 70), 0.35)
    skyline(img, base=0.70, color=(14, 7, 15), seed=7)
    skyline(img, base=0.78, color=(8, 4, 9), seed=17, max_h=0.20)
    add_water(img, int(H * 0.79), darken=0.62, blur=5, glitter=False)
    # reflections of lit windows
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(31)
    for _ in range(260):
        x = rnd.randrange(W)
        y = int(H * 0.80 + rnd.random() ** 1.4 * H * 0.19)
        ln = rnd.randint(3, 18)
        d.line([(x, y), (x + ln, y)],
               fill=(255, 180, 110, rnd.randint(15, 70)), width=1)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(layer, (0, 0), layer)
    return grain(img, 6, 0.04)


def road_plain():
    img = vgrad((120, 168, 206), (238, 216, 182), gamma=1.2)
    clouds(img, 0.26, n=9, color=(255, 252, 246), alpha=110, seed=4, size=1.3)
    # distant hills and tree line
    ridge(img, 0.56, 40, (120, 124, 100), 12, blur=1.0, alpha=200)
    tree_line(img, 0.575, (64, 78, 52), seed=5, height=0.035, density=1.6)
    # fields
    img.paste(Image.new("RGB", (W, H - int(H * 0.57)), (150, 148, 92)),
              (0, int(H * 0.57)))
    vx, vy = W * 0.54, H * 0.575
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(8)
    # furrows converging on the vanishing point
    for k in range(-26, 27):
        x_end = vx + k * 0.075 * W
        shade = rnd.randint(20, 55)
        d.line([(vx + k * 3, vy), (x_end, H)],
               fill=(92, 100, 52, shade), width=rnd.choice([1, 1, 2]))
    for _ in range(900):
        x = rnd.randrange(W)
        y = rnd.randint(int(H * 0.57), H)
        ln = rnd.randint(4, 18) * (0.4 + (y / H))
        d.line([(x, y), (x + ln * 0.3, y - ln * 0.12)],
               fill=(96, 104, 54, rnd.randint(15, 45)), width=1)
    img.paste(layer, (0, 0), layer)
    # road: perspective trapezoid + thin dashes
    d = ImageDraw.Draw(img)
    d.polygon([(vx - 8, vy), (vx + 8, vy), (W * 0.88, H), (W * 0.08, H)],
              fill=(74, 72, 76))
    d.line([(vx - 8, vy), (W * 0.08, H)], fill=(224, 214, 192), width=3)
    d.line([(vx + 8, vy), (W * 0.88, H)], fill=(224, 214, 192), width=3)
    for i in range(8):
        t0, t1 = i / 8 + 0.02, i / 8 + 0.09
        y0 = vy + (H - vy) * (t0 ** 1.9)
        y1 = vy + (H - vy) * (t1 ** 1.9)
        half0 = 1.5 + 34 * (t0 ** 1.9)
        half1 = 1.5 + 34 * (t1 ** 1.9)
        d.polygon([(vx - half0, y0), (vx + half0, y0),
                   (vx + half1, y1), (vx - half1, y1)],
                  fill=(234, 224, 202))
    return grain(img, 6, 0.03)


def field_gold():
    img = vgrad((86, 128, 176), (250, 210, 146), gamma=1.3)
    clouds(img, 0.30, n=6, color=(255, 250, 240), alpha=95, seed=13, size=1.5)
    glow(img, W * 0.78, H * 0.42, 260, (255, 220, 150), 0.4)
    ridge(img, 0.56, 30, (140, 122, 72), 15, blur=1.2, alpha=180)
    tree_line(img, 0.565, (90, 76, 40), seed=16, height=0.030, density=1.4)
    img.paste(Image.new("RGB", (W, H - int(H * 0.57)), (196, 158, 62)),
              (0, int(H * 0.57)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(19)
    for _ in range(2600):
        x = rnd.randrange(W)
        y = rnd.randint(int(H * 0.565), H)
        t = (y - H * 0.565) / (H * 0.435)
        ln = rnd.randint(6, 26) * (0.3 + t)
        d.line([(x, y), (x + ln * 0.18, y - ln)],
               fill=(226, 184, 84, rnd.randint(30, 90)),
               width=max(1, int(1 + t * 2)))
    img.paste(layer, (0, 0), layer)
    return grain(img, 7, 0.035)


def _pine(d, x, base_y, h, half, color):
    """A simple layered conifer silhouette."""
    trunk_w = max(2, half * 0.12)
    d.rectangle([x - trunk_w / 2, base_y - h * 0.18,
                 x + trunk_w / 2, base_y], fill=color)
    for k in range(3):
        top = base_y - h * (0.95 - k * 0.20)
        yy = base_y - h * (0.34 - k * 0.16)
        ww = half * (0.55 + k * 0.28)
        d.polygon([(x, top), (x - ww, yy), (x + ww, yy)], fill=color)


def forest_mist():
    img = vgrad((44, 74, 64), (208, 220, 198), gamma=1.7)
    glow(img, W * 0.68, H * 0.20, 360, (244, 248, 220), 0.42)
    clouds(img, 0.18, n=4, color=(236, 244, 226), alpha=55, seed=42, size=1.6)

    # far pines
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(41)
    for x in range(-20, W + 40, 26):
        h = rnd.randint(45, 95)
        _pine(d, x + rnd.randint(-6, 6), H * 0.63, h, h * 0.30,
              (126, 146, 120, 150))
    img.paste(layer, (0, 0), layer)
    mist(img, 0.56, 0.12, color=(226, 236, 212), alpha=80, blur=30)

    # mid pines
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(43)
    for x in range(-30, W + 60, 64):
        h = rnd.randint(120, 210)
        _pine(d, x + rnd.randint(-14, 14), H * 0.78, h, h * 0.30,
              (68, 94, 72, 215))
    img.paste(layer, (0, 0), layer)
    mist(img, 0.72, 0.10, color=(214, 228, 202), alpha=55, blur=26)

    # near trunks with branches, cropped by the frame
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(47)
    for x in range(-40, W + 80, 120):
        tw = rnd.randint(26, 64)
        top = rnd.randint(-120, 80)
        lean = rnd.randint(-30, 30)
        d.polygon([(x - tw * 0.5, H), (x + lean - tw * 0.30, top),
                   (x + lean + tw * 0.30, top), (x + tw * 0.5, H)],
                  fill=(26, 46, 36, 255))
        # a few branches with leaf clusters
        for k in range(3):
            by = rnd.randint(int(H * 0.10), int(H * 0.55))
            dx = rnd.choice([-1, 1]) * rnd.randint(40, 110)
            ey = by - rnd.randint(20, 70)
            d.line([(x + lean * 0.5, by), (x + dx, ey)],
                   fill=(26, 46, 36, 255), width=max(3, tw // 6))
            for _ in range(4):
                rx = x + dx + rnd.randint(-34, 34)
                ry = ey + rnd.randint(-28, 28)
                rr = rnd.randint(14, 34)
                d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr],
                          fill=(22, 44, 32, 210))
    img.paste(layer, (0, 0), layer)

    # canopy along the top edge
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(51)
    for _ in range(220):
        x = rnd.randrange(W)
        y = rnd.randint(-70, int(H * 0.18))
        r = rnd.randint(30, 100)
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(20, 42, 32, rnd.randint(50, 140)))
    layer = layer.filter(ImageFilter.GaussianBlur(9))
    img.paste(layer, (0, 0), layer)

    # ground and low fog
    img.paste(Image.new("RGB", (W, int(H * 0.14)), (34, 52, 34)),
              (0, int(H * 0.86)))
    mist(img, 0.84, 0.08, color=(198, 214, 188), alpha=60, blur=24)
    return grain(img, 7, 0.035)


def starry_sky():
    img = vgrad((4, 6, 22), (76, 18, 26), gamma=2.0)
    stars(img, bottom=0.72, count=1100, seed=23)
    milky_way(img, cx=0.38, cy=0.28, length=1.4)
    glow(img, W * 0.80, H * 0.58, 260, (255, 140, 90), 0.25)
    ridge(img, 0.74, 90, (22, 10, 20), 61, blur=1.2, alpha=245)
    ridge(img, 0.86, 60, (12, 5, 12), 62, blur=0.6)
    return grain(img, 6, 0.04)


def river_bend():
    img = vgrad((118, 166, 198), (232, 214, 178), gamma=1.2)
    clouds(img, 0.24, n=7, color=(255, 252, 246), alpha=100, seed=71, size=1.2)
    ridge(img, 0.48, 90, (108, 122, 104), 72, blur=1.8, alpha=170)
    tree_line(img, 0.52, (60, 82, 56), seed=73, height=0.04, density=1.5)
    # land
    img.paste(Image.new("RGB", (W, H - int(H * 0.52)), (118, 140, 84)),
              (0, int(H * 0.52)))
    # S-shaped river
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    left, right = [], []
    for y in range(int(H * 0.53), H + 10, 8):
        t = (y - H * 0.53) / (H * 0.47)
        cx = W * (0.52 + 0.20 * math.sin(t * 2.6 + 0.4) - 0.10 * t)
        half = 8 + 150 * (t ** 1.3)
        left.append((cx - half, y))
        right.append((cx + half, y))
    d.polygon(left + right[::-1], fill=(126, 166, 190, 255))
    # banks
    for pts in (left, right):
        d.line(pts, fill=(86, 104, 60, 255), width=10)
    # water shimmer
    rnd = random.Random(74)
    for _ in range(500):
        t = rnd.random() ** 1.3
        y = int(H * 0.55 + t * H * 0.45)
        cx = W * (0.52 + 0.20 * math.sin(t * 2.6 + 0.4) - 0.10 * t)
        half = 8 + 150 * (t ** 1.3)
        x = cx + rnd.uniform(-half * 0.8, half * 0.8)
        ln = rnd.randint(4, 30) * (0.3 + t)
        d.line([(x, y), (x + ln, y)],
               fill=(232, 240, 238, rnd.randint(20, 80)), width=1)
    img.paste(layer, (0, 0), layer)
    return grain(img, 6, 0.03)


def grassland():
    img = vgrad((86, 142, 196), (216, 228, 210), gamma=1.1)
    clouds(img, 0.22, n=10, color=(255, 255, 252), alpha=125, seed=81, size=1.5)
    glow(img, W * 0.25, H * 0.25, 300, (255, 246, 214), 0.35)
    ridge(img, 0.55, 45, (122, 146, 92), 82, blur=1.6, alpha=200)
    ridge(img, 0.64, 55, (96, 128, 70), 83, blur=1.0, alpha=230)
    ridge(img, 0.76, 65, (72, 108, 52), 84, blur=0.5)
    ridge(img, 0.90, 55, (52, 86, 38), 85, blur=0.3)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(86)
    for _ in range(2400):
        x = rnd.randrange(W)
        y = rnd.randint(int(H * 0.62), H)
        t = (y - H * 0.62) / (H * 0.38)
        ln = rnd.randint(4, 16) * (0.4 + t)
        d.line([(x, y), (x + ln * 0.4, y - ln)],
               fill=(36, 68, 28, rnd.randint(20, 70)), width=1)
    img.paste(layer, (0, 0), layer)
    return grain(img, 6, 0.03)


def bridge():
    img = vgrad((36, 10, 28), (216, 116, 78), gamma=1.8)
    glow(img, W * 0.30, H * 0.58, 280, (255, 176, 110), 0.45)
    disc(img, W * 0.30, H * 0.58, 38, (255, 218, 160, 230), 2)
    clouds(img, 0.34, n=6, color=(255, 178, 140), alpha=45, seed=91, size=1.3)
    add_water(img, int(H * 0.66), darken=0.58, blur=7, glitter_x=0.30)
    # distant city on the right
    skyline(img, base=0.665, color=(28, 12, 22), seed=92, max_h=0.10)
    # suspension bridge silhouette
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = (18, 8, 12, 255)
    deck_y = int(H * 0.60)
    d.rectangle([0, deck_y, W, deck_y + 12], fill=col)
    for tx in (int(W * 0.28), int(W * 0.72)):
        d.rectangle([tx - 9, int(H * 0.28), tx + 9, deck_y], fill=col)
        d.line([(tx - 9, int(H * 0.30)), (tx + 9, int(H * 0.30))],
               fill=col, width=6)
    # main cables: catenary between towers, then down to the edges
    for side in (-1, 1):
        pts = []
        for x in range(0, W + 1, 10):
            t = x / W
            if 0.28 <= t <= 0.72:
                u = (t - 0.28) / 0.44
                y = H * 0.30 + (deck_y - H * 0.30) * (4 * (u - 0.5) ** 2)
            elif t < 0.28:
                u = t / 0.28
                y = H * 0.30 + (deck_y - H * 0.30) * (1 - u) ** 1.6
            else:
                u = (t - 0.72) / 0.28
                y = H * 0.30 + (deck_y - H * 0.30) * u ** 1.6
            pts.append((x, y))
        d.line(pts, fill=col, width=5)
        # hangers
        for x in range(20, W, 26):
            t = x / W
            if 0.28 <= t <= 0.72:
                u = (t - 0.28) / 0.44
                y = H * 0.30 + (deck_y - H * 0.30) * (4 * (u - 0.5) ** 2)
                d.line([(x, y), (x, deck_y)], fill=(18, 8, 12, 170), width=1)
    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    img.paste(layer, (0, 0), layer)
    # reflection of the bridge deck
    refl = img.crop((0, deck_y, W, deck_y + 120)).transpose(Image.FLIP_TOP_BOTTOM)
    refl = refl.filter(ImageFilter.GaussianBlur(5))
    refl.putalpha(70)
    img.paste(refl, (0, deck_y + 12), refl)
    return grain(img, 6, 0.035)


def terraces():
    img = vgrad((120, 156, 186), (246, 214, 156), gamma=1.3)
    clouds(img, 0.24, n=6, color=(255, 250, 240), alpha=90, seed=101, size=1.3)
    ridge(img, 0.48, 70, (128, 132, 100), 102, blur=1.6, alpha=170)
    # terraced bands: wavy polygons stacked from the horizon down
    rnd = random.Random(103)
    base_cols = [(186, 160, 84), (156, 144, 74), (196, 172, 96),
                 (138, 132, 68), (170, 152, 82), (120, 120, 62)]
    d = ImageDraw.Draw(img)
    for i in range(7):
        y0 = H * (0.50 + i * 0.072)
        amp = 16 + i * 5
        pts = [(0, H)]
        for x in range(0, W + 1, 16):
            t = x / W
            y = y0 + amp * math.sin(t * math.tau * (0.8 + i * 0.12) + i)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=base_cols[i % len(base_cols)])
        # lip highlight
        d.line(pts[1:-1], fill=(236, 208, 142), width=3)
    # crop marks / texture
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(1800):
        x = rnd.randrange(W)
        y = rnd.randint(int(H * 0.50), H)
        ln = rnd.randint(3, 12)
        d.line([(x, y), (x + ln, y - rnd.randint(0, 3))],
               fill=(96, 84, 40, rnd.randint(15, 45)), width=1)
    img.paste(layer, (0, 0), layer)
    return grain(img, 7, 0.03)


def torch_rays():
    """Abstract deep-red background with golden light rays (closing/chapter)."""
    img = vgrad((96, 14, 16), (28, 3, 6), gamma=1.5)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W * 0.5, H * 1.05
    rnd = random.Random(111)
    for i in range(46):
        a0 = -math.pi / 2 + (i - 23) * 0.045 + rnd.uniform(-0.01, 0.01)
        spread = rnd.uniform(0.008, 0.030)
        ln = H * rnd.uniform(0.75, 1.25)
        x1 = cx + math.cos(a0 - spread) * ln
        y1 = cy + math.sin(a0 - spread) * ln
        x2 = cx + math.cos(a0 + spread) * ln
        y2 = cy + math.sin(a0 + spread) * ln
        d.polygon([(cx, cy), (x1, y1), (x2, y2)],
                  fill=(255, 196, 112, rnd.randint(6, 26)))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    img.paste(layer, (0, 0), layer)
    glow(img, W * 0.5, H * 0.98, 420, (255, 160, 80), 0.35)
    return grain(img, 7, 0.04)


SCENES = [
    ("mountain_dawn.jpg", mountain_dawn),
    ("sea_dusk.jpg", sea_dusk),
    ("city_night.jpg", city_night),
    ("road_plain.jpg", road_plain),
    ("field_gold.jpg", field_gold),
    ("forest_mist.jpg", forest_mist),
    ("starry_sky.jpg", starry_sky),
    ("river_bend.jpg", river_bend),
    ("grassland.jpg", grassland),
    ("bridge.jpg", bridge),
    ("terraces.jpg", terraces),
    ("torch_rays.jpg", torch_rays),
]


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for name, fn in SCENES:
        path = os.path.join(out_dir, name)
        fn().save(path, "JPEG", quality=90, optimize=True)
        size = os.path.getsize(path)
        total += size
        print(f"{path}  {size // 1024} KB")
    print(f"{len(SCENES)} images, {total / 1024 / 1024:.1f} MB total")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/assets")
