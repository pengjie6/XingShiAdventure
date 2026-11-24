# -*- coding: utf-8 -*-
"""新品牌：闯越奇境解锁征途 —— 星辉罗盘徽记 + 行楷字标（全程序化，无水印）。"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from kit import *

FONT = "C:/Windows/Fonts/FZYTK.TTF"
TEXT = "闯越奇境解锁征途"


def star_path(cx, cy, r, inner=0.26, points=4, rot=-90):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180.0 / points)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def emblem(size, s=None):
    """圆盘罗盘徽记（含外发光），返回 RGBA。"""
    w, h = size
    s = s or min(w, h)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    cx, cy = w / 2, h / 2
    R = s * 0.44

    # 外发光
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - R * 1.12, cy - R * 1.12, cx + R * 1.12, cy + R * 1.12], fill=(247, 186, 92, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s * 0.05)))

    d = ImageDraw.Draw(img)
    # 外环（深浅两圈金）
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=COPPER_D)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=max(2, int(s * 0.012)))
    d.ellipse([cx - R * 0.955, cy - R * 0.955, cx + R * 0.955, cy + R * 0.955],
              outline=GOLD, width=max(3, int(s * 0.022)))
    d.ellipse([cx - R * 0.86, cy - R * 0.86, cx + R * 0.86, cy + R * 0.86],
              outline=GOLD_L, width=max(1, int(s * 0.008)))

    # 内盘：深空径向
    inner_r = R * 0.845
    disc = rgrad((int(inner_r * 2), int(inner_r * 2)), (30, 58, 96, 255), (8, 15, 28, 255))
    dm = Image.new("L", disc.size, 0)
    ImageDraw.Draw(dm).ellipse([0, 0, disc.size[0] - 1, disc.size[1] - 1], fill=255)
    img.paste(disc, (int(cx - inner_r), int(cy - inner_r)), dm)
    d = ImageDraw.Draw(img)

    # 罗盘刻度
    for k in range(48):
        a = math.radians(k * 7.5)
        r1 = inner_r * (0.80 if k % 4 else 0.72)
        r2 = inner_r * 0.90
        wdt = 2 if k % 4 == 0 else 1
        col = GOLD if k % 4 == 0 else (196, 150, 90, 120)
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], fill=col, width=wdt)

    # 星轨圆
    d.ellipse([cx - inner_r * 0.70, cy - inner_r * 0.70, cx + inner_r * 0.70, cy + inner_r * 0.70],
              outline=(90, 150, 210, 90), width=2)
    d.arc([cx - inner_r * 0.92, cy - inner_r * 0.92, cx + inner_r * 0.92, cy + inner_r * 0.92],
          200, 340, fill=GOLD_L, width=2)

    # 主星（四芒）
    sr = inner_r * 0.56
    star = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(star)
    sd.polygon(star_path(cx, cy, sr, 0.24), fill=(255, 226, 150, 255), outline=COPPER_D)
    sd.polygon(star_path(cx, cy, sr * 0.52, 0.30), fill=(255, 250, 226, 255))
    # 星芯光
    sd.ellipse([cx - sr * 0.16, cy - sr * 0.16, cx + sr * 0.16, cy + sr * 0.16], fill=WHITE)
    img.alpha_composite(star)
    img.alpha_composite(star.filter(ImageFilter.GaussianBlur(s * 0.02)))

    # 四颗小宝石
    d = ImageDraw.Draw(img)
    for k in range(4):
        a = math.radians(45 + k * 90)
        gx, gy = cx + inner_r * 0.60 * math.cos(a), cy + inner_r * 0.60 * math.sin(a)
        gr = inner_r * 0.075
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=TEAL, outline=INK, width=max(1, int(s * 0.006)))
        d.ellipse([gx - gr * 0.4, gy - gr * 0.5, gx + gr * 0.1, gy - gr * 0.05], fill=(210, 255, 250, 220))
    return img


def wordmark(width, font_size, text=TEXT, spacing=0.10, gradient=True):
    f = ImageFont.truetype(FONT, font_size)
    tmp = Image.new("RGBA", (10, 10))
    td = ImageDraw.Draw(tmp)
    widths, heights = [], []
    for ch in text:
        bb = td.textbbox((0, 0), ch, font=f)
        widths.append(bb[2] - bb[0])
        heights.append(bb[3] - bb[1])
    gap = int(font_size * spacing)
    total = sum(widths) + gap * (len(text) - 1)
    H = int(max(heights) * 1.55)
    img = Image.new("RGBA", (total + 8, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 4
    for i, ch in enumerate(text):
        bb = td.textbbox((0, 0), ch, font=f)
        d.text((x - bb[0], (H - (bb[3] - bb[1])) / 2 - bb[1]), ch, font=f, fill=(255, 255, 255, 255))
        x += widths[i] + gap

    # 描边 + 渐变金填充
    mask = img.split()[3]
    outline = mask.filter(ImageFilter.MaxFilter(9)).point(lambda v: 255 if v > 90 else 0)
    ol = Image.new("RGBA", img.size, (46, 26, 12, 255))
    ol.putalpha(outline)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(ol)
    # 外发光（两层）+ 深色投影，保证在任何底面上都能看清
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for blur, alpha in ((int(font_size * 0.22) | 1, 70), (int(font_size * 0.10) | 1, 130)):
        gl = Image.new("RGBA", img.size, (255, 186, 84, alpha))
        gl.putalpha(outline.filter(ImageFilter.GaussianBlur(blur)))
        base.alpha_composite(gl)
    sh = Image.new("RGBA", img.size, (8, 12, 20, 210))
    sh.putalpha(outline.filter(ImageFilter.GaussianBlur(max(2, int(font_size * 0.05)))))
    base.alpha_composite(ImageChops.offset(sh, 0, max(2, int(font_size * 0.07))))
    base.alpha_composite(ol)

    fill = vgrad(img.size, (255, 246, 208, 255), (226, 152, 54, 255), gamma=1.05) if gradient else Image.new("RGBA", img.size, GOLD)
    fill.putalpha(mask)
    base.alpha_composite(fill)

    if width and base.width > width:
        k = width / base.width
        base = base.resize((int(base.width * k), int(base.height * k)), Image.LANCZOS)
    return base


def make_logo(size, layout="stack"):
    """stack: 徽记在上、字标在下（主页用）；card: 深色卡片底（Boot 用）"""
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    if layout == "card":
        card = rgrad(size, (24, 46, 74, 255), (7, 12, 22, 255))
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(w * 0.10), fill=255)
        img.paste(card, (0, 0), mask)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([2, 2, w - 3, h - 3], radius=int(w * 0.10), outline=INK, width=6)
        d.rounded_rectangle([10, 10, w - 11, h - 11], radius=int(w * 0.09), outline=COPPER, width=4)
        d.rounded_rectangle([18, 18, w - 19, h - 19], radius=int(w * 0.085), outline=GOLD_L, width=2)
        for (cx, cy) in [(34, 34), (w - 35, 34), (34, h - 35), (w - 35, h - 35)]:
            star4(d, cx, cy, 12, GOLD, inner=0.32, outline=COPPER_D, ow=2)

    if layout == "card":
        em_s = int(w * 0.52)
        em = emblem((em_s, em_s))
        wm = wordmark(int(w * 0.86), int(w * 0.145))
        gap = int(h * 0.035)
        total = em_s + gap + wm.height
        y0 = int((h - total) / 2)
        img.alpha_composite(em, ((w - em_s) // 2, y0))
        img.alpha_composite(wm, ((w - wm.width) // 2, y0 + em_s + gap))
    else:
        em_s = int(h * 0.62)
        em = emblem((em_s, em_s))
        wm = wordmark(int(w * 0.96), int(h * 0.155))
        gap = int(h * 0.035)
        total = em_s + gap + wm.height
        y0 = int((h - total) / 2)
        img.alpha_composite(em, ((w - em_s) // 2, y0))
        img.alpha_composite(wm, ((w - wm.width) // 2, y0 + em_s + gap))
    return img


if __name__ == "__main__":
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
    os.makedirs(out, exist_ok=True)
    targets = [("Branding/GameLogo.png", "card"), ("Branding/GameLogoHome.png", "stack")]
    for rel, layout in targets:
        p = os.path.join(root, "Assets", "Resources", rel)
        with Image.open(p) as im:
            size = im.size
        img = make_logo(size, layout)
        img.save(os.path.join(out, "logo_" + os.path.basename(p)))
        print(rel, size, "ok")
