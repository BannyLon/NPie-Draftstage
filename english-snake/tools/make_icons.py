#!/usr/bin/env python3
"""
生成 Snake English 的 PWA 图标 PNG（192/512），仅使用 Python 标准库。

设计：
- 深色圆角方形背景（径向渐变）
- 蛇身：青→紫渐变的圆角折线（用“粗线 + 圆头”近似 stroke-linecap=round）
- 蛇头：渐变圆 + 黑色眼睛 + 白色高光
- 食豆：发光黄橙圆 + 白色高光

仅依赖 zlib + struct 手写 PNG，无需 PIL。
"""
import math
import struct
import zlib
import os


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# 深色径向渐变背景（cx=0.5, cy=0.35）
BG_CENTER = hex_rgb("#16203b")
BG_MID = hex_rgb("#0b1224")
BG_EDGE = hex_rgb("#050816")
SNAKE_A = hex_rgb("#22d3ee")
SNAKE_B = hex_rgb("#a78bfa")
ORB_CORE = hex_rgb("#fde68a")
ORB_MID = hex_rgb("#f59e0b")
ORB_EDGE = hex_rgb("#b45309")


def make_canvas(size):
    # 像素缓冲：每点 [r,g,b,a]
    return [[[0, 0, 0, 0] for _ in range(size)] for _ in range(size)]


def blend(px, x, y, color, alpha):
    """把颜色按 alpha 叠加到 (x,y) 像素上。"""
    if x < 0 or y < 0 or x >= len(px) or y >= len(px):
        return
    r, g, b = color
    a = alpha
    # 简单 over 合成
    ea = px[y][x][3] / 255.0
    da = a / 1.0  # alpha 是 0..1
    out_a = da + ea * (1 - da)
    if out_a <= 0:
        return
    px[y][x][0] = int((r * da + px[y][x][0] * ea * (1 - da)) / out_a)
    px[y][x][1] = int((g * da + px[y][x][1] * ea * (1 - da)) / out_a)
    px[y][x][2] = int((b * da + px[y][x][2] * ea * (1 - da)) / out_a)
    px[y][x][3] = int(out_a * 255)


def fill_bg(px):
    size = len(px)
    cx, cy = size * 0.5, size * 0.35
    maxr = size * 0.75
    for y in range(size):
        for x in range(size):
            dx = x - cx
            dy = y - cy
            r = math.sqrt(dx * dx + dy * dy) / maxr
            r = clamp(r, 0, 1)
            if r < 0.55:
                t = r / 0.55
                col = tuple(int(lerp(BG_CENTER[i], BG_MID[i], t)) for i in range(3))
            else:
                t = (r - 0.55) / 0.45
                col = tuple(int(lerp(BG_MID[i], BG_EDGE[i], t)) for i in range(3))
            px[y][x][0] = col[0]
            px[y][x][1] = col[1]
            px[y][x][2] = col[2]
            px[y][x][3] = 255


def round_rect_mask(size, radius):
    """返回布尔掩码：圆角方形内为 True。"""
    m = [[False] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            # 到四角的距离判断
            inside = True
            for (cx, cy) in [(radius, radius), (size - radius, radius),
                             (radius, size - radius), (size - radius, size - radius)]:
                if (x < radius or x > size - radius) and (y < radius or y > size - radius):
                    dx = x - cx
                    dy = y - cy
                    if dx * dx + dy * dy > radius * radius:
                        inside = False
                        break
            m[y][x] = inside
    return m


def apply_mask(px, mask):
    size = len(px)
    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                px[y][x][3] = 0


def fill_disc(px, cx, cy, radius, color, alpha_fn=None):
    """以 (cx,cy) 圆心、radius 半径填充圆，支持每点自定义 alpha。"""
    size = len(px)
    r2 = radius * radius
    x0 = int(cx - radius - 1)
    x1 = int(cx + radius + 1)
    y0 = int(cy - radius - 1)
    y1 = int(cy + radius + 1)
    for y in range(max(0, y0), min(size, y1)):
        for x in range(max(0, x0), min(size, x1)):
            dx = x - cx
            dy = y - cy
            d2 = dx * dx + dy * dy
            if d2 <= r2:
                # 边缘抗锯齿
                d = math.sqrt(d2)
                edge = clamp(radius - d, 0, 1)
                a = alpha_fn(x, y, d) if alpha_fn else edge
                if a > 0:
                    blend(px, x, y, color, clamp(a, 0, 1))


def radial_disc(px, cx, cy, radius, stops):
    """径向渐变圆。stops: [(t,color)] 升序。"""
    size = len(px)
    r2 = radius * radius
    x0 = int(cx - radius - 1)
    x1 = int(cx + radius + 1)
    y0 = int(cy - radius - 1)
    y1 = int(cy + radius + 1)
    for y in range(max(0, y0), min(size, y1)):
        for x in range(max(0, x0), min(size, x1)):
            dx = x - cx
            dy = y - cy
            d2 = dx * dx + dy * dy
            if d2 <= r2:
                d = math.sqrt(d2)
                t = d / radius
                # 查找相邻 stops
                col = stops[0][1]
                for i in range(len(stops) - 1):
                    t0, c0 = stops[i]
                    t1, c1 = stops[i + 1]
                    if t0 <= t <= t1:
                        local = (t - t0) / (t1 - t0) if t1 > t0 else 0
                        col = tuple(int(lerp(c0[k], c1[k], local)) for k in range(3))
                        break
                else:
                    col = stops[-1][1]
                edge = clamp(radius - d, 0, 1)
                blend(px, x, y, col, edge)


def fill_thick_segment(px, p0, p1, radius, color_fn):
    """在两点间画一条“圆头粗线”（球扫掠近似 stroke-linecap=round）。
    color_fn(t)->color, t 沿 0..1。"""
    x0, y0 = p0
    x1, y1 = p1
    length = math.hypot(x1 - x0, y1 - y0)
    if length < 1e-6:
        fill_disc(px, x0, y0, radius, color_fn(0))
        return
    # 在画线上每隔 step 步进一个圆盘
    steps = max(1, int(length))
    for i in range(steps + 1):
        t = i / steps
        cx = lerp(x0, x1, t)
        cy = lerp(y0, y1, t)
        fill_disc(px, cx, cy, radius, color_fn(t))


def draw_glow(px, draw_fn, radius_extra=10, alpha=0.18):
    """对绘制动作做一次模糊辉光（粗暴版：放大半径、低 alpha 再画一遍）。"""
    pass  # 直接在主绘制中用半透明大圆即可，这里保持占位


def render(size):
    px = make_canvas(size)
    fill_bg(px)

    # 圆角方形蒙版
    radius = int(size * 96 / 512)
    mask = round_rect_mask(size, radius)
    apply_mask(px, mask)

    s = size / 512.0  # 缩放因子

    # 蛇身路径采样点（近似 Q 二次贝塞尔，直接用二次曲线参数式）
    def bezier(p0, pc, p2, n=40):
        pts = []
        for i in range(n + 1):
            t = i / n
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * pc[0] + t * t * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * pc[1] + t * t * p2[1]
            pts.append((x * s, y * s))
        return pts

    # 三段二次曲线拼出“L”形蛇身（左下→中→右上）
    seg1 = bezier((150, 360), (150, 250), (250, 250))
    seg2 = bezier((250, 250), (360, 250), (360, 175))
    seg3 = bezier((360, 175), (360, 130), (310, 130))
    path = seg1 + seg2[1:] + seg3[1:]
    total = len(path)

    body_r = 23 * s

    # 辉光：先画一圈低透明大圆
    for i, (cx, cy) in enumerate(path):
        glow_col = SNAKE_A if i / total < 0.5 else SNAKE_B
        fill_disc(px, cx, cy, body_r + 8 * s, glow_col, alpha_fn=lambda *a: 0.10)

    # 蛇身主体：沿路径画渐变粗线
    def body_color(t):
        return tuple(int(lerp(SNAKE_A[k], SNAKE_B[k], t)) for k in range(3))

    for i in range(total - 1):
        t0 = i / total
        t1 = (i + 1) / total
        col = body_color((t0 + t1) / 2)

        def cf(t, c=col):
            return c
        fill_thick_segment(px, path[i], path[i + 1], body_r, cf)

    # 蛇头（在 path 末端）
    hx, hy = path[-1]
    head_r = 40 * s
    radial_disc(px, hx, hy, head_r, [(0.0, SNAKE_A), (1.0, SNAKE_B)])
    # 辉光
    fill_disc(px, hx, hy, head_r + 8 * s, SNAKE_A, alpha_fn=lambda *a: 0.10)

    # 蛇眼
    eye_r = 9 * s
    e1 = (hx + 12 * s, hy - 12 * s)
    e2 = (hx - 14 * s, hy - 12 * s)
    fill_disc(px, *e1, eye_r, hex_rgb("#0b1020"), alpha_fn=lambda *a: 1.0)
    fill_disc(px, *e2, eye_r, hex_rgb("#0b1020"), alpha_fn=lambda *a: 1.0)
    fill_disc(px, e1[0] + 3 * s, e1[1] - 2 * s, 3 * s, hex_rgb("#ffffff"), alpha_fn=lambda *a: 1.0)
    fill_disc(px, e2[0] + 3 * s, e2[1] - 2 * s, 3 * s, hex_rgb("#ffffff"), alpha_fn=lambda *a: 1.0)

    # 食豆
    ox, oy = 150 * s, 360 * s
    orb_r = 34 * s
    radial_disc(px, ox, oy, orb_r, [(0.0, ORB_CORE), (0.6, ORB_MID), (1.0, ORB_EDGE)])
    fill_disc(px, ox, oy, orb_r + 8 * s, ORB_MID, alpha_fn=lambda *a: 0.12)
    # 食豆高光
    fill_disc(px, ox - 10 * s, oy - 10 * s, 8 * s, hex_rgb("#ffffff"), alpha_fn=lambda *a: 0.6)

    return px


def write_png(px, path):
    size = len(px)
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0
        for x in range(size):
            r, g, b, a = px[y][x]
            raw.extend((r, g, b, a))
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return c + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.dirname(here)
    for size in (192, 512):
        px = render(size)
        out = os.path.join(out_dir, f"icon-{size}.png")
        write_png(px, out)
        print(f"wrote {out} ({size}x{size})")


if __name__ == "__main__":
    main()
