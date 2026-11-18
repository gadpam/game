"""Исправляет непрерывность формы соперника в кадре замены Главы 3 v2.

Исходная генерация сохранена как ``v2_10_subbed_src.jpg``. Скрипт меняет
только две дальние зелёные формы на чёрные и заодно убирает ложный номер;
поле, Ветров и тренер остаются неизменными.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps


SRC = Path("ch3/v2_10_subbed_src.jpg")
OUT = Path("ch3/v2_10_subbed.jpg")
EXPECTED_SIZE = (768, 1376)
PLAYER_REGIONS = [
    [(338, 600), (380, 575), (421, 590), (446, 625),
     (442, 705), (398, 722), (356, 690), (337, 642)],
    [(600, 600), (636, 582), (667, 604), (677, 649),
     (667, 714), (626, 720), (601, 683)],
]


def build(src=SRC, out=OUT):
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"неожиданный размер кадра замены: {image.size}")

    width, height = image.size
    hsv = np.asarray(image.convert("HSV"))
    hue, saturation = hsv[..., 0], hsv[..., 1]

    regions = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(regions)
    for polygon in PLAYER_REGIONS:
        draw.polygon(polygon, fill=255)

    # Внутри двух дальних силуэтов выбирается только зелёная ткань.
    green = (
        (hue >= 75)
        & (hue <= 126)
        & (saturation >= 30)
        & (np.asarray(regions) > 0)
    )
    mask = Image.fromarray((green * 255).astype("uint8"))
    # Closing заполняет светлые штрихи ложного номера и дождевые разрывы.
    mask = mask.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(11))
    mask = mask.filter(ImageFilter.GaussianBlur(1.1))
    mask = Image.fromarray(
        np.minimum(np.asarray(mask), np.asarray(regions)).astype("uint8")
    )

    grey = ImageOps.grayscale(image)
    smooth = np.asarray(grey.filter(ImageFilter.GaussianBlur(6)), dtype=np.float32)
    original = np.asarray(grey, dtype=np.float32)
    shade = np.clip(18 + smooth * 0.24 + (original - smooth) * 0.04, 22, 55)
    target = np.empty((height, width, 3), dtype=np.uint8)
    target[..., 0] = np.clip(shade * 0.82, 0, 255)
    target[..., 1] = np.clip(shade * 0.85, 0, 255)
    target[..., 2] = np.clip(shade * 0.87, 0, 255)

    result = Image.composite(Image.fromarray(target), image, mask)
    result.save(out, quality=94, optimize=True)
    print(f"{out}: дальние формы соперника чёрные · ложный номер удалён")


if __name__ == "__main__":
    build()
