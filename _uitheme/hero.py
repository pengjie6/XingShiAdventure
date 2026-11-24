# -*- coding: utf-8 -*-
"""主角重绘：月辉旅人（hero00）。

设计依据 = Pollinations 生成的概念图（深蓝兜帽 + 金边 + 深棕刘海 + 奶白脸 + 青玉内衬）。

原则：
1. 画布尺寸与原始帧逐帧一致（不动 .meta、不动 pivot、不动引用）；
2. 内容包围盒对齐原始帧的包围盒（底对齐 + 水平居中），保证站位/碰撞不偏移；
3. 扁平硬边 + 粗描边，与游戏内其余贴图同一语言。
"""
import os, sys, math
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPR = os.path.join(ROOT, "Assets", "Sprites")

# ---------------------------------------------------------------- 调色
# 层次：斗篷最暗 → 兜帽 → 袖子最亮，保证小块画布上肢体可分辨
INK      = (10, 20, 34, 255)
CLOAK    = (20, 42, 68, 255)     # 斗篷（最暗，退后）
CLOAK_L  = (34, 62, 96, 255)     # 斗篷受光面
HOOD     = (30, 60, 96, 255)     # 兜帽
HOOD_L   = (52, 94, 138, 255)    # 兜帽高光
SLEEVE   = (56, 100, 146, 255)   # 袖子（最亮，前压）
SLEEVE_D = (36, 70, 108, 255)
GOLD     = (244, 181, 76, 255)
GOLD_L   = (255, 216, 152, 255)
GOLD_D   = (172, 106, 36, 255)
CREAM    = (246, 235, 214, 255)
CREAM_S  = (218, 196, 164, 255)
HAIR     = (62, 38, 26, 255)
HAIR_L   = (104, 66, 42, 255)
TEAL     = (46, 168, 158, 255)
TEAL_D   = (22, 100, 96, 255)
PANT     = (62, 82, 110, 255)
BOOT     = (58, 40, 30, 255)
BOOT_L   = (86, 60, 42, 255)
EYE      = (24, 32, 50, 255)
WHITE    = (255, 255, 255, 255)
BLUSH    = (232, 148, 138, 255)
STEEL    = (206, 224, 240, 255)
STEEL_D  = (136, 162, 188, 255)
WOOD     = (124, 82, 48, 255)

K = 4
CW, CH = 780, 720
OX, OY = 390, 170


def P(x, y):
    return (OX + x * K, OY + y * K)


def S(v):
    return v * K


# ---------------------------------------------------------------- 基元
def cap(d, a, b, w, fill, ow=1.5):
    A, B = P(*a), P(*b)
    W, OW = S(w), S(ow)
    d.line([A, B], fill=INK, width=int(W + 2 * OW))
    for p in (A, B):
        r = W / 2 + OW
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=INK)
    d.line([A, B], fill=fill, width=int(W))
    for p in (A, B):
        r = W / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def poly(d, pts, fill, ow=1.5, outline=INK):
    PP = [P(*p) for p in pts]
    d.polygon(PP, fill=fill)
    if ow:
        d.line(PP + [PP[0]], fill=outline, width=max(1, int(S(ow))), joint="curve")


def ell(d, cx, cy, rx, ry, fill, ow=1.5, outline=INK):
    d.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], fill=fill,
              outline=outline, width=max(1, int(S(ow))) if ow else 0)


def arc(d, cx, cy, rx, ry, a0, a1, fill, w):
    d.arc([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], a0, a1, fill=fill,
          width=max(1, int(S(w))))


def tail(d, p0, p1, p2, w0, w1, fill, n=18):
    """沿二次贝塞尔生成一条由粗到细的带（帽尾/飘带）。"""
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
    poly(d, A + B[::-1], fill, 1.5)


# ---------------------------------------------------------------- 头
def head(d, cx, cy, rx=25.0, ry=24.0, expr="smile", hood=True, tilt=0.0,
         hair_shown=True, eye_dy=0.0):
    if hood:
        # 下垂帽尾：从帽子左上甩出、往上拱再垂下来，收成尖
        tail(d,
             (cx - rx * 0.34, cy - ry * 0.84),
             (cx - rx * 1.20, cy - ry * 1.58),
             (cx - rx * 1.56, cy - ry * 0.94),
             11.5, 2.0, HOOD)
        # 帽尾内侧受光
        tail(d,
             (cx - rx * 0.60, cy - ry * 0.92),
             (cx - rx * 1.18, cy - ry * 1.40),
             (cx - rx * 1.44, cy - ry * 1.04),
             4.0, 0.8, HOOD_L)

    # 兜帽主体
    ell(d, cx, cy, rx, ry, HOOD, 1.6)
    arc(d, cx, cy, rx * 0.82, ry * 0.82, 200, 312, HOOD_L, 2.2)
    # 帽侧金扣
    ell(d, cx - rx * 0.80, cy - ry * 0.34, 2.2, 2.2, GOLD, 1.2)

    # 脸
    fx, fy = cx + rx * 0.04, cy + ry * 0.13
    frx, fry = rx * 0.72, ry * 0.69
    ell(d, fx, fy, frx, fry, CREAM, 0)
    arc(d, fx, fy, frx * 0.98, fry * 0.98, 24, 156, CREAM_S, 1.6)

    # 帽檐金边（沿脸部开口）
    arc(d, fx, fy, frx * 1.10, fry * 1.10, 176, 364, GOLD, 1.5)
    arc(d, fx, fy, frx * 1.24, fry * 1.24, 178, 362, INK, 0.7)

    # 刘海
    if hair_shown:
        hy = fy - fry * 0.50
        for k, sx in enumerate((-0.66, -0.24, 0.20, 0.62)):
            bx = fx + frx * sx
            bw = frx * 0.32
            bh = fry * (0.50 + 0.09 * (k % 2))
            d.pieslice([P(bx - bw, hy - bh * 0.42), P(bx + bw, hy + bh * 0.98)],
                       180, 360, fill=HAIR)
        d.line([P(fx - frx * 0.44, fy - fry * 0.58), P(fx - frx * 0.22, fy - fry * 0.84)],
               fill=HAIR_L, width=max(2, int(S(0.9))))
        d.line([P(fx + frx * 0.10, fy - fry * 0.60), P(fx + frx * 0.32, fy - fry * 0.86)],
               fill=HAIR_L, width=max(2, int(S(0.9))))

    # 表情
    ey = fy + fry * 0.16 + eye_dy
    dx = frx * 0.40
    if expr == "dead":
        for s in (-1, 1):
            x0 = fx + s * dx
            d.line([P(x0 - 2.4, ey - 2.4), P(x0 + 2.4, ey + 2.4)], fill=EYE, width=max(2, int(S(1.4))))
            d.line([P(x0 - 2.4, ey + 2.4), P(x0 + 2.4, ey - 2.4)], fill=EYE, width=max(2, int(S(1.4))))
    elif expr == "hurt":
        for s in (-1, 1):
            x0 = fx + s * dx
            d.line([P(x0 - 2.7, ey - 2.0), P(x0, ey + 1.2), P(x0 + 2.7, ey - 2.0)],
                   fill=EYE, width=max(2, int(S(1.3))), joint="curve")
    elif expr == "fierce":
        for s_ in (-1, 1):
            x0 = fx + s_ * dx
            ell(d, x0, ey + 0.8, 2.6, 2.4, EYE, 0)
            d.ellipse([P(x0 - 1.6, ey - 1.2), P(x0 - 0.2, ey + 0.3)], fill=WHITE)
            # 皱眉：外高内低
            d.line([P(x0 + s_ * 3.2, ey - 4.6), P(x0 - s_ * 3.2, ey - 3.0)],
                   fill=HAIR, width=max(2, int(S(1.5))))
    elif expr in ("happy", "win"):
        for s in (-1, 1):
            x0 = fx + s * dx
            arc(d, x0, ey + 1.2, 2.9, 2.6, 200, 340, EYE, 1.5)
    else:
        er = 3.1 if expr == "surprised" else 2.9
        for s in (-1, 1):
            x0 = fx + s * dx
            ell(d, x0, ey, er, er * 1.06, EYE, 0)
            d.ellipse([P(x0 - er * 0.66, ey - er * 0.80), P(x0 - er * 0.06, ey - er * 0.08)],
                      fill=WHITE)

    # 嘴
    my = fy + fry * 0.64
    if expr in ("happy", "win"):
        d.chord([P(fx - 5.0, my - 3.2), P(fx + 5.0, my + 4.6)], 180, 360, fill=(112, 38, 42, 255))
        d.chord([P(fx - 3.2, my + 1.2), P(fx + 3.2, my + 4.0)], 180, 360, fill=(234, 130, 128, 255))
    elif expr == "surprised":
        ell(d, fx, my + 0.6, 2.3, 2.9, (112, 38, 42, 255), 0)
    elif expr == "hurt":
        d.arc([P(fx - 3.6, my - 2.8), P(fx + 3.6, my + 2.8)], 20, 160,
              fill=(112, 38, 42, 255), width=max(2, int(S(1.2))))
    elif expr == "dead":
        d.arc([P(fx - 3.2, my - 3.2), P(fx + 3.2, my + 2.2)], 20, 160,
              fill=(112, 38, 42, 255), width=max(2, int(S(1.2))))
    else:
        arc(d, fx, my - 1.6, 3.3, 3.0, 20, 160, (112, 38, 42, 255), 1.4)

    if expr != "dead":
        for s in (-1, 1):
            ell(d, fx + s * frx * 0.64, ey + 2.8, 2.2, 1.5, BLUSH, 0)


# ---------------------------------------------------------------- 四肢
def arm(d, sh, hand, w=6.2, bend=0.5, sleeve=SLEEVE, glove=True):
    mx, my = (sh[0] + hand[0]) / 2, (sh[1] + hand[1]) / 2
    dx, dy = hand[0] - sh[0], hand[1] - sh[1]
    L = math.hypot(dx, dy) or 1.0
    px, py = -dy / L, dx / L
    el = (mx + px * bend * L * 0.30, my + py * bend * L * 0.30)
    cap(d, sh, el, w, sleeve)
    cap(d, el, hand, w * 0.88, sleeve)
    # 袖口金边
    d.line([P(hand[0] - px * w * 0.42, hand[1] - py * w * 0.42),
            P(hand[0] + px * w * 0.42, hand[1] + py * w * 0.42)],
           fill=GOLD_D, width=max(2, int(S(0.9))))
    if glove:
        ell(d, hand[0], hand[1], w * 0.58, w * 0.58, CREAM, 1.3)


def leg(d, hip, foot, w=7.6, bend=0.0, pant=PANT):
    mx, my = (hip[0] + foot[0]) / 2, (hip[1] + foot[1]) / 2
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    L = math.hypot(dx, dy) or 1.0
    px, py = -dy / L, dx / L
    kn = (mx + px * bend * L * 0.30, my + py * L * 0.10)
    cap(d, hip, kn, w, pant)
    cap(d, kn, foot, w * 0.86, pant)
    # 靴筒
    ell(d, foot[0], foot[1] - 1.2, w * 0.80, w * 0.62, BOOT, 1.3)
    # 靴口
    d.arc([P(foot[0] - w * 0.72, foot[1] - 2.8), P(foot[0] + w * 0.72, foot[1] + 1.4)],
          196, 344, fill=GOLD_D, width=max(2, int(S(0.9))))


# ---------------------------------------------------------------- 武器（月牙刃）
def weapon(d, hand, ang, scale=1.0):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux

    def W(t, v):
        return (hand[0] + (ux * t + vx * v) * scale,
                hand[1] + (uy * t + vy * v) * scale)

    cap(d, W(-16, 0), W(1, 0), 3.2 * scale, WOOD, 1.3)
    ell(d, *W(-16.5, 0), 2.4 * scale, 2.4 * scale, GOLD, 1.2)
    cap(d, W(1.2, -5.4), W(1.2, 5.4), 2.2 * scale, GOLD, 1.2)
    poly(d, [W(3.2, -4.0), W(15, -4.6), W(23.5, 0.0), W(15, 4.6), W(3.2, 4.0)],
         STEEL, 1.4)
    poly(d, [W(4.6, -2.6), W(14, -3.0), W(20.4, -0.2), W(14, -0.6), W(4.6, -0.4)],
         (246, 252, 255, 255), 0)
    d.line([P(*W(4.6, 3.2)), P(*W(14, 3.7)), P(*W(22.0, 0.4))], fill=TEAL,
           width=max(2, int(S(0.9) * scale)), joint="curve")


# ---------------------------------------------------------------- 身体
def cloak(d, cx, cy, wid=11.5, bottom=86.0):
    poly(d, [(cx - wid - 1.5, cy + 1.5), (cx + wid + 1.5, cy + 1.5),
             (cx + wid + 8.5, bottom - 4), (cx + wid + 5.0, bottom),
             (cx - wid - 5.0, bottom), (cx - wid - 8.5, bottom - 4)], CLOAK, 1.6)
    # 内衬受光
    poly(d, [(cx + wid - 2, cy + 6), (cx + wid + 1, cy + 6),
             (cx + wid + 6, bottom - 3), (cx + wid + 3, bottom - 1)], CLOAK_L, 0)
    # 斗篷下摆金线
    d.line([P(cx - wid - 7.6, bottom - 3.4), P(cx - wid - 4.4, bottom - 1.4),
            P(cx + wid + 4.4, bottom - 1.4), P(cx + wid + 7.6, bottom - 3.4)],
           fill=GOLD_D, width=max(2, int(S(0.9))), joint="curve")


def tunic(d, cx, cy, wid=11.0, hipy=None):
    hipy = cy + 26 if hipy is None else hipy
    # 肩甲（把手臂根遮住，读起来才有"衣服"的结构）
    poly(d, [(cx - wid - 2.6, cy + 0.4), (cx - wid * 0.30, cy - 2.6),
             (cx + wid * 0.30, cy - 2.6), (cx + wid + 2.6, cy + 0.4),
             (cx + wid + 0.6, cy + 6.4), (cx - wid - 0.6, cy + 6.4)], CLOAK, 1.5)
    d.line([P(cx - wid - 1.6, cy + 5.6), P(cx + wid + 1.6, cy + 5.6)],
           fill=GOLD, width=max(2, int(S(1.2))))

    poly(d, [(cx - wid * 0.92, cy + 3), (cx + wid * 0.92, cy + 3),
             (cx + wid * 0.86, hipy), (cx - wid * 0.86, hipy)], TEAL, 1.5)
    # 前襟
    poly(d, [(cx - 2.0, cy + 3), (cx + 2.0, cy + 3),
             (cx + 1.4, hipy - 6.5), (cx - 1.4, hipy - 6.5)], TEAL_D, 0)
    # 腰带
    poly(d, [(cx - wid * 0.94, hipy - 6.6), (cx + wid * 0.94, hipy - 6.6),
             (cx + wid * 0.94, hipy - 2.2), (cx - wid * 0.94, hipy - 2.2)], GOLD, 1.3)
    ell(d, cx, hipy - 4.4, 2.3, 1.9, GOLD_L, 1.1)


# ---------------------------------------------------------------- 组合
def figure(p):
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    drop = p.get("drop", 0.0)
    hx, hy = p.get("head", (0.0, 27.0))
    hy += drop
    sh_y = p.get("sh_y", 53.0) + drop
    hipy = sh_y + p.get("torso_h", 26.0)

    sl = (hx - 10.5, sh_y + 2.0)
    sr = (hx + 10.5, sh_y + 2.0)
    hip_l = (hx - 6.6, hipy)
    hip_r = (hx + 6.6, hipy)

    feet = p.get("feet", ((-8.5, 99.0), (9.0, 99.0)))
    hands = p.get("hands", ((-19.0, 74.0), (19.0, 74.0)))
    expr = p.get("expr", "smile")
    legb = p.get("legbend", (0.0, 0.0))

    # 1 斗篷（最底）
    if p.get("cloak", True):
        cloak(d, hx, sh_y, bottom=hipy + 9)
    # 2 腿
    leg(d, hip_l, feet[0], bend=legb[0])
    leg(d, hip_r, feet[1], bend=legb[1])
    # 3 后手
    arm(d, sl, hands[0], bend=-0.55, sleeve=SLEEVE_D)
    # 4 衣服
    tunic(d, hx, sh_y, hipy=hipy)
    # 5 头
    head(d, hx, hy, expr=expr, hood=p.get("hood", True),
         hair_shown=p.get("hair", True), eye_dy=p.get("eye_dy", 0.0))
    # 6 武器
    wp = p.get("weapon")
    if wp:
        weapon(d, hands[1], wp[0], wp[1] if len(wp) > 1 else 1.0)
    # 7 前手
    arm(d, sr, hands[1], bend=0.55, sleeve=SLEEVE)

    return img


def fit(img, target):
    w, h, (x0, y0, x1, y1) = target
    bb = img.getbbox()
    if not bb:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sub = img.crop(bb)
    tw, th = x1 - x0 + 1, y1 - y0 + 1
    s = min(tw / sub.width, th / sub.height)
    nw, nh = max(1, int(round(sub.width * s))), max(1, int(round(sub.height * s)))
    sub = sub.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(sub, (int(round((x0 + x1 + 1) / 2 - nw / 2)), int(round(y1 + 1 - nh))))
    return out


# ---------------------------------------------------------------- 姿势表
POSES = {
    "idle": dict(head=(0, 27), hands=((-19, 75), (19, 75)),
                 feet=((-8.5, 99), (9, 99)), expr="smile", legbend=(-0.4, 0.4)),

    "weapon": dict(head=(0, 27), hands=((-19, 76), (16, 69)),
                   feet=((-9, 99), (9.5, 99)), expr="smile",
                   weapon=(-34, 1.0), legbend=(-0.4, 0.4)),

    "run01": dict(head=(2.5, 27), hands=((-15, 64), (24, 80)),
                  feet=((-16, 99), (17, 92)), expr="smile",
                  weapon=(-30, 0.95), legbend=(-0.9, 0.9), sh_y=54),

    "run02": dict(head=(2.5, 27), hands=((-24, 80), (15, 64)),
                  feet=((-16, 92), (16, 99)), expr="smile",
                  weapon=(-22, 0.95), legbend=(0.9, -0.9), sh_y=54),

    "jump": dict(head=(0, 27), hands=((-27, 47), (26, 46)),
                 feet=((-11, 84), (9, 89)), expr="smile",
                 weapon=(-58, 1.0), legbend=(-1.1, 1.1), sh_y=52),

    "attack": dict(head=(2.5, 26), hands=((-22, 61), (23, 31)),
                   feet=((-16, 99), (15, 99)), expr="fierce",
                   weapon=(-68, 1.0), legbend=(-0.6, 0.6), sh_y=53),

    "hit01": dict(head=(-4.5, 27), hands=((-27, 63), (26, 72)),
                  feet=((-11, 99), (10, 99)), expr="hurt",
                  weapon=(-40, 0.9), legbend=(-0.3, 0.3)),

    "hit02": dict(head=(-7, 29), hands=((-30, 58), (28, 69)),
                  feet=((-14, 99), (11, 99)), expr="hurt",
                  weapon=(-54, 0.9), legbend=(-0.5, 0.2)),

    "dodge": dict(head=(-5, 33), hands=((-25, 69), (21, 61)),
                  feet=((-13, 99), (12, 99)), expr="hurt",
                  weapon=(-66, 0.85), legbend=(-1.0, 1.0), drop=6),

    "death01": dict(head=(-5, 28), hands=((-28, 60), (27, 73)),
                    feet=((-10, 99), (11, 99)), expr="hurt",
                    weapon=(38, 0.9), legbend=(-0.2, 0.2)),
    "death02": dict(head=(-7, 30), hands=((-31, 64), (30, 77)),
                    feet=((-13, 99), (13, 99)), expr="dead",
                    weapon=(56, 0.85), legbend=(-0.4, 0.4)),
    "death03": dict(head=(-1, 30), hands=((-31, 66), (31, 79)),
                    feet=((-12, 99), (12, 99)), expr="dead",
                    weapon=(72, 0.85), legbend=(-0.2, 0.2)),

    "surprised": dict(head=(0, 26), hands=((-27, 51), (27, 50)),
                      feet=((-9, 99), (10, 99)), expr="surprised",
                      weapon=(82, 0.95), legbend=(-0.3, 0.3), sh_y=53),

    "win": dict(head=(0, 26), hands=((-28, 43), (28, 42)),
                feet=((-9, 99), (10, 99)), expr="win",
                weapon=(-72, 1.0), legbend=(-0.3, 0.3), sh_y=53),
}

ROT = {"death02": -18, "death03": -88, "dodge": -12}


def build_frame(name, size, bbox):
    img = figure(POSES[name])
    ang = ROT.get(name)
    if ang:
        img = img.rotate(ang, resample=Image.BICUBIC, expand=True)
    return fit(img, (size[0], size[1], bbox))


def main():
    import json
    meta = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "hero_frames.json"), encoding="utf-8"))
    only = sys.argv[1:] or None
    for name, info in meta.items():
        if only and name not in only:
            continue
        out = build_frame(name, tuple(info["size"]), tuple(info["bbox"]))
        assert out.size == tuple(info["size"]), (name, out.size, info["size"])
        out.save(os.path.join(SPR, "hero00_%s.png" % name))
        print("saved", name, out.size)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------- 头像（半身）
def bust_frame(size, expr="smile", crop=(-46, -16, 32, 80)):
    """半身像：头部占满画面，躯干在底部被裁切（与原头像构图一致）。"""
    p = dict(POSES["idle"])
    p["expr"] = expr
    p.pop("weapon", None)
    img = figure(p)
    a = P(crop[0], crop[1])
    b = P(crop[2], crop[3])
    sub = img.crop((int(a[0]), int(a[1]), int(b[0]), int(b[1])))

    W, H = size
    s = max(W / sub.width, H / sub.height)
    nw, nh = int(round(sub.width * s)), int(round(sub.height * s))
    sub = sub.resize((nw, nh), Image.LANCZOS)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sub, ((W - nw) // 2, 0))
    return out


def main_bust():
    # UI_hero00 / _happy 在原工程里就是 idle / win 帧的副本，直接复用帧图，零风险
    jobs = [
        ("Assets/Resources/heroes/UI_hero00.png", (95, 112), "idle"),
        ("Assets/Resources/heroes/UI_hero00_happy.png", (95, 108), "win"),
    ]
    for rel, size, frame in jobs:
        out = build_frame(frame, size, (2, 1, size[0] - 2, size[1] - 3))
        assert out.size == size
        out.save(os.path.join(ROOT, rel))
        print("saved", rel, out.size, "<-", frame)
    # 奖励卡是大图半身像
    out = bust_frame((191, 192), "smile")
    out.save(os.path.join(ROOT, "Assets/Resources/UI/UI_reward_hero00.png"))
    print("saved UI_reward_hero00.png", out.size)
