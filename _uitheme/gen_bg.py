# -*- coding: utf-8 -*-
"""用 Pollinations 生成世界背景（免费额度），裁掉水印后落到目标尺寸。"""
import os, sys, time, urllib.parse, subprocess, io
from PIL import Image, ImageFilter, ImageEnhance

PROXY = "http://127.0.0.1:7897"
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(TMP, exist_ok=True)

PROMPTS = {
    "meadow": ("night fantasy meadow for a side scrolling mobile game, starry deep blue sky, "
               "big soft moon, distant ancient ruins and obelisks on the horizon, "
               "dark teal grass ground filling the lower two thirds, fireflies, fog, "
               "flat vector illustration, clean shapes, no text, no letters, no watermark"),
    "cavern": ("underground crystal cavern for a side scrolling mobile game, glowing blue and teal crystals, "
               "dark stone floor filling the lower two thirds, stalactites, mist, "
               "flat vector illustration, clean shapes, no text, no letters, no watermark"),
    "ember":  ("volcanic dungeon hall for a side scrolling mobile game, ember and lava glow, "
               "dark cracked stone floor filling the lower two thirds, embers in the air, "
               "flat vector illustration, clean shapes, no text, no letters, no watermark"),
}
SEEDS = {"meadow": 1201, "cavern": 1307, "ember": 1409}


def fetch(name, w=928, h=1424, tries=8):
    p = os.path.join(TMP, name + "_src.jpg")
    if os.path.exists(p) and os.path.getsize(p) > 20000:
        return p
    q = urllib.parse.quote(PROMPTS[name])
    for i in range(tries):
        url = (f"https://image.pollinations.ai/prompt/{q}?width={w}&height={h}"
               f"&seed={SEEDS[name] + i * 37}&nologo=true")
        r = subprocess.run(["curl", "-sS", "-m", "180", "-x", PROXY, "-o", p, "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        print(name, "try", i, "http", code, flush=True)
        if code == "200" and os.path.getsize(p) > 20000:
            return p
        time.sleep(25)
    return None


def prepare(name, target):
    src = fetch(name)
    if not src:
        return None
    im = Image.open(src).convert("RGB")
    w, h = im.size
    # 裁掉底部 8%（水印区）+ 底部再收一点保证地面完整
    im = im.crop((0, 0, w, int(h * 0.92)))
    # 轻微提亮阴影、压一点高光，贴近游戏内暗背景
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = im.resize(target, Image.LANCZOS)
    # 上下暗角，保证 UI 文字压得住
    v = Image.new("L", target, 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(v)
    for i in range(int(target[1] * 0.12)):
        a = int(110 * (1 - i / (target[1] * 0.12)))
        d.line([(0, i), (target[0], i)], fill=a)
    for i in range(int(target[1] * 0.10)):
        a = int(90 * (1 - i / (target[1] * 0.10)))
        d.line([(0, target[1] - 1 - i), (target[0], target[1] - 1 - i)], fill=a)
    dark = Image.new("RGBA", target, (4, 8, 16, 255))
    dark.putalpha(v.filter(ImageFilter.GaussianBlur(10)))
    out = Image.alpha_composite(im.convert("RGBA"), dark)
    return out


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
    for name, rel in [("meadow", "Assets/Sprites/bg_w00.png"),
                      ("cavern", "Assets/Sprites/bg_w01.png"),
                      ("ember", "Assets/Sprites/bg_w02.png")]:
        p = os.path.join(root, rel)
        target = Image.open(p).size
        img = prepare(name, target)
        if img is None:
            print("跳过", name)
            continue
        img.save(os.path.join(outs, "genbg_" + name + ".png"))
        print("ok", name, target)
