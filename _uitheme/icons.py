# -*- coding: utf-8 -*-
"""按 WeaponConfigs 的真实武器类型，用局内武器图重做面板/奖励图标（圆盘徽章）。"""
import os, sys, glob
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rewards
from kit import INK

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WROOT = os.path.join(ROOT, "Assets", "Resources", "weapons")
UROOT = os.path.join(ROOT, "Assets", "Resources", "UI")

# 目录名 -> 武器名（与 WeaponConfigs.Title 对齐）
WFILES = {
    "weapon01": "剑", "weapon02": "铁锤", "weapon03": "弓", "weapon04": "铁拳套",
    "weapon05": "斧", "weapon06": "长矛", "weapon07": "短柄斧", "weapon08": "钉头锤",
    "weapon09": "苦无", "weapon04bomb": "炸弹",
}


def blank(d, w, h, ow):
    return None


def source_sprite(folder):
    """取该武器目录下的局内贴图（优先 <folder>.png）。"""
    base = os.path.join(WROOT, folder)
    cands = [os.path.join(base, folder + ".png")]
    cands += sorted(glob.glob(os.path.join(base, "*.png")))
    for p in cands:
        if os.path.exists(p) and os.path.basename(p).startswith("UI_") is False \
           and not os.path.basename(p).startswith("target-shape"):
            return p
    return None


def compose(size, sprite, fill_ratio=0.70, desaturate=False, crack=False):
    w, h = size
    plate = rewards.medallion(size, blank)
    r = min(w, h) * 0.485
    src = Image.open(sprite).convert("RGBA")
    target = 2 * r * fill_ratio
    s = target / max(src.width, src.height)
    src = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)

    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.alpha_composite(src, (int(w / 2 - src.width / 2), int(h / 2 - src.height / 2)))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse([w / 2 - r * 0.94, h / 2 - r * 0.94,
                                  w / 2 + r * 0.94, h / 2 + r * 0.94], fill=255)
    layer.putalpha(Image.composite(layer.split()[3], Image.new("L", size, 0), mask))

    if desaturate:
        a = layer.split()[3]
        lum = layer.convert("L")
        grey = Image.merge("RGB", (lum, lum, lum)).convert("RGBA")
        grey = Image.blend(grey, Image.new("RGBA", size, (196, 204, 216, 255)), 0.35)
        grey.putalpha(a)
        layer = grey
        d = ImageDraw.Draw(layer, "RGBA")
        for (p0, p1) in [((w * 0.30, h * 0.18), (w * 0.48, h * 0.46)),
                         ((w * 0.48, h * 0.46), (w * 0.36, h * 0.72)),
                         ((w * 0.56, h * 0.24), (w * 0.70, h * 0.58))]:
            d.line([p0, p1], fill=(54, 60, 76, 230), width=max(2, int(min(w, h) * 0.030)))

    plate.alpha_composite(layer)
    return plate


def main(only=None):
    n = 0
    for folder in sorted(WFILES):
        if only and folder not in only:
            continue
        src = source_sprite(folder)
        if not src:
            print("!! 找不到源图", folder); continue
        # 面板图标
        for suffix in ("", "_broken"):
            if folder.startswith("weapon04bomb"):
                p = os.path.join(WROOT, folder, "UI_w_weapon04Bomb%s.png" % suffix)
            else:
                idx = folder[-2:]
                p = os.path.join(WROOT, folder, "UI_w_weapon%s%s.png" % (idx, suffix))
            if not os.path.exists(p):
                continue
            size = Image.open(p).size
            out = compose(size, src, 0.64, desaturate=bool(suffix), crack=bool(suffix))
            out.save(p)
            n += 1
            print("图标", os.path.basename(p), size)
        # 奖励图标
        if folder.startswith("weapon04bomb"):
            continue
        idx = folder[-2:]
        rp = os.path.join(UROOT, "UI_reward_weapon%s.png" % idx)
        if os.path.exists(rp):
            size = Image.open(rp).size
            out = compose(size, src, 0.62)
            out.save(rp)
            n += 1
            print("奖励", os.path.basename(rp), size)
    print("完成", n)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
