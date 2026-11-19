"""Леттеринг и производственная партитура Главы 4 v2."""
from __future__ import annotations

from PIL import Image, ImageDraw

from build_ch4_v2_numbers import apply_ch4_numbers
from build_lettering import DARK, PAPER, say, sfx, shout, stamp
from grid import F


W = 800
TITLE = "ПРОТОКОЛ 1:0"

MATCH_STAMP = "«ВЕРЕСК» — «ТОРПЕДО-2» · ВТОРАЯ ЛИГА"
GOAL_MINUTE = "38′"
CALL_MINUTE = "62′"
SUB_MINUTE = "65′"
COACH_CALL = ("ВЕТРОВ!", "РАЗМИНАЙСЯ!")
COACH_INSTRUCTION = ("Подбери за Шатским.", "И первый пас — проще.")
VETROV_REPLY = ("Понял.",)
FINAL_SCORE_STAMP = "«ВЕРЕСК» 1:0 «ТОРПЕДО-2»"
COACH_ASSESSMENT = (
    "Ветров нормально вошёл.",
    "Не полез за мячом —",
    "поэтому успел закрыть зону.",
)


def _protocol_phone(image: Image.Image) -> None:
    """Наносит настоящую кириллицу только на пустой физический экран телефона."""
    draw = ImageDraw.Draw(image)
    screen = (292, 718, 514, 1170)
    draw.rounded_rectangle(screen, radius=18, fill=(242, 246, 245, 255), outline=(30, 42, 48, 255), width=3)
    draw.text((403, 748), "ПРОТОКОЛ МАТЧА", font=F("m", 16), fill=(75, 88, 93, 255), anchor="ma")
    draw.line((316, 778, 490, 778), fill=(180, 190, 190, 255), width=2)
    draw.text((403, 814), "ВЕРЕСК 1:0", font=F("b", 24), fill=(25, 31, 34, 255), anchor="ma")
    draw.text((403, 846), "ТОРПЕДО-2", font=F("b", 22), fill=(25, 31, 34, 255), anchor="ma")
    draw.line((316, 874, 490, 874), fill=(180, 190, 190, 255), width=2)
    draw.text((403, 910), "ВЕТРОВ", font=F("b", 25), fill=(151, 31, 42, 255), anchor="ma")
    draw.text((403, 946), "25 МИНУТ", font=F("m", 20), fill=(48, 57, 61, 255), anchor="ma")
    draw.line((316, 974, 490, 974), fill=(180, 190, 190, 255), width=2)
    draw.text((403, 1015), "ОТБОРЫ · 2", font=F("b", 21), fill=(25, 31, 34, 255), anchor="ma")
    draw.text((403, 1063), "ОЦЕНКА · 6.6", font=F("b", 21), fill=(25, 31, 34, 255), anchor="ma")


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

    elif num == "12":
        keepouts = [
            ("ветров", (155, 300, 610, 1240)),
            ("соперник", (555, 390, 795, 1030)),
            ("мяч", (515, 925, 720, 1165)),
        ]
        sfx(image, (660, 210), "ТК!", boxes, keepouts, tag="12_tk", size=52, angle=-8)

    elif num == "13":
        keepouts = [
            ("ветров", (0, 300, 585, 1200)),
            ("соперник", (450, 260, 795, 1160)),
            ("мяч", (500, 930, 720, 1185)),
        ]
        shout(image, (155, 170), ["ЕСТЬ!"], boxes, keepouts, tag="13_yes", size=38, spikes=22)

    elif num == "15":
        keepouts = [
            ("ветров", (145, 390, 590, 1190)),
            ("мяч", (520, 780, 700, 1045)),
        ]
        sfx(image, (665, 215), "ТУК!", boxes, keepouts, tag="15_tuk", size=52, angle=-8)

    elif num == "16":
        keepouts = [
            ("игроки", (0, 520, 800, 1220)),
            ("судья", (360, 540, 515, 850)),
        ]
        stamp(image, (0, 30), FINAL_SCORE_STAMP, boxes, keepouts, tag="16_score", size=25, center_x=True)
        sfx(image, (650, 330), "ФЬЮ-ИТЬ!", boxes, keepouts, tag="16_whistle", size=48, angle=-5)

    elif num == "18":
        keepouts = [
            ("тренер", (0, 390, 465, 1290)),
            ("пресс-атташе", (530, 390, 800, 1290)),
            ("ветров", (440, 430, 620, 1110)),
        ]
        say(
            image,
            [(398, 185, list(COACH_ASSESSMENT))],
            tail_to=(270, 455),
            boxes=boxes,
            keepouts=keepouts,
            tag="18_coach",
            size=25,
            bend=-0.08,
        )

    elif num == "19":
        _protocol_phone(image)
        boxes.append(("19_protocol", (292, 718, 514, 1170)))

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
        bg=(DARK, PAPER), pad_top=90, pad_bot=0, items=[
            {"lines": ["Решения. Снова."], "pos": "center", "size": 37, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 66, "pad_after": 0},
        ])),
    ("ch4/v2_12_recovery_one_src.jpg", "12", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_13_recovery_two_src.jpg", "13", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_14_hold_zone_src.jpg", "14", 1370, 3, "paper", dict(
        bg=(PAPER, PAPER), pad_top=88, pad_bot=92, items=[
            {"lines": ["Не выдёргиваться."], "pos": "center", "size": 38, "w": "em"},
        ])),
    ("ch4/v2_15_recovery_three_src.jpg", "15", 1320, 3, "paper", dict(
        bg=(PAPER, PAPER), min_h=105, items=[])),
    ("ch4/v2_16_final_whistle_src.jpg", "16", 1320, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 72, "pad_after": 0},
        ])),
    ("ch4/v2_17_result.png", "17", 1120, 3, "dark", dict(
        bg=(DARK, PAPER), pad_top=92, pad_bot=0, items=[
            {"lines": ["Двадцать восемь."], "pos": "center", "size": 38, "w": "em"},
            {"kind": "fade", "h": 180, "pad_before": 68, "pad_after": 0},
        ])),
    ("ch4/v2_18_coach_corridor_src.jpg", "18", 1320, 3, "paper", dict(
        bg=(PAPER, DARK), pad_bot=0, items=[
            {"kind": "fade", "h": 180, "pad_before": 82, "pad_after": 0},
        ])),
    ("ch4/v2_19_protocol_phone_src.jpg", "19", 1370, 3, "dark", dict(
        bg=(DARK, DARK), pad_top=96, pad_bot=98, items=[
            {"lines": ["Два."], "pos": "center", "size": 40, "w": "em"},
        ])),
    ("ch4/v2_20_night_bus_src.jpg", "20", 1370, 3, "dark", dict(
        bg=(DARK, DARK), min_h=360, items=[])),
]
