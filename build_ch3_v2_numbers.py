"""Номера формы Ветрова для versioned-сборки Главы 3.

Реалистичная схема: крупный контрастный номер на спине и небольшой номер
на передней части шорт. Номер на груди не добавляется. В текущей главе
Ветров носит 19; желание получить номер 8 относится к будущей арке.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from build_lettering import LF
from ch3_roster import VETROV_NUMBER


# Координаты заданы после приведения кадров к финальной ширине 800 px.
# Номер ставится только там, где соответствующая часть формы реально видна.
SHORTS_PLACEMENTS = {
    "03": ((617, 836), 28, -2.0),
    "06": ((326, 700), 27, -7.0),
    "07": ((345, 687), 28, -8.0),
    "08": ((259, 703), 27, -7.0),
    "09": ((300, 754), 27, -9.0),
    "10": ((515, 992), 27, 1.0),
    "11": ((220, 886), 25, -5.0),
}

BACK_PLACEMENTS = {
    # Послематчевый разговор: Ветров стоит к читателю спиной на переднем плане.
    "12": ((164, 704), 92, -5.0),
}


def _number_art(
    text: str,
    size: int,
    angle: float,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int],
    blur: float = 0.0,
) -> Image.Image:
    ss = 4
    font = LF("ob", size * ss)
    bbox = font.getbbox(text, stroke_width=ss)
    pad = 8 * ss
    width = bbox[2] - bbox[0] + pad * 2
    height = bbox[3] - bbox[1] + pad * 2
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (pad - bbox[0], pad - bbox[1]),
        text,
        font=font,
        fill=fill,
        stroke_width=ss,
        stroke_fill=stroke,
    )
    layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    layer = layer.resize(
        (max(1, layer.width // ss), max(1, layer.height // ss)),
        Image.Resampling.LANCZOS,
    )
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return layer


def _place(image: Image.Image, art: Image.Image, center: tuple[int, int]) -> None:
    x = int(round(center[0] - art.width / 2))
    y = int(round(center[1] - art.height / 2))
    image.alpha_composite(art, (x, y))


def apply_vetrov_number(frame_number: str, image_rgba: Image.Image) -> Image.Image:
    """Возвращает RGBA-копию кадра с номером 19 на видимой части формы."""
    image = image_rgba.convert("RGBA").copy()
    text = str(VETROV_NUMBER)

    if frame_number in SHORTS_PLACEMENTS:
        center, size, angle = SHORTS_PLACEMENTS[frame_number]
        art = _number_art(
            text,
            size,
            angle,
            fill=(232, 234, 230, 225),
            stroke=(20, 24, 27, 210),
            blur=0.18,
        )
        _place(image, art, center)

    if frame_number in BACK_PLACEMENTS:
        center, size, angle = BACK_PLACEMENTS[frame_number]
        art = _number_art(
            text,
            size,
            angle,
            fill=(24, 28, 32, 225),
            stroke=(215, 218, 214, 145),
            blur=0.55,
        )
        _place(image, art, center)

    return image
