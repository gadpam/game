# -*- coding: utf-8 -*-
"""
Мини-движок вёрстки слайдов.

Один и тот же контент → две выдачи:
  * PPTX  — редактируемый текст (python-pptx), шрифт Exo 2;
  * PNG   — превью 1920x1080 (Pillow) для визуальной проверки.

Координаты — в дюймах. Размер слайда 13.333 x 7.5 (16:9).
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "..")

# ─────────────────────────────────────────────────────────────── токены

SLIDE_W = 13.333
SLIDE_H = 7.5
DPI = 144                     # превью 1920x1080

PAPER = "F7F6F3"             # тёплый белый
CARD = "FFFFFF"
INK = "14171A"               # заголовки
BODY = "464C54"              # основной текст
MUTED = "8A9099"             # подписи
LINE = "E2E0D9"              # тонкие линейки
ACCENT = "1D5C57"            # глубокая бирюза
ACCENT_SOFT = "E5EFED"
ACCENT2 = "B2552F"           # терракота
ACCENT2_SOFT = "F7E9E1"
GREEN = "2E6B4F"
GREEN_SOFT = "E4EFE8"

WEIGHT_FILE = {
    "light": "Exo2-Light.ttf",
    "medium": "Exo2-Medium.ttf",
    "bold": "Exo2-Bold.ttf",
}
# В Windows статические начертания Exo 2 — три отдельные гарнитуры:
# «Exo 2 Light» (nameID 1), «Exo 2 Medium» (nameID 1), «Exo 2» + bold.
PPTX_TYPEFACE = {
    "light": "Exo 2 Light",
    "medium": "Exo 2 Medium",
    "bold": "Exo 2",
}
PPTX_BOLD = {"light": False, "medium": False, "bold": True}

# поля и базовая сетка
M_L = 0.95                   # левое поле
M_R = 0.95
CW = SLIDE_W - M_L - M_R     # ширина контента
BODY_TOP = 2.18              # верх контентной области на обычном слайде
BODY_BOTTOM = 6.62           # низ контентной области
FOOT_Y = 6.92


def px(inches: float) -> int:
    return int(round(inches * DPI))


def pt_px(pt: float) -> float:
    return pt * DPI / 72.0


_font_cache: Dict[Tuple[str, float], ImageFont.FreeTypeFont] = {}


def pil_font(weight: str, size_pt: float) -> ImageFont.FreeTypeFont:
    key = (weight, round(size_pt, 2))
    if key not in _font_cache:
        path = os.path.join(ASSETS, WEIGHT_FILE[weight])
        _font_cache[key] = ImageFont.truetype(path, max(6, int(round(pt_px(size_pt)))))
    return _font_cache[key]


def measure(text: str, weight: str, size_pt: float, spc: float = 0.0) -> float:
    """Ширина строки в пикселях превью."""
    if not text:
        return 0.0
    f = pil_font(weight, size_pt)
    w = f.getlength(text)
    if spc:
        w += pt_px(spc) * len(text)
    return w


# ─────────────────────────────────────────────────────── спецификация

class Canvas:
    """Список элементов слайда. Порядок = порядок отрисовки."""

    def __init__(self, kind: str = "content"):
        self.kind = kind
        self.els: List[dict] = []
        self.notes: str = ""

    # — геометрия —
    def rect(self, x, y, w, h, fill=None, line=None, lw=0.75, radius=0.0):
        self.els.append(dict(t="rect", x=x, y=y, w=w, h=h, fill=fill,
                             line=line, lw=lw, radius=radius))

    def hline(self, x, y, w, color=LINE, lw=0.75):
        self.els.append(dict(t="rect", x=x, y=y, w=w, h=lw / 72.0,
                             fill=color, line=None, lw=0, radius=0.0))

    def vline(self, x, y, h, color=LINE, lw=0.75):
        self.els.append(dict(t="rect", x=x, y=y, w=lw / 72.0, h=h,
                             fill=color, line=None, lw=0, radius=0.0))

    def dot(self, cx, cy, r, fill=ACCENT):
        self.els.append(dict(t="dot", cx=cx, cy=cy, r=r, fill=fill))

    # — текст —
    def text(self, x, y, w, paras, align="l") -> float:
        """paras: список абзацев (см. norm_paras). Возвращает высоту блока."""
        norm = norm_paras(paras)
        lines = wrap_paras(norm, w)
        h = 0.0
        for ln in lines:
            h += ln["line_h"]
        # + интервалы после абзацев
        for i, p in enumerate(norm):
            if i < len(norm) - 1:
                h += p.get("space", 0) / 72.0
        self.els.append(dict(t="text", x=x, y=y, w=w, paras=norm,
                             lines=lines, h=h, align=align))
        return h

    # — сложные блоки —
    def card(self, x, y, w, h, fill=CARD, line=LINE, radius=0.10):
        self.rect(x, y, w, h, fill=fill, line=line, lw=0.75, radius=radius)


def run(text, weight="medium", size=14.0, color=BODY, spc=0.0, caps=False) -> dict:
    return dict(text=text, weight=weight, size=size, color=color, spc=spc, caps=caps)


def para(*runs, align="l", space=6.0, line=1.34) -> dict:
    return dict(runs=list(runs), align=align, space=space, line=line)


def norm_paras(paras) -> List[dict]:
    out = []
    for p in paras:
        rs = []
        for r in p["runs"]:
            r = dict(r)
            if r.get("caps"):
                r["text"] = r["text"].upper()
            rs.append(r)
        out.append(dict(runs=rs, align=p.get("align", "l"),
                        space=p.get("space", 6.0), line=p.get("line", 1.34)))
    return out


def _tokens(runs) -> List[Tuple[str, dict, bool]]:
    """Разбор абзаца в слова: (слово, стиль, явный перенос строки)."""
    toks: List[Tuple[str, dict, bool]] = []
    for r in runs:
        chunks = r["text"].split("\n")
        for ci, chunk in enumerate(chunks):
            if ci > 0:
                toks.append(("\n", r, True))
            for word in chunk.split(" "):
                if word == "":
                    continue
                toks.append((word, r, False))
    return toks


def wrap_paras(paras: List[dict], w_in: float) -> List[dict]:
    """Ручной перенос — только для PNG-превью. PPTX переносит сам."""
    max_px = w_in * DPI
    lines: List[dict] = []
    for p in paras:
        max_size = max((r["size"] for r in p["runs"]), default=12.0)
        line_h = max_size * p["line"] / 72.0
        toks = _tokens(p["runs"])
        cur: List[Tuple[str, dict]] = []
        cur_w = 0.0

        def flush():
            nonlocal cur, cur_w
            if cur:
                lines.append(dict(words=list(cur), align=p["align"],
                                  line_h=line_h, space=p.get("space", 0.0)))
                cur, cur_w = [], 0.0

        for word, style, hard in toks:
            if hard:
                flush()
                continue
            wpx = measure(word, style["weight"], style["size"], style.get("spc", 0.0))
            spx = (measure(" ", style["weight"], style["size"], style.get("spc", 0.0))
                   if cur else 0.0)
            if cur and cur_w + spx + wpx > max_px:
                flush()
                spx = 0.0
            cur.append((word, style))
            cur_w += spx + wpx
        flush()
    return lines


def block_height(paras, w_in: float) -> float:
    norm = norm_paras(paras)
    lines = wrap_paras(norm, w_in)
    h = sum(ln["line_h"] for ln in lines)
    for i, p in enumerate(norm):
        if i < len(norm) - 1:
            h += p.get("space", 0) / 72.0
    return h


# ────────────────────────────────────────────────────── рендер в PNG

def render_png(canvas: Canvas, path: str, bg=PAPER):
    img = Image.new("RGB", (px(SLIDE_W), px(SLIDE_H)), "#" + bg)
    dr = ImageDraw.Draw(img)

    for el in canvas.els:
        if el["t"] == "rect":
            x0, y0 = px(el["x"]), px(el["y"])
            x1, y1 = px(el["x"] + el["w"]), px(el["y"] + el["h"])
            fill = "#" + el["fill"] if el["fill"] else None
            line = "#" + el["line"] if el["line"] else None
            if el["radius"] > 0:
                r = px(el["radius"])
                if x1 <= x0 or y1 <= y0:
                    continue
                dr.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                                     outline=line, width=max(1, int(el["lw"])))
            else:
                if x1 <= x0 or y1 <= y0:
                    continue
                dr.rectangle([x0, y0, x1, y1], fill=fill, outline=line,
                             width=max(1, int(el["lw"])) if line else 0)
        elif el["t"] == "dot":
            r = px(el["r"])
            cx, cy = px(el["cx"]), px(el["cy"])
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#" + el["fill"])
        elif el["t"] == "text":
            y = px(el["y"])
            x0 = px(el["x"])
            wpx_total = px(el["w"])
            for ln in el["lines"]:
                words = ln["words"]
                if not words:
                    y += px(ln["line_h"])
                    continue
                widths = []
                for word, style in words:
                    widths.append(measure(word, style["weight"], style["size"],
                                          style.get("spc", 0.0)))
                spw = measure(" ", words[0][1]["weight"], words[0][1]["size"],
                              words[0][1].get("spc", 0.0))
                total = sum(widths) + spw * (len(words) - 1)
                if ln["align"] == "c":
                    x = x0 + (wpx_total - total) / 2
                elif ln["align"] == "r":
                    x = x0 + wpx_total - total
                else:
                    x = x0
                for (word, style), wpx in zip(words, widths):
                    f = pil_font(style["weight"], style["size"])
                    spc = style.get("spc", 0.0)
                    if spc:
                        step = pt_px(spc)
                        for ch in word:
                            dr.text((x, y), ch, font=f, fill="#" + style["color"])
                            x += f.getlength(ch) + step
                    else:
                        dr.text((x, y), word, font=f, fill="#" + style["color"])
                        x += f.getlength(word)
                    x += spw
                y += px(ln["line_h"])
    img.save(path, "PNG")


# ────────────────────────────────────────────────────── рендер в PPTX

def render_pptx(canvases: Sequence[Canvas], path: str, title: str = "",
                author: str = ""):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
    from pptx.util import Emu, Inches, Pt

    ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}

    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    blank = prs.slide_layouts[6]

    def rgb(h):
        return RGBColor.from_string(h)

    for canvas in canvases:
        slide = prs.slides.add_slide(blank)
        # фон
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                    prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = rgb(PAPER)
        bg.line.fill.background()
        bg.shadow.inherit = False

        for el in canvas.els:
            if el["t"] == "rect":
                shp_type = MSO_SHAPE.ROUNDED_RECTANGLE if el["radius"] > 0 else MSO_SHAPE.RECTANGLE
                shp = slide.shapes.add_shape(
                    shp_type, Inches(el["x"]), Inches(el["y"]),
                    Inches(el["w"]), Inches(max(el["h"], 0.008)))
                if el["radius"] > 0:
                    try:
                        shp.adjustments[0] = min(0.5, el["radius"] / max(el["w"], el["h"]))
                    except Exception:
                        pass
                if el["fill"]:
                    shp.fill.solid()
                    shp.fill.fore_color.rgb = rgb(el["fill"])
                else:
                    shp.fill.background()
                if el["line"]:
                    shp.line.color.rgb = rgb(el["line"])
                    shp.line.width = Pt(el["lw"])
                else:
                    shp.line.fill.background()
                shp.shadow.inherit = False
                shp.text_frame.text = ""
            elif el["t"] == "dot":
                r = el["r"]
                shp = slide.shapes.add_shape(
                    MSO_SHAPE.OVAL, Inches(el["cx"] - r), Inches(el["cy"] - r),
                    Inches(2 * r), Inches(2 * r))
                shp.fill.solid()
                shp.fill.fore_color.rgb = rgb(el["fill"])
                shp.line.fill.background()
                shp.shadow.inherit = False
            elif el["t"] == "text":
                tb = slide.shapes.add_textbox(
                    Inches(el["x"]), Inches(el["y"]),
                    Inches(el["w"]), Inches(max(el["h"], 0.2)))
                tf = tb.text_frame
                tf.word_wrap = True
                tf.auto_size = MSO_AUTO_SIZE.NONE
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.TOP
                for pi, p in enumerate(el["paras"]):
                    par = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
                    par.alignment = ALIGN.get(p["align"], PP_ALIGN.LEFT)
                    max_size = max((r["size"] for r in p["runs"]), default=12.0)
                    par.line_spacing = Pt(max_size * p["line"])
                    par.space_after = Pt(p.get("space", 0))
                    par.space_before = Pt(0)
                    for r in p["runs"]:
                        run_ = par.add_run()
                        run_.text = r["text"]
                        f = run_.font
                        f.name = PPTX_TYPEFACE.get(r["weight"], "Exo 2 Medium")
                        f.size = Pt(r["size"])
                        f.bold = PPTX_BOLD.get(r["weight"], False)
                        f.color.rgb = rgb(r["color"])
                        if r.get("spc"):
                            f._rPr.set("spc", str(int(round(r["spc"] * 100))))
                        # кириллица берёт latin-гарнитуру
                        f._rPr.set("dirty", "0")

        if getattr(canvas, "notes", ""):
            tf = slide.notes_slide.notes_text_frame
            tf.text = canvas.notes
            for p in tf.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(12)

    cp = prs.core_properties
    cp.title = title
    cp.author = author
    cp.comments = "Собрано скриптом presentation/build.py"
    prs.save(path)
