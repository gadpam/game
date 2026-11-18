"""Детерминированно закрывает единственный блокнот в финале Главы 3 v2.

Исходная генерация сохранена отдельно как ``v2_20_bus_src.jpg``. Скрипт
заменяет только раскрытый разворот на одну чистую закрытую обложку и не
добавляет в кадр текст или второй предмет.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


SRC = Path("ch3/v2_20_bus_src.jpg")
OUT = Path("ch3/v2_20_bus.jpg")
EXPECTED_SIZE = (768, 1376)
COVER = [(257, 831), (498, 733), (580, 951), (337, 1033)]
INNER_EDGE = [(265, 834), (496, 741), (570, 948), (341, 1024)]


def build(src=SRC, out=OUT):
    image = Image.open(src).convert("RGB")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"неожиданный размер автобусного кадра: {image.size}")

    pixels = np.asarray(image).astype(np.int16)
    height, width = pixels.shape[:2]
    yy, xx = np.indices((height, width))

    cover_mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(cover_mask).polygon(COVER, fill=255)

    # Рука остаётся над обложкой вместе с тушевым контуром по краю.
    red, green, blue = pixels[..., 0], pixels[..., 1], pixels[..., 2]
    hand = (
        (red > 92)
        & (red >= green - 3)
        & (green > blue - 5)
        & ((red - blue) > 8)
        & (yy > 830)
        & (yy < 1040)
        & (xx > 260)
        & (xx < 570)
    )
    hand_mask = Image.fromarray((hand * 255).astype("uint8"))
    hand_mask = hand_mask.filter(ImageFilter.MaxFilter(17)).filter(
        ImageFilter.GaussianBlur(1.2)
    )

    # Холодная однотонная тканевая обложка: без клеток, букв и символов.
    rng = np.random.default_rng(31415)
    noise = rng.normal(0, 2.3, (height, width))
    shade = (xx - 400) * 0.008 + (yy - 880) * 0.003
    texture = np.empty((height, width, 3), dtype=np.float32)
    texture[..., 0] = 42 + noise + shade
    texture[..., 1] = 54 + noise + shade
    texture[..., 2] = 58 + noise + shade
    cover = Image.fromarray(np.clip(texture, 0, 255).astype("uint8"), "RGB")
    draw = ImageDraw.Draw(cover)
    draw.line(COVER + [COVER[0]], fill=(16, 23, 26), width=5, joint="curve")
    draw.line(INNER_EDGE + [INNER_EDGE[0]], fill=(70, 83, 85), width=2, joint="curve")

    mask_array = np.minimum(
        np.asarray(cover_mask), 255 - np.asarray(hand_mask)
    ).astype("uint8")
    result = Image.composite(cover, image, Image.fromarray(mask_array))
    result.save(out, quality=94, optimize=True)
    print(f"{out}: один полностью закрытый блокнот · без текста")


if __name__ == "__main__":
    build()
