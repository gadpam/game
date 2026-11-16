"""
Пересборка ВСЕХ панелей глав 1–5 на 12 характеристиках.
Единственный источник чисел — CANON ниже. Панели только читают его.

Проверки при сборке:
  · ни одного символа вне шрифта (ловит «→» и «◆», которых в Exo 2 нет);
  · текст не выходит за рамку панели;
  · текст не пересекается с текстом;
  · ни одна характеристика > 70 и не < 0;
  · кредиты в кадре не печатаются нигде.

Глава 4: ПОЗИЦИЯ = 70 — это ПОТОЛОК. «70 → 71» запрещено: пробивает 70.
Поэтому квест гл. 4 платит ИВ, а характеристика остаётся на потолке.
"""
import sys
sys.path.insert(0, '.')
from grid import *          # noqa
from fontTools.ttLib import TTFont

# ══════════════════════════════════════════════════════════════════
# КАНОН ЧИСЕЛ (единственный источник)
# ══════════════════════════════════════════════════════════════════
CANON = {
    'ПЕРВОЕ КАСАНИЕ': 42, 'ПАС': 39, 'ОТБОР': 26, 'УДАР': 11,
    'ПОЗИЦИЯ': 70, 'ВИДЕНИЕ': 58, 'ИГРА БЕЗ МЯЧА': 47, 'РЕШЕНИЕ': 44,
    'ВЫНОСЛИВОСТЬ': 38, 'СКОРОСТЬ': 31, 'ПРЫГУЧЕСТЬ': 22, 'СИЛА': 16,
}
CEIL = 70
IV = 68


def audit(tag):
    vals = list(CANON.values())
    s, m = sum(vals), sum(vals) / 12
    assert all(0 <= v <= CEIL for v in vals), f'{tag}: выход за потолок/ноль'
    assert len(vals) == 12
    print(f'  {tag:38s} сумма {s:3d}  среднее {m:6.2f}  ОБЩ {round(m)}')
    return s, m


def step(name, delta, tag):
    CANON[name] += delta
    assert 0 <= CANON[name] <= CEIL, f'{name}: {CANON[name]} вне 0–70'
    return audit(tag)


# ══════════════════════════════════════════════════════════════════
# ГЛИФЫ И ВЁРСТКА
# ══════════════════════════════════════════════════════════════════
_CMAP = set()
for _w, _f in [('b', 'Bold'), ('m', 'Medium'), ('l', 'Light')]:
    for _t in TTFont(f'fonts/Exo2-{_f}.ttf')['cmap'].tables:
        _CMAP |= set(_t.cmap.keys())


class S:
    """Draw-обёртка: следит за глифами, рамкой и пересечениями."""

    def __init__(self, p, box=None, pad=(24, 44, 24, 10)):
        self.p, self.box, self.pad = p, box or p.box, pad
        self.items = []

    def text(self, xy, s, font, fill, anchor='la'):
        for ch in s:
            if ch not in ' \n' and ord(ch) not in _CMAP:
                raise ValueError(f'глифа {ch!r} (U+{ord(ch):04X}) нет в Exo 2 — в «{s}»')
        bb = self.p.d.textbbox(xy, s, font=font, anchor=anchor)
        self.items.append((s, bb))
        self.p.d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return bb

    def check(self, tol=2):
        x0, y0, x1, y1 = self.box
        l, t, r, b = self.pad
        for s, bb in self.items:
            if bb[0] < x0 + l - tol or bb[2] > x1 - r + tol \
               or bb[1] < y0 + t - tol or bb[3] > y1 - b + tol:
                raise ValueError(f'«{s}» вылезает за панель: {bb}')
        for i in range(len(self.items)):
            for j in range(i + 1, len(self.items)):
                a, b2 = self.items[i][1], self.items[j][1]
                if a[0] < b2[2] - tol and b2[0] < a[2] - tol and \
                   a[1] < b2[3] - tol and b2[1] < a[3] - tol:
                    raise ValueError(f'пересечение: «{self.items[i][0]}» / «{self.items[j][0]}»')


INK, DIM = (238, 246, 255), (150, 178, 202)
RED, GRN, YEL = (255, 128, 108), (150, 235, 190), (255, 222, 96)


def trim(im, tol=8, maxfrac=0.12):
    """Срезает запечённые генератором однотонные белые/чёрные полосы по краям."""
    im = im.convert('RGB')
    w, h = im.size
    px = im.load()

    def uniform(vals):
        r = [v[0] for v in vals], [v[1] for v in vals], [v[2] for v in vals]
        return all(max(c) - min(c) <= tol for c in r) and (sum(vals[len(vals) // 2]) / 3 > 236
                                                           or sum(vals[len(vals) // 2]) / 3 < 14)

    def row(y):
        return [px[x, y] for x in range(0, w, max(1, w // 90))]

    def col(x):
        return [px[x, y] for y in range(0, h, max(1, h // 90))]

    top = 0
    while top < h * maxfrac and uniform(row(top)):
        top += 1
    bot = h
    while bot > h * (1 - maxfrac) and uniform(row(bot - 1)):
        bot -= 1
    left = 0
    while left < w * maxfrac and uniform(col(left)):
        left += 1
    right = w
    while right > w * (1 - maxfrac) and uniform(col(right - 1)):
        right -= 1
    if top or bot < h or left or right < w:
        im = im.crop((left, top, right, bot))
    return im


def load(path, focus=3, zoom=1.0, cx=0.5, cy=0.5):
    im = cover(trim(Image.open(path)), focus=focus)
    if zoom > 1.0:
        w, h = im.size
        nw, nh = int(w / zoom), int(h / zoom)
        x, y = int((w - nw) * cx), int((h - nh) * cy)
        im = im.crop((x, y, x + nw, y + nh)).resize((W, H), Image.LANCZOS)
    return im


# Панельный кадр не повторяет соседний кадр главы: у него своё кадрирование.
# (zoom, cx, cy) — крупность и точка, вокруг которой кропим.
PANEL_FRAME = {
    'ch1/k2b_bench.jpg':    (1.30, 0.55, 0.36),
    'ch1/k17_enter.jpg':    (1.32, 0.50, 0.42),
    'ch1/k3c_loss.jpg':     (1.28, 0.50, 0.45),
    'ch1/k5_kitchen.jpg':   (1.38, 0.42, 0.60),
    'ch2/c_manege.jpg':     (1.45, 0.62, 0.46),
    'ch2/c_touch.jpg':      (1.38, 0.52, 0.52),
    'ch2/c_notebook.jpg':   (1.32, 0.46, 0.50),
    'ch3/g07_pitch.jpg':    (1.25, 0.50, 0.48),
    'ch3/g23_empty.jpg':    (1.22, 0.50, 0.45),
    'ch4/h08_bench_cold.jpg': (1.52, 0.66, 0.48),
    'ch4/h25_protocol.jpg': (1.46, 0.58, 0.34),
    'ch5/e14_bench_edge.jpg': (1.30, 0.55, 0.42),
    'ch5/e23_zone.jpg':     (1.22, 0.50, 0.42),
}


def bg(path, focus=3):
    z, cx, cy = PANEL_FRAME.get(path, (1.0, 0.5, 0.5))
    return load(path, focus=focus, zoom=z, cx=cx, cy=cy)


def head(p, sc, y, title, sub=None, size=30):
    sc.text((p.cx, y), sp(title, 2), F('b', size), (255, 255, 255, 255), anchor='ma')
    if sub:
        sc.text((p.cx, y + size + 12), sub, F('l', 14), DIM + (200,), anchor='ma')


def kv(p, sc, y, label, value, vcol=None, vsize=19, w='b'):
    sc.text((p.g['lbl'], y), label, F('m', 16), p.st['ink'] + (240,))
    sc.text((p.g['val'], y - 2), value, F(w, vsize), (vcol or (255, 255, 255)) + (255,), anchor='ra')


def diamonds(p, y, items):
    yy = y
    for t in items:
        p.d.polygon([(p.g['lbl'], yy + 9), (p.g['lbl'] + 6, yy - 2),
                     (p.g['lbl'] + 12, yy + 9), (p.g['lbl'] + 6, yy + 20)],
                    fill=p.st['edge'] + (228,))
        sc = S.text((p.g['lbl'] + 26, yy), t, F('m', 19), INK)  # placeholder not used
        yy += 42
    return yy


OUT = []

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 1
# ══════════════════════════════════════════════════════════════════
print('ЧИСЛА:')
audit('база · пролог / до матча')
PROMISE = CANON['ОТБОР']          # 26 — обещание квеста гл. 1, ещё не выполнено

# 04 · КВЕСТ F− · ставка ОТБОР 26
p = Panel(bg('ch1/k2b_bench.jpg'), (64, 168, 736, 900), 'n', frame_id='04')
sc = S(p)
p.div(204)
p.d.rounded_rectangle([p.cx - 66, 216, p.cx + 66, 302], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 259), 'F−', F('b', 48), (255, 255, 255, 255), anchor='mm')
sc.text((p.cx, 326), 'КВЕСТ', F('m', 18), p.st['ink'] + (230,), anchor='ma')
p.div(362)
sc.text((p.cx, 382), 'СТАВКА', F('l', 12), DIM + (190,), anchor='ma')
sc.text((p.cx, 402), 'ОТБОР ' + str(PROMISE), F('b', 30), (255, 255, 255, 255), anchor='ma')
p.div(452)
y = 480
for t in ['0 потерь в своей трети', 'пока мяч не уйдёт за лицевую']:
    p.d.polygon([(p.g['lbl'], y + 4), (p.g['lbl'] + 6, y - 8),
                 (p.g['lbl'] + 12, y + 4), (p.g['lbl'] + 6, y + 16)], fill=p.st['edge'] + (228,))
    sc.text((p.g['lbl'] + 26, y - 11), t, F('m' if y == 480 else 'l', 20 if y == 480 else 17), INK + (240,))
    y += 44
p.div(568)
sc.text((p.cx, 590), 'ВЫПОЛНИШЬ — ОТБОР +1', F('m', 16), p.st['ink'] + (235,), anchor='ma')
num_change(p, 622, PROMISE, PROMISE + 1, size=26, color_r=(255, 255, 255))
sc.text((p.cx, 664), 'до финального свистка', F('l', 14), DIM + (175,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p07_quest.png'))

# 09 · ВЫХОД НА ПОЛЕ
p = Panel(bg('ch1/k17_enter.jpg'), (70, 232, 730, 664), 'g', frame_id='09')
sc = S(p)
p.div(272)
sc.text((p.cx, 296), sp('ВЫХОД НА ПОЛЕ', 2), F('b', 23), (255, 255, 255, 255), anchor='ma')
p.div(344)
sc.text((p.cx, 366), '72′ · ЗАМЕНА', F('m', 19), p.st['ink'] + (240,), anchor='ma')
p.div(404)
sc.text((p.cx, 424), 'квест тот же · ставка ОТБОР', F('l', 15), DIM + (205,), anchor='ma')
sc.text((p.cx, 452), 'задача не изменилась', F('l', 14), (112, 164, 142, 200), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p18_enter.png'))

# 11 · ПРОВАЛ — единственное падение в книге
before = CANON['ОТБОР']
step('ОТБОР', -1, 'после гл. 1 (провал F−)')
p = Panel(bg('ch1/k3c_loss.jpg'), (64, 904, 736, 1298), 'f', frame_id='88′')
sc = S(p)
p.div(946)
sc.text((p.cx, 974), sp('НЕ ВЫПОЛНЕНО', 2), F('b', 24), (255, 228, 220, 255), anchor='ma')
p.div(1022)
sc.text((p.cx, 1042), 'КВЕСТ · F− · СТАВКА ОТБОР', F('l', 15), p.st['dim'] + (220,), anchor='ma')
num_change(p, 1076, before, CANON['ОТБОР'], size=34, color_r=RED)
p.div(1140)
sc.text((p.cx, 1160), '88′ · ПОТЕРЯ ПОД ПРЕССИНГОМ', F('m', 13), p.st['dim'] + (215,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p23_fail.png'))

# 16 · ИТОГ МАТЧА
s1, m1 = audit('гл. 1 итог')
p = Panel(bg('ch1/k5_kitchen.jpg'), (54, 116, 746, 716), 'n', frame_id='16')
sc = S(p)
p.div(152)
sc.text((p.cx, 182), sp('ИТОГ МАТЧА', 3), F('b', 29), (255, 255, 255, 255), anchor='ma')
p.div(236)
y = 264
kv(p, sc, y, 'КВЕСТ', 'F− НЕ ВЫПОЛНЕН', RED, 16)
y += 48
sc.text((p.g['lbl'], y), 'ОТБОР', F('m', 16), p.st['ink'] + (240,))
sc.text((p.g['lbl'] + 92, y + 4), 'ставка не взята', F('l', 12), DIM + (150,))
num_change(p, y - 8, before, CANON['ОТБОР'], size=26, color_r=RED)
y += 50
kv(p, sc, y, 'ИВ · МАТЧ', str(IV), None, 20)
y += 40
kv(p, sc, y, 'ИВ · СЕЗОН', str(IV), None, 20)
p.div(520)
sc.text((p.cx, 540), 'СЛЕДУЮЩИЙ КВЕСТ — ТРЕНИРОВОЧНАЯ НЕДЕЛЯ', F('m', 13), p.st['dim'] + (205,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p37_day.png'))

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 2 — плато: квест выполнен, характеристика НЕ растёт
# ══════════════════════════════════════════════════════════════════
audit('гл. 2 до квеста (плато)')

p = Panel(bg('ch2/c_manege.jpg'), (64, 168, 736, 920), 'n', frame_id='14')
sc = S(p)
p.div(204)
p.d.rounded_rectangle([p.cx - 52, 216, p.cx + 52, 288], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 252), 'F', F('b', 44), (255, 255, 255, 255), anchor='mm')
sc.text((p.cx, 316), 'КВЕСТ', F('m', 18), p.st['ink'] + (230,), anchor='ma')
p.div(350)
sc.text((p.cx, 372), 'СТАВКА', F('l', 12), DIM + (190,), anchor='ma')
sc.text((p.cx, 390), 'ПЕРВОЕ КАСАНИЕ ' + str(CANON['ПЕРВОЕ КАСАНИЕ']), F('b', 22), (255, 255, 255, 255), anchor='ma')
p.div(430)
y = 458
for i, t in enumerate(['300 касаний в грудь и подошву', 'без единой потери', '20 минут · таймер на банкетке']):
    p.d.polygon([(p.g['lbl'], y + 4), (p.g['lbl'] + 6, y - 8),
                 (p.g['lbl'] + 12, y + 4), (p.g['lbl'] + 6, y + 16)], fill=p.st['edge'] + (228,))
    sc.text((p.g['lbl'] + 26, y - 11), t, F('m' if i < 2 else 'l', 19 if i < 2 else 16), INK + (238,))
    y += 42
p.div(600)
sc.text((p.cx, 622), 'ВЫПОЛНИШЬ — ЗАЧТЁН В ИВ', F('m', 16), p.st['ink'] + (235,), anchor='ma')
sc.text((p.cx, 650), 'прироста не будет', F('l', 14), DIM + (185,), anchor='ma')
p.div(690)
sc.text((p.cx, 712), 'плато — норма, не провал', F('l', 13), DIM + (160,), anchor='ma')
sc.check()
OUT.append(p.save('ch2/p14_quest.png'))

p = Panel(bg('ch2/c_touch.jpg'), (64, 620, 736, 1290), 'g', frame_id='22')
sc = S(p)
p.div(656)
sc.text((p.cx, 684), sp('ВЫПОЛНЕНО', 2), F('b', 26), (255, 255, 255, 255), anchor='ma')
p.div(734)
sc.text((p.cx, 754), '300 / 300 · НИ ОДНОЙ ПОТЕРИ', F('m', 16), p.st['ink'] + (240,), anchor='ma')
sc.text((p.cx, 780), '20 минут · таймер не соврал', F('l', 14), DIM + (195,), anchor='ma')
p.div(822)
kv(p, sc, 844, 'ПЕРВОЕ КАСАНИЕ', str(CANON['ПЕРВОЕ КАСАНИЕ']), None, 21)
p.div(890)
sc.text((p.cx, 914), 'числа не изменились', F('l', 15), p.st['dim'] + (215,), anchor='ma')
sc.text((p.cx, 944), 'он ждал другого — и видит это сам', F('l', 13), DIM + (150,), anchor='ma')
sc.check()
OUT.append(p.save('ch2/p22_done.png'))

p = Panel(bg('ch2/c_notebook.jpg'), (54, 150, 746, 760), 'n', frame_id='24')
sc = S(p)
p.div(190)
sc.text((p.cx, 218), sp('ИТОГ ДНЯ', 3), F('b', 28), (255, 255, 255, 255), anchor='ma')
p.div(268)
y = 296
kv(p, sc, y, 'ОБЩ', str(round(m1)), None, 20)
y += 42
kv(p, sc, y, 'ИВ', str(IV), None, 20)
y += 42
kv(p, sc, y, 'ПЕРВОЕ КАСАНИЕ', str(CANON['ПЕРВОЕ КАСАНИЕ']), None, 20)
p.div(452)
sc.text((p.cx, 474), 'СТАТУС · ВЫПОЛНЕНО · F', F('m', 14), p.st['ink'] + (235,), anchor='ma')
sc.text((p.cx, 502), 'плато — это тоже строка', F('l', 13), DIM + (170,), anchor='ma')
p.div(540)
sc.text((p.cx, 560), 'он закрывает глаза · стекло исчезает', F('l', 13), DIM + (150,), anchor='ma')
sc.check()
OUT.append(p.save('ch2/p24_total.png'))

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 3 — ОТБОР возвращается с 25 на 26
# ══════════════════════════════════════════════════════════════════
PRE3 = CANON['ОТБОР']
assert PRE3 == 25, PRE3
audit('гл. 3 выполнен · плато (ОТБОР не вернулся)')
assert CANON['ОТБОР'] == 25

p = Panel(bg('ch3/g07_pitch.jpg'), (64, 168, 736, 900), 'n', frame_id='09')
sc = S(p)
p.div(204)
p.d.rounded_rectangle([p.cx - 70, 216, p.cx + 70, 306], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 261), 'F+', F('b', 48), (255, 255, 255, 255), anchor='mm')
sc.text((p.cx, 334), 'КВЕСТ', F('m', 18), p.st['ink'] + (230,), anchor='ma')
p.div(368)
sc.text((p.cx, 390), 'СТАВКА', F('l', 12), DIM + (190,), anchor='ma')
sc.text((p.cx, 408), 'ОТБОР ' + str(PRE3), F('b', 30), (255, 255, 255, 255), anchor='ma')
p.div(456)
y = 484
for i, t in enumerate(['3 отката под давлением', 'не больше трёх потерь', '60 минут · без замены']):
    p.d.polygon([(p.g['lbl'], y + 4), (p.g['lbl'] + 6, y - 8),
                 (p.g['lbl'] + 12, y + 4), (p.g['lbl'] + 6, y + 16)], fill=p.st['edge'] + (228,))
    sc.text((p.g['lbl'] + 26, y - 11), t, F('m' if i < 2 else 'l', 20 if i < 2 else 17), INK + (240,))
    y += 44
p.div(632)
sc.text((p.cx, 654), 'СТАВКА НЕ ПОДНИМЕТСЯ', F('m', 16), p.st['ink'] + (235,), anchor='ma')
sc.text((p.cx, 682), 'потерянный пункт вернёт СВЕРКА', F('l', 14), DIM + (185,), anchor='ma')
sc.text((p.cx, 716), 'выполнишь — зачтётся в ИВ', F('l', 13), DIM + (160,), anchor='ma')
sc.check()
OUT.append(p.save('ch3/p09_quest.png'))

p = Panel(bg('ch3/g23_empty.jpg'), (64, 600, 736, 1290), 'g', frame_id='22')
sc = S(p)
p.div(636)
sc.text((p.cx, 664), sp('ВЫПОЛНЕНО', 2), F('b', 26), (255, 255, 255, 255), anchor='ma')
p.div(712)
sc.text((p.cx, 732), 'КВЕСТ · F+ · СТАВКА ОТБОР', F('l', 15), p.st['dim'] + (220,), anchor='ma')
bx0, bx1, by = p.g['lbl'], p.g['val'], 776
p.d.line([(bx0, by), (bx1, by)], fill=(120, 160, 200, 45), width=4)
p.d.line([(bx0, by), (bx1, by)], fill=p.st['edge'] + (225,), width=4)
for i in range(3):
    mx = bx0 + int((bx1 - bx0) * (i + 0.5) / 3)
    p.d.polygon([(mx, by - 9), (mx + 8, by), (mx, by + 9), (mx - 8, by)], fill=p.st['edge'] + (255,))
sc.text((bx0, by + 24), '3 / 3', F('m', 16), p.st['edge'] + (240,))
sc.text((bx1, by + 24), '60 минут · 0 замен', F('l', 14), p.st['dim'] + (200,), anchor='ra')
p.div(876)
kv(p, sc, 900, 'ОТБОР', str(CANON['ОТБОР']), None, 26)
sc.text((p.g['lbl'] + 96, 906), 'как после провала', F('l', 13), DIM + (170,))
sc.text((p.cx, 946), 'ИВ 68 — тот же', F('l', 14), DIM + (185,), anchor='ma')
p.div(982)
sc.text((p.cx, 1004), 'никто не сказал «молодец»', F('l', 14), DIM + (200,), anchor='ma')
sc.text((p.cx, 1030), 'три отката — и никто не заметил', F('l', 13), DIM + (150,), anchor='ma')
sc.check()
OUT.append(p.save('ch3/p22_done.png'))

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 4 — ПОЗИЦИЯ 70 = ПОТОЛОК. Прироста нет, платит ИВ.
# ══════════════════════════════════════════════════════════════════
assert CANON['ПОЗИЦИЯ'] == CEIL
audit('после гл. 3 · до гл. 4')

p = Panel(bg('ch4/h08_bench_cold.jpg'), (60, 170, 740, 920), 'n', frame_id='09')
sc = S(p)
p.div(206)
p.d.rounded_rectangle([p.cx - 70, 218, p.cx + 70, 308], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 263), 'F+', F('b', 48), (255, 255, 255, 255), anchor='mm')
sc.text((p.cx, 336), 'КВЕСТ', F('m', 18), p.st['ink'] + (230,), anchor='ma')
p.div(370)
sc.text((p.cx, 392), 'СТАВКА', F('l', 12), DIM + (190,), anchor='ma')
sc.text((p.cx, 410), 'ПОЗИЦИЯ ' + str(CANON['ПОЗИЦИЯ']), F('b', 30), (255, 255, 255, 255), anchor='ma')
p.div(458)
y = 486
for i, t in enumerate(['верни мяч 3 раза', 'только из своей зоны', 'любым весом ИВ · пока на поле']):
    p.d.polygon([(p.g['lbl'], y + 4), (p.g['lbl'] + 6, y - 8),
                 (p.g['lbl'] + 12, y + 4), (p.g['lbl'] + 6, y + 16)], fill=p.st['edge'] + (228,))
    sc.text((p.g['lbl'] + 26, y - 11), t, F('m' if i < 2 else 'l', 20 if i < 2 else 17), INK + (240,))
    y += 44
p.div(634)
sc.text((p.cx, 656), 'ПОЗИЦИЯ НА ПОТОЛКЕ', F('m', 16), YEL + (240,), anchor='ma')
sc.text((p.cx, 684), 'выше 70 Система не считает', F('l', 14), DIM + (195,), anchor='ma')
sc.text((p.cx, 712), 'выполнишь — зачтётся в ИВ', F('l', 13), DIM + (165,), anchor='ma')
sc.check()
OUT.append(p.save('ch4/p09_quest.png'))

p = Panel(bg('ch4/h25_protocol.jpg'), (60, 520, 740, 1290), 'g', frame_id='28')
sc = S(p)
p.div(556)
sc.text((p.cx, 584), sp('ВЫПОЛНЕНО', 2), F('b', 26), (255, 255, 255, 255), anchor='ma')
p.div(632)
sc.text((p.cx, 652), 'КВЕСТ · F+ · СТАВКА ПОЗИЦИЯ', F('l', 15), p.st['dim'] + (220,), anchor='ma')
bx0, bx1, by = p.g['lbl'], p.g['val'], 698
p.d.line([(bx0, by), (bx1, by)], fill=(120, 160, 200, 45), width=4)
p.d.line([(bx0, by), (bx1, by)], fill=p.st['edge'] + (225,), width=4)
for i in range(3):
    mx = bx0 + int((bx1 - bx0) * (i + 0.5) / 3)
    p.d.polygon([(mx, by - 9), (mx + 8, by), (mx, by + 9), (mx - 8, by)], fill=p.st['edge'] + (255,))
sc.text((bx0, by + 24), '3 / 3', F('m', 16), p.st['edge'] + (240,))
sc.text((bx1, by + 24), '25 минут · выход на 68′', F('l', 14), p.st['dim'] + (200,), anchor='ra')
p.div(796)
kv(p, sc, 820, 'ПОЗИЦИЯ', str(CANON['ПОЗИЦИЯ']), None, 24)
sc.text((p.g['lbl'] + 128, 826), 'потолок', F('l', 13), YEL + (215,))
p.div(880)
sc.text((p.cx, 904), 'ПАНЕЛЬ ВИДИТ 3 · ПРОТОКОЛ 2', F('m', 15), p.st['ink'] + (240,), anchor='ma')
sc.text((p.cx, 932), 'протокол не видит одного', F('l', 13), DIM + (175,), anchor='ma')
p.div(966)
sc.text((p.cx, 990), 'оценка 6.6', F('b', 21), (255, 170, 150, 235), anchor='ma')
sc.text((p.cx, 1020), 'двойное подчёркивание — не для кого', F('l', 13), DIM + (160,), anchor='ma')
sc.check()
OUT.append(p.save('ch4/p28_done.png'))

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 5 — первый ВЫБОР и первая выплата после провала
# ══════════════════════════════════════════════════════════════════
PRE5 = CANON['ВЫНОСЛИВОСТЬ']
step('ВЫНОСЛИВОСТЬ', +1, 'после гл. 5 (F+ выбран)')

p = Panel(bg('ch5/e14_bench_edge.jpg'), (56, 150, 744, 1060), 'n', frame_id='15')
sc = S(p)
p.div(186)
sc.text((p.g['val'], 202), sp('ВЫБОР', 2), F('m', 13), YEL + (235,), anchor='ra')
sc.text((p.cx, 236), 'СИСТЕМА ПРЕДЛАГАЕТ ТРИ', F('b', 26), (255, 255, 255, 255), anchor='ma')
sc.text((p.cx, 272), 'выбор остаётся за тобой · остальные исчезнут', F('l', 14), DIM + (200,), anchor='ma')
p.div(304)
opts = [('F−', '15′ «усталости»', 'замены не просить', False),
        ('F', '20′ «усталости»', 'замены не просить', False),
        ('F+', '20′ «усталости» в концовке', 'замены не просить', True)]
y = 332
for rank, main, sub, mark in opts:
    p.d.rounded_rectangle([p.g['lbl'] - 14, y - 10, p.g['val'] + 14, y + 84], radius=5,
                          outline=p.st['edge'] + ((255 if mark else 90),), width=2 if mark else 1)
    sc.text((p.g['lbl'] + 4, y + 2), rank, F('b', 30 if mark else 26),
            (255, 255, 255, 255) if mark else (200, 220, 236, 225))
    sc.text((p.g['lbl'] + 96, y + 4), main, F('m', 18 if mark else 17),
            (255, 255, 255, 255) if mark else (206, 222, 238, 235))
    sc.text((p.g['lbl'] + 96, y + 34), sub, F('l', 14), p.st['dim'] + (200,))
    if mark:
        p.d.polygon([(p.g['val'] - 34, y + 22), (p.g['val'] - 22, y + 34),
                     (p.g['val'] - 34, y + 46), (p.g['val'] - 46, y + 34)], fill=YEL + (255,))
    y += 106
p.div(700)
sc.text((p.cx, 722), 'ВЫБРАННЫЙ КВЕСТ ОСТАНЕТСЯ ОДИН', F('m', 13), p.st['ink'] + (235,), anchor='ma')
sc.text((p.cx, 748), 'двух других не будет', F('l', 13), DIM + (185,), anchor='ma')
p.div(782)
sc.text((p.cx, 804), 'СТАВКА', F('l', 12), DIM + (190,), anchor='ma')
sc.text((p.cx, 826), 'ВЫНОСЛИВОСТЬ', F('b', 28), (255, 255, 255, 255), anchor='ma')
num_change(p, 864, PRE5, CANON['ВЫНОСЛИВОСТЬ'], size=20, color_r=(255, 255, 255))
p.div(908)
sc.text((p.cx, 928), 'решение — одно нажатие', F('l', 13), DIM + (185,), anchor='ma')
sc.text((p.cx, 954), 'отказаться нельзя', F('l', 13), (255, 170, 150, 208), anchor='ma')
sc.check()
OUT.append(p.save('ch5/p15_choice.png'))

p = Panel(bg('ch5/e23_zone.jpg'), (56, 600, 744, 1300), 'g', frame_id='25')
sc = S(p)
p.div(636)
sc.text((p.cx, 664), sp('ВЫПОЛНЕНО', 2), F('b', 26), (255, 255, 255, 255), anchor='ma')
p.div(712)
sc.text((p.cx, 732), 'ВЫБРАННЫЙ КВЕСТ · F+', F('l', 15), p.st['dim'] + (220,), anchor='ma')
sc.text((p.cx, 756), 'ВЫНОСЛИВОСТЬ', F('m', 17), p.st['ink'] + (240,), anchor='ma')
bx0, bx1, by = p.g['lbl'], p.g['val'], 800
p.d.line([(bx0, by), (bx1, by)], fill=(120, 160, 200, 45), width=4)
p.d.line([(bx0, by), (bx1, by)], fill=p.st['edge'] + (225,), width=4)
p.d.polygon([((bx0 + bx1) // 2, by - 9), ((bx0 + bx1) // 2 + 8, by),
             ((bx0 + bx1) // 2, by + 9), ((bx0 + bx1) // 2 - 8, by)], fill=p.st['edge'] + (255,))
sc.text((bx0, by + 24), 'без замены', F('m', 15), p.st['edge'] + (235,))
sc.text((bx1, by + 24), '20′ в концовке', F('l', 14), p.st['dim'] + (200,), anchor='ra')
p.div(880)
kv(p, sc, 904, 'ВЫНОСЛИВОСТЬ', str(CANON['ВЫНОСЛИВОСТЬ']), None, 22)
p.div(940)
sc.text((p.cx, 966), 'ОБЩ ' + str(round(sum(CANON.values()) / 12)) + ' · ИВ ' + str(IV),
        F('m', 17), p.st['ink'] + (240,), anchor='ma')
sc.check()
OUT.append(p.save('ch5/p25_done.png'))

s5, m5 = audit('гл. 5 итог')
print(f'\nОБЩ после гл. 5: среднее {m5:.3f} → на панели печатается {round(m5)}')
print('Все 12 значений в 0–70:', all(0 <= v <= 70 for v in CANON.values()))
print('Панелей собрано:', len(OUT))
for o in OUT:
    print('  ', o)
