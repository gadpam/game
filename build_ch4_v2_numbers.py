"""Неразрушающе наносит утверждённые номера на кадры Главы 4 v2."""
from __future__ import annotations

from PIL import Image, ImageDraw

from grid import F


VETROV_NUMBER = "19"
SHATSKY_NUMBER = "16"


def _number(
    image: Image.Image,
    center: tuple[int, int],
    text: str,
    *,
    size: int,
    angle: float = 0.0,
    fill=(218, 36, 48, 255),
    stroke=(22, 15, 18, 220),
    stroke_width: int = 2,
) -> None:
    pad = size // 2
    layer = Image.new("RGBA", (size * 3, size * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (layer.width // 2, layer.height // 2),
        text,
        font=F("b", size),
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke,
        anchor="mm",
    )
    if angle:
        layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    image.alpha_composite(layer, (center[0] - layer.width // 2, center[1] - layer.height // 2))


def apply_ch4_numbers(num: str, image_rgba: Image.Image) -> Image.Image:
    image = image_rgba.convert("RGBA")
    w, h = image.size

    # Только ракурсы, где поверхность формы действительно видна. Никаких
    # ложных номеров на груди/рукавах или дальних пиксельных игроках.
    if num == "04":
        _number(image, (int(w * 0.392), int(h * 0.415)), VETROV_NUMBER, size=max(28, int(w * 0.048)), angle=-2)
        _number(image, (int(w * 0.732), int(h * 0.386)), SHATSKY_NUMBER, size=max(24, int(w * 0.041)), angle=4)
    elif num == "10":
        _number(image, (int(w * 0.385), int(h * 0.425)), VETROV_NUMBER, size=max(36, int(w * 0.075)), angle=-3)
        _number(image, (int(w * 0.365), int(h * 0.685)), VETROV_NUMBER, size=max(20, int(w * 0.036)), angle=-5)

    return image
