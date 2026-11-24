# -*- coding: utf-8 -*-
"""武器贴图重绘（月辉旅人套）。

- 只替换"看得见的武器美术"：weapon0X.png（手持刀身）、0Xb（损坏）、03c/cb（箭）、
  04Bomb（炸弹）、09_*（残影/掉落/命中）。
- **不动** `*Shape.png`（挥砍蒙版，绑着 PolygonCollider2D）和 `target-shape_*.png`（攻击范围指示）。
- 画布尺寸与包围盒沿用原图，`.meta`/pivot 不动。
"""
import os, math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hero as H

ROOT = H.ROOT
K = 6.0
OK_ = 3.0   # 描边换算：ow 按"目标像素"给，render 时按绘制倍率放大

INK      = H.INK
NAVY     = H.HOOD
NAVY_D   = H.CLOAK
NAVY_L   = H.SLEEVE
GOLD     = H.GOLD
GOLD_L   = H.GOLD_L
GOLD_D   = H.GOLD_D
CREAM    = H.CREAM
TEAL     = H.TEAL
TEAL_D   = H.TEAL_D
STEEL    = H.STEEL
STEEL_D  = H.STEEL_D
WOOD     = H.WOOD
WOOD_D   = (88, 56, 32, 255)
STONE    = (150, 164, 182, 255)
STONE_D  = (104, 118, 136, 255)


# ---------------------------------------------------------------- 基元
def E(d, x0, y0, x1, y1, fill, ow=1.6, outline=INK):
    d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=max(1, int(ow * OK_)))


def R(d, x0, y0, x1, y1, fill, r=0, ow=1.6, outline=INK):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline,
                        width=max(1, int(ow)))


def PG(d, pts, fill, ow=1.6, outline=INK):
    d.polygon(pts, fill=fill)
    if ow:
        d.line(list(pts) + [pts[0]], fill=outline, width=max(1, int(ow * OK_)), joint="curve")


def CAP(d, a, b, w, fill, ow=1.6):
    o = ow * OK_
    d.line([a, b], fill=INK, width=int(w + o * 2))
    for p in (a, b):
        r = w / 2 + o
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=INK)
    d.line([a, b], fill=fill, width=int(w))
    for p in (a, b):
        r = w / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def glove(d, cx, cy, r, angle=0.0):
    """握持的手：奶白拳 + 指缝 + 金袖口（不画拇指外凸，避免小尺寸变白蛋）。"""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    E(d, cx - r, cy - r * 0.92, cx + r, cy + r * 0.92, CREAM, 1.6)
    # 指缝
    for k in (-0.34, 0.10):
        x0, y0 = cx + px * r * 0.92 + ux * r * k, cy + py * r * 0.92 + uy * r * k
        x1, y1 = cx - px * r * 0.92 + ux * r * k, cy - py * r * 0.92 + uy * r * k
        d.line([(x0, y0), (x1, y1)], fill=(206, 186, 156, 255), width=max(2, int(r * 0.26)))
    # 金袖口
    cx0, cy0 = cx - ux * r * 0.80, cy - uy * r * 0.80
    d.line([(cx0 + px * r * 0.95, cy0 + py * r * 0.95),
            (cx0 - px * r * 0.95, cy0 - py * r * 0.95)],
           fill=INK, width=max(3, int(r * 0.52)))
    d.line([(cx0 + px * r * 0.95, cy0 + py * r * 0.95),
            (cx0 - px * r * 0.95, cy0 - py * r * 0.95)],
           fill=GOLD, width=max(2, int(r * 0.34)))


def band(d, p0, p1, p2, w0, w1, fill, ow=1.7, n=22):
    """二次贝塞尔渐细带（刃/飘带）。"""
    A, B = [], []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        hw = (w0 + (w1 - w0) * t) / 2
        A.append((x + nx * hw, y + ny * hw))
        B.append((x - nx * hw, y - ny * hw))
    PG(d, A + B[::-1], fill, ow)


def crescent(d, cx, ty, by, bulge, thick, fill, ow=1.8, n=26):
    """月牙刃：外弧朝 -x 鼓出，两端收成尖。"""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        k = math.sin(math.pi * t)
        y = ty + (by - ty) * t
        outer.append((cx - bulge * k, y))
        inner.append((cx - (bulge - thick) * k, y))
    PG(d, outer + inner[::-1], fill, ow)


# ---------------------------------------------------------------- 各武器
def w_sword(d, W, H, **kw):
    cx = W * 0.5
    tip = H * 0.03
    bw = W * 0.160
    base = H * 0.55
    # 刃
    PG(d, [(cx, tip), (cx + bw, H * 0.16), (cx + bw, base), (cx - bw, base),
           (cx - bw, H * 0.16)], STEEL, 1.7)
    # 血槽
    PG(d, [(cx, H * 0.10), (cx + bw * 0.30, H * 0.20), (cx + bw * 0.30, base - H * 0.02),
           (cx - bw * 0.30, base - H * 0.02), (cx - bw * 0.30, H * 0.20)],
       (244, 251, 255, 255), 0)
    # 青玉刃口
    d.line([(cx - bw * 0.78, H * 0.17), (cx - bw * 0.78, base - H * 0.02)], fill=TEAL,
           width=max(2, int(W * 0.045)))
    d.line([(cx + bw * 0.80, H * 0.17), (cx + bw * 0.80, base - H * 0.02)], fill=TEAL_D,
           width=max(2, int(W * 0.035)))
    # 护手
    R(d, cx - W * 0.285, base - H * 0.014, cx + W * 0.285, base + H * 0.056, GOLD, W * 0.05, 1.7)
    E(d, cx - W * 0.055, base + H * 0.002, cx + W * 0.055, base + H * 0.042, TEAL, 1.4)
    # 柄
    R(d, cx - W * 0.072, base + H * 0.048, cx + W * 0.072, base + H * 0.30, WOOD, W * 0.05, 1.7)
    for i in range(3):
        yy = base + H * (0.075 + i * 0.062)
        d.line([(cx - W * 0.055, yy), (cx + W * 0.055, yy)], fill=WOOD_D, width=2)
    # 尾饰
    E(d, cx - W * 0.075, base + H * 0.285, cx + W * 0.075, base + H * 0.40, GOLD, 1.7)
    # 双手
    glove(d, cx - W * 0.070, base + H * 0.150, W * 0.125, -20)
    glove(d, cx + W * 0.070, base + H * 0.250, W * 0.125, 200)


def w_axe(d, W, H, **kw):
    cx = W * 0.62
    CAP(d, (cx, H * 0.03), (cx, H * 0.95), W * 0.105, WOOD, 1.7)
    # 月牙斧刃（朝左）
    crescent(d, cx, H * 0.07, H * 0.39, W * 0.42, W * 0.31, STEEL, 1.9)
    # 刃口高光
    crescent(d, cx, H * 0.105, H * 0.355, W * 0.37, W * 0.075, (246, 252, 255, 255), 0)
    # 金箍
    R(d, cx - W * 0.10, H * 0.075, cx + W * 0.11, H * 0.115, GOLD, W * 0.02, 1.6)
    R(d, cx - W * 0.10, H * 0.345, cx + W * 0.11, H * 0.385, GOLD, W * 0.02, 1.6)
    E(d, cx - W * 0.015, H * 0.925, cx + W * 0.10, H * 0.975, GOLD, 1.6)
    glove(d, cx, H * 0.74, W * 0.115, -90)


def w_double_axe(d, W, H, **kw):
    cx = W * 0.5
    CAP(d, (cx, H * 0.03), (cx, H * 0.97), W * 0.10, WOOD, 1.7)
    for s_ in (-1, 1):
        ty, by = H * 0.10, H * 0.40
        n = 26
        outer, inner = [], []
        for i in range(n + 1):
            t = i / n
            k = math.sin(math.pi * t)
            y = ty + (by - ty) * t
            outer.append((cx + s_ * W * 0.42 * k, y))
            inner.append((cx + s_ * W * 0.17 * k, y))
        PG(d, outer + inner[::-1], STEEL, 1.9)
    # 中脊金饰
    R(d, cx - W * 0.055, H * 0.075, cx + W * 0.055, H * 0.425, GOLD, W * 0.02, 1.6)
    PG(d, [(cx, H * 0.10), (cx + W * 0.045, H * 0.155), (cx, H * 0.21), (cx - W * 0.045, H * 0.155)],
       TEAL, 1.4)
    E(d, cx - W * 0.075, H * 0.955, cx + W * 0.075, H * 0.998, GOLD, 1.6)
    glove(d, cx, H * 0.70, W * 0.115, -90)
    glove(d, cx, H * 0.85, W * 0.115, 90)


def w_bow(d, W, H, **kw):
    cx, cy = W * 0.62, H * 0.5
    rx, ry = W * 0.34, H * 0.46
    # 弓臂（左半弧）
    d.arc([cx - rx, cy - ry, cx + rx, cy + ry], 120, 240, fill=INK, width=int(W * 0.27))
    d.arc([cx - rx, cy - ry, cx + rx, cy + ry], 120, 240, fill=WOOD, width=int(W * 0.18))
    # 弓梢金饰
    for s_ in (-1, 1):
        a = math.radians(120 if s_ < 0 else 240)
        px, py = cx + rx * math.cos(a), cy + ry * math.sin(a)
        E(d, px - W * 0.07, py - W * 0.07, px + W * 0.07, py + W * 0.07, GOLD, 1.6)
    # 弦
    sx = cx - rx * 0.5
    d.line([(sx, cy - ry * 0.866), (sx, cy + ry * 0.866)],
           fill=(232, 242, 252, 255), width=max(2, int(W * 0.035)))
    # 握把（弓腹最左点）
    gx = cx - rx
    R(d, gx - W * 0.10, cy - H * 0.10, gx + W * 0.10, cy + H * 0.10, TEAL_D, W * 0.05, 1.7)
    d.line([(gx - W * 0.10, cy - H * 0.05), (gx + W * 0.10, cy - H * 0.05)], fill=GOLD, width=2)
    d.line([(gx - W * 0.10, cy + H * 0.05), (gx + W * 0.10, cy + H * 0.05)], fill=GOLD, width=2)
    glove(d, gx, cy, W * 0.145, 0)


def w_arrow(d, W, H, **kw):
    cy = H * 0.5
    # 箭杆
    CAP(d, (W * 0.10, cy), (W * 0.74, cy), H * 0.16, WOOD, 1.4)
    # 箭头
    PG(d, [(W * 0.97, cy), (W * 0.70, cy - H * 0.26), (W * 0.74, cy), (W * 0.70, cy + H * 0.26)],
       STEEL, 1.6)
    # 尾羽
    for s in (-1, 1):
        PG(d, [(W * 0.10, cy), (W * 0.24, cy + s * H * 0.34), (W * 0.30, cy + s * H * 0.30),
               (W * 0.22, cy)], TEAL_D, 1.4)
    E(d, W * 0.05, cy - H * 0.13, W * 0.14, cy + H * 0.13, GOLD, 1.4)


def w_fist(d, W, H, **kw):
    cx, cy = W * 0.5, H * 0.46
    # 护腕
    R(d, cx - W * 0.30, cy + H * 0.26, cx + W * 0.30, cy + H * 0.50, NAVY, W * 0.08, 1.8)
    R(d, cx - W * 0.32, cy + H * 0.22, cx + W * 0.32, cy + H * 0.31, GOLD, W * 0.05, 1.7)
    # 拳身
    R(d, cx - W * 0.35, cy - H * 0.34, cx + W * 0.35, cy + H * 0.28, STEEL, W * 0.14, 1.9)
    # 指节
    for i in range(3):
        x0 = cx - W * 0.29 + i * W * 0.195
        E(d, x0, cy - H * 0.42, x0 + W * 0.185, cy - H * 0.20, STEEL, 1.7)
    # 拇指
    E(d, cx + W * 0.14, cy - H * 0.06, cx + W * 0.40, cy + H * 0.16, STEEL, 1.7)
    # 高光与铆钉
    d.line([(cx - W * 0.28, cy - H * 0.10), (cx + W * 0.26, cy - H * 0.14)], fill=(246, 252, 255, 255), width=3)
    for i in range(2):
        E(d, cx - W * 0.20 + i * W * 0.32, cy + H * 0.08,
          cx - W * 0.13 + i * W * 0.32, cy + H * 0.15, GOLD, 1.2)


def w_bomb(d, W, H, **kw):
    cx, cy = W * 0.5, H * 0.62
    r = min(W * 0.40, H * 0.33)
    # 弹体
    E(d, cx - r, cy - r, cx + r, cy + r, (36, 44, 62, 255), 2.0)
    # 金箍
    R(d, cx - r * 0.9, cy - r * 0.22, cx + r * 0.9, cy + r * 0.16, GOLD, r * 0.14, 1.7)
    # 高光
    d.arc([cx - r * 0.72, cy - r * 0.78, cx + r * 0.42, cy + r * 0.10], 200, 300,
          fill=(150, 190, 230, 200), width=max(2, int(r * 0.16)))
    # 引信
    CAP(d, (cx + r * 0.10, cy - r * 0.92), (cx + r * 0.44, cy - r * 1.42), r * 0.16, WOOD, 1.4)
    # 火花
    d.ellipse([cx + r * 0.32, cy - r * 1.62, cx + r * 0.60, cy - r * 1.34], fill=GOLD_L)
    for a in range(0, 360, 60):
        aa = math.radians(a)
        d.line([(cx + r * 0.46 + math.cos(aa) * r * 0.14, cy - r * 1.48 + math.sin(aa) * r * 0.14),
                (cx + r * 0.46 + math.cos(aa) * r * 0.28, cy - r * 1.48 + math.sin(aa) * r * 0.28)],
               fill=GOLD, width=2)
    # 眼睛
    for s in (-1, 1):
        E(d, cx + s * r * 0.30 - r * 0.11, cy + r * 0.28, cx + s * r * 0.30 + r * 0.11,
          cy + r * 0.50, CREAM, 0)


def w_staff(d, W, H, **kw):
    cx = W * 0.5
    CAP(d, (cx, H * 0.16), (cx, H * 0.96), W * 0.085, WOOD, 1.7)
    # 金托
    PG(d, [(cx - W * 0.19, H * 0.20), (cx - W * 0.09, H * 0.10),
           (cx + W * 0.09, H * 0.10), (cx + W * 0.19, H * 0.20),
           (cx + W * 0.10, H * 0.28), (cx - W * 0.10, H * 0.28)], GOLD, 1.7)
    # 宝珠
    E(d, cx - W * 0.155, H * 0.015, cx + W * 0.155, H * 0.215, TEAL, 1.8)
    E(d, cx - W * 0.075, H * 0.055, cx + W * 0.035, H * 0.135, (206, 255, 248, 230), 0)
    # 光晕
    d.arc([cx - W * 0.20, H * -0.03, cx + W * 0.20, H * 0.25], 200, 340, fill=(160, 240, 230, 140), width=3)
    glove(d, cx, H * 0.66, W * 0.155, -90)


def w_hammer(d, W, H, **kw):
    cx = W * 0.5
    CAP(d, (cx, H * 0.30), (cx, H * 0.96), W * 0.085, WOOD, 1.7)
    # 锤头
    R(d, cx - W * 0.36, H * 0.05, cx + W * 0.36, H * 0.29, STEEL, W * 0.05, 1.9)
    R(d, cx - W * 0.36, H * 0.14, cx + W * 0.36, H * 0.20, GOLD, 0, 1.6)
    # 侧面装饰
    for s in (-1, 1):
        PG(d, [(cx + s * W * 0.36, H * 0.07), (cx + s * W * 0.46, H * 0.12),
               (cx + s * W * 0.46, H * 0.22), (cx + s * W * 0.36, H * 0.27)], GOLD, 1.6)
    d.line([(cx - W * 0.30, H * 0.08), (cx + W * 0.30, H * 0.08)], fill=(246, 252, 255, 255), width=3)
    glove(d, cx, H * 0.68, W * 0.145, -90)


def w_boomerang(d, W, H, **kw):
    cx, cy = W * 0.5, H * 0.5
    # 两段弧形刃，夹角 ~100°
    p0 = (cx - W * 0.34, cy + H * 0.28)
    p1 = (cx - W * 0.12, cy - H * 0.30)
    p2 = (cx + W * 0.34, cy - H * 0.30)
    band(d, p0, p1, p2, W * 0.20, W * 0.13, WOOD, 1.9)
    band(d, (cx - W * 0.30, cy + H * 0.24), (cx - W * 0.10, cy - H * 0.22),
         (cx + W * 0.30, cy - H * 0.24), W * 0.075, W * 0.045, (156, 106, 62, 255), 0)
    # 金端 + 青玉尖
    E(d, cx - W * 0.40, cy + H * 0.20, cx - W * 0.26, cy + H * 0.34, GOLD, 1.6)
    E(d, cx + W * 0.28, cy - H * 0.36, cx + W * 0.42, cy - H * 0.22, GOLD, 1.6)
    # 握把
    R(d, cx - W * 0.12, cy - H * 0.09, cx + W * 0.10, cy + H * 0.09, TEAL_D, W * 0.03, 1.6)
    glove(d, cx - W * 0.01, cy, W * 0.095, 180)


def w_kunai(d, W, H, **kw):
    cx = W * 0.5
    # 刃（叶片形）
    PG(d, [(cx, H * 0.03), (cx + W * 0.22, H * 0.30), (cx + W * 0.06, H * 0.44),
           (cx - W * 0.06, H * 0.44), (cx - W * 0.22, H * 0.30)], (52, 60, 84, 255), 1.8)
    PG(d, [(cx, H * 0.09), (cx + W * 0.12, H * 0.30), (cx, H * 0.38), (cx - W * 0.12, H * 0.30)],
       (96, 116, 150, 255), 0)
    # 中脊光
    d.line([(cx, H * 0.08), (cx, H * 0.40)], fill=(198, 226, 250, 220), width=2)
    # 握柄
    CAP(d, (cx, H * 0.44), (cx, H * 0.80), W * 0.15, (34, 40, 58, 255), 1.7)
    # 环
    E(d, cx - W * 0.13, H * 0.78, cx + W * 0.13, H * 0.98, (0, 0, 0, 0), 1.9)
    E(d, cx - W * 0.13, H * 0.78, cx + W * 0.13, H * 0.98, (0, 0, 0, 0), 1.9)


def w_slash(d, W, H, **kw):
    """命中特效：两道交叉的月牙刃光 + 火星。"""
    band(d, (W * 0.06, H * 0.86), (W * 0.44, H * 0.10), (W * 0.94, H * 0.30),
         H * 0.10, H * 0.30, GOLD_L, 2)
    band(d, (W * 0.10, H * 0.20), (W * 0.50, H * 0.92), (W * 0.96, H * 0.66),
         H * 0.10, H * 0.26, GOLD_L, 2)
    band(d, (W * 0.10, H * 0.86), (W * 0.46, H * 0.16), (W * 0.90, H * 0.34),
         H * 0.04, H * 0.14, (255, 252, 235, 255), 0)
    band(d, (W * 0.14, H * 0.24), (W * 0.52, H * 0.86), (W * 0.92, H * 0.64),
         H * 0.04, H * 0.12, (255, 252, 235, 255), 0)
    for a, r in [(20, 0.46), (150, 0.42), (250, 0.48), (320, 0.40)]:
        aa = math.radians(a)
        r0 = min(W, H) * r
        r1 = r0 + min(W, H) * 0.16
        d.line([(W * 0.5 + math.cos(aa) * r0, H * 0.5 + math.sin(aa) * r0),
                (W * 0.5 + math.cos(aa) * r1, H * 0.5 + math.sin(aa) * r1)],
               fill=GOLD, width=max(2, int(min(W, H) * 0.05)))




def w_handaxe(d, W, H, **kw):
    """短柄斧：粗短木柄 + 单侧厚斧刃。"""
    cx = W * 0.60
    CAP(d, (cx, H * 0.30), (cx, H * 0.94), W * 0.115, WOOD, 1.8)
    crescent(d, cx, H * 0.10, H * 0.52, W * 0.50, W * 0.34, STEEL, 1.9)
    crescent(d, cx, H * 0.155, H * 0.475, W * 0.45, W * 0.09, (246, 252, 255, 255), 0)
    R(d, cx - W * 0.10, H * 0.09, cx + W * 0.12, H * 0.135, GOLD, W * 0.02, 1.6)
    R(d, cx - W * 0.10, H * 0.495, cx + W * 0.12, H * 0.54, GOLD, W * 0.02, 1.6)
    glove(d, cx, H * 0.76, W * 0.135, -90)


def w_spear(d, W, H, **kw):
    """长矛：长杆 + 叶形矛头 + 金箍。"""
    cx = W * 0.5
    CAP(d, (cx, H * 0.06), (cx, H * 0.98), W * 0.095, WOOD, 1.8)
    # 矛头
    PG(d, [(cx, H * 0.01), (cx + W * 0.28, H * 0.13), (cx + W * 0.18, H * 0.30),
           (cx, H * 0.35), (cx - W * 0.18, H * 0.30), (cx - W * 0.28, H * 0.13)], STEEL, 1.9)
    PG(d, [(cx, H * 0.05), (cx + W * 0.10, H * 0.15), (cx + W * 0.06, H * 0.29),
           (cx, H * 0.32), (cx - W * 0.06, H * 0.29), (cx - W * 0.10, H * 0.15)],
       (248, 253, 255, 255), 0)
    d.line([(cx, H * 0.05), (cx, H * 0.32)], fill=(214, 232, 248, 255), width=2)
    # 金箍 + 青玉
    R(d, cx - W * 0.13, H * 0.33, cx + W * 0.13, H * 0.40, GOLD, W * 0.03, 1.7)
    E(d, cx - W * 0.07, H * 0.335, cx + W * 0.07, H * 0.395, TEAL, 1.4)
    # 缠绳
    for i in range(3):
        yy = H * (0.44 + i * 0.045)
        d.line([(cx - W * 0.10, yy), (cx + W * 0.10, yy)], fill=(120, 78, 46, 255), width=max(2, int(W * 0.03)))
    glove(d, cx, H * 0.72, W * 0.135, -90)
    glove(d, cx, H * 0.86, W * 0.135, 90)


def w_mace(d, W, H, **kw):
    """钉头锤：球首 + 放射尖刺 + 金箍。"""
    cx = W * 0.5
    CAP(d, (cx, H * 0.40), (cx, H * 0.97), W * 0.085, WOOD, 1.8)
    cy = H * 0.22
    r = min(W * 0.34, H * 0.19)
    # 尖刺
    for a in range(0, 360, 45):
        aa = math.radians(a)
        PG(d, [(cx + math.cos(aa) * r * 1.62, cy + math.sin(aa) * r * 1.62),
               (cx + math.cos(aa + 0.32) * r * 0.92, cy + math.sin(aa + 0.32) * r * 0.92),
               (cx + math.cos(aa - 0.32) * r * 0.92, cy + math.sin(aa - 0.32) * r * 0.92)], GOLD, 1.5)
    # 球体
    E(d, cx - r, cy - r, cx + r, cy + r, STEEL, 2.0)
    d.arc([cx - r * 0.62, cy - r * 0.70, cx + r * 0.44, cy + r * 0.18], 190, 300,
          fill=(250, 253, 255, 255), width=max(2, int(r * 0.22)))
    # 金箍
    R(d, cx - W * 0.10, H * 0.395, cx + W * 0.10, H * 0.445, GOLD, W * 0.03, 1.6)
    glove(d, cx, H * 0.70, W * 0.135, -90)
    glove(d, cx, H * 0.86, W * 0.135, 90)


DRAW = {
    "sword": w_sword,
    "axe": w_axe,
    "double_axe": w_double_axe,
    "bow": w_bow,
    "arrow": w_arrow,
    "fist": w_fist,
    "bomb": w_bomb,
    "staff": w_staff,
    "hammer": w_hammer,
    "boomerang": w_boomerang,
    "kunai": w_kunai,
    "handaxe": w_handaxe,
    "spear": w_spear,
    "mace": w_mace,
    "slash": w_slash,
}


def render(kind, W, H, scale=3.0):
    """按目标宽高比在高分辨率画布上绘制。"""
    global OK_
    OK_ = scale * 1.55
    w, h = int(W * scale), int(H * scale)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    DRAW[kind](d, w, h)
    return img


def breakify(img, pale=0.72):
    """损坏版：褪色发灰 + 裂纹 + X 眼。"""
    a = img.split()[3]
    rgb = img.convert("RGB")
    lum = rgb.convert("L")
    grey = Image.merge("RGB", (lum, lum, lum))
    tint = Image.new("RGB", img.size, (188, 198, 212))
    out = Image.blend(grey, tint, 0.45).convert("RGBA")
    out.putalpha(a)
    out = Image.blend(out, Image.new("RGBA", img.size, (206, 214, 226, 255)), 1 - pale - 0.05)
    out.putalpha(a)

    d = ImageDraw.Draw(out, "RGBA")
    w, h = img.size
    for (a, b) in [((0.34, 0.08), (0.46, 0.42)),
                   ((0.46, 0.42), (0.38, 0.66)),
                   ((0.58, 0.20), (0.68, 0.52))]:
        d.line([(w * a[0], h * a[1]), (w * b[0], h * b[1])], fill=(52, 58, 74, 235),
               width=max(2, int(min(w, h) * 0.022)))
    # X 眼
    ex, ey, r = w * 0.47, h * 0.50, min(w, h) * 0.055
    for s in (-1, 1):
        cx = ex + s * r * 1.5
        d.line([(cx - r, ey - r), (cx + r, ey + r)], fill=(40, 46, 62, 255), width=max(2, int(r * 0.55)))
        d.line([(cx - r, ey + r), (cx + r, ey - r)], fill=(40, 46, 62, 255), width=max(2, int(r * 0.55)))
    return out


def fit(img, W, H, bbox):
    x0, y0, x1, y1 = bbox
    bb = img.getbbox()
    if not bb:
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sub = img.crop(bb)
    tw, th = x1 - x0 + 1, y1 - y0 + 1
    s = min(tw / sub.width, th / sub.height)
    nw, nh = max(1, int(round(sub.width * s))), max(1, int(round(sub.height * s)))
    sub = sub.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sub, (int(round((x0 + x1 + 1) / 2 - nw / 2)), int(round((y0 + y1 + 1) / 2 - nh / 2))))
    return out


# ---------------------------------------------------------------- 任务表
# (相对路径, 种类, 是否损坏, 额外参数)
JOBS = [
    ("weapon01/weapon01.png",      "sword",      False),
    ("weapon01/weapon01b.png",     "sword",      True),
    ("weapon02/weapon02.png",      "hammer",     False),
    ("weapon02/weapon02b.png",     "hammer",     True),
    ("weapon03/weapon03.png",      "bow",        False),
    ("weapon03/weapon03b.png",     "bow",        True),
    ("weapon03/weapon03c.png",     "arrow",      False),
    ("weapon03/weapon03cb.png",    "arrow",      True),
    ("weapon04/weapon04.png",      "fist",       False),
    ("weapon04/weapon04b.png",     "fist",       True),
    ("weapon04bomb/weapon04Bomb.png",  "bomb",   False),
    ("weapon04bomb/weapon04bBomb.png", "bomb",   True),
    ("weapon05/weapon05.png",      "axe",        False),
    ("weapon05/weapon05b.png",     "axe",        True),
    ("weapon06/weapon06.png",      "spear",      False),
    ("weapon06/weapon06b.png",     "spear",      True),
    ("weapon07/weapon07.png",      "handaxe",    False),
    ("weapon07/weapon07b.png",     "handaxe",    True),
    ("weapon08/weapon08.png",      "mace",       False),
    ("weapon08/weapon08b.png",     "mace",       True),
    ("weapon09/weapon09.png",      "kunai",      False),
    ("weapon09/weapon09b.png",     "kunai",      True),
    ("weapon09/weapon09_d1.png",   "kunai",      True),
    ("weapon09/weapon09_hit.png",  "slash",      False),
]


def main():
    import json
    meta_p = os.path.join(HERE, "weapon_frames.json")
    meta = json.load(open(meta_p, encoding="utf-8"))
    only = sys.argv[1:] or None
    for rel, kind, broken in JOBS:
        key = os.path.basename(rel)[:-4]
        if only and key not in only:
            continue
        info = meta[key]
        W, Hh = info["size"]
        img = render(kind, W, Hh, scale=3.0)
        if broken:
            img = breakify(img)
        out = fit(img, W, Hh, info["bbox"])
        assert out.size == (W, Hh), (key, out.size)
        out.save(os.path.join(ROOT, "Assets", "Resources", "weapons", rel))
        print("saved", rel, out.size)




def motion_trail(kind, W, H):
    """残影：3 层拖尾 + 1 层清晰本体。"""
    base = render(kind, W * 0.42, H * 0.86, 3.0)
    out = Image.new("RGBA", (int(W * 3), int(H * 3)), (0, 0, 0, 0))
    lay = [(-0.30, 0.00, 80), (-0.16, 0.02, 110), (0.00, 0.03, 200), (0.10, 0.05, 255)]
    for dx, dy, al in lay:
        ghost = base.copy()
        a = ghost.split()[3].point(lambda v, al=al: int(v * al / 255))
        ghost.putalpha(a)
        if al < 200:
            ghost = ghost.filter(ImageFilter.GaussianBlur(max(1, W * 0.02)))
        out.alpha_composite(ghost, (int(out.width * (0.10 + dx)), int(out.height * dy)))
    return out


JOBS_EXTRA = [
    ("weapon09/weapon09_blur.png", "kunai"),
]


def main_all():
    main()
    import json
    meta = json.load(open(os.path.join(HERE, "weapon_frames.json"), encoding="utf-8"))
    for rel, kind in JOBS_EXTRA:
        key = os.path.basename(rel)[:-4]
        info = meta[key]
        W, Hh = info["size"]
        img = motion_trail(kind, W, Hh)
        out = fit(img, W, Hh, info["bbox"])
        assert out.size == (W, Hh)
        out.save(os.path.join(ROOT, "Assets", "Resources", "weapons", rel))
        print("saved", rel, out.size)


if __name__ == "__main__":
    main_all()
