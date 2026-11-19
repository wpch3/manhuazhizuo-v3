"""可复用漫画排版引擎（lv1 起用）。

- 椭圆对白气泡：使用 assets 中 MIT 许可的 speechbubble 闭合轮廓，
  尾巴与气泡是同一闭合路径，填充与描边各一次，不产生根部内线。
- 文字按真实 glyph bbox 居中；所有可见角点必须落在椭圆安全半径内。
- 矩形旁白框只用于旁白/画外/黑页。
- 全部文字层 2 倍超采样后下采样，保证手机端细线清晰。
"""
from __future__ import annotations

import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from speech_bubble_geometry import oval_speech

ROOT = Path(__file__).resolve().parents[1]
FONT_REG = ROOT / "assets/fonts/NotoSansCJKsc-Regular.otf"
FONT_BOLD = ROOT / "assets/fonts/NotoSansCJKsc-Bold.otf"

PAGE_W, PAGE_H = 1440, 1920
SS = 2  # supersample

PAPER = (246, 241, 231)
BUBBLE = (253, 251, 245)
INK = (58, 54, 51)
INK_SOFT = (96, 88, 80)
CREAM = (247, 240, 226)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)


# ---------------------------------------------------------------- art prep
def grade_art(im: Image.Image, seed: int = 0) -> Image.Image:
    """轻微统一色温，让各页拼在一本书里不跳。"""
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx, yy = xx / max(1, w - 1), yy / max(1, h - 1)
    light = 1.02 + 0.03 * (1 - xx) + 0.012 * (1 - yy)
    light -= 0.02 * ((xx - 0.45) ** 2 + (yy - 0.42) ** 2)
    a *= light[..., None]
    a[..., 0] *= 1.010
    a[..., 2] *= 0.990
    rng = np.random.default_rng(seed)
    a += rng.normal(0, 0.5, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def prep_page(art_path: Path, seed: int = 0) -> Image.Image:
    """原画可以是 PNG，也可以是压缩后的 WebP（同名不同后缀任选其一）。"""
    art_path = Path(art_path)
    if not art_path.exists():
        for ext in (".webp", ".png", ".jpg"):
            alt = art_path.with_suffix(ext)
            if alt.exists():
                art_path = alt
                break
        else:
            raise FileNotFoundError(f"找不到原画：{art_path}")
    im = Image.open(art_path).convert("RGB").resize((PAGE_W, PAGE_H), Image.Resampling.LANCZOS)
    return grade_art(im, seed)


def erase_ellipses(im: Image.Image, ellipses, radius: int = 110, paper_mix: float = 0.55,
                   feather: int = 26) -> Image.Image:
    """用重度失焦+纸色混合擦掉生成图自带的空白气泡，边界羽化后不留硬边。"""
    w, h = im.size
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    for cx, cy, rx, ry in ellipses:
        md.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))

    blurred = im.filter(ImageFilter.GaussianBlur(radius))
    paper = Image.new("RGB", im.size, PAPER)
    fill = Image.blend(blurred, paper, paper_mix)
    im = im.copy()
    im.paste(fill, (0, 0), mask)
    # 再叠一层更细的模糊过渡，避免中心与边缘的纹理差异
    soft = im.filter(ImageFilter.GaussianBlur(3))
    m2 = mask.filter(ImageFilter.GaussianBlur(feather // 2)).point(lambda v: int(v * 0.35))
    im = Image.composite(soft, im, m2)
    return im


def fade_top(im: Image.Image, height: int = 430, strength: float = 0.94) -> Image.Image:
    """顶部纸色渐隐：压掉生成图自带的空白气泡，同时保留画面感。"""
    w, h = im.size
    ramp = np.zeros((h, 1), np.float32)
    ys = np.clip(np.arange(h) / max(1, height), 0, 1)
    ramp[:, 0] = (np.cos(ys * np.pi / 2) ** 1.6) * strength
    arr = np.asarray(im).astype(np.float32)
    paper = np.array(PAPER, np.float32)
    out = arr * (1 - ramp[:, :, None]) + paper * ramp[:, :, None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def add_grain(im: Image.Image, seed: int = 0, strength: float = 4.0) -> Image.Image:
    a = np.asarray(im).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, strength, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------- text
def _layout_lines(draw, lines, cx, cy, f, size, safety=0.80):
    """把多行文字排成可见墨迹居中的块，返回 positions 与气泡尺寸。"""
    gap = round(size * 0.40)
    line_h = size + gap
    boxes = [draw.textbbox((0, 0), s, font=f) for s in lines]
    widths = [b[2] - b[0] for b in boxes]
    text_h = len(lines) * line_h - gap

    nominal_y = cy - text_h / 2
    positions = []
    for s, w, b in zip(lines, widths, boxes):
        positions.append([cx - w / 2 - b[0], nominal_y - b[1], s])
        nominal_y += line_h

    def vis():
        return [draw.textbbox((round(x), round(y)), s, font=f) for x, y, s in positions]

    ib = vis()
    ink_cy = (min(b[1] for b in ib) + max(b[3] for b in ib)) / 2
    for p in positions:
        p[0] = round(p[0])
        p[1] = round(p[1] + cy - ink_cy)

    pad_x, pad_y = round(size * 1.25), round(size * 0.95)
    bw, bh = max(widths) + 2 * pad_x + 12, text_h + 2 * pad_y + 10
    while True:
        rx, ry = bw / 2, bh / 2
        worst = max(
            ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            for b in vis()
            for x in (b[0], b[2])
            for y in (b[1], b[3])
        )
        if worst <= safety ** 2:
            break
        bw += 6
        bh += 6
    return [(round(x), round(y), s) for x, y, s in positions], (bw, bh)


def speech(layer, center, lines, size=46, target=None, tail_len=54, tail_w=44, bend=3,
           fill=BUBBLE):
    """椭圆气泡 + 同一闭合轮廓的尾巴。全部坐标使用 1x 页面坐标。

    target=None 表示说话者不在画面内：画无尾椭圆，避免尾巴误指画面中其他人。
    """
    d = ImageDraw.Draw(layer)
    S = SS
    f = font(size * S, True)
    cx, cy = center[0] * S, center[1] * S
    positions, (bw, bh) = _layout_lines(d, lines, cx, cy, f, size * S)
    if target is None:
        pts = [(cx + np.cos(t / 720 * 2 * np.pi) * bw / 2,
                cy + np.sin(t / 720 * 2 * np.pi) * bh / 2) for t in range(720)]
    else:
        tgt = (target[0] * S, target[1] * S)
        pts = oval_speech((cx, cy), (bw, bh), tgt, tail_length=tail_len * S,
                          tail_width=tail_w * S, bend=bend * S)
    d.polygon([(p[0], p[1]) for p in pts], fill=fill)
    d.line([(p[0], p[1]) for p in pts] + [(pts[0][0], pts[0][1])],
           fill=INK, width=5 * S, joint="curve")
    for x, y, s in positions:
        d.text((x, y), s, font=f, fill=INK)
    return {"box": (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2),
            "size": (bw, bh), "text": lines}


def caption(layer, top_left, lines, size=40, width=None, align="center",
            pad=(34, 26), fill=BUBBLE, bold=True, radius=10, max_width=None):
    """矩形旁白框。宽度按最长行自动计算，也可指定。"""
    S = SS
    d = ImageDraw.Draw(layer)
    f = font(size * S, bold)
    boxes = [d.textbbox((0, 0), s, font=f) for s in lines]
    tw = max(b[2] - b[0] for b in boxes)
    gap = round(size * 0.42) * S
    line_h = size * S + gap
    th = len(lines) * line_h - gap
    bw = (width * S if width else tw + 2 * pad[0] * S)
    bh = th + 2 * pad[1] * S
    x0, y0 = top_left[0] * S, top_left[1] * S
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=radius * S,
                        fill=fill, outline=INK, width=4 * S)
    y = y0 + pad[1] * S
    for s, b in zip(lines, boxes):
        if align == "center":
            x = x0 + (bw - (b[2] - b[0])) / 2 - b[0]
        else:
            x = x0 + pad[0] * S - b[0]
        d.text((round(x), round(y)), s, font=f, fill=INK)
        y += line_h
    return {"box": (x0, y0, x0 + bw, y0 + bh)}


def free_text(layer, xy, text, size, color=INK, bold=True, anchor="la", spacing=0):
    S = SS
    f = font(size * S, bold)
    ImageDraw.Draw(layer).text((xy[0] * S, xy[1] * S), text, font=f,
                              fill=color, anchor=anchor, spacing=spacing * S)


def compose(art_path, draw_fn, seed=0, out=None, erase=None, fade=None, webp_quality=95):
    page = prep_page(art_path, seed)
    if fade:
        page = fade_top(page, **fade)
    if erase:
        page = erase_ellipses(page, erase)
    layer = Image.new("RGBA", (PAGE_W * SS, PAGE_H * SS), (0, 0, 0, 0))
    report = draw_fn(layer) or {}
    layer = layer.resize((PAGE_W, PAGE_H), Image.Resampling.LANCZOS)
    page = Image.alpha_composite(page.convert("RGBA"), layer).convert("RGB")
    page = add_grain(page, seed)
    if out:
        out = Path(out)
        if out.suffix.lower() == ".webp":
            page.save(out, "WEBP", quality=webp_quality, method=6)
        else:
            page.save(out, optimize=True)
        # 母版体积大，默认不落盘；需要无损母版时用 --master 打开
        if os.environ.get("COMIC_KEEP_MASTER") == "1":
            master = ROOT / "art/lv1/master" / f"{out.stem}.png"
            master.parent.mkdir(parents=True, exist_ok=True)
            page.save(master, optimize=True)
    return page, report


def plain_page(bg, draw_fn, out=None, seed=0):
    page = Image.new("RGB", (PAGE_W, PAGE_H), bg)
    layer = Image.new("RGBA", (PAGE_W * SS, PAGE_H * SS), (0, 0, 0, 0))
    draw_fn(layer)
    layer = layer.resize((PAGE_W, PAGE_H), Image.Resampling.LANCZOS)
    page = Image.alpha_composite(page.convert("RGBA"), layer).convert("RGB")
    page = add_grain(page, seed, 3.0)
    if out:
        page.save(out, quality=95)
    return page
