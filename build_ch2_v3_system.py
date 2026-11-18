"""Панели Системы для читательской ревизии Главы 2 v3.

Версия v2 остаётся нетронутой. В v3 профиль снова читается как фрагмент
знакомого полного профиля Главы 1: все двенадцать строк присутствуют в
расфокусе, а ``ПЕРВОЕ КАСАНИЕ 42`` остаётся единственной резкой строкой.
Панели 07 и 12 побайтово одинаковы; 14 содержит только приветствие.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from build_ch2_system import (
    FIRST_TOUCH,
    INK,
    PROFILE_TITLE,
    STAT_NAME,
    SafeText,
    WELCOME_TEXT,
    _welcome_panel,
)
from grid import F, Panel, decorate_panel, depth_bg, glow_text, holo_card

OUT_DIR = Path("ch2")
PROFILE_07_V3 = OUT_DIR / "v3_07_profile.png"
PROFILE_12_V3 = OUT_DIR / "v3_12_profile.png"
WELCOME_14_V3 = OUT_DIR / "v3_14_welcome.png"

STATS = [
    ("ПЕРВОЕ КАСАНИЕ", 42),
    ("ПАС", 39),
    ("ОТБОР", 26),
    ("УДАР", 11),
    ("ПОЗИЦИЯ", 70),
    ("ВИДЕНИЕ", 58),
    ("ИГРА БЕЗ МЯЧА", 47),
    ("ПРИНЯТИЕ РЕШЕНИЙ", 26),
    ("ВЫНОСЛИВОСТЬ", 38),
    ("СКОРОСТЬ", 31),
    ("ПРЫГУЧЕСТЬ", 22),
    ("СИЛА", 16),
]
assert STATS[0] == (STAT_NAME, FIRST_TOUCH)


def _blurred_stats(panel: Panel) -> None:
    """Рисует знакомые строки достаточно различимо как структуру, но не как новый инфоблок."""
    layer = Image.new("RGBA", (panel.bw, panel.bh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    columns = (STATS[:6], STATS[6:])
    for column, rows in enumerate(columns):
        label_x = 108 if column == 0 else 430
        value_x = 370 if column == 0 else 700
        for index, (label, value) in enumerate(rows):
            if column == 0 and index == 0:
                continue
            y = 304 + index * 82
            size = 13 if len(label) > 17 else 15
            draw.text((label_x, y), label, font=F("m", size), fill=panel.st["dim"] + (105,))
            draw.text((value_x, y - 2), str(value), font=F("b", 22), fill=panel.st["ink"] + (112,), anchor="ra")
            draw.line(
                [(label_x, y + 34), (value_x, y + 34)],
                fill=panel.st["edge"] + (32,),
                width=1,
            )
    panel.lay.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.8)))
    panel.d = ImageDraw.Draw(panel.lay)


def _profile_panel_v3(path: Path) -> None:
    height = 1100
    box = (48, 72, 752, 1028)
    panel = Panel(depth_bg("n", box, h=height), box, "n", frame_id=None)
    decorate_panel(panel)
    safe = SafeText(panel, pad=(20, 66, 20, 20))

    safe.text(
        (panel.cx, 152),
        PROFILE_TITLE,
        F("b", 34),
        (245, 252, 255, 255),
        anchor="ma",
        glow=True,
    )
    panel.div(214)
    holo_card(panel, 76, 252, 724, 822, alpha=112)
    panel.d.line([(400, 270), (400, 804)], fill=panel.st["edge"] + (80,), width=1)
    _blurred_stats(panel)

    # Активная строка — единственный полностью резкий фрагмент полного профиля.
    holo_card(panel, 88, 276, 388, 360, alpha=142, active=True)
    safe.text(
        (108, 318),
        STAT_NAME,
        F("b", 17),
        INK + (255,),
        anchor="lm",
        glow=True,
    )
    safe.text(
        (366, 318),
        str(FIRST_TOUCH),
        F("b", 31),
        panel.st["hot"] + (255,),
        anchor="rm",
        glow=True,
    )
    panel.div(890)
    safe.check(overlap=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_v3() -> list[str]:
    _profile_panel_v3(PROFILE_07_V3)
    shutil.copyfile(PROFILE_07_V3, PROFILE_12_V3)
    _welcome_panel(WELCOME_14_V3)
    assert _sha256(PROFILE_07_V3) == _sha256(PROFILE_12_V3)
    return [str(PROFILE_07_V3), str(PROFILE_12_V3), str(WELCOME_14_V3)]


if __name__ == "__main__":
    outputs = build_v3()
    print("Глава 2 v3: панели читательской ревизии собраны")
    for output in outputs:
        print(" ", output)
    print("Профили 07/12 побайтово идентичны · резкая строка ПЕРВОЕ КАСАНИЕ 42")
