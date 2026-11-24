# -*- coding: utf-8 -*-
"""重绘 Resources/UI 下的奖励图标（原本是带白色粗描边的旧画风，必须整体换掉）。"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFilter
from kit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "Assets", "Resources", "UI")

STEEL = (206, 220, 236, 255)
STEEL_D = (128, 148, 172, 255)
WOOD = (150, 96, 52, 255)
WOOD_D = (98, 58, 30, 255)


def _rot(pts, deg, cx, cy):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def _poly(d, pts, fill, ow):
    d.polygon(pts, fill=fill, outline=INK)
    d.line(pts + [pts[0]], fill=INK, width=ow, joint="curve")


def _bar(d, x0, y0, x1, y1, w, fill, ow):
    d.line([(x0, y0), (x1, y1)], fill=INK, width=w + ow * 2)
    d.line([(x0, y0), (x1, y1)], fill=fill, width=w)


def glyph_coin(d, w, h, ow):
    cx, cy = w * 0.5, h * 0.5
    r = min(w, h) * 0.30
    d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], fill=GOLD, outline=INK, width=ow)
    d.ellipse([cx - r * 0.72, cy - r * 0.66, cx + r * 0.72, cy + r * 0.66], outline=GOLD_D, width=ow)
    star4(d, cx, cy, r * 0.52, GOLD_L)


def glyph_ruby(d, w, h, ow):
    cx, cy = w * 0.5, h * 0.5
    s = min(w, h) * 0.30
    pts = [(cx, cy - s), (cx + s * 0.86, cy - s * 0.14), (cx + s * 0.5, cy + s), (cx - s * 0.5, cy + s), (cx - s * 0.86, cy - s * 0.14)]
    _poly(d, pts, (214, 62, 108, 255), ow)
    _poly(d, [(cx, cy - s), (cx + s * 0.34, cy - s * 0.10), (cx, cy + s * 0.44), (cx - s * 0.34, cy - s * 0.10)], (255, 168, 196, 255), ow // 2)


def glyph_heart(d, w, h, ow):
    cx, cy = w * 0.5, h * 0.52
    s = min(w, h) * 0.30
    d.ellipse([cx - s, cy - s * 0.92, cx, cy + s * 0.10], fill=CRIMSON, outline=INK, width=ow)
    d.ellipse([cx, cy - s * 0.92, cx + s, cy + s * 0.10], fill=CRIMSON, outline=INK, width=ow)
    _poly(d, [(cx - s * 0.96, cy - s * 0.05), (cx + s * 0.96, cy - s * 0.05), (cx, cy + s * 1.02)], CRIMSON, ow)
    d.ellipse([cx - s * 0.46, cy - s * 0.52, cx - s * 0.06, cy - s * 0.16], fill=(255, 176, 176, 200))


def glyph_wrench(d, w, h, ow):
    cx, cy = w * 0.5, h * 0.5
    s = min(w, h) * 0.34
    # 手柄
    _bar(d, cx - s * 0.58, cy + s * 0.58, cx + s * 0.30, cy - s * 0.30, int(s * 0.26), STEEL, ow)
    # 开口端（C 形环）
    bx0, by0, bx1, by1 = cx + s * 0.02, cy - s * 0.92, cx + s * 0.92, cy - s * 0.02
    d.arc([bx0, by0, bx1, by1], 300, 240, fill=INK, width=int(s * 0.30) + ow * 2)
    d.arc([bx0, by0, bx1, by1], 300, 240, fill=STEEL, width=int(s * 0.30))
    # 尾端环
    d.ellipse([cx - s * 0.74, cy + s * 0.42, cx - s * 0.26, cy + s * 0.90], fill=STEEL, outline=INK, width=ow)
    d.ellipse([cx - s * 0.60, cy + s * 0.56, cx - s * 0.40, cy + s * 0.76], fill=NAVY)


def glyph_hero(d, w, h, ow):
    cx, cy = w * 0.5, h * 0.52
    s = min(w, h) * 0.30
    body = [(cx - s * 0.92, cy + s * 1.00), (cx - s * 0.66, cy + s * 0.10),
            (cx - s * 0.30, cy - s * 0.16), (cx + s * 0.30, cy - s * 0.16),
            (cx + s * 0.66, cy + s * 0.10), (cx + s * 0.92, cy + s * 1.00)]
    _poly(d, body, TEAL, ow)
    d.ellipse([cx - s * 0.44, cy - s * 1.00, cx + s * 0.44, cy - s * 0.14], fill=GOLD, outline=INK, width=ow)


def glyph_weapon(d, w, h, ow, kind):
    cx, cy = w * 0.5, h * 0.52
    s = min(w, h) * 0.34
    if kind == "sword":
        _poly(d, [(cx, cy - s * 1.05), (cx + s * 0.20, cy - s * 0.70), (cx + s * 0.17, cy + s * 0.20),
                  (cx - s * 0.17, cy + s * 0.20), (cx - s * 0.20, cy - s * 0.70)], STEEL, ow)
        _bar(d, cx - s * 0.52, cy + s * 0.24, cx + s * 0.52, cy + s * 0.24, int(s * 0.22), GOLD, ow)
        _bar(d, cx, cy + s * 0.32, cx, cy + s * 0.90, int(s * 0.20), WOOD, ow)
    elif kind == "dagger":
        _poly(d, [(cx, cy - s * 0.70), (cx + s * 0.17, cy - s * 0.42), (cx + s * 0.14, cy + s * 0.16),
                  (cx - s * 0.14, cy + s * 0.16), (cx - s * 0.17, cy - s * 0.42)], STEEL, ow)
        _bar(d, cx - s * 0.36, cy + s * 0.20, cx + s * 0.36, cy + s * 0.20, int(s * 0.18), GOLD, ow)
        _bar(d, cx, cy + s * 0.28, cx, cy + s * 0.72, int(s * 0.17), WOOD, ow)
    elif kind == "axe":
        sx = cx + s * 0.26
        _bar(d, sx, cy - s * 0.86, sx, cy + s * 0.98, int(s * 0.20), WOOD, ow)
        # 斧头：宽刃朝左，带内凹的须刃
        blade = [(sx - s * 0.04, cy - s * 0.72), (cx - s * 0.36, cy - s * 0.90),
                 (cx - s * 0.86, cy - s * 0.76), (cx - s * 0.94, cy - s * 0.30),
                 (cx - s * 0.84, cy + s * 0.14), (cx - s * 0.40, cy + s * 0.04),
                 (sx - s * 0.04, cy - s * 0.14)]
        _poly(d, blade, STEEL, ow)
        _poly(d, [(sx - s * 0.10, cy - s * 0.62), (cx - s * 0.40, cy - s * 0.74),
                  (cx - s * 0.74, cy - s * 0.62), (cx - s * 0.72, cy - s * 0.34),
                  (cx - s * 0.40, cy - s * 0.26), (sx - s * 0.10, cy - s * 0.34)], (240, 248, 255, 255), ow // 2)
        # 斧背
        _poly(d, [(sx + s * 0.06, cy - s * 0.74), (sx + s * 0.34, cy - s * 0.66),
                  (sx + s * 0.34, cy - s * 0.18), (sx + s * 0.06, cy - s * 0.12)], STEEL_D, ow)
    elif kind == "bow":
        ccx, ccy, R = cx + s * 0.45, cy, s * 1.00
        bbox = [ccx - R, ccy - R, ccx + R, ccy + R]
        d.arc(bbox, 240, 120, fill=INK, width=int(s * 0.30) + ow * 2)
        d.arc(bbox, 240, 120, fill=WOOD, width=int(s * 0.30))
        d.line([(cx - s * 0.05, cy - s * 0.87), (cx - s * 0.05, cy + s * 0.87)], fill=MOON, width=max(2, ow))
        _bar(d, cx - s * 0.86, cy, cx + s * 0.78, cy, int(s * 0.13), GOLD_L, ow)
        _poly(d, [(cx + s * 1.02, cy), (cx + s * 0.62, cy - s * 0.20), (cx + s * 0.62, cy + s * 0.20)], STEEL, ow)
        _bar(d, cx - s * 0.62, cy - s * 0.16, cx - s * 0.62, cy + s * 0.16, int(s * 0.16), COPPER, ow)
    elif kind == "staff":
        _bar(d, cx, cy - s * 0.22, cx, cy + s * 1.02, int(s * 0.20), WOOD, ow)
        d.ellipse([cx - s * 0.40, cy - s * 0.98, cx + s * 0.40, cy - s * 0.18], fill=TEAL, outline=INK, width=ow)
        d.ellipse([cx - s * 0.20, cy - s * 0.82, cx + s * 0.04, cy - s * 0.56], fill=(216, 255, 250, 230))
        # 托住宝珠的两只爪
        _poly(d, [(cx - s * 0.44, cy - s * 0.30), (cx - s * 0.20, cy - s * 0.56),
                  (cx - s * 0.10, cy - s * 0.42), (cx - s * 0.30, cy - s * 0.14)], GOLD, ow // 2)
        _poly(d, [(cx + s * 0.44, cy - s * 0.30), (cx + s * 0.20, cy - s * 0.56),
                  (cx + s * 0.10, cy - s * 0.42), (cx + s * 0.30, cy - s * 0.14)], GOLD, ow // 2)
    elif kind == "hammer":
        _bar(d, cx, cy - s * 0.02, cx, cy + s * 1.02, int(s * 0.17), WOOD, ow)
        d.ellipse([cx - s * 0.16, cy + s * 0.86, cx + s * 0.16, cy + s * 1.06], fill=COPPER, outline=INK, width=ow)
        _poly(d, [(cx - s * 0.90, cy - s * 0.98), (cx + s * 0.90, cy - s * 0.98),
                  (cx + s * 0.90, cy - s * 0.16), (cx - s * 0.90, cy - s * 0.16)], STEEL, ow)
        _poly(d, [(cx - s * 0.90, cy - s * 0.56), (cx + s * 0.90, cy - s * 0.56),
                  (cx + s * 0.90, cy - s * 0.16), (cx - s * 0.90, cy - s * 0.16)], STEEL_D, ow // 2)
        _bar(d, cx - s * 0.74, cy - s * 0.76, cx + s * 0.74, cy - s * 0.76, int(s * 0.10), GOLD_L, ow // 2)
    elif kind == "spear":
        _bar(d, cx, cy - s * 0.30, cx, cy + s * 1.05, int(s * 0.16), WOOD, ow)
        _poly(d, [(cx, cy - s * 1.06), (cx + s * 0.30, cy - s * 0.56),
                  (cx, cy - s * 0.26), (cx - s * 0.30, cy - s * 0.56)], STEEL, ow)
        _bar(d, cx - s * 0.24, cy - s * 0.26, cx + s * 0.24, cy - s * 0.26, int(s * 0.13), GOLD, ow)
    elif kind == "scythe":
        sx = cx + s * 0.34
        _bar(d, sx, cy - s * 0.80, sx, cy + s * 1.02, int(s * 0.18), WOOD, ow)
        # 以刀柄顶端为圆心，向上-向左扫出一片月牙刀刃（与刀柄相连）
        ox, oy = sx, cy - s * 0.80
        pts_o, pts_i = [], []
        for k in range(21):
            a = math.radians(-96 - k * (94 / 20.0))
            ro = s * 0.92
            ri = s * (0.92 - 0.46 * (k / 20.0) ** 0.7)
            pts_o.append((ox + ro * math.cos(a), oy + ro * math.sin(a)))
            pts_i.append((ox + ri * math.cos(a), oy + ri * math.sin(a)))
        _poly(d, pts_o + pts_i[::-1], STEEL, ow)
    else:  # mace
        _bar(d, cx, cy + s * 0.14, cx, cy + s * 1.02, int(s * 0.20), WOOD, ow)
        hx, hy = cx, cy - s * 0.44
        for a in range(0, 360, 45):
            ax, ay = math.cos(math.radians(a)), math.sin(math.radians(a))
            p0 = (hx + ax * s * 0.86, hy + ay * s * 0.86)
            p1 = (hx + ax * s * 0.50 - ay * s * 0.16, hy + ay * s * 0.50 + ax * s * 0.16)
            p2 = (hx + ax * s * 0.50 + ay * s * 0.16, hy + ay * s * 0.50 - ax * s * 0.16)
            _poly(d, [p0, p1, p2], GOLD, ow // 2)
        d.ellipse([hx - s * 0.50, hy - s * 0.50, hx + s * 0.50, hy + s * 0.50], fill=STEEL_D, outline=INK, width=ow)


def medallion(size, drawer):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    r = min(w, h) * 0.485
    cx, cy = w / 2, h / 2
    ow = max(2, int(min(w, h) * 0.030))
    # 外发光
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(244, 181, 76, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(max(3, int(r * 0.16)))))
    d = ImageDraw.Draw(img)
    # 深蓝盘 + 铜环
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 38, 62, 255), outline=INK, width=ow)
    d.ellipse([cx - r * 0.90, cy - r * 0.90, cx + r * 0.90, cy + r * 0.90], outline=COPPER, width=max(2, ow - 1))
    d.ellipse([cx - r * 0.80, cy - r * 0.80, cx + r * 0.80, cy + r * 0.80], outline=(52, 82, 112, 255), width=max(1, ow // 2))
    drawer(d, w, h, ow)
    return img


def build_one(name, drawer):
    p = os.path.join(DIR, name)
    im = Image.open(p)
    size = im.size
    out = medallion(size, drawer)
    out.save(p)
    return p, size


def main():
    jobs = {
        "UI_reward_lootCoin.png": glyph_coin,
        "UI_reward_lootRuby.png": glyph_ruby,
        "UI_reward_InstantHeal.png": glyph_heart,
        "UI_reward_InstantRepair.png": glyph_wrench,
        "UI_reward_hero00.png": glyph_hero,
    }
    kinds = {1: "sword", 2: "dagger", 3: "axe", 4: "bow", 5: "staff",
             6: "hammer", 7: "spear", 8: "scythe", 9: "mace"}
    for i, k in kinds.items():
        jobs["UI_reward_weapon%02d.png" % i] = (lambda kk: (lambda d, w, h, ow: glyph_weapon(d, w, h, ow, kk)))(k)
    n = 0
    for name, fn in jobs.items():
        try:
            p, s = build_one(name, fn)
            print("ok", os.path.basename(p), s)
            n += 1
        except Exception as e:
            print("FAIL", name, e)
    print("完成", n)


if __name__ == "__main__":
    main()
