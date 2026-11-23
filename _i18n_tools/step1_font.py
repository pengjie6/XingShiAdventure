import os, re, shutil, random, json, sys

ROOT = r"E:/unitystudy/project/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG/Unity2018_小小RPG_MicroRPG"
os.chdir(ROOT)

FONT_GUID = "781095ea128f1d64884a9fd28a6cead2"          # DroidSansFallback SDF.asset
FONT_ATLAS_ID = "7918471459484868180"                    # 字体资源内的图集贴图 fileID
FONT_TTF_GUID = "4b55cb2df6c16834786823b918fe5b7f"       # DroidSansFallback.ttf

# ---------- 1. 把字体资源移动到 Resources，便于 Resources.Load ----------
src_asset = "Assets/AdSDK/AdSDK/Font/DroidSansFallback SDF.asset"
dst_dir = "Assets/Resources/fonts & materials"
dst_asset = os.path.join(dst_dir, "DroidSansFallback SDF.asset")
if os.path.exists(src_asset):
    os.makedirs(dst_dir, exist_ok=True)
    for ext in ("", ".meta"):
        shutil.move(src_asset + ext, dst_asset + ext)
    print("字体资源已移动 ->", dst_asset)
else:
    print("字体资源已在目标位置或不存在:", dst_asset, os.path.exists(dst_asset))

font_meta = open(dst_asset + ".meta", encoding="utf-8").read()
assert FONT_GUID in font_meta, "字体 GUID 不一致，中止"

# ---------- 2. 克隆材质，_MainTex 指向 DroidSans 图集 ----------
MATS = {
    "f6b21b1a7a1744ecbbc41b2fba0a869c": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - NoOutline.mat", "DroidSans SDF - NoOutline"),
    "428a567874894d6dbcf7ef03f8f0c51f": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Button.mat", "DroidSans SDF - Button"),
    "72a577cf93ab4622a5dc00528dd6ff63": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF Material.mat", "DroidSans SDF Material"),
    "e4b28440e7944532bb24f41cf6c326be": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Paragraph.mat", "DroidSans SDF - Paragraph"),
    "7a8c1b16662f453abec6a24a04694501": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - DropShadow.mat", "DroidSans SDF - DropShadow"),
    "e4b6f4dd6bd441c09a82362dba27c628": ("Fonts & materials/LiberationSans SDF Material.mat", "DroidSans SDF Material (Liberation)"),
    "234dfef763f14325b57ecc2109098a84": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - BigOutline.mat", "DroidSans SDF - BigOutline"),
    "b2976378fbdd44198e9b4adafe739d57": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - BigOutlineShadow.mat", "DroidSans SDF - BigOutlineShadow"),
    "f600c7bae57549bf9f8920b642d45cea": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - BigOutlineInner.mat", "DroidSans SDF - BigOutlineInner"),
    "595696b2f03a44a89ca9148aa259c76c": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - BigOutlineBlack.mat", "DroidSans SDF - BigOutlineBlack"),
    "edb21f47ac8848ef9154f9ebaac8e255": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Title.mat", "DroidSans SDF - Title"),
    "fb9b0827c5794df9a09fa3710ea4191b": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Damage.mat", "DroidSans SDF - Damage"),
    "66661cf9a4614cd294f0e0d1498178d1": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Healing.mat", "DroidSans SDF - Healing"),
    "0d49670c97434b23a7e801bdcb0664da": ("Fonts & materials/ARIALBD NumbersSymbols SDF Material.mat", "DroidSans SDF Material (Numbers)"),
    "e44e364a8ad44a98b5eea2a1d0a74613": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Default.mat", "DroidSans SDF - Default"),
    "4eac2241f0ca4edfb5d97f8599418323": ("Fonts & materials/FiraSansExtraCondensed-ExtraBold SDF - Negative.mat", "DroidSans SDF - Negative"),
}

MAT_META_TMPL = """fileFormatVersion: 2
guid: {guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 2100000
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

def new_guid(seed):
    rnd = random.Random(seed)
    return "".join(rnd.choice("0123456789abcdef") for _ in range(32))

master = {}   # 旧材质 guid -> 新材质 guid
for old_guid, (rel, new_name) in MATS.items():
    src = "Assets/Resources/" + rel
    if not os.path.exists(src):
        print("!! 源材质缺失:", src)
        continue
    txt = open(src, encoding="utf-8").read()
    txt = re.sub(r"(?m)^  m_Name: .*$", "  m_Name: " + new_name, txt, count=1)
    txt = re.sub(
        r"(    - _MainTex:\n        m_Texture: )\{[^}]*\}",
        r"\1{fileID: %s, guid: %s, type: 2}" % (FONT_ATLAS_ID, FONT_GUID),
        txt, count=1)
    txt = re.sub(r"(?m)^    - _TextureWidth: .*$", "    - _TextureWidth: 1024", txt)
    txt = re.sub(r"(?m)^    - _TextureHeight: .*$", "    - _TextureHeight: 1024", txt)

    out = os.path.join(dst_dir, new_name + ".mat")
    nguid = new_guid("mat:" + old_guid)
    open(out, "w", encoding="utf-8", newline="\n").write(txt)
    open(out + ".meta", "w", encoding="utf-8", newline="\n").write(MAT_META_TMPL.format(guid=nguid))
    master[old_guid] = nguid
    print("材质:", new_name, "->", nguid)

json.dump(master, open("_i18n_tools/mat_map.json", "w"), indent=1)

# ---------- 3. 场景/预制体：字体 + 材质引用替换 ----------
OLD_FONTS = [
    "5b0da991e2cc47a594a00011eab9a12d",
    "7a9f1ba3dd604f62a94c82963746a18a",
    "0c76811278c341c0a14a552c2529cf51",
]
DEFAULT_MAT = master["72a577cf93ab4622a5dc00528dd6ff63"]

changed = 0
for dp, dn, fn in os.walk("Assets"):
    for f in fn:
        if not (f.endswith(".unity") or f.endswith(".prefab")):
            continue
        p = os.path.join(dp, f)
        txt = open(p, encoding="utf-8").read()
        orig = txt

        # 字体资源引用
        for g in OLD_FONTS:
            txt = txt.replace("guid: %s, type: 2}" % g, "guid: %s, type: 2}" % FONT_GUID)

        # 字体材质引用
        for og, ng in master.items():
            txt = txt.replace("m_sharedMaterial: {fileID: 2100000, guid: %s, type: 2}" % og,
                              "m_sharedMaterial: {fileID: 2100000, guid: %s, type: 2}" % ng)

        # 空材质 -> 默认材质
        txt = txt.replace("m_sharedMaterial: {fileID: 0}",
                          "m_sharedMaterial: {fileID: 2100000, guid: %s, type: 2}" % DEFAULT_MAT)

        # 旧版 Text / TextMesh 的内建 Arial -> DroidSansFallback.ttf
        txt = txt.replace("m_Font: {fileID: 10102, guid: 0000000000000000e000000000000000, type: 0}",
                          "m_Font: {fileID: 12800000, guid: %s, type: 3}" % FONT_TTF_GUID)

        if txt != orig:
            open(p, "w", encoding="utf-8", newline="").write(txt)
            changed += 1

print("已更新场景/预制体:", changed)
