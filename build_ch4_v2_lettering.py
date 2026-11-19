"""Леттеринг и первая производственная партитура Главы 4 v2."""
from __future__ import annotations

from PIL import Image

from build_ch4_v2_numbers import apply_ch4_numbers
from build_lettering import DARK, PAPER, say, sfx, shout, stamp


W = 800
TITLE = "ПРОТОКОЛ 1:0"

MATCH_STAMP = "«ВЕРЕСК» — «ТОРПЕДО-2» · ВТОРАЯ ЛИГА"
GOAL_MINUTE = "38′"
CALL_MINUTE = "62′"
SUB_MINUTE = "65′"
COACH_CALL = ("ВЕТРОВ!", "РАЗМИНАЙСЯ!")
COACH_INSTRUCTION = ("Подбери за Шатским.", "И первый пас — проще.")
VETROV_REPLY = ("Понял.",)


def apply_ch4_v2_frame(num: str, image_rgb: Image.Image):
    image = apply_ch4_numbers(num, image_rgb.convert("RGBA"))
    boxes = []

    if num == "01":
        stamp(image, (0, 30), "ВЫЕЗД · ВТОРАЯ ЛИГА", boxes, [], tag="01_trip", size=27, center_x=True)

    elif num == "03":
        stamp(image, (0, 30), MATCH_STAMP, boxes, [], tag="03_match", size=23, center_x=True)

    elif num == "06":
        keepouts = [
            ("ворота", (185, 395, 760, 770)),
            ("мяч", (585, 540, 735, 700)),
            ("игроки", (0, 500, 620, 1180)),
        ]
        stamp(image, (32, 32), GOAL_MINUTE, boxes, keepouts, tag="06_minute", size=31)
        sfx(image, (655, 260), "ГОООЛ!", boxes, keepouts, tag="06_goal", size=64, angle=-5)

    elif num == "08":
        keepouts = [
            ("ветров", (110, 420, 410, 1190)),
            ("тренер", (430, 440, 760, 1230)),
        ]
        stamp(image, (34, 32), CALL_MINUTE, boxes, keepouts, tag="08_minute", size=31)
        shout(
            image,
            (580, 208),
            list(COACH_CALL),
            boxes,
            keepouts,
            tail_to=(562, 478),
            tag="08_call",
            size=35,
            spikes=23,
        )

    elif num == "09":
        keepouts = [
            ("тренер", (5, 370, 405, 1290)),
            ("ветров", (450, 350, 790, 1270)),
        ]
        say(
            image,
            [(258, 144, list(COACH_INSTRUCTION))],
            tail_to=(330, 430),
            boxes=boxes,
            keepouts=keepouts,
            tag="09_coach",
            size=27,
            bend=-0.10,
        )
        say(
            image,
            [(638, 208, list(VETROV_REPLY))],
            tail_to=(612, 434),
            boxes=boxes,
            keepouts=keepouts,
            tag="09_vetrov",
            size=29,
            bend=0.10,
        )

    elif num == "10":
        keepouts = [
            ("ветров", (130, 320, 540, 1270)),
            ("партнёр", (430, 350, 760, 1240)),
            ("табло замены", (5, 160, 245, 515)),
        ]
        stamp(image, (34, 32), SUB_MINUTE, boxes, keepouts, tag="10_minute", size=31)

    return image.convert("RGB"), len(boxes)


OPENING_GUTTER = dict(
    bg=(DARK, PAPER),
    pad_bot=72,
    items=[
        {"kind": "fade", "h": 180, "pad_after": 62},
        {"kind": "stamp", "text": "ГЛАВА 4"},
        {"lines": [TITLE], "pos": "center", "size": 44, "w": "eb"},
    ],
)


# Кадр 11 — первая панель Системы. Он создаётся вместе с пакетом 01–10,
# но не входит в него, чтобы не нарушать жёсткий лимит десяти фреймов.
CH4_V2_SCORE = [
    ("ch4/v2_01_bus_arrival_src.jpg", "01", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, items=[
            {"lines": ["В автобусе тренер повторил состав", "ещё раз. Моей фамилии среди первых", "одиннадцати не было."], "pos": "left", "size": 33, "w": "el"},
        ])),
    ("ch4/v2_02_lineup.jpg", "02", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=74, pad_bot=80, items=[
            {"lines": ["Шатский вернулся в основу.", "Значит, сегодня снова с лавки."], "pos": "right", "size": 35, "w": "em"},
        ])),
    ("ch4/v2_03_veresk_stadium_establishing_src.jpg", "03", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_04_lockeroom_before_src.jpg", "04", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=80, pad_bot=84, items=[
            {"lines": ["В прошлый раз меня выпустили первым.", "Сегодня даже разминаться не позвали."], "pos": "left", "size": 34, "w": "el"},
        ])),
    ("ch4/v2_05_bench_first_half_src.jpg", "05", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=82, pad_bot=86, items=[
            {"lines": ["«Вереск» не лез вперёд толпой.", "Ждали нашу ошибку."], "pos": "right", "size": 35, "w": "em"},
        ])),
    ("ch4/v2_06_veresk_goal_src.jpg", "06", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, items=[
            {"lines": ["Дождались."], "pos": "center", "size": 37, "w": "em"},
        ])),
    ("ch4/v2_07_halftime_corridor_src.jpg", "07", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=84, pad_bot=88, items=[
            {"lines": ["В перерыве тренер прошёл мимо.", "Ни слова."], "pos": "left", "size": 35, "w": "el"},
        ])),
    ("ch4/v2_08_coach_calls_62_src.jpg", "08", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_09_touchline_instruction_src.jpg", "09", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_10_substitution_65_src.jpg", "10", 1370, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"lines": ["Двадцать пять минут."], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 62, "pad_after": 0},
        ])),
    ("ch4/v2_11_quest.png", "11", 1120, 3, "dark", dict(
        bg=(DARK, DARK), min_h=110, items=[])),
]
