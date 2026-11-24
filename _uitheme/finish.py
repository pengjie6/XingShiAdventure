# -*- coding: utf-8 -*-
"""补齐剩余 UI 图（商店/奖励/宝箱），并对玩法美术做统一"星辉夜航"调色。"""
import os, sys, glob, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
from kit import *
from build import orig_size, emit, resolve, button, panel, chest, icon, bar_fill, vignette
import build as B

ROOT = B.ROOT


def coin_stack(size, n=3):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cw, ch = w * 0.72, h * 0.20
    for i in range(n):
        cx = w / 2 + (i - n // 2) * w * 0.05
        cy = h * 0.82 - i * ch * 0.75
        d.ellipse([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2],
                  fill=GOLD, outline=INK, width=max(2, int(w * 0.03)))
        d.ellipse([cx - cw * 0.35, cy - ch * 0.28, cx + cw * 0.35, cy + ch * 0.28],
                  outline=GOLD_D, width=max(1, int(w * 0.02)))
    return img


def gem_cluster(size, n=3, color=(226, 74, 120, 255)):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(n):
        cx = w * (0.30 + 0.22 * i)
        cy = h * (0.58 - 0.10 * (i % 2))
        s = min(w, h) * (0.34 if i == 1 else 0.24)
        pts = [(cx, cy - s), (cx + s * 0.8, cy - s * 0.1), (cx, cy + s), (cx - s * 0.8, cy - s * 0.1)]
        d.polygon(pts, fill=color, outline=INK)
        d.line(pts + [pts[0]], fill=INK, width=max(2, int(w * 0.025)))
        d.polygon([(cx, cy - s), (cx + s * 0.38, cy - s * 0.06), (cx, cy + s * 0.45),
                   (cx - s * 0.38, cy - s * 0.06)], fill=(255, 170, 200, 255))
    return img


def reward_icon(size, kind):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    # 背景圆盘
    d = ImageDraw.Draw(img)
    r = min(w, h) * 0.46
    d.ellipse([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r], fill=(24, 44, 70, 255))
    d.ellipse([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r], outline=COPPER, width=max(2, int(w * 0.03)))
    inner = icon((int(w * 0.66), int(h * 0.66)), kind)
    img.alpha_composite(inner, (int(w * 0.17), int(h * 0.17)))
    return img


def themed_chest(size, variant=0):
    img = chest(size, "idle")
    if variant:
        d = ImageDraw.Draw(img)
        w, h = size
        col = [(80, 200, 180, 255), (200, 90, 140, 255), (240, 190, 90, 255)][variant % 3]
        d.ellipse([w * 0.46, h * 0.30, w * 0.54, h * 0.36], fill=col, outline=INK)
    return img


# ---------------------------------------------------------------- 调色
def grade(img, hue_shift=0.06, sat=1.06, shadow_tint=(18, 34, 62), hilite_tint=(255, 214, 150),
          strength=0.55):
    """把旧配色往"夜空蓝 + 琥珀金"推，保留剪影可辨识度。"""
    im = img.convert("RGBA")
    a = im.split()[3]
    hsv = im.convert("RGB").convert("HSV")
    hh, ss, vv = hsv.split()
    hh = hh.point(lambda x: (x + int(255 * hue_shift)) % 256)
    ss = ss.point(lambda x: min(255, int(x * sat)))
    rgb = Image.merge("HSV", (hh, ss, vv)).convert("RGB")

    # 阴影偏冷、亮部偏暖
    lum = rgb.convert("L")
    sh = Image.new("RGB", rgb.size, shadow_tint)
    hi = Image.new("RGB", rgb.size, hilite_tint)
    cold = ImageChops.multiply(rgb, sh.point(lambda x: 255))  # 占位，实际用混合
    out = Image.composite(hi, rgb, lum.point(lambda x: 255 if x > 200 else 0))
    out = Image.composite(out, Image.blend(out, sh, 0.35), lum.point(lambda x: 255 if x < 60 else 0))
    res = Image.blend(rgb, out, strength)
    res = ImageEnhance.Contrast(res).enhance(1.04)
    res.putalpha(a)
    return res


def run():
    # ---- 补 UI 图标
    ui = os.path.join(ROOT, "Assets", "Resources", "UI")
    jobs = []
    for i in (1, 2, 3):
        jobs.append((f"shopProductCoins{i}.png", lambda p, n=i: coin_stack(orig_size(p), 1 + n)))
    for i in (1, 2, 3, 4, 5):
        jobs.append((f"shopProductRubies{i}.png", lambda p, n=i: gem_cluster(orig_size(p), 2 + (n % 3))))
    for nm, var in [("chestAds", 0), ("chestPremium1", 1), ("chestPremium2", 2),
                    ("chestTimedFree", 0), ("chestTimedFreeSleep", 1)]:
        jobs.append((nm + ".png", (lambda v: (lambda p: themed_chest(orig_size(p), v)))(var)))
    for i in (1, 2, 3):
        jobs.append((f"UI_shop_chest0{i}.png", (lambda v: (lambda p: themed_chest(orig_size(p), v)))(i)))
    for nm, kind in [("UI_reward_lootCoin", "coin"), ("UI_reward_lootRuby", "ruby"),
                     ("UI_reward_InstantHeal", "heart"), ("UI_reward_InstantRepair", "wrench")]:
        jobs.append((nm + ".png", (lambda k: (lambda p: reward_icon(orig_size(p), k)))(kind)))

    cnt = 0
    for name, fn in jobs:
        for p in resolve(name):
            img = fn(p)
            emit(p, img)
            cnt += 1
    print("UI 补齐", cnt)

    # ---- 玩法美术统一调色（跳过已重绘的 UI）
    skip_prefix = ("UI_", "btn_", "box", "popup", "slice9", "bg_w0", "chest_", "loot", "key_chest",
                   "card", "heart_", "coin_ico", "ruby_ico", "tab_", "header_footer", "InputField",
                   "Background", "play_button", "roundedBar", "shadow", "target", "attack_ico",
                   "notification", "upgrade_available", "ico_skull", "whiteSquare", "sparkling",
                   "square_round", "KT_bar", "rays", "weapon01Shape", "weapon02Shape",
                   "weapon03Shape", "weapon04Shape", "weapon04BombShape", "weapon05Shape",
                   "weapon06Shape", "weapon07Shape", "weapon08Shape", "weapon09Shape")
    graded = 0
    roots = [os.path.join(ROOT, "Assets", "Sprites"),
             os.path.join(ROOT, "Assets", "Resources", "monsters"),
             os.path.join(ROOT, "Assets", "Resources", "heroes"),
             os.path.join(ROOT, "Assets", "Resources", "mapobjects"),
             os.path.join(ROOT, "Assets", "Resources", "weapons"),
             os.path.join(ROOT, "Assets", "Images")]
    for r in roots:
        if not os.path.isdir(r):
            continue
        for p in glob.glob(os.path.join(r, "**", "*.png"), recursive=True):
            n = os.path.basename(p)
            if n.startswith(skip_prefix):
                continue
            try:
                with Image.open(p) as im:
                    if im.mode not in ("RGBA", "RGB"):
                        continue
                    src = im.convert("RGBA")
                if src.getbbox() is None:
                    continue
                out = grade(src)
                out.save(p, optimize=True)
                graded += 1
            except Exception as e:
                print("skip", n, e)
    print("玩法美术调色", graded)


if __name__ == "__main__":
    run()
