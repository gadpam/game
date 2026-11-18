"""Леттеринг и режиссёрская партитура кандидата Главы 3 v2.

Модуль не собирает скролл и не изменяет legacy. Он создаёт только отдельные
превью кадров для проверки текста до авторского утверждения кода главы.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from build_ch3_v2_numbers import apply_ch3_numbers
from build_lettering import (
    DARK,
    PAPER,
    render_gutter,
    say,
    sfx,
    shout,
    stamp,
)
from grid import cover


W = 800

INNER_CHAIN = (
    ("Сегодня — с первых минут.",),
    ("Шатского после травмы берегут.",),
    ("В центре — я.",),
    ("Три.",),
    ("Не лезть.",),
    ("Ждать.",),
    ("Ровно час.",),
    ("Три чистых.",),
    ("Двадцать восемь.",),
    ("Квест сработал.",),
)

OPENING_STAMP = "КУБОК · ДЕНЬ МАТЧА"
MATCH_STAMP = "«ГОРЕЦ» — «ТОРПЕДО-2» · КУБОК"
MINUTE_STAMP = "60′"
FINAL_WHISTLE_SFX = "ФЬЮ-ИТЬ!"
COACH_BRIEFING = ("Первый час играешь.", "Потом выйдет Мельник.")
VETROV_REPLY = ("Понял.",)
SUB_CALL = ("ВЕТРОВ УХОДИТ!", "МЕЛЬНИК ВЫХОДИТ!")
COACH_AFTER = (
    ("Замена была по плану.", "Не из-за тебя."),
    ("Начал ждать момент.", "Так и играй."),
)


def apply_ch3_v2_frame(num: str, image_rgb: Image.Image):
    image = apply_ch3_numbers(num, image_rgb.convert("RGBA"))
    boxes = []

    if num == "01":
        stamp(image, (0, 30), OPENING_STAMP, boxes, [], tag="01_day", size=28, center_x=True)

    elif num == "03":
        keepouts = [
            ("тренер", (145, 280, 425, 1160)),
            ("ветров", (455, 300, 735, 1170)),
        ]
        say(
            image,
            [(268, 142, list(COACH_BRIEFING))],
            tail_to=(294, 398),
            boxes=boxes,
            keepouts=keepouts,
            tag="03_coach",
            size=25,
            bend=-0.10,
        )
        say(
            image,
            [(613, 180, list(VETROV_REPLY))],
            tail_to=(584, 418),
            boxes=boxes,
            keepouts=keepouts,
            tag="03_vetrov",
            size=30,
            bend=0.10,
        )

    elif num == "04":
        stamp(
            image,
            (0, 30),
            MATCH_STAMP,
            boxes,
            [],
            tag="04_match",
            size=24,
            center_x=True,
        )

    elif num == "06":
        keepouts = [
            ("ветров", (100, 220, 565, 1110)),
            ("соперник", (560, 210, 795, 1090)),
            ("мяч", (540, 820, 735, 1060)),
        ]
        sfx(image, (674, 1190), "ТК!", boxes, keepouts, tag="06_tk", size=50, angle=-8.0)

    elif num == "07":
        keepouts = [
            ("ветров", (40, 250, 555, 1140)),
            ("соперник", (370, 255, 780, 1130)),
        ]
        shout(
            image,
            (642, 136),
            ["ЕЩЁ!"],
            boxes,
            keepouts,
            tail_to=None,
            tag="07_more",
            size=39,
        )

    elif num == "09":
        keepouts = [
            ("ветров", (65, 315, 610, 1090)),
            ("соперник", (455, 235, 795, 1020)),
            ("мяч", (560, 780, 770, 1030)),
        ]
        sfx(image, (664, 1190), "ТК!", boxes, keepouts, tag="09_tk", size=50, angle=-8.0)

    elif num == "10":
        keepouts = [
            ("официальный", (0, 390, 160, 1250)),
            ("тренер", (160, 400, 470, 1190)),
            ("ветров", (410, 420, 720, 1260)),
        ]
        stamp(image, (38, 30), MINUTE_STAMP, boxes, keepouts, tag="10_minute", size=31)
        shout(
            image,
            (540, 174),
            list(SUB_CALL),
            boxes,
            keepouts,
            tail_to=(330, 446),
            tag="10_sub",
            size=34,
            spikes=24,
        )

    elif num == "13":
        keepouts = [
            ("судья", (378, 580, 530, 940)),
            ("игрок слева", (100, 690, 250, 1010)),
            ("игрок справа", (555, 745, 735, 1230)),
        ]
        sfx(
            image,
            (650, 350),
            FINAL_WHISTLE_SFX,
            boxes,
            keepouts,
            tag="13_whistle",
            size=49,
            angle=-5.0,
        )

    elif num == "17":
        keepouts = [
            ("ветров", (0, 300, 340, 1370)),
            ("тренер", (360, 250, 730, 1170)),
        ]
        say(
            image,
            [
                (205, 128, list(COACH_AFTER[0])),
                (590, 128, list(COACH_AFTER[1])),
            ],
            tail_to=(515, 358),
            boxes=boxes,
            keepouts=keepouts,
            tag="17_coach",
            size=23,
            bend=-0.08,
        )

    return image.convert("RGB"), len(boxes)


OPENING_GUTTER = dict(
    bg=(DARK, PAPER),
    pad_bot=72,
    items=[{"kind": "fade", "h": 180, "pad_after": 72}],
)

# Высоты нужны для индивидуального QC и будущей финальной сборки, но этот
# модуль сам скролл не создаёт.
CH3_V2_SCORE = [
    ("ch3/v2_01_kitchen.jpg", "01", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, items=[
            {"lines": INNER_CHAIN[0], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch3/v2_02_lineup.jpg", "02", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=88, item_gap=40, items=[
            {"lines": INNER_CHAIN[1], "pos": "left", "size": 34, "w": "el"},
            {"lines": INNER_CHAIN[2], "pos": "right", "size": 36, "w": "em"},
        ])),
    ("ch3/v2_03_coach_briefing.jpg", "03", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=120, items=[])),
    ("ch3/v2_04_pitch.jpg", "04", 1420, 2, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 84, "pad_after": 0},
        ])),
    ("ch3/v2_05_quest.png", "05", 920, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=92, pad_bot=0, items=[
            {"lines": INNER_CHAIN[3], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 72, "pad_after": 0},
        ])),
    ("ch3/v2_06_tackle_one.jpg", "06", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_07_tackle_two.jpg", "07", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_08_wait.jpg", "08", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=78, pad_bot=82, item_gap=38, items=[
            {"lines": INNER_CHAIN[4], "pos": "left", "size": 35, "w": "el"},
            {"lines": INNER_CHAIN[5], "pos": "right", "size": 37, "w": "em"},
        ])),
    ("ch3/v2_09_tackle_three.jpg", "09", 1260, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_10_subbed.jpg", "10", 1360, 2, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=88, items=[
            {"lines": INNER_CHAIN[6], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch3/v2_11_bench.jpg", "11", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=88, items=[
            {"lines": INNER_CHAIN[7], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch3/v2_12_bench_detail.jpg", "12", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_13_final_whistle.jpg", "13", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_14_walk_off.jpg", "14", 1420, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 84, "pad_after": 0},
        ])),
    ("ch3/v2_15_done.png", "15", 830, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=94, pad_bot=0, items=[
            {"lines": INNER_CHAIN[8], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 72, "pad_after": 0},
        ])),
    ("ch3/v2_16_result_reaction.jpg", "16", 1280, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=88, items=[
            {"lines": INNER_CHAIN[9], "pos": "center", "size": 36, "w": "em"},
        ])),
    ("ch3/v2_17_coach.jpg", "17", 1420, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=110, items=[])),
    ("ch3/v2_18_empty.jpg", "18", 1420, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 84, "pad_after": 0},
        ])),
    ("ch3/v2_19_bus_window.jpg", "19", 1240, 3, "dark", dict(
        bg=(DARK, DARK), min_h=120, items=[])),
    ("ch3/v2_20_bus.jpg", "20", 1420, 3, "dark", dict(
        bg=(DARK, DARK), min_h=360, items=[])),
]


def _gutter_text_count() -> int:
    return sum(
        sum(1 for item in spec["items"] if item.get("kind", "mono") not in ("space", "fade"))
        for *_, spec in CH3_V2_SCORE
    )


def build_lettered_previews(out_dir=Path("_backup/ch3_v2_lettered")):
    """Собирает только отдельные кадры; полной ленты здесь намеренно нет."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()

    inside = 0
    for path, number, height, focus, _, gutter in CH3_V2_SCORE:
        raw = Image.open(path).convert("RGB")
        framed = raw if raw.size == (W, height) else cover(raw, W, height, focus=focus)
        lettered, count = apply_ch3_v2_frame(number, framed)
        lettered.save(out_dir / f"{number}.jpg", quality=93, optimize=True)
        inside += count
        render_gutter(
            gutter["bg"][0], gutter["bg"][1], gutter["items"],
            pad_top=gutter.get("pad_top", 74), pad_bot=gutter.get("pad_bot", 78),
            item_gap=gutter.get("item_gap", 44), min_h=gutter.get("min_h", 130),
        )

    render_gutter(
        OPENING_GUTTER["bg"][0], OPENING_GUTTER["bg"][1], OPENING_GUTTER["items"],
        pad_top=OPENING_GUTTER.get("pad_top", 74), pad_bot=OPENING_GUTTER.get("pad_bot", 78),
        item_gap=OPENING_GUTTER.get("item_gap", 44), min_h=OPENING_GUTTER.get("min_h", 130),
    )
    return inside, _gutter_text_count()


if __name__ == "__main__":
    inside, gutters = build_lettered_previews()
    print(
        f"гл. 3 v2: {len(CH3_V2_SCORE)} отдельных кадров · "
        f"{inside} внутрикадровых + {gutters} межкадровых блоков · скролл не создавался"
    )
