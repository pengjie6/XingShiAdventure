# -*- coding: utf-8 -*-
"""生成 TMP 1.4 旧格式的中文 SDF 字体资源（DroidSansFallback）"""
import os, re, json, math, random
import numpy as np
from PIL import Image, ImageFont, ImageDraw

ROOT = r"E:/unitystudy/project/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG"
os.chdir(ROOT)

TTF = "Assets/Resources/fonts & materials/DroidSansFallback.ttf"
if not os.path.exists(TTF):
    TTF = "Assets/AdSDK/AdSDK/Font/DroidSansFallback.ttf"

SIZE = 60          # 采样字号（TMP PointSize）
PAD = 5            # 图集内边距
SPREAD = 5.0       # SDF 扩散半径（像素）
ATLAS_W = 4096
ATLAS_H = 2048
OUT_PNG = "Assets/Resources/fonts & materials/DroidSansFallback SDF Atlas.png"
OUT_ASSET = "Assets/Resources/fonts & materials/DroidSansFallback SDF.asset"
PNG_GUID = "b7c1e5a4d92f4c3f8a61d0e2c4f7b913"
FONT_GUID = "781095ea128f1d64884a9fd28a6cead2"      # 保持原 GUID，引用不变
OLD_TMP_SCRIPT = "631471c2a5a23f603a67786f6dad2714"
BASE_MATERIAL_GUID = "ec09463889d60829ad49076695bc0aec"  # DroidSans SDF Material

# ---------------- 字符集 ----------------
chars = set(chr(c) for c in range(32, 127))
chars |= set("，。！？：；、（）《》“”‘’…—～·％＋－×÷【】「」『』〈〉￥")
SCAN_EXT = (".unity", ".prefab", ".cs", ".asset", ".txt", ".csv", ".json", ".bytes", ".xml")
for dp, dn, fn in os.walk("Assets"):
    for f in fn:
        if not f.endswith(SCAN_EXT):
            continue
        try:
            s = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if "Unity.TextMeshPro" in dp or "TextMesh Pro" in dp:
            continue
        # Unity 的 .unity/.prefab/.asset 里中文以 \uXXXX 转义保存，先解码
        if f.endswith((".unity", ".prefab", ".asset")):
            s = re.sub(r"\\u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), s)
        for ch in s:
            if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" or "\uff00" <= ch <= "\uffef":
                chars.add(ch)
chars = sorted(c for c in chars if c not in "\t\r\n")
print("字符数:", len(chars))

font = ImageFont.truetype(TTF, SIZE)
ascent, descent = font.getmetrics()
print("ascent/descent:", ascent, descent)


def edt_1d(f):
    n = len(f)
    d = np.zeros(n)
    v = np.zeros(n, dtype=int)
    z = np.zeros(n + 1)
    k = 0
    v[0] = 0
    z[0] = -1e20
    z[1] = 1e20
    for q in range(1, n):
        s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        while s <= z[k]:
            k -= 1
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        k += 1
        v[k] = q
        z[k] = s
        z[k + 1] = 1e20
    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        d[q] = (q - v[k]) ** 2 + f[v[k]]
    return d


def edt(mask):
    """mask: bool, True=内部；返回每个像素到最近边界的有符号距离（内部为正）"""
    h, w = mask.shape
    INF = 1e12
    # 内部像素：到最近「非墨」像素的距离
    f = np.where(mask, INF, 0.0)
    for y in range(h):
        f[y] = edt_1d(f[y])
    for x in range(w):
        f[:, x] = edt_1d(f[:, x])
    dist_to_outside = np.sqrt(f)

    # 外部像素：到最近「墨」像素的距离
    g = np.where(mask, 0.0, INF)
    for y in range(h):
        g[y] = edt_1d(g[y])
    for x in range(w):
        g[:, x] = edt_1d(g[:, x])
    dist_to_inside = np.sqrt(g)

    return np.where(mask, dist_to_outside, -dist_to_inside)


# ---------------- 逐个字形生成 ----------------
glyphs = []   # dict: ch,x,y,w,h,xoff,yoff,adv
surfaces = {}  # ch -> np.array (alpha)
for ch in chars:
    try:
        mask, offset = font.getmask2(ch, mode="L")
    except Exception:
        continue
    w, h = mask.size
    if w <= 0 or h <= 0:
        # 空白字符（空格等）
        glyphs.append(dict(ch=ch, x=0, y=0, w=0, h=0,
                           xoff=0, yoff=0, adv=float(font.getlength(ch)), blank=True))
        continue
    arr = np.array(mask, dtype=np.uint8)
    if arr.ndim == 1:
        arr = arr.reshape(h, w)
    binary = arr > 127
    if binary.sum() == 0:
        glyphs.append(dict(ch=ch, x=0, y=0, w=0, h=0,
                           xoff=0, yoff=0, adv=float(font.getlength(ch)), blank=True))
        continue

    sd = edt(binary)
    alpha = 128.0 + 127.0 * np.clip(sd / SPREAD, -1.0, 1.0)

    canvas = np.zeros((h + 2 * PAD, w + 2 * PAD), dtype=np.uint8)
    canvas[PAD:PAD + h, PAD:PAD + w] = alpha.astype(np.uint8)

    xoff = float(offset[0])
    yoff = float(ascent - offset[1])
    adv = float(font.getlength(ch))
    glyphs.append(dict(ch=ch, w=w, h=h, xoff=xoff, yoff=yoff, adv=adv, blank=False))
    surfaces[ch] = canvas

# ---------------- 打包 ----------------
order = sorted([g for g in glyphs if not g["blank"]], key=lambda g: (-g["h"], -g["w"]))
atlas = np.zeros((ATLAS_H, ATLAS_W), dtype=np.uint8)
cx, cy, shelf_h = PAD, PAD, 0
for g in order:
    cw, chh = g["w"] + 2 * PAD, g["h"] + 2 * PAD
    if cx + cw + PAD > ATLAS_W:
        cx = PAD
        cy += shelf_h + PAD
        shelf_h = 0
    if cy + chh + PAD > ATLAS_H:
        raise RuntimeError("图集空间不足，请增大 ATLAS 或降低 SIZE")
    atlas[cy:cy + chh, cx:cx + cw] = surfaces[g["ch"]]
    g["x"] = cx + PAD
    g["y"] = cy + PAD
    cx += cw + PAD
    shelf_h = max(shelf_h, chh)
print("占用高度:", cy + shelf_h + PAD)

rgba = np.empty((ATLAS_H, ATLAS_W, 4), dtype=np.uint8)
rgba[..., 0] = 255
rgba[..., 1] = 255
rgba[..., 2] = 255
rgba[..., 3] = atlas
Image.fromarray(rgba, "RGBA").save(OUT_PNG)
print("已写图集:", OUT_PNG)

# ---------------- 度量 ----------------
cap = 0.0
try:
    b = font.getbbox("H")
    cap = float(b[3] - b[1])
except Exception:
    cap = SIZE * 0.7

def gline(g):
    return (f"  - id: {ord(g['ch'])}\n"
            f"    serializedVersion: 2\n"
            f"    x: {g['x']}\n"
            f"    y: {g['y']}\n"
            f"    width: {g['w']}\n"
            f"    height: {g['h']}\n"
            f"    xOffset: {round(g['xoff'],4)}\n"
            f"    yOffset: {round(g['yoff'],4)}\n"
            f"    xAdvance: {round(g['adv'],4)}\n"
            f"    scale: 1\n")

glyph_yaml = "".join(gline(g) for g in sorted(glyphs, key=lambda g: ord(g["ch"])))
count = len(glyphs)

space_adv = float(font.getlength(" ")) if " " in chars else SIZE * 0.3

fontinfo = f"""  m_fontInfo:
    Name: "Droid Sans Fallback"
    PointSize: {SIZE}
    Scale: 1
    CharacterCount: {count}
    LineHeight: {ascent + descent}
    Baseline: 0
    Ascender: {ascent}
    CapHeight: {round(cap,4)}
    Descender: {-descent}
    CenterLine: 0
    SuperscriptOffset: {ascent}
    SubscriptOffset: {round(-descent*0.4,4)}
    SubSize: 0.5
    Underline: {round(-descent*0.4,4)}
    UnderlineThickness: {round(SIZE*0.05,4)}
    strikethrough: {round(cap/2.5,4)}
    strikethroughThickness: {round(SIZE*0.05,4)}
    TabWidth: {round(space_adv*10,4)}
    Padding: {PAD}
    AtlasWidth: {ATLAS_W}
    AtlasHeight: {ATLAS_H}
"""

# ---------------- 生成字体资源 ----------------
src = open("Assets/Resources/fonts & materials/FiraSansExtraCondensed-ExtraBold SDF.asset", encoding="utf-8").read()
head = src.split("  m_fontInfo:")[0]
tail = "  m_kerningInfo:" + src.split("  m_kerningInfo:", 1)[1]

head = re.sub(r'(?m)^  m_Name: .*$', '  m_Name: "DroidSansFallback SDF"', head)
head = re.sub(r'(?m)^  material: .*$', "  material: {fileID: 2100000, guid: %s, type: 2}" % BASE_MATERIAL_GUID, head)
head = head.replace("fontAssetType: 1", "fontAssetType: 1")

out = head + fontinfo + f"  atlas: {{fileID: 2800000, guid: {PNG_GUID}, type: 3}}\n  m_glyphInfoList:\n" + glyph_yaml + tail
open(OUT_ASSET, "w", encoding="utf-8", newline="\n").write(out)
print("已写字体资源:", OUT_ASSET, "字形数:", count)

# ---------------- 图集 meta ----------------
meta_src = open("Assets/Resources/fonts & materials/FiraSansExtraCondensed-ExtraBold SDF Atlas.png.meta", encoding="utf-8").read()
meta = re.sub(r'(?m)^guid: .*$', "guid: " + PNG_GUID, meta_src)
meta = meta.replace("maxTextureSize: 2048", "maxTextureSize: 4096")
meta = meta.replace("indices: \n", "indices: []\n")
open(OUT_PNG + ".meta", "w", encoding="utf-8", newline="\n").write(meta)

# ---------------- 材质贴图指向新图集 ----------------
import glob
n = 0
for p in glob.glob("Assets/Resources/fonts & materials/DroidSans SDF*.mat"):
    s = open(p, encoding="utf-8").read()
    s2 = re.sub(r"(    - _MainTex:\n        m_Texture: )\{[^}]*\}",
                r"\1{fileID: 2800000, guid: %s, type: 3}" % PNG_GUID, s, count=1)
    s2 = re.sub(r"(?m)^    - _TextureWidth: .*$", "    - _TextureWidth: %d" % ATLAS_W, s2)
    s2 = re.sub(r"(?m)^    - _TextureHeight: .*$", "    - _TextureHeight: %d" % ATLAS_H, s2)
    if s2 != s:
        open(p, "w", encoding="utf-8", newline="").write(s2)
        n += 1
print("材质已指向新图集:", n)

# ---------------- 预览 ----------------
prev = Image.new("RGB", (1400, 240), (20, 20, 20))
d = ImageDraw.Draw(prev)
text = "欢迎来到微型RPG！铁锤 商店 升级 每日任务"
x, y = 20, 60
for ch in text:
    g = next((g for g in glyphs if g["ch"] == ch), None)
    if g is None:
        x += SIZE // 2
        continue
    if not g["blank"]:
        cell = atlas[g["y"]:g["y"] + g["h"], g["x"]:g["x"] + g["w"]]
        ink = (cell > 128)
        sub = Image.fromarray((ink * 255).astype(np.uint8), "L")
        prev.paste((240, 240, 240), (int(x + g["xoff"]), int(y - g["yoff"])), sub)
    x += g["adv"]
d.text((20, 180), "SDF atlas preview (thresholded)", fill=(120, 120, 120))
prev.save("_i18n_tools/font_preview.png")
print("预览已生成")
