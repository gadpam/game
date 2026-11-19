"""Собирает clean-art заявки Главы 4 v2 без преждевременной замены."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ch4_roster import STARTERS, SUBS, SQUAD_NUMBERS


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ch4" / "v2_02_lineup.jpg"
W, H = 1200, 1700

FONT_PATHS = (
    ROOT / "fonts" / "Exo2-Bold.ttf",
    ROOT / "fonts" / "Oswald-Bold.ttf",
)
FONT_PATH = next(path for path in FONT_PATHS if path.exists())


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], text: str, fnt, fill) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    tw, th = box[2] - box[0], box[3] - box[1]
    left, top, right, bottom = xy
    draw.text(
        (left + (right - left - tw) / 2, top + (bottom - top - th) / 2 - box[1]),
        text,
        font=fnt,
        fill=fill,
    )


def round_rect(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build() -> Path:
    image = Image.new("RGB", (W, H), "#E9E3D6")
    draw = ImageDraw.Draw(image)

    # Холодный бумажный лист на тёмном планшете: без Системы и без glow.
    draw.rectangle((0, 0, W, H), fill="#25272B")
    draw.rectangle((48, 42, W - 48, H - 42), fill="#36383C", outline="#50535A", width=3)
    round_rect(draw, (90, 70, W - 90, H - 70), 22, "#EEE9DD", "#C5BDAE", 3)
    draw.line((142, 250, W - 142, 250), fill="#9B9384", width=2)

    centered(draw, (120, 95, W - 120, 155), "ЗАЯВКА НА МАТЧ", font(48), "#191A1D")
    centered(draw, (120, 160, W - 120, 215), "«ВЕРЕСК» — «ТОРПЕДО-2»", font(34), "#343438")
    centered(draw, (120, 215, W - 120, 250), "ГОСТИ", font(21), "#777064")

    def section(title: str, names: tuple[str, ...], top: int, rows: int) -> int:
        left, right = 145, W - 145
        header_h, row_h = 55, 72
        round_rect(draw, (left, top, right, top + header_h), 10, "#2D3035")
        draw.text((left + 22, top + 12), title, font=font(25), fill="#F3EFE7")
        y = top + header_h + 10
        columns = 2
        col_gap = 20
        col_w = (right - left - col_gap) // columns
        for index, name in enumerate(names):
            col = index // rows
            row = index % rows
            x = left + col * (col_w + col_gap)
            yy = y + row * row_h
            round_rect(draw, (x, yy, x + col_w, yy + row_h - 10), 8, "#F8F4EA", "#C9C0B0", 2)
            num = str(SQUAD_NUMBERS[name])
            centered(draw, (x + 8, yy + 6, x + 73, yy + row_h - 16), num, font(30), "#A92732")
            draw.line((x + 82, yy + 12, x + 82, yy + row_h - 22), fill="#C9C0B0", width=2)
            draw.text((x + 100, yy + 15), name, font=font(22), fill="#202126")
        return y + rows * row_h

    after_start = section("ОСНОВНОЙ СОСТАВ", STARTERS, 305, 6)
    after_subs = section("ЗАПАСНЫЕ", SUBS, after_start + 38, 4)

    note_top = after_subs + 36
    draw.line((145, note_top, W - 145, note_top), fill="#B7AE9F", width=2)
    centered(
        draw,
        (145, note_top + 35, W - 145, note_top + 88),
        "СТАРТОВЫЙ СОСТАВ",
        font(22),
        "#666055",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, quality=95, subsampling=0)
    print(f"{OUT.relative_to(ROOT)}: {W}x{H} · 11 + 7 · без минуты замены")
    return OUT


if __name__ == "__main__":
    build()
