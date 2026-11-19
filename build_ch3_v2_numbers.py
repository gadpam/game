"""Игровые номера формы для versioned-сборки Главы 3.

Реалистичная схема: крупный контрастный номер на спине и небольшой номер
на передней части шорт. Номер на груди не добавляется. Ветров носит 19;
желание получить номер 8 относится к будущей арке.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from build_lettering import LF
from ch3_roster import SQUAD_NUMBERS, VETROV_NUMBER


# Координаты заданы после приведения кадров к финальной ширине 800 px.
# Номер ставится только там, где соответствующая часть формы реально видна.
SHORTS_PLACEMENTS = {
    "03": ((617, 836), 28, -2.0),
    "06": ((326, 700), 27, -7.0),
    "07": ((345, 687), 28, -8.0),
    "08": ((259, 703), 27, -7.0),
    "09": ((300, 754), 27, -9.0),
    "10": ((515, 992), 27, 1.0),
    "11": ((229, 978), 25, -5.0),
}

BACK_PLACEMENTS = {
    # После финального свистка Ветров уходит в раздевалку спиной к читателю.
    "14": ((552, 764), 66, -1.0),
    # В разговоре с тренером его спина занимает размытый передний план.
    "17": ((154, 806), 72, -4.0),
}

# В кадре финального свистка два различимых партнёра получают номера из
# канонической заявки: Савельев 2 и Новик 9.
TEAMMATE_SHORTS_PLACEMENTS = {
    "13": (
        (SQUAD_NUMBERS["САВЕЛЬЕВ"], (170, 864), 22, -2.0),
        (SQUAD_NUMBERS["НОВИК"], (638, 1038), 23, 1.0),
    ),
}

# В коридоре впереди идут вышедший Мельник 14 и Гончар 7.
TEAMMATE_BACK_PLACEMENTS = {
    "14": (
        (SQUAD_NUMBERS["МЕЛЬНИК"], (277, 695), 40, -1.0),
        (SQUAD_NUMBERS["ГОНЧАР"], (381, 715), 28, 0.0),
    ),
}


def _number_art(
    text: str,
    size: int,
    angle: float,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int],
    blur: float = 0.0,
    stroke_width: int = 1,
) -> Image.Image:
    ss = 4
    font = LF("ob", size * ss)
    scaled_stroke = stroke_width * ss
    bbox = font.getbbox(text, stroke_width=scaled_stroke)
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
        stroke_width=scaled_stroke,
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


def _shorts_art(number: int, size: int, angle: float, blur: float = 0.18) -> Image.Image:
    return _number_art(
        str(number),
        size,
        angle,
        fill=(232, 234, 230, 225),
        stroke=(20, 24, 27, 210),
        blur=blur,
    )


def _back_art(number: int, size: int, angle: float, blur: float = 0.72) -> Image.Image:
    # Спинной номер печатается прямо на белой ткани: без светлой цифровой
    # обводки, с умеренной прозрачностью и мягким краем под фактуру/фокус.
    return _number_art(
        str(number),
        size,
        angle,
        fill=(25, 29, 31, 184),
        stroke=(25, 29, 31, 0),
        blur=blur,
        stroke_width=0,
    )


def apply_ch3_numbers(frame_number: str, image_rgba: Image.Image) -> Image.Image:
    """Возвращает RGBA-копию кадра с номерами на видимых частях формы."""
    image = image_rgba.convert("RGBA").copy()

    if frame_number in SHORTS_PLACEMENTS:
        center, size, angle = SHORTS_PLACEMENTS[frame_number]
        _place(image, _shorts_art(VETROV_NUMBER, size, angle), center)

    if frame_number in BACK_PLACEMENTS:
        center, size, angle = BACK_PLACEMENTS[frame_number]
        blur = 1.45 if frame_number == "17" else 0.72
        _place(image, _back_art(VETROV_NUMBER, size, angle, blur=blur), center)

    for number, center, size, angle in TEAMMATE_SHORTS_PLACEMENTS.get(frame_number, ()):
        _place(image, _shorts_art(number, size, angle, blur=0.3), center)

    for number, center, size, angle in TEAMMATE_BACK_PLACEMENTS.get(frame_number, ()):
        _place(image, _back_art(number, size, angle, blur=0.7), center)

    return image


# Совместимость с уже опубликованным импортом первого пакета.
def apply_vetrov_number(frame_number: str, image_rgba: Image.Image) -> Image.Image:
    return apply_ch3_numbers(frame_number, image_rgba)
