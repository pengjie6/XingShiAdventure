# -*- coding: utf-8 -*-
"""按原尺寸重绘 UI 素材（星辉远征主题）。"""
import math, os, sys, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from kit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPR = os.path.join(ROOT, "Assets", "Sprites")
UI   = os.path.join(ROOT, "Assets", "Resources", "UI")


def orig_size(path):
    with Image.open(path) as im:
        return im.size


def emit(path, img):
    assert img.size == orig_size(path), f"{path} 尺寸不一致 {img.size} != {orig_size(path)}"
    img.save(path, optimize=True)
    return img.size


# ---------------------------------------------------------------- 面板
def panel(size, border, style="moon", radius=None, ornament=True):
    w, h = size
    b = max(4, border if border > 4 else min(28, min(w, h) // 6))
    radius = radius if radius is not None else max(6, int(b * 0.5))

    if style == "moon":
        base = vgrad(size, (250, 252, 255, 255), (203, 214, 231, 255), gamma=1.1)
    elif style == "slot":
        base = vgrad(size, (46, 68, 96, 255), (17, 30, 48, 255), gamma=1.0)
    else:
        base = vgrad(size, (34, 60, 88, 255), (11, 22, 38, 255), gamma=1.0)

    # 极轻的颗粒，避免"脏"
    rnd = random.Random(w * 7 + h)
    noise = Image.new("L", (max(1, w // 3), max(1, h // 3)))
    npx = noise.load()
    for y in range(noise.size[1]):
        for x in range(noise.size[0]):
            npx[x, y] = rnd.randint(118, 138)
    noise = noise.resize(size, Image.BICUBIC)
    nz = Image.merge("RGBA", (noise, noise, noise, Image.new("L", size, 255)))
    base = Image.blend(base, nz, 0.10 if style == "moon" else 0.16)

    mask = rr_mask(size, radius)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)

    # 内侧：上亮下暗的厚度感
    inner = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(inner)
    for i in range(max(2, int(b * 0.42))):
        a = int((48 if style == "moon" else 70) * (1 - i / max(1, b * 0.42)))
        d.rounded_rectangle([i, i, w - 1 - i, h - 1 - i], radius=max(2, radius - i),
                            outline=(30, 44, 68, a), width=1)
    out.alpha_composite(Image.composite(inner, Image.new("RGBA", size, (0, 0, 0, 0)), mask))

    d = ImageDraw.Draw(out)
    ring_in = max(4, int(b * 0.12))
    # 外深边
    d.rounded_rectangle([0.5, 0.5, w - 1.5, h - 1.5], radius=radius, outline=INK,
                        width=max(2, int(b * 0.09)))
    # 铜主边
    d.rounded_rectangle([ring_in, ring_in, w - 1 - ring_in, h - 1 - ring_in],
                        radius=max(2, radius - ring_in), outline=COPPER,
                        width=max(2, int(b * 0.085)))
    # 内侧金线
    g = ring_in + max(2, int(b * 0.085))
    d.rounded_rectangle([g + 1, g + 1, w - 2 - g, h - 2 - g],
                        radius=max(2, radius - g - 1), outline=GOLD_L if style == "moon" else GOLD,
                        width=1)

    if ornament and min(w, h) >= 90:
        c = max(11, int(b * 0.46))
        sr = max(4.0, b * 0.17)
        for (cx, cy) in [(c, c), (w - 1 - c, c), (c, h - 1 - c), (w - 1 - c, h - 1 - c)]:
            star4(d, cx, cy, sr, GOLD, inner=0.30, outline=COPPER_D, ow=1)
            d.ellipse([cx - sr * 0.16, cy - sr * 0.16, cx + sr * 0.16, cy + sr * 0.16], fill=GOLD_L)

    # 柔和外投影
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([b * 0.10, b * 0.14, w - 1 - b * 0.10, h - 2],
                                             radius=radius, fill=(8, 16, 28, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(1.5, b * 0.08)))
    res = Image.new("RGBA", size, (0, 0, 0, 0))
    res.alpha_composite(shadow)
    res.alpha_composite(out)
    return res


# ---------------------------------------------------------------- 按钮
BTN_STYLES = {
    # 白字按钮：底色压深，保证白色文字对比度（原版按钮是亮粉/亮绿/亮蓝，白字很糊）
    "primary":   ((46, 158, 146, 255), (10, 74, 70, 255), TEAL, GOLD_L),
    "gold":      ((206, 138, 44, 255), (124, 66, 16, 255), GOLD_D, (255, 240, 200, 255)),
    "secondary": ((52, 96, 142, 255), (16, 34, 56, 255), NAVY_L, (140, 200, 230, 255)),
    "danger":    ((190, 66, 48, 255), (104, 26, 20, 255), CRIM_D, (255, 190, 170, 255)),
    "disabled":  ((126, 140, 158, 255), (72, 84, 100, 255), (60, 70, 86, 255), (170, 182, 196, 255)),
    "ghost":     ((40, 62, 88, 255), (18, 30, 48, 255), COPPER, GOLD_L),
}


def button(size, border, style="primary", chamfer=9, round_pill=False):
    w, h = size
    c1, c2, rim, hi = BTN_STYLES[style]
    radius = h // 2 if round_pill else max(6, int(h * 0.22))
    mask = cut_mask(size, chamfer=0 if round_pill else chamfer, radius=radius)

    body = vgrad(size, c1, c2, gamma=0.85)
    body = Image.composite(body, Image.new("RGBA", size, (0, 0, 0, 0)), mask)

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([2, 4, w - 3, h - 1], radius=radius, fill=(8, 14, 24, 90))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)))
    out.alpha_composite(body)

    # 顶部高光
    gl = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle([int(w * 0.06), int(h * 0.10), w - int(w * 0.06), int(h * 0.46)],
                         radius=max(3, radius // 2), fill=(255, 255, 255, 46))
    gl = gl.filter(ImageFilter.GaussianBlur(2))
    out.alpha_composite(Image.composite(gl, Image.new("RGBA", size, (0, 0, 0, 0)), mask))

    d = ImageDraw.Draw(out)
    if round_pill:
        d.rounded_rectangle([1, 1, w - 2, h - 2], radius=radius, outline=INK, width=3)
        d.rounded_rectangle([4, 4, w - 5, h - 5], radius=radius - 3, outline=rim, width=2)
        d.rounded_rectangle([7, 7, w - 8, h - 8], radius=radius - 6, outline=hi, width=1)
    else:
        ch = chamfer
        d.polygon([(ch, 1), (w - 1 - ch, 1), (w - 1, 1 + ch), (w - 1, h - 1 - ch),
                   (w - 1 - ch, h - 1), (ch, h - 1), (1, h - 1 - ch), (1, 1 + ch)],
                  outline=INK, width=3)
        d.polygon([(ch + 3, 4), (w - 4 - ch, 4), (w - 4, 4 + ch), (w - 4, h - 5 - ch),
                   (w - 4 - ch, h - 5), (ch + 3, h - 5), (4, h - 5 - ch), (4, 4 + ch)],
                  outline=rim, width=2)
        d.polygon([(ch + 6, 7), (w - 7 - ch, 7), (w - 7, 7 + ch), (w - 7, h - 8 - ch),
                   (w - 7 - ch, h - 8), (ch + 6, h - 8), (7, h - 8 - ch), (7, 7 + ch)],
                  outline=hi, width=1)

    # 左右两颗小星
    star4(d, 13, h // 2, max(3, h * 0.09), hi, inner=0.35, outline=COPPER_D, ow=1)
    star4(d, w - 14, h // 2, max(3, h * 0.09), hi, inner=0.35, outline=COPPER_D, ow=1)
    return out


# ---------------------------------------------------------------- 圆形按钮
def round_button(size, kind="play"):
    w, h = size
    s = min(w, h)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    # 投影
    d.ellipse([cx - s * 0.44, cy - s * 0.40, cx + s * 0.44, cy + s * 0.48], fill=(8, 14, 24, 110))
    img = img.filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(img)
    band = int(s * 0.055)
    d.ellipse([cx - s * 0.45, cy - s * 0.45, cx + s * 0.45, cy + s * 0.45], fill=GOLD)
    d.ellipse([cx - s * 0.45 + band, cy - s * 0.45 + band, cx + s * 0.45 - band, cy + s * 0.45 - band],
              fill=vgrad((int(s * 0.8), int(s * 0.8)), NAVY_L, NAVY_D).resize((4, 4)).getpixel((1, 1)))
    inner = [cx - s * 0.31, cy - s * 0.31, cx + s * 0.31, cy + s * 0.31]
    # 内圈渐变
    grad = rgrad((int(s * 0.62), int(s * 0.62)), (46, 84, 122, 255), (14, 26, 44, 255))
    gm = Image.new("L", grad.size, 0)
    ImageDraw.Draw(gm).ellipse([0, 0, grad.size[0] - 1, grad.size[1] - 1], fill=255)
    img.paste(grad, (int(inner[0]), int(inner[1])), gm)
    d = ImageDraw.Draw(img)
    d.ellipse(inner, outline=GOLD_L, width=max(1, int(s * 0.008)))

    if kind == "play":
        tri = [(cx - s * 0.10, cy - s * 0.17), (cx - s * 0.10, cy + s * 0.17),
               (cx + s * 0.19, cy)]
        d.polygon(tri, fill=WHITE, outline=INK)
    elif kind == "close":
        t = s * 0.055
        d.line([(cx - t, cy - t), (cx + t, cy + t)], fill=WHITE, width=max(3, int(s * 0.055)))
        d.line([(cx + t, cy - t), (cx - t, cy + t)], fill=WHITE, width=max(3, int(s * 0.055)))
    return img


def close_button(size):
    """深红圆 + 金色环 + 白色叉"""
    w, h = size
    s = min(w, h)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    r = s * 0.46
    d.ellipse([cx - r, cy - r + 2, cx + r, cy + r + 2], fill=(8, 14, 24, 110))
    img = img.filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(img)
    grad = rgrad((int(s), int(s)), (222, 92, 72, 255), (120, 30, 22, 255))
    gm = Image.new("L", grad.size, 0)
    ImageDraw.Draw(gm).ellipse([0, 0, s - 1, s - 1], fill=255)
    img.paste(grad, (int(cx - s / 2), int(cy - s / 2)), gm)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=max(2, int(s * 0.045)))
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86],
              outline=GOLD, width=max(1, int(s * 0.022)))
    t = s * 0.17
    wdt = max(3, int(s * 0.075))
    d.line([(cx - t, cy - t), (cx + t, cy + t)], fill=WHITE, width=wdt)
    d.line([(cx + t, cy - t), (cx - t, cy + t)], fill=WHITE, width=wdt)
    return img


# ---------------------------------------------------------------- 条
def bar_track(size, radius=None, style="hp"):
    w, h = size
    r = radius if radius is not None else h // 2
    mask = rr_mask(size, r, 1)
    # 浅色羊皮凹槽：原本底图是白底，这里的文字多为深色，保持浅底才不会糊
    body = vgrad(size, (226, 214, 190, 255), (188, 174, 148, 255))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)
    # 内阴影（顶部压暗，做出凹槽感）
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([0, 0, w, int(h * 0.55)], radius=r, fill=(96, 78, 52, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(max(1, h // 8)))
    out.alpha_composite(Image.composite(sh, Image.new("RGBA", size, (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=r, outline=INK, width=max(2, h // 14))
    d.rounded_rectangle([max(2, h // 10), max(2, h // 10), w - 1 - max(2, h // 10), h - 1 - max(2, h // 10)],
                        radius=max(2, r - h // 10), outline=COPPER, width=max(1, h // 22))
    return out


def bar_fill(size, radius=None, color1=(255, 196, 96, 255), color2=(196, 112, 34, 255)):
    w, h = size
    r = radius if radius is not None else h // 2
    mask = rr_mask(size, r, 1)
    body = vgrad(size, color1, color2, gamma=0.8)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(body, (0, 0), mask)
    # 斜纹
    d = ImageDraw.Draw(out, "RGBA")
    step = max(8, h // 2)
    for x in range(-h, w + h, step):
        d.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 26), width=max(2, h // 8))
    # 顶部高光
    gl = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle([2, 2, w - 3, int(h * 0.45)], radius=r, fill=(255, 255, 255, 60))
    gl = gl.filter(ImageFilter.GaussianBlur(2))
    out.alpha_composite(Image.composite(gl, Image.new("RGBA", size, (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=r, outline=INK, width=max(1, h // 16))
    return out


# ---------------------------------------------------------------- 图标
def icon(size, glyph, fg=GOLD, bg=None, ring=None):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    s = min(w, h)

    if ring:
        d.ellipse([cx - s * 0.46, cy - s * 0.46, cx + s * 0.46, cy + s * 0.46], fill=ring)
        d.ellipse([cx - s * 0.46, cy - s * 0.46, cx + s * 0.46, cy + s * 0.46],
                  outline=INK, width=max(2, int(s * 0.05)))
    if bg:
        d.ellipse([cx - s * 0.36, cy - s * 0.36, cx + s * 0.36, cy + s * 0.36], fill=bg)

    ow = max(2, int(s * 0.045))
    if glyph == "coin":
        r = s * 0.40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=INK, width=ow)
        d.ellipse([cx - r * 0.76, cy - r * 0.76, cx + r * 0.76, cy + r * 0.76],
                  outline=GOLD_D, width=max(1, int(s * 0.03)))
        star4(d, cx, cy, r * 0.52, GOLD_L, inner=0.4, outline=GOLD_D, ow=1)
    elif glyph == "ruby":
        pts = [(cx, cy - s * 0.42), (cx + s * 0.34, cy - s * 0.05), (cx, cy + s * 0.42),
               (cx - s * 0.34, cy - s * 0.05)]
        d.polygon(pts, fill=(226, 74, 120, 255), outline=INK)
        d.line(pts + [pts[0]], fill=INK, width=ow)
        d.polygon([(cx, cy - s * 0.42), (cx + s * 0.16, cy - s * 0.02), (cx, cy + s * 0.2),
                   (cx - s * 0.16, cy - s * 0.02)], fill=(255, 160, 190, 255))
    elif glyph == "key":
        r = s * 0.20
        d.ellipse([cx - r, cy - s * 0.34, cx + r, cy - s * 0.34 + 2 * r],
                  outline=GOLD, width=ow)
        d.line([(cx, cy - s * 0.34 + 2 * r), (cx, cy + s * 0.36)], fill=GOLD, width=ow)
        d.line([(cx, cy + s * 0.30), (cx + s * 0.20, cy + s * 0.30)], fill=GOLD, width=ow)
        d.line([(cx, cy + s * 0.14), (cx + s * 0.14, cy + s * 0.14)], fill=GOLD, width=ow)
    elif glyph == "heart":
        d.ellipse([cx - s * 0.34, cy - s * 0.30, cx + s * 0.02, cy + s * 0.10],
                  fill=(214, 58, 58, 255))
        d.ellipse([cx - s * 0.02, cy - s * 0.30, cx + s * 0.34, cy + s * 0.10],
                  fill=(214, 58, 58, 255))
        d.polygon([(cx - s * 0.34, cy - s * 0.06), (cx + s * 0.34, cy - s * 0.06), (cx, cy + s * 0.38)],
                  fill=(214, 58, 58, 255))
    elif glyph == "sword":
        d.line([(cx - s * 0.24, cy + s * 0.28), (cx + s * 0.26, cy - s * 0.30)],
               fill=GOLD_L, width=max(3, int(s * 0.10)))
        d.line([(cx - s * 0.20, cy + s * 0.06), (cx + s * 0.04, cy + s * 0.26)],
               fill=COPPER, width=max(2, int(s * 0.07)))
        d.polygon([(cx + s * 0.30, cy - s * 0.34), (cx + s * 0.34, cy - s * 0.20),
                   (cx + s * 0.20, cy - s * 0.24)], fill=GOLD_L)
    elif glyph == "chevron":
        d.line([(cx - s * 0.16, cy - s * 0.24), (cx + s * 0.16, cy), (cx - s * 0.16, cy + s * 0.24)],
               fill=fg, width=max(3, int(s * 0.12)), joint="curve")
    elif glyph == "arrow_left":
        d.line([(cx + s * 0.16, cy - s * 0.24), (cx - s * 0.16, cy), (cx + s * 0.16, cy + s * 0.24)],
               fill=fg, width=max(3, int(s * 0.12)), joint="curve")
    elif glyph == "up":
        d.polygon([(cx, cy - s * 0.34), (cx + s * 0.28, cy + s * 0.02), (cx + s * 0.10, cy + s * 0.02),
                   (cx + s * 0.10, cy + s * 0.34), (cx - s * 0.10, cy + s * 0.34),
                   (cx - s * 0.10, cy + s * 0.02), (cx - s * 0.28, cy + s * 0.02)],
                  fill=fg, outline=INK)
    elif glyph == "question":
        d.ellipse([cx - s * 0.34, cy - s * 0.40, cx + s * 0.34, cy + s * 0.28], fill=(30, 44, 66, 255))
        d.arc([cx - s * 0.19, cy - s * 0.28, cx + s * 0.19, cy + s * 0.10], 160, 20,
              fill=WHITE, width=max(4, int(s * 0.09)))
        d.line([(cx, cy + s * 0.10), (cx, cy + s * 0.20)], fill=WHITE, width=max(4, int(s * 0.09)))
        d.ellipse([cx - s * 0.06, cy + s * 0.28, cx + s * 0.06, cy + s * 0.40], fill=WHITE)
    elif glyph == "clock":
        d.ellipse([cx - s * 0.38, cy - s * 0.38, cx + s * 0.38, cy + s * 0.38],
                  fill=(24, 38, 58, 255), outline=GOLD, width=ow)
        d.line([(cx, cy), (cx, cy - s * 0.24)], fill=GOLD_L, width=max(2, int(s * 0.06)))
        d.line([(cx, cy), (cx + s * 0.18, cy + s * 0.10)], fill=GOLD_L, width=max(2, int(s * 0.06)))
    elif glyph == "wrench":
        d.line([(cx - s * 0.22, cy + s * 0.24), (cx + s * 0.16, cy - s * 0.16)],
               fill=GOLD_L, width=max(3, int(s * 0.09)))
        d.arc([cx + s * 0.02, cy - s * 0.34, cx + s * 0.36, cy], 300, 200, fill=GOLD_L,
              width=max(3, int(s * 0.07)))
    elif glyph == "lock":
        d.rounded_rectangle([cx - s * 0.26, cy - s * 0.06, cx + s * 0.26, cy + s * 0.34],
                            radius=max(2, s * 0.06), fill=GOLD, outline=INK, width=ow)
        d.arc([cx - s * 0.17, cy - s * 0.34, cx + s * 0.17, cy + s * 0.04], 180, 360,
              fill=GOLD_L, width=max(3, int(s * 0.07)))
        d.ellipse([cx - s * 0.05, cy + s * 0.08, cx + s * 0.05, cy + s * 0.18], fill=INK)
    elif glyph == "video":
        d.rounded_rectangle([cx - s * 0.34, cy - s * 0.24, cx + s * 0.16, cy + s * 0.24],
                            radius=max(2, s * 0.05), fill=WHITE, outline=INK, width=ow)
        d.polygon([(cx + s * 0.16, cy + s * 0.02), (cx + s * 0.34, cy + s * 0.16),
                   (cx + s * 0.34, cy - s * 0.16), (cx + s * 0.16, cy - s * 0.02)],
                  fill=WHITE, outline=INK)
    elif glyph == "star":
        star4(d, cx, cy, s * 0.40, GOLD, inner=0.36, outline=COPPER_D, ow=max(1, int(s * 0.03)))
    return img


# ---------------------------------------------------------------- 背景
HORIZON = 0.28  # 与旧素材一致：地平线在 23%~30% 处，下面是地面


def _ridge(d, w, h, base, amp, color, seed):
    rnd = random.Random(seed)
    pts = [(-20, h * (HORIZON + 0.02))]
    x = -20
    while x < w + 40:
        step = max(24, w // rnd.randint(9, 16))
        y = h * base - abs(math.sin(x / (w / rnd.uniform(2.2, 3.6)))) * h * amp
        y -= rnd.uniform(0, h * amp * 0.5)
        pts.append((x, y))
        x += step
    pts.append((w + 20, h * (HORIZON + 0.02)))
    d.polygon(pts, fill=color)


def backdrop(size, variant="meadow"):
    w, h = size
    hz = h * HORIZON
    PAL = {
        "meadow": dict(sky=((16, 34, 62), (6, 11, 22)), ground=((28, 52, 62), (10, 22, 30)),
                       ridge=((26, 50, 78), (14, 28, 48), (7, 14, 26)), tuft=(96, 150, 120)),
        "cavern": dict(sky=((22, 34, 58), (8, 12, 24)), ground=((30, 40, 66), (12, 16, 30)),
                       ridge=((34, 44, 76), (18, 24, 52), (8, 12, 26)), tuft=(110, 130, 190)),
        "ember":  dict(sky=((52, 30, 34), (12, 10, 16)), ground=((48, 28, 26), (16, 12, 16)),
                       ridge=((58, 36, 38), (32, 22, 28), (10, 9, 14)), tuft=(190, 110, 70)),
    }[variant]
    img = vgrad(size, PAL["sky"][0] + (255,), PAL["sky"][1] + (255,), gamma=1.4)

    # 星云
    neb = Image.new("RGBA", size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    rnd = random.Random(9)
    for i in range(14):
        cx, cy = rnd.uniform(0, w), rnd.uniform(0, hz)
        r = rnd.uniform(w * 0.16, w * 0.5)
        nd.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6],
                   fill=rnd.choice([(70, 130, 210, 26), (120, 90, 190, 22), (40, 160, 170, 20)]))
    img.alpha_composite(neb.filter(ImageFilter.GaussianBlur(w * 0.06)))

    # 月亮
    moon = Image.new("RGBA", size, (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    mx, my, mr = w * 0.68, h * 0.10, min(w, h) * 0.060
    md.ellipse([mx - mr * 5, my - mr * 5, mx + mr * 5, my + mr * 5], fill=(120, 170, 230, 30))
    img.alpha_composite(moon.filter(ImageFilter.GaussianBlur(w * 0.05)))
    d = ImageDraw.Draw(img)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(246, 247, 234, 255))
    d.ellipse([mx - mr * 1.04, my - mr * 1.04, mx + mr * 1.04, my + mr * 1.04],
              outline=(255, 250, 225, 55), width=3)

    # 星点
    rnd = random.Random(21)
    for _ in range(w * h // 2600):
        x, y = rnd.randrange(w), rnd.randrange(int(hz * 1.1))
        r = rnd.choice([0.5, 0.7, 0.9, 1.2, 1.7])
        a = rnd.randint(50, 190)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 248, 224, a))
        if r > 1.5:
            d.line([(x - r * 3, y), (x + r * 3, y)], fill=(255, 248, 224, int(a * 0.45)), width=1)
            d.line([(x, y - r * 3), (x, y + r * 3)], fill=(255, 248, 224, int(a * 0.45)), width=1)

    # 远山 + 尖塔
    _ridge(d, w, h, HORIZON - 0.06, 0.055, PAL["ridge"][0] + (255,), 3)
    _ridge(d, w, h, HORIZON - 0.01, 0.035, PAL["ridge"][1] + (255,), 5)
    twd = ImageDraw.Draw(img)
    for (fx, fh, fw) in [(0.13, 0.13, 0.026), (0.87, 0.16, 0.030), (0.60, 0.09, 0.020)]:
        bx, by = w * fx, hz + h * 0.01
        tw_ = w * fw
        top = by - h * fh
        twd.polygon([(bx - tw_ / 2, by), (bx - tw_ * 0.34, top), (bx, top - tw_ * 1.9),
                     (bx + tw_ * 0.34, top), (bx + tw_ / 2, by)], fill=PAL["ridge"][2] + (250,))
        twd.ellipse([bx - tw_ * 0.12, top + h * 0.055, bx + tw_ * 0.12, top + h * 0.055 + tw_ * 0.6],
                    fill=(248, 190, 96, 150))

    # 地面（顶边为缓曲线，避免直线接缝）
    gh = int(h - hz) + 40
    ground = vgrad((w, gh), PAL["ground"][0] + (255,), PAL["ground"][1] + (255,), gamma=0.75)
    # 中央微光
    gl = rgrad((w, gh), PAL["ground"][0] + (255,), (255, 255, 255, 0))
    ground = Image.blend(ground, gl, 0.18)
    # 苔藓斑块
    rnd = random.Random(55)
    mott = Image.new("RGBA", (w, gh), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mott)
    for _ in range(int(w * gh / 3200)):
        cx, cy = rnd.randrange(w), rnd.randrange(gh)
        r = rnd.uniform(16, 70)
        mdraw.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5],
                      fill=PAL["tuft"] + (rnd.randint(14, 32),))
    for _ in range(int(w * gh / 9000)):
        cx, cy = rnd.randrange(w), rnd.randrange(gh)
        r = rnd.uniform(30, 110)
        mdraw.ellipse([cx - r, cy - r * 0.45, cx + r, cy + r * 0.45],
                      fill=PAL["ground"][1] + (rnd.randint(16, 30),))
    ground.alpha_composite(mott.filter(ImageFilter.GaussianBlur(10)))
    # 碎石
    rnd = random.Random(131)
    for _ in range(int(w * gh / 5200)):
        cx, cy = rnd.randrange(w), rnd.randrange(gh)
        k = cy / max(1, gh)
        r = rnd.uniform(2.5, 6.5) * (0.6 + k * 0.9)
        ground_d = ImageDraw.Draw(ground, "RGBA")
        ground_d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=(12, 20, 24, 150))
        ground_d.ellipse([cx - r, cy - r * 0.72, cx + r * 0.9, cy + r * 0.1], fill=(64, 84, 86, 120))
    # 顶边曲线蒙版
    gm = Image.new("L", (w, gh), 0)
    gmd = ImageDraw.Draw(gm)
    pts = [(0, 26)]
    x = 0
    while x <= w:
        pts.append((x, 26 + math.sin(x / (w / 3.4)) * 9 + math.sin(x / (w / 9.0)) * 4))
        x += max(20, w // 40)
    pts.append((w, gh))
    pts.append((0, gh))
    gmd.polygon(pts, fill=255)
    img.paste(ground, (0, int(hz) - 26), gm)

    # 地平线雾带
    seam = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(seam).rectangle([0, hz - 26, w, hz + 30], fill=(170, 205, 230, 34))
    img.alpha_composite(seam.filter(ImageFilter.GaussianBlur(16)))

    # 草丛（成簇、带明暗、按纵深放大）
    gd = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(77)
    for _ in range(int(w * (h - hz) / 3400)):
        x = rnd.randrange(w)
        y = int(hz + rnd.uniform(30, h - hz))
        k = (y - hz) / max(1, (h - hz))
        base_h = rnd.uniform(6, 15) * (0.6 + k * 1.0)
        n = rnd.randint(3, 6)
        for b in range(n):
            ox = (b - (n - 1) / 2.0) * rnd.uniform(1.8, 3.4)
            tipx = x + ox + rnd.uniform(-3.5, 3.5) * (0.4 + k)
            tipy = y - base_h * rnd.uniform(0.65, 1.15)
            gd.line([(x + ox, y), (tipx, tipy)], fill=(8, 18, 20, 130), width=2)
            gd.line([(x + ox, y), (tipx, tipy)], fill=PAL["tuft"] + (rnd.randint(55, 105),), width=1)
    # 萤火
    for _ in range(max(8, w * h // 60000)):
        x, y = rnd.randrange(w), int(hz + rnd.uniform(40, h - hz))
        r = rnd.uniform(1.0, 2.2)
        gd.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=(255, 228, 160, 26))
        gd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 232, 168, 150))

    # 暗角
    v = Image.new("L", size, 0)
    vd = ImageDraw.Draw(v)
    for i in range(int(h * 0.14)):
        a = int(130 * (1 - i / (h * 0.14)) ** 1.4)
        vd.line([(0, i), (w, i)], fill=a)
    for i in range(int(h * 0.22)):
        a = int(160 * (1 - i / (h * 0.22)) ** 1.4)
        vd.line([(0, h - 1 - i), (w, h - 1 - i)], fill=a)
    for i in range(int(w * 0.16)):
        a = int(110 * (1 - i / (w * 0.16)) ** 1.4)
        vd.line([(i, 0), (i, h)], fill=a)
        vd.line([(w - 1 - i, 0), (w - 1 - i, h)], fill=a)
    dark = Image.new("RGBA", size, (3, 6, 12, 255))
    dark.putalpha(v.filter(ImageFilter.GaussianBlur(22)))
    return Image.alpha_composite(img, dark)


# ---------------------------------------------------------------- 业务部件
def shadow_strip(size):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        a = int(120 * (1 - y / max(1, h - 1)) ** 1.6)
        for x in range(w):
            px[x, y] = (6, 12, 22, a)
    return img


def header_strip(size):
    w, h = size
    img = vgrad(size, NAVY_L, NAVY_D)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - 3, w, h - 1], fill=GOLD)
    d.rectangle([0, 0, w, 2], fill=COPPER)
    for x in range(0, w, max(18, int(h * 2.2))):
        star4(d, x + h * 0.3, h / 2, h * 0.15, (255, 255, 255, 26), inner=0.35)
    return img


def banner(size):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ch = int(h * 0.11)
    pad = 1 if h <= 52 else 2
    pts = [(ch, pad), (w - 1 - ch * 2, pad), (w - 1 - pad, h // 2), (w - 1 - ch * 2, h - 1 - pad), (ch, h - 1 - pad), (pad, h // 2)]
    grad = vgrad((w, h), (58, 104, 146, 255), (18, 38, 62, 255))
    gm = Image.new("L", size, 0)
    ImageDraw.Draw(gm).polygon(pts, fill=255)
    img.paste(grad, (0, 0), gm)
    d = ImageDraw.Draw(img)
    d.polygon(pts, outline=INK, width=3)
    d.line(pts + [pts[0]], fill=GOLD, width=2)
    return img


def bubble(size):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body_h = int(h * 0.80)
    r = int(min(w, body_h) * 0.22)
    d.rounded_rectangle([2, 2, w - 3, body_h], radius=r, fill=MOON, outline=INK, width=3)
    d.rounded_rectangle([7, 7, w - 8, body_h - 5], radius=max(3, r - 5), outline=COPPER, width=2)
    d.polygon([(w * 0.42, body_h - 2), (w * 0.58, body_h - 2), (w * 0.5, h - 3)],
              fill=MOON, outline=INK)
    return img


def vignette(size, filled=True):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(w * 0.10)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=r,
                        fill=(38, 62, 92, 255) if filled else (26, 42, 62, 210))
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=r, outline=INK, width=3)
    d.rounded_rectangle([6, 6, w - 7, h - 7], radius=max(3, r - 5), outline=COPPER, width=2)
    for (cx, cy) in [(13, 13), (w - 14, 13), (13, h - 14), (w - 14, h - 14)]:
        star4(d, cx, cy, max(4, w * 0.035), GOLD, inner=0.32, outline=COPPER_D, ow=1)
    return img


def chest(size, state="idle"):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw, bh = w * 0.92, h * 0.62
    bx, by = (w - bw) / 2, h * 0.36
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(h * 0.05),
                        fill=(92, 56, 32, 255), outline=INK, width=3)
    for i in range(1, 3):
        x = bx + bw * i / 3
        d.line([(x, by + 5), (x, by + bh - 5)], fill=(56, 32, 18, 255), width=3)
    lid_h = bh * 0.34
    if state == "open":
        d.rounded_rectangle([bx - 2, by - lid_h * 1.9, bx + bw + 2, by - lid_h * 0.75],
                            radius=int(h * 0.05), fill=(112, 70, 40, 255), outline=INK, width=3)
        d.rectangle([bx + 6, by - lid_h * 0.6, bx + bw - 6, by - lid_h * 0.45], fill=GOLD_D)
    else:
        d.rounded_rectangle([bx - 2, by - lid_h, bx + bw + 2, by + 5],
                            radius=int(h * 0.055), fill=(112, 70, 40, 255), outline=INK, width=3)
    d.rounded_rectangle([bx - 1, by - 3, bx + bw + 1, by + bh + 1], radius=int(h * 0.045),
                        outline=GOLD, width=3)
    d.rectangle([bx - 1, by - 3, bx + bw + 1, by + 2], fill=GOLD_D)
    lw = bw * 0.13
    d.rounded_rectangle([w / 2 - lw, by + bh * 0.14, w / 2 + lw, by + bh * 0.42],
                        radius=4, fill=GOLD, outline=INK, width=2)
    d.ellipse([w / 2 - lw * 0.3, by + bh * 0.22, w / 2 + lw * 0.3, by + bh * 0.36], fill=INK)
    if state == "idle":
        star4(d, w * 0.16, by + bh * 0.10, w * 0.06, (255, 236, 180, 210), inner=0.35)
    return img


def lifebar(size, monster=False):
    w, h = size
    img = bar_track(size, radius=h // 2)
    d = ImageDraw.Draw(img)
    r = h * 0.30
    cx, cy = h * 0.60, h / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 34, 52, 255), outline=COPPER, width=2)
    hr = r * 0.62
    d.ellipse([cx - hr, cy - hr * 0.95, cx - hr * 0.05, cy + hr * 0.15], fill=(214, 58, 58, 255))
    d.ellipse([cx + hr * 0.05 - hr, cy - hr * 0.95, cx + hr * 0.05, cy + hr * 0.15], fill=(214, 58, 58, 255))
    d.polygon([(cx - hr, cy - hr * 0.05), (cx + hr, cy - hr * 0.05), (cx, cy + hr)], fill=(214, 58, 58, 255))
    return img


# ---------------------------------------------------------------- 任务表
import glob

DIRS = [SPR, UI, os.path.join(ROOT, "Assets", "Images"),
        os.path.join(ROOT, "Assets", "Resources", "heroes"),
        os.path.join(ROOT, "Assets", "Resources", "monsters"),
        os.path.join(ROOT, "Assets", "Resources", "world")]


def resolve(name):
    hits = []
    for d in DIRS + glob.glob(os.path.join(ROOT, "Assets", "Resources", "weapons", "*")):
        p = os.path.join(d, name)
        if os.path.exists(p):
            hits.append(p)
    return hits


def jobs():
    J = {}
    def add(name, fn):
        J[name] = fn

    add("box.png",              lambda p: panel(orig_size(p), 32, "moon"))
    add("boxWhite.png",         lambda p: panel(orig_size(p), 80, "moon", radius=10))
    add("popup_slice9.png",     lambda p: panel(orig_size(p), 98, "moon", radius=26))
    add("slice9_popup.png",     lambda p: panel(orig_size(p), 60, "moon", radius=22))
    add("popup_weapons.png",    lambda p: panel(orig_size(p), 70, "moon", radius=26))
    add("popup_weapons_small.png", lambda p: panel(orig_size(p), 70, "moon", radius=26))
    add("box_header.png",       lambda p: banner(orig_size(p)))
    add("box_shadow.png",       lambda p: shadow_strip(orig_size(p)))
    add("Background.png",       lambda p: panel(orig_size(p), 10, "moon", radius=4, ornament=False))
    add("InputFieldBackground.png", lambda p: panel(orig_size(p), 10, "moon", radius=4, ornament=False))
    add("header_footer.png",    lambda p: banner(orig_size(p)))
    add("UI_mission_banner.png", lambda p: banner(orig_size(p)))
    add("UI_bubble.png",        lambda p: bubble(orig_size(p)))

    add("play_button.png",      lambda p: round_button(orig_size(p), "play"))
    add("btn_red.png",          lambda p: button(orig_size(p), 0, "danger"))
    add("btn_buy.png",          lambda p: button(orig_size(p), 0, "gold"))
    add("btn_buy_large.png",    lambda p: button(orig_size(p), 40, "gold"))
    add("btn_blue_large.png",   lambda p: button(orig_size(p), 50, "secondary"))
    add("btn_disabled.png",     lambda p: button(orig_size(p), 0, "disabled"))
    add("btn_upgrade.png",      lambda p: button(orig_size(p), 0, "primary"))
    add("btn_selection.png",    lambda p: button(orig_size(p), 0, "gold"))
    add("btn_close.png",        lambda p: close_button(orig_size(p)))
    add("btn_options.png",      lambda p: icon(orig_size(p), "star", ring=NAVY))
    add("btn_pause.png",        lambda p: icon(orig_size(p), "clock", ring=NAVY))
    add("btn_icon_music.png",   lambda p: icon(orig_size(p), "star", ring=NAVY))
    add("btn_icon_music_off.png", lambda p: icon(orig_size(p), "star", ring=(70, 78, 92, 255)))
    add("btn_icon_sound.png",   lambda p: icon(orig_size(p), "star", ring=NAVY))
    add("btn_icon_sound_off.png", lambda p: icon(orig_size(p), "star", ring=(70, 78, 92, 255)))
    add("btn_icon_battery.png", lambda p: icon(orig_size(p), "star", ring=TEAL_D))
    add("btn_icon_twitter.png", lambda p: icon(orig_size(p), "star", ring=NAVY))
    add("tab_selected.png",     lambda p: button(orig_size(p), 0, "gold"))
    add("UI_btn_heroes.png",    lambda p: icon(orig_size(p), "heart", ring=NAVY))
    add("UI_btn_weapons.png",   lambda p: icon(orig_size(p), "sword", ring=NAVY))
    add("UI_btn_shop.png",      lambda p: icon(orig_size(p), "coin", ring=NAVY))

    add("UI_lifebar.png",         lambda p: lifebar(orig_size(p)))
    add("UI_lifebar_monster.png", lambda p: lifebar(orig_size(p)))
    add("KT_bar_bg.png",          lambda p: bar_track(orig_size(p), radius=8))
    add("KT_bar_box.png",         lambda p: panel(orig_size(p), 60, "moon", radius=12))
    add("KT_bar_fill.png",        lambda p: bar_fill(orig_size(p), radius=8))
    add("roundedBar.png",         lambda p: bar_track(orig_size(p), radius=10))
    add("heart_full.png",         lambda p: icon(orig_size(p), "heart"))
    add("heart_empty.png",        lambda p: icon(orig_size(p), "heart").point(lambda v: int(v * 0.45)))
    add("heart_ico.png",          lambda p: icon(orig_size(p), "heart"))

    for nm, gl in [("coin_ico", "coin"), ("lootCoin", "coin"), ("ruby_ico", "ruby"),
                   ("lootRuby", "ruby"), ("lootKey", "key"), ("lootLife", "heart"),
                   ("lootKingToken", "star"), ("attack_ico", "sword"), ("UI_ads_ico", "video"),
                   ("UI_surprise_ico", "question")]:
        add(nm + ".png", (lambda g: (lambda p: icon(orig_size(p), g)))(gl))
    add("UI_price_badge.png",  lambda p: icon(orig_size(p), "coin", ring=NAVY))
    add("UI_round_counter.png", lambda p: icon(orig_size(p), "coin", ring=NAVY))
    add("UI_mini_arrow.png",   lambda p: icon(orig_size(p), "chevron"))
    add("UI_pink_arrow.png",   lambda p: icon(orig_size(p), "chevron"))
    add("target.png",          lambda p: icon(orig_size(p), "star"))
    add("target_critical.png", lambda p: icon(orig_size(p), "star"))
    add("target_weak.png",     lambda p: icon(orig_size(p), "star"))
    add("target_triangle.png", lambda p: icon(orig_size(p), "up"))
    add("UI_reward_questionmark.png", lambda p: icon(orig_size(p), "question"))
    add("notification.png",    lambda p: icon(orig_size(p), "star", ring=NAVY))
    add("upgrade_available.png", lambda p: icon(orig_size(p), "up", fg=TEAL))
    add("ico_skull_border.png", lambda p: icon(orig_size(p), "question"))
    add("key_chest_big.png",   lambda p: icon(orig_size(p), "key"))
    add("key_chest_big_overlay.png", lambda p: icon(orig_size(p), "key"))
    add("UI_lock_on.png",      lambda p: icon(orig_size(p), "lock"))
    add("UI_lock_off.png",     lambda p: icon(orig_size(p), "lock"))
    add("UI_weaponStatusClock.png", lambda p: icon(orig_size(p), "clock"))
    add("UI_weaponStatusRepair.png", lambda p: icon(orig_size(p), "wrench"))
    add("UI_weaponStatusUpgrade.png", lambda p: icon(orig_size(p), "up", fg=TEAL))
    add("UI_weaponStatusOverlay.png", lambda p: icon(orig_size(p), "clock"))
    add("UI_chest_ico.png",    lambda p: chest(orig_size(p), "idle"))
    add("UI_chest_box.png",    lambda p: panel(orig_size(p), 40, "moon", radius=18))

    for nm, st in [("chest_big_idle", "idle"), ("chest_big_hit", "idle"), ("chest_big_open", "open"),
                   ("chest_medium_idle", "idle"), ("chest_medium_hit", "idle"), ("chest_medium_open", "open"),
                   ("chest_pub_idle", "idle"), ("chest_pub_hit", "idle"), ("chest_pub_open", "open"),
                   ("chest_pub_sleep", "idle"), ("chest_small_idle", "idle"), ("chest_small_hit", "idle"),
                   ("chest_small_open", "open"), ("chest_small_idle_d1", "idle"),
                   ("chest_small_hit_d1", "idle"), ("chest_locked-idle", "idle")]:
        add(nm + ".png", (lambda s: (lambda p: chest(orig_size(p), s)))(st))

    add("UI_vignette.png",       lambda p: vignette(orig_size(p), True))
    add("UI_vignette_empty.png", lambda p: vignette(orig_size(p), False))
    add("UI_weapon_bg.png",      lambda p: panel(orig_size(p), 60, "moon", radius=20))
    add("UI_weapon_selected_bg.png", lambda p: panel(orig_size(p), 60, "moon", radius=20))
    add("UI_weapon_empty.png",   lambda p: panel(orig_size(p), 30, "moon", radius=18))
    add("UI_weapon_attk_box.png", lambda p: panel(orig_size(p), 16, "moon", radius=8, ornament=False))
    add("UI_weapon_menu_bg.png", lambda p: panel(orig_size(p), 40, "moon", radius=14))
    add("UI_cards_mini.png",     lambda p: panel(orig_size(p), 12, "moon", radius=6, ornament=False))
    for nm in ["cards_item_boost", "cards_item_hero", "cards_item_long",
               "cards_item_medium", "cards_item_short", "cards_item_reward"]:
        add(nm + ".png", lambda p: panel(orig_size(p), 8, "moon", radius=4, ornament=False))

    add("bg_w00.png", lambda p: backdrop(orig_size(p), "meadow"))
    add("bg_w00_menu.png", lambda p: backdrop(orig_size(p), "meadow"))
    add("bg_w01.png", lambda p: backdrop(orig_size(p), "cavern"))
    add("bg_w02.png", lambda p: backdrop(orig_size(p), "ember"))
    for nm in ["bg_w00_overlayTop.png", "bg_w01_overlayTop.png", "bg_w02_overlayTop.png"]:
        add(nm, lambda p: shadow_strip(orig_size(p)).transpose(Image.FLIP_TOP_BOTTOM))
    for nm in ["bg_w00_overlayBottom.png", "bg_w02_overlayBottom.png"]:
        add(nm, lambda p: shadow_strip(orig_size(p)))
    return J


def run(pattern=None, save=True):
    J = jobs()
    prev = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
    os.makedirs(prev, exist_ok=True)
    done, miss = 0, []
    for name, fn in J.items():
        if pattern and pattern.lower() not in name.lower():
            continue
        paths = resolve(name)
        if not paths:
            miss.append(name)
            continue
        for p in paths:
            try:
                img = fn(p)
            except Exception as e:
                print("[FAIL]", name, e)
                continue
            if save:
                emit(p, img)
            else:
                tag = os.path.basename(os.path.dirname(p))
                img.save(os.path.join(prev, tag + "_" + name))
            done += 1
    print("完成", done, "缺失", miss[:10])


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--preview":
        run(sys.argv[2] if len(sys.argv) > 2 else None, save=False)
    else:
        run(arg or None, save=True)
