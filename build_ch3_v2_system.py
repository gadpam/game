"""Изолированные панели Системы для кандидата Главы 3 v2.

Первый успешно выполненный матчевый квест остаётся уровнем F−. Он даёт две
единицы закрепления на нижней ступени и видимый рост ``ОТБОР 26 → 28``.
Legacy-панели Главы 3 не изменяются.
"""
from __future__ import annotations

from pathlib import Path

from build_ch2_system import INK, SafeText
from grid import F, Panel, decorate_panel, depth_bg, holo_card, num_change, rank_crest, sp


OUT_DIR = Path("ch3")
QUEST = OUT_DIR / "v2_05_quest.png"
DONE = OUT_DIR / "v2_13_done.png"
QUEST_RANK = "F−"
TACKLE_BEFORE = 26
TACKLE_AFTER = 28
GOAL = 3

assert QUEST_RANK == "F−"
assert TACKLE_AFTER - TACKLE_BEFORE == 2


def _save(panel: Panel, safe: SafeText, path: Path) -> None:
    safe.check(overlap=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(path)


def _quest_panel() -> None:
    box = (42, 76, 758, 844)
    panel = Panel(depth_bg("n", box, h=920), box, "n", frame_id=None)
    decorate_panel(panel)
    safe = SafeText(panel)

    rank_crest(panel, panel.cx, 142, 244, w_half=82)
    safe.text((panel.cx, 192), QUEST_RANK, F("b", 58), (244, 252, 255, 255),
              anchor="mm", glow=True)
    safe.text((panel.cx, 264), sp("КВЕСТ", 2), F("b", 26),
              panel.st["hot"] + (252,), anchor="ma", glow=True)
    panel.div(314)

    holo_card(panel, box[0] + 38, 342, box[2] - 38, 500, alpha=118, active=True)
    diamond_x = panel.g["lbl"] + 2
    panel.d.polygon(
        [(diamond_x, 409), (diamond_x + 9, 394), (diamond_x + 18, 409), (diamond_x + 9, 424)],
        fill=panel.st["hot"] + (245,), outline=panel.st["edge"] + (255,),
    )
    safe.text((diamond_x + 34, 374), "3 ЧИСТЫХ ОТБОРА", F("b", 29), INK + (255,), glow=True)
    safe.text((diamond_x + 34, 424), "В ЭТОМ МАТЧЕ", F("m", 24), INK + (245,))

    panel.div(530)
    safe.text((panel.cx, 556), sp("НАГРАДА", 2), F("m", 17),
              panel.st["dim"] + (225,), anchor="ma")
    safe.text((panel.cx, 592), "ОТБОР", F("b", 29), panel.st["ink"] + (255,),
              anchor="ma", glow=True)
    change_box = num_change(panel, 660, TACKLE_BEFORE, TACKLE_AFTER, size=48,
                            color_r=(112, 224, 255), align="center")
    safe.items.append(("26-28", change_box))
    _save(panel, safe, QUEST)


def _done_panel() -> None:
    box = (42, 76, 758, 754)
    panel = Panel(depth_bg("g", box, h=830), box, "g", frame_id=None)
    decorate_panel(panel)
    safe = SafeText(panel)

    safe.text((panel.cx, 150), sp("ВЫПОЛНЕНО", 2), F("b", 34),
              (239, 255, 249, 255), anchor="ma", glow=True)
    safe.text((panel.cx, 206), f"КВЕСТ · {QUEST_RANK}", F("m", 20),
              panel.st["dim"] + (235,), anchor="ma")
    panel.div(250)

    holo_card(panel, box[0] + 42, 282, box[2] - 42, 432, alpha=126, active=True)
    safe.text((panel.cx, 316), "ЧИСТЫЕ ОТБОРЫ", F("m", 20),
              panel.st["ink"] + (242,), anchor="ma")
    safe.text((panel.cx, 382), f"{GOAL} / {GOAL}", F("b", 48),
              panel.st["hot"] + (255,), anchor="mm", glow=True)

    panel.div(468)
    safe.text((panel.cx, 504), "ОТБОР", F("b", 28),
              panel.st["ink"] + (255,), anchor="ma", glow=True)
    change_box = num_change(panel, 584, TACKLE_BEFORE, TACKLE_AFTER, size=54,
                            color_r=(116, 236, 190), align="center")
    safe.items.append(("26-28", change_box))
    panel.div(654)
    _save(panel, safe, DONE)


def build() -> list[str]:
    _quest_panel()
    _done_panel()
    return [str(QUEST), str(DONE)]


if __name__ == "__main__":
    for output in build():
        print(output)
