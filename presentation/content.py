# -*- coding: utf-8 -*-
"""
Содержимое презентации для родительского собрания группы П32
(3 курс, специальность «Разработка и сопровождение программного
обеспечения информационных систем»).

Фактура — в data.py, вёрстка — в deck.py.
Пустые места (___) заполняются перед встречей.
"""
from __future__ import annotations

from math import ceil

import data
from deck import (ACCENT, ACCENT2, ACCENT2_SOFT, ACCENT_SOFT, BODY, CARD, CW, DPI,
                  GREEN, GREEN_SOFT, INK, LINE, M_L, MUTED, PAPER, SLIDE_H,
                  SLIDE_W, BODY_BOTTOM, BODY_TOP, Canvas, block_height, measure,
                  para, run)

SOFT_NUM = "CFE3E0"
AMBER = "B8860B"
AMBER_SOFT = "F6EEDD"
TRACK = "EBE9E3"
STATUS_COLOR = {"ok": GREEN, "near": ACCENT, "mid": AMBER, "zero": ACCENT2}
TOTAL = 22
COURSE = "3 курс · П32 · Программирование"

# пороги зон: (зелёный от, жёлтый от) — по ним красим цифры и полоски
ZONE_ABS = (85, 60)      # абсолютная успеваемость, %
ZONE_AVG = (7.0, 5.0)    # средний балл (шкала 1–10)
ZONE_QUAL = (70, 50)     # качественная успеваемость, %


def zone_color(value: float, limits) -> str:
    """Цвет зоны: зелёный — сильная позиция, жёлтый — средняя, терракота — внимание."""
    green, amber = limits
    if value >= green:
        return GREEN
    if value >= amber:
        return AMBER
    return ACCENT2


# ─────────────────────────────────────────────────────── блоки-шаблоны

def head(c: Canvas, kicker: str, title: str, num: int):
    c.text(M_L, 0.62, CW, [para(run(kicker, "medium", 10.5, ACCENT, spc=1.8, caps=True), space=0)])
    c.text(M_L, 0.94, CW * 0.92, [para(run(title, "bold", 29, INK), space=0, line=1.16)])
    c.hline(M_L, 1.88, CW, LINE, 0.75)
    c.hline(M_L, 6.88, CW, LINE, 0.75)
    c.text(M_L, 7.02, 7.0, [para(run(COURSE, "light", 9.5, MUTED), space=0)])
    c.text(M_L + CW - 1.6, 7.02, 1.6,
           [para(run(f"{num:02d} / {TOTAL}", "medium", 9.5, MUTED), align="r", space=0)])


def bullets(c: Canvas, x, y, w, items, size=13.0, gap=0.24, marker="square",
            color=BODY, weight="light", line=1.32, mcolor=ACCENT):
    for it in items:
        if marker == "square":
            c.rect(x, y + 0.085, 0.095, 0.095, fill=mcolor)
            tx = x + 0.32
        elif marker == "dash":
            c.rect(x, y + 0.185, 0.17, 0.022, fill=mcolor)
            tx = x + 0.40
        elif marker == "tick":
            c.rect(x, y + 0.045, 0.17, 0.17, fill=None, line=mcolor, lw=1.0, radius=0.03)
            tx = x + 0.40
        else:
            tx = x
        h = c.text(tx, y, w - (tx - x),
                   [para(run(it, weight, size, color), space=0, line=line)])
        y += h + gap
    return y


def grid_cards(c: Canvas, items, cols=2, top=BODY_TOP, bottom=BODY_BOTTOM, gap=0.34):
    """items: (eyebrow, title, [строки])"""
    rows = ceil(len(items) / cols)
    w = (CW - gap * (cols - 1)) / cols
    h = (bottom - top - gap * (rows - 1)) / rows
    for i, (eb, ttl, lines) in enumerate(items):
        r, cc = divmod(i, cols)
        x = M_L + cc * (w + gap)
        y = top + r * (h + gap)
        c.card(x, y, w, h)
        c.rect(x, y, 0.055, h, fill=ACCENT if i % 2 == 0 else ACCENT2, radius=0.0)
        ty = y + 0.34
        if eb:
            eb_p = [para(run(eb, "medium", 9.5, MUTED, spc=1.4, caps=True), space=0)]
            c.text(x + 0.42, ty, w - 0.78, eb_p)
            ty += block_height(eb_p, w - 0.78) + 0.16
        ttl_p = [para(run(ttl, "bold", 16.5, INK), space=0, line=1.2)]
        c.text(x + 0.42, ty, w - 0.78, ttl_p)
        ty += block_height(ttl_p, w - 0.78) + 0.16
        for ln in lines:
            ty = bullets(c, x + 0.42, ty, w - 0.78, [ln], size=12.5, gap=0.14,
                         marker="dash", mcolor=ACCENT if i % 2 == 0 else ACCENT2)


def stat_tiles(c: Canvas, tiles, top=2.42, h=2.05, note_color=MUTED):
    n = len(tiles)
    gap = 0.30
    w = (CW - gap * (n - 1)) / n
    for i, (value, label, note) in enumerate(tiles):
        x = M_L + i * (w + gap)
        c.card(x, top, w, h)
        c.text(x + 0.36, top + 0.34, w - 0.72,
               [para(run(value, "bold", 33, ACCENT), space=0, line=1.1)])
        c.text(x + 0.36, top + 1.00, w - 0.72,
               [para(run(label, "medium", 13, INK), space=0, line=1.25)])
        c.text(x + 0.36, top + 1.56, w - 0.72,
               [para(run(note, "light", 10.5, note_color), space=0, line=1.25)])


def rows_table(c: Canvas, rows, top=BODY_TOP, bottom=BODY_BOTTOM, label_w=3.1,
               size=13.5):
    n = len(rows)
    h = (bottom - top) / n
    for i, (label, desc) in enumerate(rows):
        y = top + i * h
        c.text(M_L, y + 0.26, label_w, [para(run(label, "bold", 15, INK), space=0, line=1.2)])
        c.text(M_L + label_w + 0.35, y + 0.28, CW - label_w - 0.35,
               [para(run(desc, "light", 13.5, BODY), space=0, line=1.3)])
        if i < n - 1:
            c.hline(M_L, y + h - 0.10, CW, LINE, 0.75)


def bars(c: Canvas, rows, top=2.55, bottom=6.05):
    """rows: (подпись, процент, пояснение)"""
    n = len(rows)
    h = (bottom - top) / n
    bar_x = M_L + 4.6
    bar_w = CW - 4.6 - 3.0
    for i, (label, pct, note) in enumerate(rows):
        y = top + i * h
        c.text(M_L, y + 0.12, 4.3, [para(run(label, "medium", 14.5, INK), space=0, line=1.2)])
        c.text(M_L, y + 0.52, 4.3, [para(run(note, "light", 11.5, MUTED), space=0, line=1.25)])
        c.rect(bar_x, y + 0.30, bar_w, 0.16, fill=ACCENT_SOFT, radius=0.08)
        c.rect(bar_x, y + 0.30, bar_w * pct / 100.0, 0.16, fill=ACCENT, radius=0.08)
        c.text(bar_x + bar_w + 0.22, y + 0.24, 2.2,
               [para(run(f"{pct}%", "bold", 17, ACCENT), space=0)])


def timeline(c: Canvas, steps, top=3.0):
    n = len(steps)
    gap = 0.28
    w = (CW - gap * (n - 1)) / n
    y_line = top + 0.30
    c.hline(M_L + w / 2, y_line, CW - w, LINE, 1.0)
    for i, (ttl, note) in enumerate(steps):
        x = M_L + i * (w + gap)
        c.dot(x + w / 2, y_line + 0.007, 0.075, ACCENT if i < n - 1 else ACCENT2)
        c.text(x, top - 0.16, w, [para(run(ttl, "bold", 14.5, INK), align="c", space=0, line=1.2)])
        c.text(x, top + 0.62, w, [para(run(note, "light", 11.5, MUTED), align="c", space=0, line=1.3)])


def code_motif(c: Canvas, x, y, w=3.05, h=3.95):
    c.card(x, y, w, h)
    rows = [(0.46, ACCENT), (0.30, LINE), (0.60, LINE), (0.38, ACCENT2), (0.52, LINE)]
    yy = y + 0.52
    for frac, col in rows:
        c.rect(x + 0.44, yy, 0.115, 0.115, fill=col, radius=0.03)
        c.rect(x + 0.76, yy + 0.028, (w - 1.25) * frac, 0.075, fill=col, radius=0.03)
        yy += 0.60
    c.rect(x + 0.44, yy + 0.10, 0.115, 0.115, fill=None, line=LINE, lw=1.0, radius=0.03)


def qa_block(c: Canvas, x, y, w, pairs, gap=0.30):
    for q, a in pairs:
        c.text(x, y, w, [para(run("— ", "medium", 13, ACCENT), run(q, "bold", 13, INK), space=0, line=1.25)])
        y += 0.30
        h = c.text(x + 0.02, y, w - 0.02, [para(run(a, "light", 12.5, BODY), space=0, line=1.32)])
        y += h + gap
    return y


def num(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


# ─────────────────────────────────────────────────────────── слайды

def s01_cover() -> Canvas:
    c = Canvas("cover")
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=PAPER)
    c.rect(M_L, 1.62, 1.15, 0.035, fill=ACCENT)
    c.text(M_L, 1.92, 7.9,
           [para(run("Родительское собрание · группа П32", "medium", 11.5, ACCENT, spc=2.0, caps=True), space=0)])
    c.text(M_L, 2.34, 8.3,
           [para(run("Программисты третьего курса:\nитоги года и план на выпуск",
                     "bold", 34, INK), space=0, line=1.18)])
    c.hline(M_L, 3.78, 6.9, LINE, 0.75)
    c.text(M_L, 4.04, 6.9,
           [para(run("Чем занимался курс, что получилось у ребят\nи что нужно от семьи — коротко и по делу.",
                     "light", 14.5, MUTED), space=0, line=1.42)])

    meta = [("Дата", "___"), ("Время", "___"), ("Место", "___")]
    mx = M_L
    for i, (lab, val) in enumerate(meta):
        if i:
            c.vline(mx - 0.34, 5.42, 0.70, LINE, 0.75)
        c.text(mx, 5.42, 2.2, [para(run(lab, "light", 9.5, MUTED, spc=1.4, caps=True), space=0)])
        c.text(mx, 5.68, 2.2, [para(run(val, "medium", 14, INK), space=0)])
        mx += 2.6
    c.text(M_L, 6.58, 8.2,
           [para(run(f"{data.COLLEGE} · группа {data.GROUP}", "light", 11, MUTED), space=3),
            para(run(f"Преподаватель: {data.TEACHER}  ·  телефон, почта", "light", 11, MUTED), space=0)])
    code_motif(c, 9.30, 1.62)
    return c


def s02_agenda() -> Canvas:
    c = Canvas("agenda")
    head(c, "Повестка", "О чём поговорим сегодня", 2)
    items = [
        ("Мониторинг", "Как мы следим за успеваемостью"),
        ("Успеваемость группы", "Цифры за сентябрь–октябрь"),
        ("Сдача лабораторных по КПиЯП", "Кто сколько сдал и что дальше"),
        ("Проекты и практика", "Что сделали руками и защитили"),
        ("Обучение и оценки", "Как устроены пары и из чего складывается балл"),
        ("План до выпуска и распределение", "Дорожная карта и целевые места"),
        ("Задачи семьи", "На что обратить внимание дома"),
        ("Поддержка и вопросы", "Куда обращаться и как помогать"),
    ]
    col_w = 5.15
    x2 = M_L + col_w + 0.85
    row_h = 1.03
    top = BODY_TOP + 0.05
    for i, (ttl, sub) in enumerate(items):
        col = 0 if i < 4 else 1
        row = i % 4
        x = M_L if col == 0 else x2
        y = top + row * row_h
        c.text(x, y, 0.7, [para(run(f"{i + 1:02d}", "bold", 15, ACCENT), space=0)])
        c.text(x + 0.72, y - 0.02, col_w - 0.72,
               [para(run(ttl, "bold", 15.5, INK), space=0, line=1.2)])
        c.text(x + 0.72, y + 0.30, col_w - 0.72,
               [para(run(sub, "light", 12.5, MUTED), space=0, line=1.25)])
        c.hline(x, y + row_h - 0.22, col_w, LINE, 0.75)
    return c


def section(num_: int, kicker: str, title: str, lead: str, idx: int) -> Canvas:
    c = Canvas("section")
    c.text(M_L, 0.62, CW, [para(run(kicker, "medium", 10.5, ACCENT, spc=1.8, caps=True), space=0)])
    c.hline(M_L, 1.88, CW, LINE, 0.75)
    c.rect(M_L, 2.22, 1.05, 0.035, fill=ACCENT)
    c.text(M_L, 2.46, 4.0, [para(run(f"{num_:02d}", "bold", 92, SOFT_NUM), space=0, line=1.0)])
    c.text(M_L, 3.72, 8.6, [para(run(title, "bold", 36, INK), space=0, line=1.15)])
    c.text(M_L, 5.08, 8.2, [para(run(lead, "light", 15, MUTED), space=0, line=1.42)])
    c.hline(M_L, 6.88, CW, LINE, 0.75)
    c.text(M_L, 7.02, 7.0, [para(run(COURSE, "light", 9.5, MUTED), space=0)])
    c.text(M_L + CW - 1.6, 7.02, 1.6,
           [para(run(f"{idx:02d} / {TOTAL}", "medium", 9.5, MUTED), align="r", space=0)])
    return c


def s04_monitoring() -> Canvas:
    c = Canvas("two-col")
    head(c, "Мониторинг", "Как мы следим за успеваемостью", 4)
    col_w = (CW - 0.9) / 2
    x2 = M_L + col_w + 0.9
    c.text(M_L, BODY_TOP, col_w, [para(run("Что смотрим регулярно", "bold", 17, INK), space=0)])
    c.text(x2, BODY_TOP, col_w, [para(run("Что делаем, если есть отставание", "bold", 17, INK), space=0)])
    c.hline(M_L, BODY_TOP + 0.42, col_w, ACCENT, 1.6)
    c.hline(x2, BODY_TOP + 0.42, col_w, ACCENT2, 1.6)
    bullets(c, M_L, BODY_TOP + 0.72, col_w, [
        "сводная ведомость успеваемости — каждый месяц по всем предметам",
        "журнал КПиЯП: отметка зачёта по каждой лабораторной работе",
        "средний балл каждого студента — динамика, а не разовый срез",
        "текущая сдача лабораторных: сколько из 15 закрыто",
    ], size=13, gap=0.30)
    bullets(c, x2, BODY_TOP + 0.72, col_w, [
        "разбор задачи на части и первый шаг вместе с преподавателем",
        "консультация в неделю — прийти можно без записи",
        "дополнительные занятия для отстающих",
        "сообщаем родителям, если за две недели нет прогресса",
    ], size=13, gap=0.30, mcolor=ACCENT2)
    c.card(M_L, 5.62, CW, 1.0)
    c.text(M_L + 0.45, 5.88, CW - 0.9,
           [para(run("Мы не ждём конца четверти: по журналу видно, кто остановился, ещё до того, как это станет проблемой.",
                     "light", 13, BODY), space=0, line=1.35)])
    return c


def s05_subjects() -> Canvas:
    c = Canvas("table")
    head(c, "Мониторинг", "Успеваемость группы за сентябрь–октябрь", 5)

    name_x, name_w = M_L, 2.45
    b1_x, b1_w = 3.55, 2.15
    p1_r = 6.35
    sc_x, sc_w = 6.70, 2.30
    avg_r = 9.70
    b2_x, b2_w = 10.05, 1.35
    p2_r = M_L + CW
    top, rh = 2.52, 0.44

    def hdr(x, w, l1, l2):
        c.text(x, 2.00, w,
               [para(run(l1, "medium", 9.5, MUTED, spc=1.2, caps=True), space=0, line=1.2),
                para(run(l2, "medium", 9.5, MUTED, spc=1.2, caps=True), space=0, line=1.2)])

    c.text(name_x, 2.00, name_w, [para(run("Предмет", "medium", 9.5, MUTED, spc=1.2, caps=True), space=0)])
    hdr(b1_x, p1_r - b1_x, "Абсолютная", "успеваемость")
    hdr(sc_x, avg_r - sc_x, "Средний балл", "по шкале 1–10")
    hdr(b2_x, p2_r - b2_x, "Качественная", "успеваемость")
    c.hline(M_L, 2.42, CW, LINE, 0.75)

    for i, (name, abs_p, avg, qual) in enumerate(data.SUBJECTS):
        y = top + i * rh
        hi = (name == data.SUBJECT)
        if hi:
            c.rect(M_L - 0.22, y - 0.02, CW + 0.44, rh - 0.05, fill=ACCENT2_SOFT, radius=0.06)
        c.text(name_x, y + 0.09, name_w,
               [para(run(name, "bold" if hi else "medium", 13 if hi else 12.5,
                         INK if hi else BODY), space=0)])

        # абсолютная успеваемость — полоса 0…100 %
        col1 = zone_color(abs_p, ZONE_ABS)
        c.rect(b1_x, y + 0.165, b1_w, 0.15, fill=TRACK, radius=0.075)
        c.rect(b1_x, y + 0.165, b1_w * abs_p / 100.0, 0.15, fill=col1, radius=0.075)
        c.text(p1_r - 0.62, y + 0.09, 0.62,
               [para(run(f"{abs_p}%", "medium", 11.5, col1), align="r", space=0)])

        # средний балл — полоса по шкале 1…10 с засечкой на месте значения
        col2 = zone_color(avg, ZONE_AVG)
        c.rect(sc_x, y + 0.165, sc_w, 0.15, fill=TRACK, radius=0.075)
        c.rect(sc_x, y + 0.165, sc_w * (avg - 1) / 9.0, 0.15, fill=col2, radius=0.075)
        mx = sc_x + sc_w * (avg - 1) / 9.0
        c.rect(mx - 0.022, y + 0.095, 0.044, 0.29, fill=INK, radius=0.022)
        c.text(avg_r - 0.70, y + 0.08, 0.70,
               [para(run(num(avg), "bold" if hi else "medium", 13, col2), align="r", space=0)])

        # качественная успеваемость — полоса 0…100 %
        col3 = zone_color(qual, ZONE_QUAL)
        c.rect(b2_x, y + 0.165, b2_w, 0.15, fill=TRACK, radius=0.075)
        c.rect(b2_x, y + 0.165, b2_w * qual / 100.0, 0.15, fill=col3, radius=0.075)
        c.text(p2_r - 0.62, y + 0.09, 0.62,
               [para(run(f"{qual}%", "medium", 11.5, col3), align="r", space=0)])

    ly = 6.14
    c.text(M_L, ly, 1.70, [para(run("Цвет — зона позиции:", "light", 10.5, MUTED), space=0)])
    lx = 2.59
    for label, col in (("сильная", GREEN), ("средняя", AMBER), ("зона внимания", ACCENT2)):
        w = measure(label, "light", 10.5) / DPI
        c.dot(lx + 0.07, ly + 0.09, 0.055, col)
        c.text(lx + 0.22, ly, w + 0.04, [para(run(label, "light", 10.5, MUTED), space=0)])
        lx += 0.22 + w + 0.34
    c.text(M_L + CW - 4.80, ly, 4.80,
           [para(run("пороги: успеваемость 85/60% · балл 7,0/5,0 · качественная 70/50%",
                     "light", 10.5, MUTED), align="r", space=0)])
    c.text(M_L, ly + 0.26, CW,
           [para(run(f"По своему предмету (КПиЯП) группа пока отстаёт: отметка есть у {data.ATTESTED_KPIAP} из "
                     f"{data.STUDENTS_TOTAL} студентов, средний балл — {num(data.AVG_KPIAP)}. "
                     "Разбираем по каждому, с кем идём дальше.",
                     "light", 11.5, BODY), space=0, line=1.3)])
    return c


def s06_kpiap_numbers() -> Canvas:
    c = Canvas("stats")
    head(c, "Мониторинг", "КПиЯП в цифрах на сегодня", 6)
    stat_tiles(c, [
        (str(data.STUDENTS_TOTAL), "студентов в группе", "П32, дневная форма обучения"),
        (f"{data.LABS_PASSED}", f"лабораторных сдано из {data.LABS_TOTAL * data.STUDENTS_TOTAL}",
         f"по {data.LABS_TOTAL} лабораторных на человека"),
        ("52%", "абсолютная успеваемость", f"у {data.ATTESTED_KPIAP} студентов есть отметка"),
        (num(data.AVG_KPIAP), "средний балл группы", "по всем предметам — 6,41"),
    ])
    c.card(M_L, 4.72, CW, 1.45)
    c.rect(M_L, 4.72, 0.055, 1.45, fill=ACCENT2)
    c.text(M_L + 0.45, 4.98, CW - 0.9,
           [para(run("Что это значит на практике", "bold", 15, INK), space=6)])
    c.text(M_L + 0.45, 5.34, CW - 0.9,
           [para(run("Отметка по предмету ставится за лабораторные работы. Пока лабораторные не закрыты — "
                     "оценки нет, а средний балл группы остаётся низким. Дальше на слайде — кто в какой позиции.",
                     "light", 13, BODY), space=0, line=1.35)])
    return c


def s07_labs_overview() -> Canvas:
    c = Canvas("stats")
    head(c, "Сдача лабораторных", "Кто сколько сдал по КПиЯП", 7)
    b = data.count_by_labs()
    stat_tiles(c, [
        (str(b["ok"]), "сдали все 15 лабораторных", "полная готовность к зачёту"),
        (str(b["near"]), "сдали 10–14 лабораторных", "осталось догонять"),
        (str(b["mid"]), "сдали 1–9 лабораторных", "в процессе"),
        (str(b["zero"]), "не сдали ни одной", "нужна помощь"),
    ], note_color=MUTED)
    rows = [
        ("Кто сдал все 15", "идут на защиту проекта, в распределении уже можно опираться на них"),
        ("Кто на 10–14", "по сути те же студенты, но с «хвостом» — доделываем точечно"),
        ("Кто на 1–9", "главная зона внимания: без системы нет и оценки"),
        ("Кто на нуле", "разбираем индивидуально: сначала одна лабораторная, затем разгон"),
    ]
    top = 4.80
    c.hline(M_L, top - 0.12, CW, LINE, 0.75)
    for i, (a, b_) in enumerate(rows):
        y = top + i * 0.46
        c.text(M_L, y, 2.5, [para(run(a, "bold", 12.5, INK), space=0)])
        c.text(M_L + 2.65, y + 0.02, CW - 2.65,
               [para(run(b_, "light", 12.5, BODY), space=0)])
    return c


def s08_student_table() -> Canvas:
    c = Canvas("table")
    head(c, "Мониторинг · по каждому", "Средний балл, лабораторные и признаки ведомости", 8)
    half = (CW - 0.75) / 2
    rows = data.STUDENTS
    top = 2.38
    rh = 0.295
    # правые границы колонок внутри половины
    col_avg = 2.45      # «Ср. балл»
    col_lab = 3.40      # «Лаб. сдано»
    col_abs = 4.30      # «Без н/а»
    col_qual = 5.30     # «Только 4–5»
    for ci in range(2):
        chunk = rows[ci * 12: ci * 12 + 12]
        x = M_L if ci == 0 else M_L + half + 0.75
        c.text(x + 0.24, 2.02, 1.46, [para(run("Студент", "medium", 9.0, MUTED, spc=1.0, caps=True), space=0)])
        c.text(x + col_avg - 0.70, 2.02, 0.70,
               [para(run("Ср. балл", "medium", 9.0, MUTED, spc=1.0, caps=True), align="r", space=0)])
        c.text(x + col_lab - 0.90, 2.02, 0.90,
               [para(run("Лаб. сдано", "medium", 9.0, MUTED, spc=1.0, caps=True), align="r", space=0)])
        c.text(x + col_abs - 0.85, 2.02, 0.85,
               [para(run("Без «н/а»", "medium", 9.0, MUTED, spc=1.0, caps=True), align="r", space=0)])
        c.text(x + col_qual - 0.95, 2.02, 0.95,
               [para(run("Только 4–5", "medium", 9.0, MUTED, spc=1.0, caps=True), align="r", space=0)])
        c.hline(x, 2.26, half, LINE, 0.75)
        for i, s in enumerate(chunk):
            y = top + i * rh
            col = STATUS_COLOR[data.labs_done(s.labs)]
            c.dot(x + 0.09, y + 0.115, 0.055, col)
            c.text(x + 0.24, y, 1.46, [para(run(f"{s.fam} {s.ini}", "light", 10.5, BODY), space=0)])
            c.text(x + col_avg - 0.70, y, 0.70,
                   [para(run(num(s.avg), "light", 11, BODY), align="r", space=0)])
            c.text(x + col_lab - 0.90, y, 0.90,
                   [para(run(f"{s.labs} / {data.LABS_TOTAL}", "medium", 11,
                             INK if s.labs >= 10 else col), align="r", space=0)])
            c.text(x + col_abs - 0.85, y, 0.85,
                   [para(run("+" if s.abs_ok else "−", "medium" if s.abs_ok else "light", 11,
                             GREEN if s.abs_ok else MUTED), align="r", space=0)])
            c.text(x + col_qual - 0.95, y, 0.95,
                   [para(run("+" if s.qual_ok else "−", "medium" if s.qual_ok else "light", 11,
                             GREEN if s.qual_ok else MUTED), align="r", space=0)])
            if i < len(chunk) - 1:
                c.hline(x + 0.24, y + 0.255, half - 0.24, LINE, 0.75)
    ly = 5.98
    legend = [("сдали все 15", STATUS_COLOR["ok"], 1.05), ("10–14", STATUS_COLOR["near"], 0.60),
              ("1–9", STATUS_COLOR["mid"], 0.48), ("0", STATUS_COLOR["zero"], 0.30)]
    lx = M_L
    for label, col, wtxt in legend:
        c.dot(lx + 0.07, ly + 0.09, 0.055, col)
        c.text(lx + 0.22, ly, wtxt, [para(run(label, "light", 10.5, MUTED), space=0)])
        lx += 0.22 + wtxt + 0.42
    c.text(M_L + CW - 4.6, ly, 4.6,
           [para(run("Источник: сводная ведомость и журнал КПиЯП", "light", 10.5, MUTED), align="r", space=0)])
    c.text(M_L, ly + 0.34, CW,
           [para(run("«+» — признак сводной ведомости: нет «н/а» по всем предметам (абсолютная успеваемость) "
                     "или только отметки 4 и 5 (качественная успеваемость).",
                     "light", 10.5, MUTED), space=0, line=1.3)])
    return c


def s10_program() -> Canvas:
    c = Canvas("cards")
    head(c, "Программа года", "Что было в третьем курсе", 10)
    grid_cards(c, [
        ("Данные", "Базы данных и SQL",
         ["проектирование схемы", "сложные запросы и индексы", "миграции и целостность данных"]),
        ("Веб", "Серверная логика и API",
         ["клиент-серверное приложение", "авторизация и роли", "обработка ошибок"]),
        ("Инструменты", "Рабочая среда",
         ["Git: ветки, слияния, ревью", "отладка и поиск причины", "тесты и контроль качества"]),
        ("Практика", "Командные проекты",
         ["работа в команде по ролям", "промежуточные показы", "защита перед группой"]),
    ], cols=2)
    return c


def s11_skills() -> Canvas:
    c = Canvas("two-col")
    head(c, "Результат", "Чему научились за год", 11)
    col_w = (CW - 0.9) / 2
    x2 = M_L + col_w + 0.9
    c.text(M_L, BODY_TOP, col_w, [para(run("Технические навыки", "bold", 17, INK), space=0)])
    c.text(x2, BODY_TOP, col_w, [para(run("Рабочие навыки", "bold", 17, INK), space=0)])
    c.hline(M_L, BODY_TOP + 0.42, col_w, ACCENT, 1.6)
    c.hline(x2, BODY_TOP + 0.42, col_w, ACCENT2, 1.6)
    bullets(c, M_L, BODY_TOP + 0.72, col_w, [
        "писать и читать чужой код",
        "работать с Git и ветками",
        "отладка и поиск причины ошибки",
        "писать тесты для своих функций",
        "проектировать базу данных под задачу",
        "собирать приложение от идеи до запуска",
    ], size=13.5, gap=0.30)
    bullets(c, x2, BODY_TOP + 0.72, col_w, [
        "оценивать задачу и срок до начала работы",
        "работать в команде и договариваться",
        "защищать решение, а не «спрятаться»",
        "доводить задачу до конца",
        "задавать вопросы вовремя",
        "документировать то, что сделал",
    ], size=13.5, gap=0.30, mcolor=ACCENT2)
    return c


def s12_projects() -> Canvas:
    c = Canvas("cards")
    head(c, "Практика", "Проекты, которые ребята защитили", 12)
    grid_cards(c, [
        ("Веб-приложение", "Магазин / сервис с базой",
         ["регистрация и роли", "каталог и заказы", "панель администратора"]),
        ("Бот и интеграции", "Связь с внешними сервисами",
         ["работа с API", "обработка ошибок и лимитов", "хранение истории"]),
        ("Аналитика", "Отчётность по своим данным",
         ["запросы и агрегаты", "графики и выгрузки", "выводы для принятия решений"]),
        ("Чужой код", "Доработка open-source проекта",
         ["чтение чужого кода", "задача — ветка — pull request", "собственное объяснение правок"]),
    ], cols=2)
    return c


def s13_process() -> Canvas:
    c = Canvas("timeline")
    head(c, "Как это устроено", "Путь проекта от темы до защиты", 13)
    timeline(c, [
        ("Тема", "идея и постановка задачи"),
        ("План", "что именно делаем и в каком порядке"),
        ("Код", "разработка, еженедельные показы"),
        ("Ревью", "разбор чужого решения, замечания"),
        ("Защита", "демонстрация и вопросы группы"),
        ("Итог", "обратная связь и план на выпуск"),
    ], top=3.25)
    c.card(M_L, 5.05, CW, 1.35)
    c.text(M_L + 0.45, 5.32, CW - 0.9,
           [para(run("Правило группы", "bold", 14.5, INK), space=6)])
    c.text(M_L + 0.45, 5.68, CW - 0.9,
           [para(run("Проект нельзя «дописать в ночь перед сдачей»: промежуточные показы обязательны, "
                     "и это не формальность — именно на них видно, где ребяту нужна помощь.",
                     "light", 13, BODY), space=0, line=1.35)])
    return c


def s14_difficulties() -> Canvas:
    c = Canvas("two-col")
    head(c, "Честно о сложном", "Типичные трудности и как мы их снимаем", 14)
    col_w = (CW - 0.9) / 2
    x2 = M_L + col_w + 0.9
    c.text(M_L, BODY_TOP, col_w, [para(run("Что обычно тревожит", "bold", 17, INK), space=0)])
    c.text(x2, BODY_TOP, col_w, [para(run("Что делаем мы", "bold", 17, INK), space=0)])
    c.hline(M_L, BODY_TOP + 0.42, col_w, ACCENT2, 1.6)
    c.hline(x2, BODY_TOP + 0.42, col_w, GREEN, 1.6)
    bullets(c, M_L, BODY_TOP + 0.72, col_w, [
        "«не понимаю, с чего начать задачу»",
        "«код не работает и непонятно почему»",
        "«не успеваю, задач слишком много»",
        "«в сравнении с сильными я слабый»",
    ], size=13.5, gap=0.34, mcolor=ACCENT2)
    bullets(c, x2, BODY_TOP + 0.72, col_w, [
        "разбираем задачу на части и делаем первый шаг",
        "отладка по шагам и работа с преподавателем",
        "план по неделям вместо гонки перед дедлайном",
        "работа в команде: сильный и начинающий — вместе",
    ], size=13.5, gap=0.34, mcolor=GREEN)
    c.text(M_L, 6.18, CW,
           [para(run("Если дома что-то не получается — это нормальная рабочая ситуация, а не повод для тревоги. "
                     "Просить помощи — часть профессии.", "light", 12.5, MUTED), space=0)])
    return c


def s16_roadmap() -> Canvas:
    c = Canvas("roadmap")
    head(c, "План", "Дорожная карта до выпуска", 16)
    steps = [
        ("___", "новые темы и сборка итогового проекта"),
        ("___", "защита проекта перед группой"),
        ("___", "повторение и подготовка к экзаменам"),
        ("___", "государственная экзаменационная работа"),
        ("___", "стажировка или первая работа"),
    ]
    n = len(steps)
    x_left = M_L + 0.55
    y0 = BODY_TOP + 0.30
    step = 0.78
    c.vline(x_left, y0 + 0.12, step * (n - 1), LINE, 1.2)
    for i, (when, what) in enumerate(steps):
        y = y0 + i * step
        c.dot(x_left, y + 0.12, 0.085, ACCENT if i < n - 1 else ACCENT2)
        c.text(x_left + 0.45, y, 2.6, [para(run(when, "bold", 15, INK), space=0, line=1.2)])
        c.text(x_left + 3.15, y + 0.02, CW - 3.7,
               [para(run(what, "light", 14, BODY), space=0, line=1.3)])
        if i < n - 1:
            c.hline(x_left + 0.45, y + 0.62, CW - 0.45, LINE, 0.75)
    c.text(M_L, 6.22, CW,
           [para(run("Точные даты зависят от расписания экзаменов — пришлём их в чате курса.",
                     "light", 12.5, MUTED), space=0)])
    return c


def s17_grads() -> Canvas:
    c = Canvas("cards")
    head(c, "Профессия", "Куда идут выпускники", 17)
    grid_cards(c, [
        ("Компании", "IT-компании и аутсорс",
         ["собеседование вместо экзамена", "проверочная задача", "стажировка с первого дня"]),
        ("Свои проекты", "Пет-проекты и фриланс",
         ["портфолио из курсовых работ", "первые заказы и отзывы", "понимание, как берут деньги"]),
        ("Учёба", "Продолжение образования",
         ["вуз по IT-специальности", "повторные курсы и сертификации", "смежные направления"]),
    ], cols=3, bottom=5.78)
    c.text(M_L, 6.05, CW,
           [para(run("Цель третьего курса — не «сдать экзамен», а выйти из колледжа с работой, "
                     "портфолио и пониманием, куда двигаться дальше.",
                     "light", 12.5, MUTED), space=0, line=1.3)])
    return c


def s18_distribution() -> Canvas:
    c = Canvas("two-col")
    head(c, "Распределение", "Кто идёт на распределение", 18)

    targets = [s for s in data.STUDENTS if s.labs == data.LABS_TOTAL and s.abs_ok]
    others = [s for s in data.STUDENTS if s not in targets]

    # ── левая колонка: цифры и критерий
    lw = 3.95
    c.text(M_L, BODY_TOP, lw,
           [para(run("Нацелены на целевое место", "bold", 14.5, GREEN), space=0, line=1.2)])
    c.text(M_L, BODY_TOP + 0.30, lw,
           [para(run(str(len(targets)), "bold", 36, GREEN), space=0, line=1.05)])
    c.text(M_L, BODY_TOP + 0.86, lw,
           [para(run("критерий по нашим данным: закрыты все 15 лабораторных по КПиЯП "
                     "и нет «н/а» ни по одному предмету",
                     "light", 11.5, MUTED), space=0, line=1.32)])
    c.hline(M_L, BODY_TOP + 1.62, lw, LINE, 0.75)
    c.text(M_L, BODY_TOP + 1.78, lw,
           [para(run("Пока без целевого места", "bold", 14.5, ACCENT2), space=0, line=1.2)])
    c.text(M_L, BODY_TOP + 2.08, lw,
           [para(run(str(len(others)), "bold", 36, ACCENT2), space=0, line=1.05)])
    c.text(M_L, BODY_TOP + 2.64, lw,
           [para(run("у каждого — свой список: закрыть лабораторные и сдать дисциплины без отметки",
                     "light", 11.5, MUTED), space=0, line=1.32)])
    c.card(M_L, BODY_TOP + 3.16, lw, 0.92)
    c.text(M_L + 0.30, BODY_TOP + 3.34, lw - 0.60,
           [para(run("Списки сверяются с отделом трудоустройства колледжа. "
                     "Здесь — по состоянию на сейчас.", "light", 11, BODY), space=0, line=1.32)])

    # ── правая колонка: весь список с отметкой «целевик / не целевик»
    rx = M_L + lw + 0.55
    rw = CW - lw - 0.55
    sub = (rw - 0.25) / 2
    c.text(rx, BODY_TOP - 0.02, sub,
           [para(run("Группа П32 · 23 студента", "medium", 9.5, MUTED, spc=1.2, caps=True), space=0)])
    rh = 0.295
    top = BODY_TOP + 0.32
    for ci in range(2):
        chunk = (targets + others)[ci * 12: ci * 12 + 12]
        x = rx + ci * (sub + 0.25)
        for i, s in enumerate(chunk):
            y = top + i * rh
            is_t = s in targets
            c.dot(x + 0.07, y + 0.115, 0.06, GREEN if is_t else LINE)
            c.text(x + 0.24, y, sub - 0.24,
                   [para(run(f"{s.fam} {s.ini}", "medium" if is_t else "light", 11.5,
                             GREEN if is_t else MUTED), space=0)])
    ly = top + 12 * rh + 0.18
    lx = rx
    for label, col in (("нацелены на целевое место", GREEN), ("пока без целевого места", LINE)):
        c.dot(lx + 0.07, ly + 0.09, 0.06, col)
        c.text(lx + 0.24, ly, 2.2, [para(run(label, "light", 10.5, MUTED), space=0)])
        lx += 2.55
    return c


def s20_family() -> Canvas:
    c = Canvas("checklist")
    head(c, "Задачи семьи", "Что помогает больше всего и куда обращаться", 20)
    col_w = (CW - 0.9) / 2
    x2 = M_L + col_w + 0.9
    c.text(M_L, BODY_TOP, col_w, [para(run("Что помогает больше всего", "bold", 17, INK), space=0)])
    c.text(x2, BODY_TOP, col_w, [para(run("Куда обращаться", "bold", 17, INK), space=0)])
    c.hline(M_L, BODY_TOP + 0.40, col_w, ACCENT, 1.6)
    c.hline(x2, BODY_TOP + 0.40, col_w, ACCENT2, 1.6)

    left = [
        "быть на связи в рабочее время — отвечать в течение дня",
        "дать доступ к ноутбуку и интернету для домашних заданий",
        "выделять 3–4 часа в неделю на самостоятельную работу",
        "не делать работу за ребёнка — цель в том, чтобы он умел сам",
    ]
    bullets(c, M_L, BODY_TOP + 0.68, col_w, left, size=13, gap=0.34, marker="tick", mcolor=ACCENT)

    channels = [
        ("Куратор курса", "ведёт расписание, помогает с организацией и решает спорные вопросы"),
        ("Преподаватель", "часы консультаций ___, разбор задач и кода"),
        ("Чат курса", "отвечаем в течение дня ___, там же дедлайны и объявления"),
    ]
    y = BODY_TOP + 0.68
    for name, note in channels:
        c.dot(x2 + 0.07, y + 0.10, 0.055, ACCENT2)
        c.text(x2 + 0.26, y, col_w - 0.26, [para(run(name, "bold", 13.5, INK), space=0)])
        h = c.text(x2 + 0.26, y + 0.28, col_w - 0.26,
                   [para(run(note, "light", 12, BODY), space=0, line=1.3)])
        y += 0.28 + h + 0.34

    c.card(M_L, 5.62, CW, 0.92)
    c.text(M_L + 0.45, 5.86, CW - 0.9,
           [para(run("Важно: мы не перекладываем воспитание на семью. Наша часть — дать знания и практику; "
                     "ваша — поддержать условия, в которых ребёнок может учиться.",
                     "light", 13, BODY), space=0, line=1.35)])
    return c


def s21_questions() -> Canvas:
    c = Canvas("qa")
    head(c, "Вопросы", "Частые вопросы родителей", 21)
    col_w = (CW - 0.9) / 2
    x2 = M_L + col_w + 0.9
    left = [
        ("Сколько это занимает времени дома?",
         "В среднем 3–4 часа в неделю плюс работа над проектом в последние недели четверти."),
        ("Нужен ли домашний компьютер?",
         "Нужен ноутбук с интернетом. Если его нет — расскажите, подскажем варианты."),
        ("Что делать, если ребёнок отстаёт?",
         "Пишите в чат курса или напрямую: подберём нагрузку и дополнительные занятия."),
    ]
    right = [
        ("Как помочь с кодом, если я не программист?",
         "Не нужно разбираться в коде. Достаточно спросить: «что сейчас делаешь и что дальше?» — "
         "проговаривание задачи само по себе помогает."),
        ("Есть ли стажировки и реальные заказы?",
         "Да: часть проектов идёт в связке с компаниями-партнёрами, часть — командные разработки."),
        ("Что дальше после выпуска?",
         "Курс даёт базу и портфолио; дальше — стажировка, работа в компании или сильная мотивация."),
    ]
    qa_block(c, M_L, BODY_TOP, col_w, left)
    qa_block(c, x2, BODY_TOP, col_w, right)
    c.text(M_L, 6.08, CW,
           [para(run("Что не успели разобрать — пишите в чат курса или напрямую: ответим по каждому вопросу.",
                     "light", 12.5, MUTED), space=0)])
    return c


def s22_close() -> Canvas:
    c = Canvas("close")
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=PAPER)
    c.rect(M_L, 1.35, 1.15, 0.035, fill=ACCENT)
    c.text(M_L, 1.66, 7.6, [para(run("Спасибо за встречу", "bold", 38, INK), space=0, line=1.16)])
    c.text(M_L, 2.48, 7.4,
           [para(run("Курс идёт хорошо: видно и по коду, и по защитам. "
                     "Спасибо, что вы рядом — остальное доделаем вместе.",
                     "light", 14.5, MUTED), space=0, line=1.42)])
    c.hline(M_L, 3.42, 7.2, LINE, 0.75)
    c.text(M_L, 3.66, 7.2, [para(run("Что сделать до следующей встречи", "medium", 12, INK, spc=1.4, caps=True), space=0)])
    bullets(c, M_L, 4.06, 7.2, [
        "записаться на индивидуальную консультацию, если остались вопросы",
        "проверить доступность рабочего ноутбука и интернета",
        "ознакомиться с расписанием экзаменов в чате курса",
    ], size=13, gap=0.26, marker="dash")
    c.text(M_L, 6.05, 7.2,
           [para(run("Следующая встреча: дата, время  ·  место", "medium", 13.5, INK), space=4),
            para(run(f"Преподаватель: {data.TEACHER}  ·  телефон / почта  ·  ссылка на чат",
                    "light", 12, MUTED), space=0)])
    code_motif(c, 9.30, 1.35, w=3.05, h=3.95)
    return c


# ─────────────────────────────────────────────────────── заметки

NOTES = [
    "Поздороваться, представиться. Назвать цель встречи и регламент: 30–40 минут, в конце — вопросы.",
    "Показать маршрут встречи. Предупредить, что в конце оставим 10 минут на вопросы родителей.",
    "Первый блок — про контроль. Сказать прямо: мониторинг у нас еженедельный, а не разовый.",
    "Объяснить механику: ведомость + журнал + средний балл. Подчеркнуть, что мы не ждём конца четверти.",
    "Назвать цифры по предметам. Не читать все восемь — остановиться на КПиЯП. "
    "Цвет = зона позиции: зелёный — сильная (успеваемость от 85%, балл от 7, качественная от 70%), "
    "жёлтый — средняя, терракота — зона внимания.",
    "Ключевой слайд блока: почему средний балл по КПиЯП низкий. Отметка зависит от лабораторных.",
    "Четыре группы. Назвать цифры и что делаем с каждой. Здесь можно назвать имена — но только если готовы.",
    "Слайд для преподавателя: если показывать родителям не хотите — пропустите и скажите, что разберёте лично. "
    "Признаки ведомости: «+» без «н/а» — 11 студентов, «+» только на 4 и 5 — 4 студента.",
    "Переход к практике: от контроля — к тому, как ребята учатся.",
    "Подчеркнуть: это не «школьные задачи», а рабочие инструменты, которые нужны на первой работе.",
    "Родителям важнее вторые навыки — именно они определяют, найдёт ли ребёнок работу.",
    "Если есть скриншоты реальных работ — показать один-два. Это убеждает лучше любых слов.",
    "Подчеркнуть промежуточные показы: именно на них видно, где ребёнку нужна помощь.",
    "Говорить честно. Родители обычно приходят со страхом «мой отстаёт» — честный разбор снимает его.",
    "Дальше — практическая часть: что будет до выпуска и что после.",
    "Назвать конкретные месяцы и напомнить, что точные даты экзаменов придут в чат.",
    "Самый убедительный слайд: привести 2–3 реальных примера из прошлых лет.",
    "Распределение: нацелены трое — Буткевич А. В., Маланочкин М. С., Папко Д. Е. "
    "Критерий: все 15 лабораторных и нет «н/а». Сказать, что окончательные списки — у отдела трудоустройства.",
    "Переход к семье: не «ваша задача», а «наша совместная часть».",
    "Не читать список подряд. Проговорить два-три главных пункта, остальные — голосом.",
    "Отвечать кратко и честно. Не обещать того, что нельзя гарантировать. Напомнить про каналы связи.",
    "Назвать, куда писать и в какой срок ждут ответа. Поблагодарить и закончить.",
]


def build() -> list:
    slides = [
        s01_cover(),
        s02_agenda(),
        section(1, "Раздел 01", "Мониторинг и сдача лабораторных",
                "Как мы видим картину по группе и что делаем с тем, что видим.", 3),
        s04_monitoring(),
        s05_subjects(),
        s06_kpiap_numbers(),
        s07_labs_overview(),
        s08_student_table(),
        section(2, "Раздел 02", "Проекты и практика",
                "Главное, чему учится программист: не «написать код», а довести задачу до результата.", 9),
        s10_program(),
        s11_skills(),
        s12_projects(),
        s13_process(),
        s14_difficulties(),
        section(3, "Раздел 03", "План до выпуска и распределение",
                "Что впереди до диплома, куда идут выпускники и кто на распределении.", 15),
        s16_roadmap(),
        s17_grads(),
        s18_distribution(),
        section(4, "Раздел 04", "Задачи семьи и поддержка",
                "Что нужно от родителей, где мы помогаем и как связаться.", 19),
        s20_family(),
        s21_questions(),
        s22_close(),
    ]
    for c, note in zip(slides, NOTES):
        c.notes = note
    return slides
