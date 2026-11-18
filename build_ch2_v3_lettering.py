"""Леттеринг читательской ревизии Главы 2 v3.

Кандидат сохраняет v2 и исправляет две причинно-следственные проблемы:
расписание больше не объясняется неправдоподобной табличкой, а знание манежа
и ход проверки звучат короткими мыслями Ветрова. Между тренировкой и вторым
профилем добавлен отдельный самостоятельный вызов.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from build_ch2_lettering import (
    CH2_OPENING_GUTTER,
    DARK,
    PAPER,
    W,
    _door_card,
    apply_ch2_frame,
    render_gutter,
)
from grid import cover


# Единственный внутренний голос v3, в точном порядке чтения. Разрывы строк
# являются частью мобильной типографики, но не добавляют новых рассуждений.
V3_INNER_CHAIN = (
    ("Луке пока не написал.",),
    ("По воскресеньям после четырёх", "здесь обычно пусто."),
    ("Вчера оно видело матч.",),
    ("А тренировку увидит?",),
    ("Сорок два.",),
    ("Мягче.",),
    ("Ещё.",),
    ("Хватит. Проверю.",),
    ("Снова сорок два.",),
    ("Тренировку не считает?",),
)


def apply_ch2_v3_frame(num: str, im_rgb: Image.Image):
    """Неразрушающий леттеринг одного скадрированного кадра v3."""
    # Неизменившиеся кадры используют проверенные примитивы v2.
    inherited = {
        "01": "01",
        "02": "02",
        "08": "08",
        "09": "09",
        "13": "12",  # диалог сдвинулся на одну позицию после нового вызова
    }
    if num in inherited:
        return apply_ch2_frame(inherited[num], im_rgb)

    im = im_rgb.convert("RGBA")
    boxes = []
    if num == "03":
        # Только физическое название. Знание времени принадлежит Ветрову,
        # а не неправдоподобной объясняющей табличке на двери.
        _door_card(
            im,
            (170, 196, 630, 334),
            [
                ("СТАРЫЙ МАНЕЖ", 238, 25, "m"),
                ("«ТОРПЕДО»", 288, 33, "b"),
            ],
            boxes,
            "03_name_v3",
            dark=True,
        )
    return im.convert("RGB"), len(boxes)


CH2_V3_SCORE = [
    ("ch2/v2_01_room.jpg", "01", 1240, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=88, pad_bot=92, items=[
            {"lines": V3_INNER_CHAIN[0], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch2/v2_02_garage.jpg", "02", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch2/v3_03_door.jpg", "03", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=86, pad_bot=90, items=[
            {"lines": V3_INNER_CHAIN[1], "pos": "center", "size": 34, "w": "el"},
        ])),
    ("ch2/v2_04_locker.jpg", "04", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=130, items=[])),
    ("ch2/v2_05_manege_master.jpg", "05", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=86, pad_bot=90, item_gap=42, items=[
            {"lines": V3_INNER_CHAIN[2], "pos": "left", "size": 35, "w": "el"},
            {"lines": V3_INNER_CHAIN[3], "pos": "right", "size": 36, "w": "em"},
        ])),
    ("ch2/v2_06_profile_call.jpg", "06", 1160, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 76, "pad_after": 0},
        ])),
    ("ch2/v3_07_profile.png", "07", 1100, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=92, pad_bot=0, item_gap=50, items=[
            {"lines": V3_INNER_CHAIN[4], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 70, "pad_after": 0},
        ])),
    ("ch2/v2_08_sole_touch.jpg", "08", 1220, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=78, pad_bot=82, items=[
            {"lines": V3_INNER_CHAIN[5], "pos": "left", "size": 35, "w": "em"},
        ])),
    ("ch2/v2_09_chest_touch.jpg", "09", 1160, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=80, pad_bot=84, items=[
            {"lines": V3_INNER_CHAIN[6], "pos": "right", "size": 35, "w": "em"},
        ])),
    ("ch2/v2_10_miscontrol.jpg", "10", 1240, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, items=[
            {"lines": V3_INNER_CHAIN[7], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch2/v3_11_profile_recall.jpg", "11", 1260, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 84, "pad_after": 0},
        ])),
    ("ch2/v3_12_profile.png", "12", 1100, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=94, pad_bot=0, item_gap=48, items=[
            {"lines": V3_INNER_CHAIN[8], "pos": "center", "size": 37, "w": "em"},
            {"lines": V3_INNER_CHAIN[9], "pos": "center", "size": 36, "w": "el"},
            {"kind": "fade", "h": 180, "pad_before": 74, "pad_after": 0},
        ])),
    ("ch2/v2_12_guard.jpg", "13", 1420, 3, "paper", dict(
        bg=(PAPER, DARK), pad_top=0, pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_after": 0},
            {"kind": "space", "h": 480},
        ])),
    ("ch2/v3_14_welcome.png", "14", 760, 3, "dark", dict(
        bg=(DARK, DARK), items=[
            {"kind": "space", "h": 340},
        ])),
    ("ch2/v2_14_room_night.jpg", "15", 1420, 3, "dark", dict(
        bg=(DARK, DARK), min_h=360, items=[])),
]


def _gutter_text_count() -> int:
    return sum(
        sum(1 for item in spec["items"] if item.get("kind", "mono") not in ("space", "fade"))
        for *_, spec in CH2_V3_SCORE
    )


def build_v3_lettered_previews(out_dir=Path("_backup/ch2_v3_lettered")):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()

    inside = 0
    for path, num, height, focus, _, gutter in CH2_V3_SCORE:
        raw = Image.open(path).convert("RGB")
        framed = raw if raw.size == (W, height) else cover(raw, W, height, focus=focus)
        lettered, count = apply_ch2_v3_frame(num, framed)
        lettered.save(out_dir / f"{num}.jpg", quality=93, optimize=True)
        inside += count
        render_gutter(
            gutter["bg"][0], gutter["bg"][1], gutter["items"],
            pad_top=gutter.get("pad_top", 74), pad_bot=gutter.get("pad_bot", 78),
            item_gap=gutter.get("item_gap", 44), min_h=gutter.get("min_h", 130),
        )

    render_gutter(
        CH2_OPENING_GUTTER["bg"][0], CH2_OPENING_GUTTER["bg"][1], CH2_OPENING_GUTTER["items"],
        pad_top=CH2_OPENING_GUTTER.get("pad_top", 74),
        pad_bot=CH2_OPENING_GUTTER.get("pad_bot", 78),
        item_gap=CH2_OPENING_GUTTER.get("item_gap", 44),
        min_h=CH2_OPENING_GUTTER.get("min_h", 130),
    )
    return inside, _gutter_text_count()


if __name__ == "__main__":
    inside, gutter = build_v3_lettered_previews()
    print(
        f"гл. 2 v3: {len(CH2_V3_SCORE)} кадров · {inside} внутрикадровых + "
        f"{gutter} межкадровых блоков · 0 пересечений"
    )
