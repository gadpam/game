"""Леттеринг и режиссёрская партитура Главы 2 ``script-v2``.

Модуль использует те же манга-примитивы и мобильный масштаб, что и
утверждённая Глава 1, но не изменяет её файлы и не касается legacy-версии
Главы 2. В тексте остаются только утверждённые реплики, мысли, SFX и точная
кириллица входной двери.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from build_lettering import (
    DARK,
    PAPER,
    LF,
    _check_box,
    check_glyphs,
    render_gutter,
    say,
    sfx,
    stamp,
    thought,
)
from grid import cover

W = 800


def _door_card(im, box, lines, boxes, tag, dark=False):
    """Чёткая программная кириллица поверх пустых физических плашек двери."""
    x0, y0, x1, y1 = box
    _check_box(tag, box, boxes, [], im.width, im.height, margin=10)
    for text, _, _, _ in lines:
        check_glyphs(text, "ob" if dark else "em")

    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 5, y0 + 8, x1 + 5, y1 + 8), radius=5, fill=(5, 8, 12, 105))
    layer = Image.alpha_composite(layer, shadow.filter(ImageFilter.GaussianBlur(7)))
    draw = ImageDraw.Draw(layer)

    if dark:
        fill = (50, 54, 55, 246)
        edge = (200, 181, 134, 245)
        ink = (246, 240, 220, 255)
    else:
        fill = (238, 235, 216, 250)
        edge = (58, 62, 64, 245)
        ink = (24, 28, 31, 255)

    draw.rounded_rectangle(box, radius=5, fill=fill, outline=edge, width=4)
    draw.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), radius=3, outline=edge[:3] + (105,), width=2)
    for text, y, size, weight in lines:
        font_key = "ob" if weight == "b" else ("om" if weight == "m" else "em")
        check_glyphs(text, font_key)
        draw.text(((x0 + x1) // 2, y), text, font=LF(font_key, size), fill=ink, anchor="mm")

    im.alpha_composite(layer)


def apply_ch2_frame(num: str, im_rgb: Image.Image):
    """Неразрушающий леттеринг одного уже скадрированного кадра Главы 2."""
    im = im_rgb.convert("RGBA")
    boxes = []

    if num == "01":
        stamp(
            im,
            (0, 30),
            "ВОСКРЕСЕНЬЕ · 16:10",
            boxes,
            [],
            tag="01_time",
            size=29,
            center_x=True,
        )

    elif num == "02":
        # Единственный сухой удар из партитуры; действие детей остаётся открытым.
        sfx(im, (642, 394), "ТУК", boxes, [], tag="02_tuk", size=50, angle=-8.0)

    elif num == "03":
        _door_card(
            im,
            (138, 184, 662, 316),
            [
                ("СТАРЫЙ МАНЕЖ", 226, 26, "m"),
                ("«ТОРПЕДО»", 276, 34, "b"),
            ],
            boxes,
            "03_name",
            dark=True,
        )
        _door_card(
            im,
            (116, 376, 684, 668),
            [
                ("ВОСКРЕСЕНЬЕ", 418, 28, "b"),
                ("СВОБОДНОЕ ВРЕМЯ", 478, 24, "m"),
                ("16:00–17:00", 526, 34, "b"),
                ("ЗАКРЫТИЕ · 17:30", 608, 27, "m"),
            ],
            boxes,
            "03_hours",
            dark=False,
        )

    elif num == "04":
        keepouts = [("ветров", (455, 410, 790, 1120))]
        thought(im, (386, 164), ["Никого.", "Тем лучше."], boxes, keepouts, tag="04_thought", size=33)

    elif num == "08":
        keepouts = [("бутса и мяч", (150, 470, 790, 1160))]
        sfx(im, (158, 350), "ТУК", boxes, keepouts, tag="08_tuk", size=52, angle=-9.0)

    elif num == "09":
        keepouts = [("ветров и мяч", (130, 350, 620, 1040))]
        sfx(im, (650, 226), "ХХ…", boxes, keepouts, tag="09_breath", size=43, angle=-5.0, mode="pulse")

    elif num == "12":
        keepouts = [
            ("ветров", (155, 560, 420, 1240)),
            ("сторож", (510, 555, 770, 955)),
        ]
        say(
            im,
            [(550, 132, ["Парень, всё.", "Закрываю."])],
            tail_to=(710, 320),
            boxes=boxes,
            keepouts=keepouts,
            tag="12_guard_close",
            size=31,
            bend=-0.12,
        )
        say(
            im,
            [(210, 300, ["А завтра можно", "прийти?"])],
            tail_to=(276, 630),
            boxes=boxes,
            keepouts=keepouts,
            tag="12_vetrov",
            size=31,
            bend=0.12,
        )
        say(
            im,
            [(600, 450, ["После четырёх", "зал свободен."])],
            tail_to=(582, 620),
            boxes=boxes,
            keepouts=keepouts,
            tag="12_guard_tomorrow",
            size=31,
            bend=-0.10,
        )

    return im.convert("RGB"), len(boxes)


# Высоты и фокус задают тот же переменный вебтун-ритм, что и у Главы 1.
# После каждого кадра идёт явная партитура межкадрового пространства.
CH2_OPENING_GUTTER = dict(
    bg=(DARK, PAPER),
    pad_bot=72,
    items=[
        {"kind": "fade", "h": 180, "pad_after": 72},
    ],
)

CH2_SCORE = [
    ("ch2/v2_01_room.jpg", "01", 1240, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=88, pad_bot=92, items=[
            {"lines": ["Луке пока не написал."], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch2/v2_02_garage.jpg", "02", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch2/v2_03_door.jpg", "03", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch2/v2_04_locker.jpg", "04", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=130, items=[])),
    ("ch2/v2_05_manege_master.jpg", "05", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=100, items=[])),
    ("ch2/v2_06_profile_call.jpg", "06", 1160, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 76, "pad_after": 0},
        ])),
    ("ch2/v2_07_profile.png", "07", 1100, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=92, pad_bot=0, item_gap=50, items=[
            {"lines": ["Сорок два."], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 70, "pad_after": 0},
        ])),
    ("ch2/v2_08_sole_touch.jpg", "08", 1220, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=100, items=[])),
    ("ch2/v2_09_chest_touch.jpg", "09", 1160, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch2/v2_10_miscontrol.jpg", "10", 1240, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 92, "pad_after": 0},
        ])),
    ("ch2/v2_11_profile.png", "11", 1100, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=94, pad_bot=0, item_gap=48, items=[
            {"lines": ["Снова сорок два."], "pos": "center", "size": 37, "w": "em"},
            {"lines": ["Тренировку не считает?"], "pos": "center", "size": 36, "w": "el"},
            {"kind": "fade", "h": 180, "pad_before": 74, "pad_after": 0},
        ])),
    ("ch2/v2_12_guard.jpg", "12", 1420, 3, "paper", dict(
        bg=(PAPER, DARK), pad_top=0, pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_after": 0},
            {"kind": "space", "h": 480},
        ])),
    ("ch2/v2_13_welcome.png", "13", 760, 3, "dark", dict(
        bg=(DARK, DARK), items=[
            {"kind": "space", "h": 340},
        ])),
    ("ch2/v2_14_room_night.jpg", "14", 1420, 3, "dark", dict(
        bg=(DARK, DARK), min_h=360, items=[])),
]


def build_lettered_previews(out_dir=Path("_backup/ch2_v2_lettered")):
    """Собирает отдельные кадры для визуального QC, не трогая clean art."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()

    inside = 0
    for path, num, height, focus, _, gutter in CH2_SCORE:
        raw = Image.open(path).convert("RGB")
        framed = raw if raw.size == (W, height) else cover(raw, W, height, focus=focus)
        lettered, count = apply_ch2_frame(num, framed)
        lettered.save(out_dir / f"{num}.jpg", quality=93, optimize=True)
        inside += count
        render_gutter(
            gutter["bg"][0],
            gutter["bg"][1],
            gutter["items"],
            pad_top=gutter.get("pad_top", 74),
            pad_bot=gutter.get("pad_bot", 78),
            item_gap=gutter.get("item_gap", 44),
            min_h=gutter.get("min_h", 130),
        )

    render_gutter(
        CH2_OPENING_GUTTER["bg"][0],
        CH2_OPENING_GUTTER["bg"][1],
        CH2_OPENING_GUTTER["items"],
        pad_top=CH2_OPENING_GUTTER.get("pad_top", 74),
        pad_bot=CH2_OPENING_GUTTER.get("pad_bot", 78),
        item_gap=CH2_OPENING_GUTTER.get("item_gap", 44),
        min_h=CH2_OPENING_GUTTER.get("min_h", 130),
    )
    gutter_text = 4
    return inside, gutter_text


if __name__ == "__main__":
    inside, gutter = build_lettered_previews()
    print(
        f"гл. 2: леттеринг script-v2 готов · {len(CH2_SCORE)} кадров · "
        f"{inside} внутрикадровых + {gutter} межкадровых блоков · 0 пересечений"
    )
