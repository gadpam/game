"""Детерминированные визуальные правки после полного QC Главы 3 v2.

Собирает три активных versioned-кадра из сохранённых исходников:

- 07: второй чистый отбор с однозначным касанием Ветрова по мячу;
- 12: победный гол вышедшего на замену Мельника на 74-й минуте;
- 13: финальный свисток, где светловолосый Новик не похож на Ветрова.

Точный номер Мельника, минута, SFX и финальный счёт добавляются позднее
сборщиками номеров и леттеринга; legacy-файлы не изменяются.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


TACKLE_SRC = Path("ch3/v2_07_tackle_two_revision_src.jpg")
TACKLE_OUT = Path("ch3/v2_07_tackle_two.jpg")
GOAL_SRC = Path("ch3/v2_12_melnik_goal_regulation_src.jpg")
GOAL_OUT = Path("ch3/v2_12_melnik_goal.jpg")
WHISTLE_SRC = Path("ch3/v2_13_final_whistle_src.jpg")
WHISTLE_OUT = Path("ch3/v2_13_final_whistle.jpg")

HOME_TEAM = "ГОРЕЦ"
AWAY_TEAM = "ТОРПЕДО-2"
HOME_SCORE = 0
AWAY_SCORE = 1
GOAL_MINUTE = "74′"
FINAL_SCORE = f"{HOME_TEAM} {HOME_SCORE}:{AWAY_SCORE} {AWAY_TEAM}"
REGULATION_GOAL_METRES = (7.32, 2.44)
PENALTY_AREA_DEPTH_METRES = 16.5
GOAL_AREA_DEPTH_METRES = 5.5

TACKLE_SOURCE_SIZE = (848, 1264)
TACKLE_SIZE = (800, 1260)
GOAL_SOURCE_SIZE = (768, 1376)
GOAL_SIZE = (800, 1320)
# Контрольные координаты полноразмерных стоек в сохранённом исходнике:
# ворота занимают >80% ширины и заметно выше стоящих полевых игроков вдали.
GOAL_SOURCE_POSTS_X = (73, 711)
GOAL_SOURCE_CROSSBAR_Y = 416
GOAL_SOURCE_GROUND_Y = 889
EXPECTED_WHISTLE_SIZE = (768, 1376)


def _fit(image: Image.Image, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGB"),
        size,
        method=Image.Resampling.LANCZOS,
        centering=centering,
    )


def _build_tackle(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != TACKLE_SOURCE_SIZE:
        raise ValueError(f"неожиданный размер исходника отбора: {image.size}")
    _fit(image, TACKLE_SIZE, centering=(0.50, 0.48)).save(
        out, quality=94, optimize=True
    )


def _build_goal(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != GOAL_SOURCE_SIZE:
        raise ValueError(f"неожиданный размер исходника гола: {image.size}")

    # В исправленном исходнике полноразмерные ворота занимают почти всю
    # ширину, а прямоугольная разметка штрафной продолжает полный газон.
    # Фокус немного смещён вниз, чтобы после кропа сохранить обе бутсы.
    _fit(image, GOAL_SIZE, centering=(0.50, 0.66)).save(
        out, quality=94, optimize=True
    )


def _build_whistle(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_WHISTLE_SIZE:
        raise ValueError(f"неожиданный размер исходника свистка: {image.size}")

    pixels = np.asarray(image).astype(np.float32)

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
    for path in (TACKLE_OUT, GOAL_OUT, WHISTLE_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
    _build_tackle(TACKLE_SRC, TACKLE_OUT)
    _build_goal(GOAL_SRC, GOAL_OUT)
    _build_whistle(WHISTLE_SRC, WHISTLE_OUT)
    print(
        "гл. 3 · QC-правки: чистый отбор 07 · "
        f"гол Мельника на {GOAL_MINUTE} · финал {FINAL_SCORE} · различимый Новик 13"
    )
    return [str(TACKLE_OUT), str(GOAL_OUT), str(WHISTLE_OUT)]


if __name__ == "__main__":
    for output in build():
        print(output)
