# -*- coding: utf-8 -*-
"""程序化 UI 素材生成工具（零积分 / 无水印）。

主题：星辉远征 —— 深墨蓝夜空 + 琥珀金 + 青玉 + 铜金双线边 + 星芒/罗盘纹饰
与旧主题（奶白圆角卡 + 亮粉 + 白描边扁平）完全区分。

所有输出尺寸严格沿用原图尺寸，9-slice 边框也沿用 .meta 里的 spriteBorder，
因此替换后不会改变任何 RectTransform / 资源引用（GUID 不变）。
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

# ---------------------------------------------------------------- 调色板
INK      = (10, 20, 34, 255)
NAVY     = (18, 42, 68, 255)
NAVY_D   = (12, 27, 45, 255)
NAVY_L   = (30, 62, 96, 255)
MOON     = (233, 239, 247, 255)
MOON_D   = (203, 213, 229, 255)
MOON_DD  = (168, 182, 204, 255)
GOLD     = (244, 181, 76, 255)
GOLD_L   = (255, 217, 145, 255)
GOLD_D   = (176, 108, 38, 255)
COPPER   = (196, 132, 66, 255)
COPPER_D = (124, 78, 38, 255)
TEAL     = (45, 205, 184, 255)
TEAL_D   = (17, 112, 102, 255)
CRIMSON  = (190, 62, 46, 255)
CRIM_D   = (120, 34, 26, 255)
WHITE    = (255, 255, 255, 255)
GREY     = (140, 152, 170, 255)


def clamp(v, a=0, b=255):
    return max(a, min(b, int(v)))


def mix(c1, c2, k):
    return tuple(clamp(c1[i] + (c2[i] - c1[i]) * k) for i in range(4))


def alpha(c, a):
    return (c[0], c[1], c[2], clamp(a if a <= 1 else a))


# ---------------------------------------------------------------- 基础绘制
def vgrad(size, c1, c2, gamma=1.0):
    w, h = size
    g = Image.new("RGBA", (1, h))
    px = g.load()
    for y in range(h):
        k = (y / max(1, h - 1)) ** gamma
        px[0, y] = mix(c1, c2, k)
    return g.resize((w, h), Image.BICUBIC)


def rgrad(size, c1, c2):
    """径向渐变，中心 c1 边缘 c2"""
    w, h = size
    small = (max(8, w // 4), max(8, h // 4))
    g = Image.new("RGBA", small)
    px = g.load()
    cx, cy = small[0] / 2.0, small[1] / 2.0
    r = math.hypot(cx, cy)
    for y in range(small[1]):
        for x in range(small[0]):
            d = math.hypot(x - cx, y - cy) / r
            px[x, y] = mix(c1, c2, min(1.0, d ** 1.2))
    return g.resize((w, h), Image.BICUBIC)


def rr_mask(size, radius, inset=0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([inset, inset, size[0] - 1 - inset, size[1] - 1 - inset],
                        radius=radius, fill=255)
    return m


def cut_mask(size, chamfer=0, radius=0, inset=0):
    """斜切角（chamfer>0）或圆角"""
    if chamfer <= 0:
        return rr_mask(size, radius, inset)
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    w, h = size
    c = chamfer
    d.polygon([(inset + c, inset), (w - 1 - inset - c, inset),
               (w - 1 - inset, inset + c), (w - 1 - inset, h - 1 - inset - c),
               (w - 1 - inset - c, h - 1 - inset), (inset + c, h - 1 - inset),
               (inset, h - 1 - inset - c), (inset, inset + c)], fill=255)
    return m


def stroke_of(mask, width, color):
    """由蒙版外扩得到描边层"""
    grown = mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    grown = grown.point(lambda v: 255 if v > 100 else 0)
    inner = mask.filter(ImageFilter.MinFilter(width * 2 + 1))
    ring = ImageChops.subtract(grown, inner)
    layer = Image.new("RGBA", mask.size, color)
    layer.putalpha(ring)
    return layer


def paper_texture(size, base=MOON, seed=3, strength=0.10):
    rnd = random.Random(seed)
    w, h = size
    img = Image.new("RGBA", size, base)
    noise = Image.new("L", (w, h))
    px = noise.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = rnd.randint(0, 255)
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    tex = Image.merge("RGBA", (noise, noise, noise, Image.new("L", size, 255)))
    img = Image.blend(img, tex, strength * 0.5)
    # 细纤维
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(w * h // 900):
        x, y = rnd.randrange(w), rnd.randrange(h)
        ln = rnd.randint(6, 26)
        a = rnd.randint(6, 16)
        d.line([(x, y), (x + ln, y + rnd.choice([-1, 0, 1]))], fill=(150, 130, 100, a), width=1)
    return img


def add_glow(img, mask, color, radius=6, alpha_k=0.55):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gl = mask.filter(ImageFilter.GaussianBlur(radius))
    layer = Image.new("RGBA", img.size, color)
    layer.putalpha(gl.point(lambda v: int(v * alpha_k)))
    g.alpha_composite(layer)
    g.alpha_composite(img)
    return g


def star4(d, cx, cy, r, color=(0, 0, 0, 0), inner=0.28, points=4, rot=-90, outline=None, ow=1):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180.0 / points)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=color, outline=outline)
    if outline and ow:
        d.line(pts + [pts[0]], fill=outline, width=ow)


def compass_ornament(d, cx, cy, r, color=COPPER, width=2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45],
              outline=color, width=width)
    for k in range(4):
        a = math.radians(45 + k * 90)
        d.line([(cx + r * 0.45 * math.cos(a), cy + r * 0.45 * math.sin(a)),
                (cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a))], fill=color, width=width)
