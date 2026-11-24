# -*- coding: utf-8 -*-
"""补最后一轮：武器面板图标、英雄头像、看广告得红宝石、金币掉落、世界背景菜单版。"""
import os, sys, glob, random
from PIL import Image, ImageDraw, ImageFilter
from kit import *
from finish import grade
import rewards
import build as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WKIND = {"01": "sword", "02": "dagger", "03": "axe", "04": "bow", "04Bomb": "bomb",
         "05": "staff", "06": "hammer", "07": "spear", "08": "scythe", "09": "mace"}


def bomb(d, w, h, ow):
    cx, cy = w * 0.5 + w * 0.04, h * 0.56
    s = min(w, h) * 0.34
    d.ellipse([cx - s * 0.86, cy - s * 0.86, cx + s * 0.86, cy + s * 0.86], fill=(42, 54, 72, 255), outline=INK, width=ow)
    d.ellipse([cx - s * 0.58, cy - s * 0.62, cx - s * 0.06, cy - s * 0.10], fill=(96, 116, 140, 210))
    # 引线
    d.line([(cx + s * 0.42, cy - s * 0.70), (cx + s * 0.72, cy - s * 1.10)], fill=INK, width=ow * 2 + 2)
    d.line([(cx + s * 0.42, cy - s * 0.70), (cx + s * 0.72, cy - s * 1.10)], fill=COPPER, width=ow + 1)
    star4(d, cx + s * 0.80, cy - s * 1.18, s * 0.26, GOLD_L, inner=0.34)
    # 塞子
    d.rounded_rectangle([cx - s * 0.22, cy - s * 1.00, cx + s * 0.22, cy - s * 0.80], radius=2, fill=GOLD_D, outline=INK, width=max(1, ow // 2))


def crack(img):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(7)
    x, y = w * 0.28, h * 0.18
    for _ in range(7):
        nx, ny = x + rnd.uniform(w * 0.05, w * 0.13), y + rnd.uniform(h * 0.06, h * 0.14)
        d.line([(x, y), (nx, ny)], fill=(10, 16, 28, 210), width=max(2, int(w * 0.022)))
        d.line([(x, y), (nx, ny)], fill=(120, 140, 165, 120), width=1)
        x, y = nx, ny
        if x > w * 0.9 or y > h * 0.9:
            break
    return img


def play_badge(img):
    w, h = img.size
    r = min(w, h) * 0.485
    cx, cy = w / 2, h / 2
    bx, by, br = cx + r * 0.58, cy + r * 0.58, r * 0.36
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([bx - br * 1.25, by - br * 1.25, bx + br * 1.25, by + br * 1.25], fill=(6, 12, 22, 190))
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=TEAL_D, outline=INK, width=max(2, int(br * 0.22)))
    d.polygon([(bx - br * 0.30, by - br * 0.46), (bx + br * 0.48, by), (bx - br * 0.30, by + br * 0.46)],
              fill=(236, 255, 250, 255), outline=INK)
    return img


def main():
    n = 0
    # 1) 武器面板图标 → 新徽章
    for p in sorted(glob.glob(os.path.join(ROOT, "Assets/Resources/weapons/*/UI_w_*.png"))):
        name = os.path.basename(p)
        key = name.replace("UI_w_weapon", "").replace(".png", "").replace("_broken", "")
        kind = WKIND.get(key, "sword")
        size = Image.open(p).size
        def drawer(d, w, h, ow, k=kind):
            if k == "bomb":
                bomb(d, w, h, ow)
            else:
                rewards.glyph_weapon(d, w, h, ow, k)

        out = rewards.medallion(size, drawer)
        if "_broken" in name:
            base = out.convert("RGBA")
            base = grade(base, hue_shift=0.0, sat=0.45, strength=0.8)
            out = crack(base)
        out.putalpha(out.split()[3])
        out.save(p)
        n += 1
    print("武器面板图标", n)

    # 2) 看广告得红宝石
    p = os.path.join(ROOT, "Assets/Resources/UI/shopProductRubiesVideo.png")
    if os.path.exists(p):
        size = Image.open(p).size
        out = rewards.medallion(size, rewards.glyph_ruby)
        out = play_badge(out)
        out.save(p)
        print("shopProductRubiesVideo ok")

    # 3) 英雄头像调色（与已在用的角色精灵统一）
    m = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "Assets/Resources/heroes/UI_hero*.png"))):
        im = Image.open(p).convert("RGBA")
        a = im.split()[3]
        out = grade(im, hue_shift=0.06, sat=0.98, strength=0.5)
        out.putalpha(a)
        out.save(p)
        m += 1
    print("英雄头像", m)

    # 4) 金币掉落
    k = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "Assets/Sprites/lootCoinsPack*.png"))):
        im = Image.open(p).convert("RGBA")
        a = im.split()[3]
        out = grade(im, hue_shift=-0.02, sat=1.12, strength=0.6)
        out.putalpha(a)
        out.save(p)
        k += 1
    print("金币掉落", k)

    # 5) 世界背景菜单版
    for nm, var in [("bg_w01_menu.png", "cavern"), ("bg_w02_menu.png", "ember")]:
        p = os.path.join(ROOT, "Assets/Resources/world", nm)
        if not os.path.exists(p):
            print("miss", nm)
            continue
        size = Image.open(p).size
        B.backdrop(size, var).save(p)
        print(nm, size, "ok")


if __name__ == "__main__":
    main()
