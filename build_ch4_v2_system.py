"""Изолированно собирает панели квеста и результата Главы 4 v2."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ch4_v2_contract import DECISION_AFTER, DECISION_BEFORE, QUEST_RANK, RECOVERY_GOAL
from grid import F, sp


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ch4" / "v2_11_quest.png"
RESULT_OUT = ROOT / "ch4" / "v2_17_result.png"
W, H = 800, 1120


def _text(draw: ImageDraw.ImageDraw, xy, text, weight, size, fill, anchor="la"):
    draw.text(xy, text, font=F(weight, size), fill=fill, anchor=anchor)


def build() -> Path:
    image = Image.new("RGBA", (W, H), (3, 7, 15, 255))

    # Сдержанная панель в уже принятом стиле Solo Leveling: никаких XP,
    # уровней, полос и скрытых чисел.
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for box, color, width in (
        ((50, 62, 750, 1058), (33, 177, 245, 90), 9),
        ((70, 82, 730, 1038), (81, 212, 255, 70), 3),
    ):
        gd.rounded_rectangle(box, radius=28, outline=color, width=width)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    image = Image.alpha_composite(image, glow)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((62, 72, 738, 1048), radius=25, fill=(7, 17, 31, 246), outline=(90, 209, 252, 230), width=3)
    draw.rounded_rectangle((82, 92, 718, 1028), radius=18, outline=(47, 103, 143, 170), width=2)
    draw.line((126, 208, 674, 208), fill=(49, 114, 158, 190), width=2)
    draw.line((126, 716, 674, 716), fill=(49, 114, 158, 190), width=2)

    _text(draw, (400, 132), sp("КВЕСТ", 4), "m", 24, (145, 212, 239), "ma")
    _text(draw, (400, 244), "ПОВТОРНЫЙ РАНГ", "m", 22, (118, 158, 184), "ma")
    _text(draw, (400, 305), QUEST_RANK, "b", 92, (236, 247, 252), "ma")

    _text(draw, (400, 420), "3 ВОЗВРАТА МЯЧА", "b", 39, (239, 248, 252), "ma")
    _text(draw, (400, 476), "ИЗ СВОЕЙ ЗОНЫ", "b", 37, (239, 248, 252), "ma")

    _text(draw, (400, 574), "УСЛОВИЕ", "m", 21, (116, 166, 195), "ma")
    _text(draw, (400, 622), f"{RECOVERY_GOAL} ПОЛЕЗНЫХ ВОЗВРАТА", "m", 27, (192, 225, 238), "ma")
    _text(draw, (400, 657), "ДО ФИНАЛЬНОГО СВИСТКА", "m", 23, (145, 190, 211), "ma")

    _text(draw, (400, 770), "НАГРАДА", "m", 21, (116, 166, 195), "ma")
    _text(draw, (400, 828), "ПРИНЯТИЕ РЕШЕНИЙ", "b", 34, (240, 249, 252), "ma")
    _text(draw, (310, 899), str(DECISION_BEFORE), "b", 56, (100, 221, 255), "ma")
    _text(draw, (490, 899), str(DECISION_AFTER), "b", 56, (100, 221, 255), "ma")
    draw.line((365, 936, 426, 936), fill=(100, 221, 255), width=7)
    draw.polygon(((426, 923), (450, 936), (426, 949)), fill=(100, 221, 255))
    _text(draw, (400, 980), "БЕЗ АВТОМАТИЧЕСКОГО ПОВЫШЕНИЯ РАНГА", "m", 18, (111, 157, 181), "ma")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT)
    print(f"{OUT.relative_to(ROOT)}: {W}x{H} · {QUEST_RANK} · {RECOVERY_GOAL} · {DECISION_BEFORE}→{DECISION_AFTER}")
    return OUT


def build_result() -> Path:
    image = Image.new("RGBA", (W, H), (3, 7, 15, 255))
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for box, color, width in (
        ((50, 62, 750, 1058), (42, 213, 209, 95), 9),
        ((70, 82, 730, 1038), (102, 238, 225, 70), 3),
    ):
        gd.rounded_rectangle(box, radius=28, outline=color, width=width)
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(18)))

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (62, 72, 738, 1048),
        radius=25,
        fill=(7, 17, 31, 246),
        outline=(105, 229, 224, 235),
        width=3,
    )
    draw.rounded_rectangle((82, 92, 718, 1028), radius=18, outline=(50, 132, 151, 180), width=2)
    draw.line((126, 208, 674, 208), fill=(55, 141, 158, 195), width=2)
    draw.line((126, 682, 674, 682), fill=(55, 141, 158, 195), width=2)

    _text(draw, (400, 132), sp("СИСТЕМА", 3), "m", 23, (151, 226, 232), "ma")
    _text(draw, (400, 260), "ВЫПОЛНЕНО", "b", 52, (112, 241, 219), "ma")
    _text(draw, (400, 356), f"КВЕСТ · {QUEST_RANK}", "m", 27, (177, 216, 229), "ma")
    _text(draw, (400, 476), f"{RECOVERY_GOAL} / {RECOVERY_GOAL}", "b", 96, (242, 250, 252), "ma")

    _text(draw, (400, 752), "ПРИНЯТИЕ РЕШЕНИЙ", "b", 36, (240, 249, 252), "ma")
    _text(draw, (310, 844), str(DECISION_BEFORE), "b", 62, (100, 221, 255), "ma")
    _text(draw, (490, 844), str(DECISION_AFTER), "b", 62, (112, 241, 219), "ma")
    draw.line((365, 884, 426, 884), fill=(105, 231, 234), width=7)
    draw.polygon(((426, 871), (450, 884), (426, 897)), fill=(105, 231, 234))

    RESULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(RESULT_OUT)
    print(
        f"{RESULT_OUT.relative_to(ROOT)}: {W}x{H} · ВЫПОЛНЕНО · "
        f"{RECOVERY_GOAL}/{RECOVERY_GOAL} · {DECISION_BEFORE}→{DECISION_AFTER}"
    )
    return RESULT_OUT


if __name__ == "__main__":
    build()
    build_result()
