"""Точная кириллица физических врезок для кандидата Главы 3 v2.

Legacy ``g03_lineup.jpg`` остаётся нетронутым. Новая заявка показывает
реальные 18 мест: 11 в основе и 7 в запасе; Ветров выделен в старте.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from grid import F


SRC = Path("ch3/g03_lineup_src.jpg")
OUT = Path("ch3/v2_02_lineup.jpg")
INK = (31, 42, 70)
DIM = (92, 91, 88)

STARTERS = (
    "ГРОМОВ",
    "САВЕЛЬЕВ",
    "АНДРЕЕВ",
    "КАРИМОВ",
    "ЛЕВЧУК",
    "ТКАЧЁВ",
    "ВЕТРОВ",
    "ГОНЧАР",
    "НОВИК",
    "МАРЧЕНКО",
    "ДЕНИСОВ",
)
SUBS = (
    "БОБРОВ",
    "МЕЛЬНИК",
    "КИСЕЛЁВ",
    "ШАТСКИЙ",
    "КОВАЛЁВ",
    "РОМАНОВ",
    "ЮРЧЕНКО",
)
assert len(STARTERS) == 11 and len(SUBS) == 7
assert len(set(STARTERS + SUBS)) == 18
assert "ВЕТРОВ" in STARTERS and "ШАТСКИЙ" in SUBS


def _fit(text: str, weight: str, size: int, max_width: int):
    while size >= 8:
        font = F(weight, size)
        if font.getlength(text) <= max_width:
            return font
        size -= 1
    raise ValueError(f"не удалось вписать строку: {text}")


def _text(draw, xy, text, weight, size, fill=INK, max_width=400, anchor="la"):
    font = _fit(text, weight, size, max_width)
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)
    return draw.textbbox(xy, text, font=font, anchor=anchor)


def build() -> str:
    image = Image.open(SRC).convert("RGB").resize((768, 1376), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)

    x0, x1 = 185, 584
    _text(draw, (x0, 260), "СОСТАВ НА МАТЧ", "b", 29, max_width=x1 - x0)
    _text(
        draw,
        (x0, 300),
        "«ГОРЕЦ» — «ТОРПЕДО-2» · КУБОК",
        "m",
        14,
        fill=DIM,
        max_width=x1 - x0,
    )
    draw.line([(x0, 326), (x1, 326)], fill=(104, 105, 103), width=2)

    left_x, right_x = 188, 398
    _text(draw, (left_x, 354), "ОСНОВА · 11", "b", 15, fill=DIM, max_width=175)
    _text(draw, (right_x, 354), "ЗАПАС · 7", "b", 15, fill=DIM, max_width=170)

    y = 388
    for name in STARTERS:
        active = name == "ВЕТРОВ"
        if active:
            draw.rounded_rectangle((left_x - 8, y - 5, left_x + 176, y + 24), radius=4, fill=(217, 229, 231))
            draw.rectangle((left_x - 8, y - 5, left_x - 3, y + 24), fill=(51, 122, 145))
        _text(draw, (left_x, y), name, "b" if active else "m", 15,
              fill=(22, 64, 86) if active else INK, max_width=172)
        y += 32

    y = 388
    for name in SUBS:
        _text(draw, (right_x, y), name, "m", 15, max_width=172)
        y += 39

    _text(draw, (x0, 770), "ВЕТРОВ · ЦПЗ · ПЕРВЫЙ СТАРТ", "b", 13,
          fill=(51, 91, 112), max_width=x1 - x0)
    draw.line([(x0, 800), (x1, 800)], fill=(140, 137, 128), width=1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, quality=95, optimize=True)
    return str(OUT)


if __name__ == "__main__":
    print(build())
