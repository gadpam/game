"""Детерминированные переходные кадры расширенного финала Главы 3 v2.

Сценарий после авторского решения расширен до 20 кадров. Три атмосферные
врезки собираются из уже утверждённых исходников, не меняя их:

- крупная реакция Ветрова после первого выполненного квеста;
- опустевшая гостевая раздевалка;
- дождь на окне автобуса перед немым финалом.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps


REACTION_SRC = Path("ch1/a13_eyes_rain.jpg")
REACTION_OUT = Path("ch3/v2_16_result_reaction.jpg")
EMPTY_SRC = Path("ch3/g23_empty.jpg")
EMPTY_OUT = Path("ch3/v2_18_empty.jpg")
BUS_WINDOW_SRC = Path("ch3/v2_20_bus_src.jpg")
BUS_WINDOW_OUT = Path("ch3/v2_19_bus_window.jpg")

EXPECTED_PORTRAIT = (768, 1376)
REACTION_SIZE = (800, 1280)
EMPTY_SIZE = (800, 1420)
BUS_WINDOW_SIZE = (800, 1240)


def _reaction(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_PORTRAIT:
        raise ValueError(f"неожиданный размер исходника реакции: {image.size}")

    # Убираем почти весь дальний план и оставляем лицо как визуальную рифму
    # с первым появлением Системы. Новый зелёный отблеск отличает выполнение.
    crop = image.crop((180, 0, 768, 940))
    crop = crop.resize(REACTION_SIZE, Image.Resampling.LANCZOS)
    pixels = np.asarray(crop).astype(np.float32)
    original = pixels.copy()
    red, green, blue = original[..., 0], original[..., 1], original[..., 2]
    cyan = (blue - red > 18) & (green - red > 9) & (green > 105)
    shifted = original.copy()
    shifted[..., 0][cyan] *= 0.78
    shifted[..., 1][cyan] = np.minimum(255, green[cyan] * 1.02 + 7)
    shifted[..., 2][cyan] *= 0.86
    pixels[cyan] = original[cyan] * 0.78 + shifted[cyan] * 0.22

    # Только у глаз остаётся слабый изумрудный отсвет выполненного квеста.
    height, width = REACTION_SIZE[1], REACTION_SIZE[0]
    yy, xx = np.indices((height, width))
    eye_glow = np.zeros((height, width), dtype=np.float32)
    for cx, cy in ((255, 775), (500, 770)):
        eye_glow = np.maximum(
            eye_glow,
            np.exp(-(((xx - cx) / 112) ** 2 + ((yy - cy) / 68) ** 2) * 2.2),
        )
    alpha = (eye_glow * 0.075)[..., None]
    emerald = np.zeros_like(pixels)
    emerald[...] = (88, 211, 176)
    pixels = pixels * (1 - alpha) + emerald * alpha

    # Мягкая виньетка направляет взгляд к глазам и не превращает кадр в
    # ещё одну интерфейсную панель.
    height, width = REACTION_SIZE[1], REACTION_SIZE[0]
    yy, xx = np.indices((height, width))
    dx = (xx - width * 0.56) / (width * 0.72)
    dy = (yy - height * 0.43) / (height * 0.78)
    vignette = np.clip((dx * dx + dy * dy - 0.28) * 15, 0, 17)[..., None]
    pixels -= vignette
    Image.fromarray(np.clip(pixels, 0, 255).astype("uint8"), "RGB").save(
        out, quality=94, optimize=True
    )


def _empty_room(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_PORTRAIT:
        raise ValueError(f"неожиданный размер раздевалки: {image.size}")
    image = ImageOps.fit(
        image,
        EMPTY_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.44),
    )
    image.save(out, quality=94, optimize=True)


def _bus_window(src: Path, out: Path) -> None:
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_PORTRAIT:
        raise ValueError(f"неожиданный размер автобусного исходника: {image.size}")
    # Окно с дождём и верх силуэта Ветрова связывают посадку с финальным
    # общим планом, не повторяя сам спящий портрет.
    crop = image.crop((0, 0, 480, 470))
    crop = ImageOps.fit(
        crop,
        BUS_WINDOW_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.46, 0.42),
    )
    # Едва заметное размытие дорожных огней оставляет резкими капли на стекле.
    glow = crop.filter(ImageFilter.GaussianBlur(5.0))
    pixels = np.asarray(crop).astype(np.float32)
    glowed = np.asarray(glow).astype(np.float32)
    mixed = np.clip(pixels * 0.88 + glowed * 0.12, 0, 255).astype("uint8")
    Image.fromarray(mixed, "RGB").save(out, quality=94, optimize=True)


def build() -> list[str]:
    REACTION_OUT.parent.mkdir(parents=True, exist_ok=True)
    _reaction(REACTION_SRC, REACTION_OUT)
    _empty_room(EMPTY_SRC, EMPTY_OUT)
    _bus_window(BUS_WINDOW_SRC, BUS_WINDOW_OUT)
    outputs = [REACTION_OUT, EMPTY_OUT, BUS_WINDOW_OUT]
    print("гл. 3 · расширенный финал: реакция + пустая раздевалка + окно автобуса")
    return [str(path) for path in outputs]


if __name__ == "__main__":
    for output in build():
        print(output)
