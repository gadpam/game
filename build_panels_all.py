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

    def text(self, xy, s, font, fill, anchor='la', glow=False):
        for ch in s:
            if ch not in ' \n' and ord(ch) not in _CMAP:
                raise ValueError(f'глифа {ch!r} (U+{ord(ch):04X}) нет в Exo 2 — в «{s}»')
        if glow:
            gcol = glow if isinstance(glow, tuple) else self.p.st['edge']
            bb = glow_text(self.p.lay, xy, s, font, fill, gcol, anchor=anchor, radius=8, strength=0.68)
            self.p.d = ImageDraw.Draw(self.p.lay)
        else:
            bb = self.p.d.textbbox(xy, s, font=font, anchor=anchor)
            self.p.d.text(xy, s, font=font, fill=fill, anchor=anchor)
        self.items.append((s, bb))
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
        hb = self.p.header_bbox
        for dy in self.p.divs:
            if hb and hb[1] - 3 <= dy <= hb[3] + 3:
                raise ValueError(f'разделитель y={dy} режет шапку СИСТЕМА {hb}')
            for s, bb in self.items:
                if bb[1] + tol < dy < bb[3] - tol:
                    raise ValueError(f'разделитель y={dy} режет текст «{s}»: {bb}')


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
    'ch1/k2b_bench.jpg':    (1.28, 0.54, 0.42),
    'ch1/k17_enter.jpg':    (1.30, 0.50, 0.44),
    'ch1/k3c_loss.jpg':     (1.22, 0.52, 0.42),
    'ch1/k5_kitchen.jpg':   (1.34, 0.58, 0.60),
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

# КВЕСТ F− · ставка ОТБОР 26 (голографическое окно Solo Leveling, 1-е появление на 72′)
_b07 = (42, 76, 758, 824)
p = Panel(void_bg('n', _b07, h=900), _b07, 'n', frame_id=None)
sc = S(p, pad=(24, 58, 24, 16))
rank_crest(p, p.cx, 150, 258, w_half=88)
sc.text((p.cx, 204), 'F−', F('b', 62), (244, 252, 255, 255), anchor='mm', glow=True)
sc.text((p.cx, 278), sp('КВЕСТ', 2), F('b', 26), p.st['hot'] + (252,), anchor='ma', glow=True)
p.div(330)
sc.text((p.cx, 352), sp('СТАВКА', 2), F('m', 18), p.st['dim'] + (228,), anchor='ma')
sc.text((p.cx, 384), 'ОТБОР ' + str(PROMISE), F('b', 42), (245, 252, 255, 255), anchor='ma', glow=True)
subbox(p, _b07[0] + 38, 456, _b07[2] - 38, 604, alpha=105)
y = 492
for idx_q, t in enumerate(['0 потерь в своей трети', 'пока мяч не уйдёт за лицевую']):
    dx0 = p.g['lbl'] + 4
    p.d.polygon([(dx0, y + 9), (dx0 + 8, y - 4),
                 (dx0 + 16, y + 9), (dx0 + 8, y + 22)],
                fill=p.st['hot'] + (245,), outline=p.st['edge'] + (255,))
    sc.text((dx0 + 30, y - 11), t, F('b' if idx_q == 0 else 'm', 28 if idx_q == 0 else 25),
            INK + (252,), glow=(idx_q == 0))
    y += 60
p.div(628)
sc.text((p.cx, 650), 'ВЫПОЛНИШЬ — ОТБОР +1', F('m', 24), p.st['ink'] + (250,), anchor='ma')
bb_nc = num_change(p, 692, PROMISE, PROMISE + 1, size=44, color_r=(112, 224, 255), align='center')
sc.items.append(('26->27', bb_nc))
sc.text((p.cx, 762), 'до финального свистка', F('l', 21), p.st['dim'] + (232,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p07_quest.png'))

# ВЫХОД НА ПОЛЕ (72′ · ЗАМЕНА — сохраняется в пайплайне канона)
_b18 = (44, 72, 756, 496)
p = Panel(void_bg('g', _b18, h=568), _b18, 'g', frame_id=None)
sc = S(p, pad=(24, 58, 24, 16))
sc.text((p.cx, 152), sp('ВЫХОД НА ПОЛЕ', 2), F('b', 31), p.st['hot'] + (255,), anchor='ma', glow=True)
p.div(214)
sc.text((p.cx, 240), '72′ · ЗАМЕНА', F('b', 30), p.st['ink'] + (252,), anchor='ma', glow=True)
p.div(304)
sc.text((p.cx, 334), 'квест тот же · ставка ОТБОР', F('m', 24), p.st['dim'] + (242,), anchor='ma')
sc.text((p.cx, 388), 'задача не изменилась', F('l', 21), p.st['dim'] + (222,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p18_enter.png'))

# ПРОВАЛ — единственное падение в книге (алое тревожное окно Solo Leveling)
before = CANON['ОТБОР']
step('ОТБОР', -1, 'после гл. 1 (провал F−)')
_b23 = (42, 76, 758, 540)
p = Panel(void_bg('f', _b23, h=616), _b23, 'f', frame_id=None)
sc = S(p, pad=(24, 58, 24, 16))
sc.text((p.cx, 154), sp('НЕ ВЫПОЛНЕНО', 2), F('b', 34), (255, 240, 238, 255), anchor='ma', glow=True)
p.div(218)
subbox(p, _b23[0] + 44, 240, _b23[2] - 44, 410, alpha=110)
sc.text((p.cx, 260), 'КВЕСТ · F− · СТАВКА ОТБОР', F('m', 22), p.st['dim'] + (246,), anchor='ma')
bb_nc = num_change(p, 308, before, CANON['ОТБОР'], size=56, color_r=(255, 86, 86), align='center')
sc.items.append(('26->25', bb_nc))
p.div(434)
sc.text((p.cx, 464), '88′ · ПОТЕРЯ ПОД ПРЕССИНГОМ', F('m', 23), p.st['ink'] + (244,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p23_fail.png'))

# ИТОГ МАТЧА (голографическая сводка Solo Leveling)
s1, m1 = audit('гл. 1 итог')
_b37 = (42, 76, 758, 658)
p = Panel(void_bg('n', _b37, h=734), _b37, 'n', frame_id=None)
sc = S(p, pad=(24, 58, 24, 16))
sc.text((p.cx, 152), sp('ИТОГ МАТЧА', 2), F('b', 36), (245, 252, 255, 255), anchor='ma', glow=True)
p.div(214)
subbox(p, _b37[0] + 38, 236, _b37[2] - 38, 518, alpha=102)
y = 264
sc.text((p.g['lbl'], y), 'КВЕСТ', F('m', 22), p.st['dim'] + (246,))
sc.text((p.g['val'], y - 1), 'F− НЕ ВЫПОЛНЕН', F('b', 24), (255, 102, 98, 255), anchor='ra', glow=(255, 68, 72))
y += 64
sc.text((p.g['lbl'], y), 'ОТБОР', F('m', 22), p.st['dim'] + (246,))
sc.text((p.g['lbl'] + 102, y + 4), 'ставка не взята', F('l', 17), p.st['dim'] + (195,))
bb_nc = num_change(p, y - 9, before, CANON['ОТБОР'], size=38, color_r=(255, 102, 98), align='right')
sc.items.append(('26->25', bb_nc))
y += 66
sc.text((p.g['lbl'], y), 'ИВ · МАТЧ', F('m', 22), p.st['ink'] + (250,))
sc.text((p.g['val'], y - 4), str(IV), F('b', 33), p.st['hot'] + (255,), anchor='ra', glow=True)
y += 58
sc.text((p.g['lbl'], y), 'ИВ · СЕЗОН', F('m', 22), p.st['ink'] + (250,))
sc.text((p.g['val'], y - 4), str(IV), F('b', 33), p.st['hot'] + (255,), anchor='ra', glow=True)
p.div(540)
sc.text((p.cx, 570), 'СЛЕДУЮЩИЙ КВЕСТ — ТРЕНИРОВОЧНАЯ НЕДЕЛЯ', F('m', 19), p.st['dim'] + (238,), anchor='ma')
sc.check()
OUT.append(p.save('ch1/p37_day.png'))

# ══════════════════════════════════════════════════════════════════
# ГЛАВА 2 — плато: квест выполнен, характеристика НЕ растёт
# ══════════════════════════════════════════════════════════════════
audit('гл. 2 до квеста (плато)')

p = Panel(bg('ch2/c_manege.jpg'), (64, 168, 736, 920), 'n', frame_id='14')
sc = S(p)
p.d.rounded_rectangle([p.cx - 52, 224, p.cx + 52, 294], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 259), 'F', F('b', 44), (255, 255, 255, 255), anchor='mm')
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
p.d.rounded_rectangle([p.cx - 70, 224, p.cx + 70, 310], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 267), 'F+', F('b', 48), (255, 255, 255, 255), anchor='mm')
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
p.d.rounded_rectangle([p.cx - 70, 226, p.cx + 70, 312], radius=7, outline=p.st['edge'] + (235,), width=2)
sc.text((p.cx, 269), 'F+', F('b', 48), (255, 255, 255, 255), anchor='mm')
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
sc.text((p.g['val'], 206), sp('ВЫБОР', 2), F('m', 13), YEL + (235,), anchor='ra')
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
