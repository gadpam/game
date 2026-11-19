"""Детерминированные визуальные правки после полного QC Главы 3 v2.

Собирает три versioned-кадра из сохранённых исходников:

- 07: второй чистый отбор с однозначным касанием Ветрова по мячу;
- 12: физическое табло на 89-й минуте, «Горец» 0:1 «Торпедо-2»;
- 13: финальный свисток, где светловолосый Новик не похож на Ветрова.

Леттеринг и номера добавляются позднее; legacy-файлы не изменяются.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from build_lettering import LF, check_glyphs


TACKLE_SRC = Path("ch3/v2_07_tackle_two_revision_src.jpg")
TACKLE_OUT = Path("ch3/v2_07_tackle_two.jpg")
SCOREBOARD_SRC = Path("ch3/v2_12_scoreboard_src.jpg")
SCOREBOARD_OUT = Path("ch3/v2_12_scoreboard.jpg")
WHISTLE_SRC = Path("ch3/v2_13_final_whistle_src.jpg")
WHISTLE_OUT = Path("ch3/v2_13_final_whistle.jpg")

HOME_TEAM = "ГОРЕЦ"
AWAY_TEAM = "ТОРПЕДО-2"
HOME_SCORE = 0
AWAY_SCORE = 1
SCORE_MINUTE = "89′"
FINAL_SCORE = f"{HOME_TEAM} {HOME_SCORE}:{AWAY_SCORE} {AWAY_TEAM}"

TACKLE_SIZE = (800, 1260)
SCOREBOARD_SIZE = (800, 1320)
EXPECTED_WHISTLE_SIZE = (768, 1376)


def _fit(image: Image.Image, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
        centering=centering,
    )


def _perspective_coefficients(
    destination: tuple[tuple[float, float], ...],
    source: tuple[tuple[float, float], ...],
) -> tuple[float, ...]:
    """Коэффициенты Pillow: координаты назначения → координаты исходника."""
    matrix = []
    values = []
    for (x, y), (u, v) in zip(destination, source):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        values.append(u)
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        values.append(v)
    return tuple(np.linalg.solve(np.asarray(matrix), np.asarray(values)))


def _warp_to_quad(layer: Image.Image, canvas_size, quad) -> Image.Image:
    w, h = layer.size
    source = ((0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1))
    coeffs = _perspective_coefficients(tuple(quad), source)
    return layer.transform(
        canvas_size,
        Image.Transform.PERSPECTIVE,
        coeffs,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )


def _score_card(label: str, score: int) -> Image.Image:
    """Прозрачная надпись для одной перекидной пластины табло."""
    check_glyphs(label, "om")
    card = Image.new("RGBA", (360, 650), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    label_font = LF("om", 54)
    digit_font = LF("ob", 390)
    ink = (232, 232, 221, 224)
    shadow = (4, 8, 10, 105)
    draw.text((184, 60), label, font=label_font, fill=shadow, anchor="ma")
    draw.text((180, 54), label, font=label_font, fill=ink, anchor="ma")
    draw.text((188, 174), str(score), font=digit_font, fill=shadow, anchor="ma")
    draw.text((180, 166), str(score), font=digit_font, fill=ink, anchor="ma")
    return card.filter(ImageFilter.GaussianBlur(0.35))


def _minute_card() -> Image.Image:
    check_glyphs(SCORE_MINUTE, "ob")
    card = Image.new("RGBA", (520, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    font = LF("ob", 172)
    draw.text((266, 51), SCORE_MINUTE, font=font, fill=(3, 7, 10, 100), anchor="ma")
    draw.text((258, 43), SCORE_MINUTE, font=font, fill=(231, 232, 222, 224), anchor="ma")
    return card.filter(ImageFilter.GaussianBlur(0.32))


def _build_tackle(src: Path, out: Path) -> None:
    image = _fit(Image.open(src), TACKLE_SIZE, centering=(0.50, 0.48))
    image.save(out, quality=94, optimize=True)


def _build_scoreboard(src: Path, out: Path) -> None:
    # Сначала вписываем точные цифры в геометрию исходника, затем делаем
    # финальный кроп: так надписи подчиняются перспективе физического табло.
    image = Image.open(src).convert("RGBA")
    if image.size != (848, 1264):
        raise ValueError(f"неожиданный размер исходника табло: {image.size}")

    quads = (
        ((374, 506), (535, 491), (506, 821), (342, 801)),
        ((571, 484), (738, 467), (718, 792), (550, 808)),
        ((447, 868), (685, 853), (686, 1003), (443, 1020)),
    )
    for card, quad in (
        (_score_card(HOME_TEAM, HOME_SCORE), quads[0]),
        (_score_card(AWAY_TEAM, AWAY_SCORE), quads[1]),
        (_minute_card(), quads[2]),
    ):
        image = Image.alpha_composite(image, _warp_to_quad(card, image.size, quad))

    fitted = _fit(image.convert("RGB"), SCOREBOARD_SIZE, centering=(0.59, 0.50))
    fitted.save(out, quality=94, optimize=True)


def _build_whistle(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_WHISTLE_SIZE:
        raise ValueError(f"неожиданный размер исходника свистка: {image.size}")

    pixels = np.asarray(image).astype(np.float32)
    yy, xx = np.indices((image.height, image.width))

    # Волосы Новика: компактная маска только по правому игроку. Сохраняем
    # тёмный контур и светотень, но меняем массу волос на светло-каштановую.
    polygon = Image.new("L", image.size, 0)
    ImageDraw.Draw(polygon).polygon(
        [(548, 770), (561, 748), (586, 738), (613, 750),
         (626, 773), (619, 799), (599, 817), (568, 809), (545, 788)],
        fill=255,
    )
    region = np.asarray(polygon).astype(np.float32) / 255.0
    luminance = pixels.mean(axis=2)
    dark_hair = np.clip((156.0 - luminance) / 74.0, 0.0, 1.0)
    alpha = (region * dark_hair * 0.82)[..., None]
    target = np.empty_like(pixels)
    target[..., 0] = np.clip(92 + luminance * 0.78, 0, 255)
    target[..., 1] = np.clip(69 + luminance * 0.61, 0, 255)
    target[..., 2] = np.clip(47 + luminance * 0.47, 0, 255)
    recolored = pixels * (1 - alpha) + target * alpha
    Image.fromarray(np.clip(recolored, 0, 255).astype("uint8"), "RGB").save(
        out, quality=94, optimize=True
    )


def build() -> list[str]:
    for path in (TACKLE_OUT, SCOREBOARD_OUT, WHISTLE_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
    _build_tackle(TACKLE_SRC, TACKLE_OUT)
    _build_scoreboard(SCOREBOARD_SRC, SCOREBOARD_OUT)
    _build_whistle(WHISTLE_SRC, WHISTLE_OUT)
    print(
        "гл. 3 · QC-правки: чистый отбор 07 · "
        f"табло {FINAL_SCORE} на {SCORE_MINUTE} · различимый Новик 13"
    )
    return [str(TACKLE_OUT), str(SCOREBOARD_OUT), str(WHISTLE_OUT)]


if __name__ == "__main__":
    for output in build():
        print(output)
