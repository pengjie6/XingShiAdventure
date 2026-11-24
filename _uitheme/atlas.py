# -*- coding: utf-8 -*-
"""重绘 TMP 内联精灵图集（文本里的 <sprite=N> 金币/红心/宝石等小图标）。"""
import os
from PIL import Image, ImageDraw
from kit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "Assets", "Resources", "sprite assets", "InlineSpriteAtlas.png")

CELLS = {
    1: (0, 0, 58, 61),
    2: (78, 0, 135, 61),
    3: (142, 0, 199, 61),
    4: (210, 0, 266, 61),
    5: (0, 75, 58, 130),
    6: (78, 75, 135, 130),
}
SS = 4  # 超采样


def _ints(v):
    if isinstance(v, float):
        return int(round(v))
    if isinstance(v, (list, tuple)):
        return [_ints(x) for x in v]
    return v


class D(object):
    """把 float 坐标收成 int，省得每处写 int()。"""

    def __init__(self, d):
        self._d = d

    def __getattr__(self, name):
        f = getattr(self._d, name)

        def g(*a, **kw):
            a = [_ints(x) for x in a]
            kw = {k: (_ints(v) if k in ("width", "radius") else v) for k, v in kw.items()}
            return f(*a, **kw)

        return g


def token(d, s):
    c = s / 2
    r = s * 0.44
    d.ellipse([c - r, c - r, c + r, c + r], fill=GOLD, outline=INK, width=s * 0.05)
    d.ellipse([c - r * 0.80, c - r * 0.80, c + r * 0.80, c + r * 0.80], fill=(24, 44, 70, 255), outline=GOLD_L, width=s * 0.035)
    # 皇冠
    y = c + r * 0.18
    pts = [(c - r * 0.42, y), (c - r * 0.34, y - r * 0.42), (c - r * 0.12, y - r * 0.16),
           (c, y - r * 0.48), (c + r * 0.12, y - r * 0.16), (c + r * 0.34, y - r * 0.42), (c + r * 0.42, y)]
    d.polygon(pts, fill=GOLD_L)
    d.line(pts + [pts[0]], fill=GOLD, width=max(1, s * 0.02))


def heart(d, s):
    c, cy = s / 2, s * 0.56
    r = s * 0.30
    d.ellipse([c - r, cy - r * 0.95, c, cy + r * 0.05], fill=(226, 62, 74, 255))
    d.ellipse([c, cy - r * 0.95, c + r, cy + r * 0.05], fill=(226, 62, 74, 255))
    d.polygon([(c - r * 0.97, cy - r * 0.02), (c + r * 0.97, cy - r * 0.02), (c, cy + r * 1.10)], fill=(226, 62, 74, 255))
    d.ellipse([c - r * 0.52, cy - r * 0.62, c - r * 0.10, cy - r * 0.24], fill=(255, 186, 190, 220))


def coin(d, s):
    c = s / 2
    r = s * 0.42
    d.ellipse([c - r, c - r, c + r, c + r], fill=GOLD, outline=INK, width=s * 0.05)
    d.ellipse([c - r * 0.72, c - r * 0.72, c + r * 0.72, c + r * 0.72], outline=GOLD_D, width=max(1, s * 0.05))
    star4(d, c, c, r * 0.52, (255, 246, 214, 255), inner=0.34)


def ruby(d, s):
    c, cy = s / 2, s / 2
    r = s * 0.30
    pts = [(c, cy - r), (c + r * 0.90, cy - r * 0.10), (c + r * 0.52, cy + r), (c - r * 0.52, cy + r), (c - r * 0.90, cy - r * 0.10)]
    d.polygon(pts, fill=(214, 48, 92, 255), outline=INK)
    d.line(pts + [pts[0]], fill=INK, width=max(1, s * 0.04))
    d.polygon([(c, cy - r), (c + r * 0.34, cy - r * 0.06), (c, cy + r * 0.42), (c - r * 0.34, cy - r * 0.06)],
              fill=(255, 150, 180, 255))


def video(d, s):
    w, h = s * 0.80, s * 0.66
    x0, y0 = (s - w) / 2, (s - h) / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=s * 0.10, fill=(26, 44, 68, 255), outline=COPPER, width=max(1, s * 0.05))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h * 0.28], radius=s * 0.07, fill=COPPER)
    d.polygon([(s * 0.41, s * 0.50), (s * 0.66, s * 0.62), (s * 0.41, s * 0.74)], fill=(240, 255, 252, 255))


def key(d, s):
    c, cy = s * 0.38, s / 2
    r = s * 0.20
    d.ellipse([c - r, cy - r, c + r, cy + r], fill=GOLD, outline=INK, width=max(1, s * 0.05))
    d.ellipse([c - r * 0.36, cy - r * 0.36, c + r * 0.36, cy + r * 0.36], fill=(26, 44, 68, 255))
    d.line([(c + r * 0.9, cy), (s * 0.84, cy)], fill=INK, width=max(2, s * 0.16))
    d.line([(c + r * 0.9, cy), (s * 0.84, cy)], fill=GOLD, width=max(1, s * 0.10))
    d.line([(s * 0.72, cy), (s * 0.72, cy + s * 0.14)], fill=GOLD, width=max(1, s * 0.10))
    d.line([(s * 0.82, cy), (s * 0.82, cy + s * 0.10)], fill=GOLD, width=max(1, s * 0.10))


FN = {1: token, 2: heart, 3: coin, 4: ruby, 5: video, 6: key}


def main():
    base = Image.open(P).convert("RGBA")
    for idx, (x0, y0, x1, y1) in CELLS.items():
        base.paste((0, 0, 0, 0), (x0, y0, x1 + 1, y1 + 1))
        w, h = x1 - x0 + 1, y1 - y0 + 1
        s = min(w, h)
        big = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
        d = D(ImageDraw.Draw(big))
        FN[idx](d, s * SS)
        small = big.resize((s, s), Image.LANCZOS)
        # 垂直居中放进单元格
        ox = x0 + (w - s) // 2
        oy = y0 + (h - s) // 2
        base.alpha_composite(small, (ox, oy))
        print("cell", idx, (x0, y0, w, h), "drawn", s)
    base.save(P)
    print("saved", P)


if __name__ == "__main__":
    main()
