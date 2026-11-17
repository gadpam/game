"""Канонические панели Системы Главы 2 ``script-v2``.

Сборщик изолирован от legacy-панелей ``p14_quest.png``, ``p22_done.png`` и
``p24_total.png``. Он создаёт только новые ``v2_*``-ресурсы:

* 07 и 11 — побайтово одинаковый фрагмент профиля
  ``ПЕРВОЕ КАСАНИЕ 42``;
* 13 — отдельный ответ ``ДОБРО ПОЖАЛОВАТЬ, ИГРОК``.

Здесь намеренно нет квеста, ранга, условий тренировки, результата сессии,
ОБЩ, ИВ, XP, прогресс-бара и скрытого остатка curve-v1.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageDraw

from grid import F, Panel, decorate_panel, depth_bg, glow_text, holo_card

OUT_DIR = Path("ch2")
PROFILE_07 = OUT_DIR / "v2_07_profile.png"
PROFILE_11 = OUT_DIR / "v2_11_profile.png"
WELCOME_13 = OUT_DIR / "v2_13_welcome.png"

INK = (238, 249, 255)
DIM = (144, 196, 232)
PROFILE_TITLE = "ПРОФИЛЬ"
STAT_NAME = "ПЕРВОЕ КАСАНИЕ"
FIRST_TOUCH = 42
WELCOME_TEXT = "ДОБРО ПОЖАЛОВАТЬ, ИГРОК"

_CMAP: set[int] = set()
for family in ("Bold", "Medium", "Light"):
    for table in TTFont(f"fonts/Exo2-{family}.ttf")["cmap"].tables:
        _CMAP |= set(table.cmap.keys())


class SafeText:
    """Минимальная проверка глифов, полей и пересечений текста панели."""

    def __init__(self, panel: Panel, pad=(26, 66, 26, 24)):
        self.panel = panel
        self.pad = pad
        self.items: list[tuple[str, tuple[int, int, int, int]]] = []

    def text(self, xy, text, font, fill, anchor="la", glow=False):
        for char in text:
            if char not in " \n" and ord(char) not in _CMAP:
                raise ValueError(f"нет глифа {char!r} в «{text}»")
        if glow:
            colour = glow if isinstance(glow, tuple) else self.panel.st["edge"]
            bbox = glow_text(
                self.panel.lay,
                xy,
                text,
                font,
                fill,
                colour,
                anchor=anchor,
                radius=8,
                strength=0.68,
            )
            self.panel.d = ImageDraw.Draw(self.panel.lay)
        else:
            bbox = self.panel.d.textbbox(xy, text, font=font, anchor=anchor)
            self.panel.d.text(xy, text, font=font, fill=fill, anchor=anchor)
        self.items.append((text, bbox))
        return bbox

    def check(self, overlap=True):
        x0, y0, x1, y1 = self.panel.box
        left, top, right, bottom = self.pad
        for text, bbox in self.items:
            if (
                bbox[0] < x0 + left - 3
                or bbox[2] > x1 - right + 3
                or bbox[1] < y0 + top - 3
                or bbox[3] > y1 - bottom + 3
            ):
                raise ValueError(f"«{text}» выходит за панель: {bbox} / {self.panel.box}")
        if overlap:
            for index, (text_a, a) in enumerate(self.items):
                for text_b, b in self.items[index + 1 :]:
                    if a[0] < b[2] - 2 and b[0] < a[2] - 2 and a[1] < b[3] - 2 and b[1] < a[3] - 2:
                        raise ValueError(f"пересечение «{text_a}» / «{text_b}»")


def _profile_panel(path: Path) -> None:
    height = 1100
    box = (48, 72, 752, 1028)
    panel = Panel(depth_bg("n", box, h=height), box, "n", frame_id=None)
    decorate_panel(panel)
    safe = SafeText(panel)

    safe.text(
        (panel.cx, 154),
        PROFILE_TITLE,
        F("b", 34),
        (245, 252, 255, 255),
        anchor="ma",
        glow=True,
    )
    panel.div(218)

    # Безымянные строки в глубине напоминают уже знакомый полный профиль,
    # но не добавляют к утверждённому фрагменту никакого нового текста.
    for y, alpha, width in (
        (278, 44, 430),
        (326, 34, 360),
        (374, 26, 470),
        (730, 30, 440),
        (778, 24, 330),
        (826, 18, 410),
    ):
        x0 = panel.cx - width // 2
        x1 = panel.cx + width // 2
        panel.d.line([(x0, y), (x1, y)], fill=panel.st["inner"] + (alpha,), width=2)
        panel.d.line([(x0, y + 10), (x0 + int(width * 0.68), y + 10)], fill=panel.st["edge"] + (alpha // 2,), width=1)

    holo_card(panel, 86, 420, 714, 664, alpha=128, active=True)
    safe.text(
        (128, 506),
        STAT_NAME,
        F("b", 30),
        INK + (255,),
        anchor="lm",
        glow=True,
    )
    safe.text(
        (668, 506),
        str(FIRST_TOUCH),
        F("b", 60),
        panel.st["hot"] + (255,),
        anchor="rm",
        glow=True,
    )
    panel.div(890)
    safe.check(overlap=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)


def _welcome_panel(path: Path) -> None:
    height = 760
    box = (48, 92, 752, 668)
    panel = Panel(depth_bg("n", box, h=height), box, "n", frame_id=None)
    decorate_panel(panel)
    safe = SafeText(panel, pad=(22, 66, 22, 22))

    panel.div(226)
    holo_card(panel, 82, 274, 718, 498, alpha=132, active=True)
    safe.text(
        (panel.cx, 372),
        WELCOME_TEXT,
        F("b", 31),
        (244, 252, 255, 255),
        anchor="mm",
        glow=True,
    )
    panel.div(548)
    safe.check(overlap=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> list[str]:
    _profile_panel(PROFILE_07)
    shutil.copyfile(PROFILE_07, PROFILE_11)
    _welcome_panel(WELCOME_13)

    assert _sha256(PROFILE_07) == _sha256(PROFILE_11), "профили 07 и 11 обязаны быть побайтово одинаковыми"
    return [str(PROFILE_07), str(PROFILE_11), str(WELCOME_13)]


if __name__ == "__main__":
    outputs = build()
    print("Глава 2: панели script-v2 собраны")
    for output in outputs:
        print(" ", output)
    print("Профили 07/11: побайтово идентичны · ПЕРВОЕ КАСАНИЕ 42")
