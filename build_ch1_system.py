"""Панели Системы главы 1 после авторской правки v10.

Только глава 1: квест на ПРИНЯТИЕ РЕШЕНИЙ 26 -> 28, при провале
характеристика не меняется; после матча — профиль, объяснение ИВ и магазин.
Главы 2–5 этим скриптом не затрагиваются (строгая работа по одной главе).
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import ImageDraw

from grid import F, Panel, arrow, glow_text, num_change, rank_crest, sp, subbox, void_bg

OUT = []
INK = (238, 246, 255)
DIM = (150, 178, 202)
YEL = (255, 222, 96)
RED = (255, 128, 108)
DECISION = 26
REWARD = 28
IV = 68

STATS = [
    ('ПЕРВОЕ КАСАНИЕ', 42), ('ПАС', 39), ('ОТБОР', 26), ('УДАР', 11),
    ('ПОЗИЦИЯ', 70), ('ВИДЕНИЕ', 58), ('ИГРА БЕЗ МЯЧА', 47),
    ('ПРИНЯТИЕ РЕШЕНИЙ', 26), ('ВЫНОСЛИВОСТЬ', 38), ('СКОРОСТЬ', 31),
    ('ПРЫГУЧЕСТЬ', 22), ('СИЛА', 16),
]
TOTAL = sum(v for _, v in STATS)
OVERALL = TOTAL / len(STATS)
assert len(STATS) == 12 and TOTAL == 426 and OVERALL == 35.5
assert all(0 <= v <= 70 for _, v in STATS)
assert DECISION == dict(STATS)['ПРИНЯТИЕ РЕШЕНИЙ']

# Категория, название, две строки эффекта, цена в очках влияния.
# Магазин намеренно далёк от стартового баланса: даже минимум выше 68 ИВ.
SHOP_ITEMS = [
    ('ФИНТ', 'ЛОЖНЫЙ ЗАМАХ', ('открывает приём', 'в тренировочном режиме'), 1000),
    ('ФИНТ', 'ФИНТ КРОЙФА', ('открывает приём', 'в тренировочном режиме'), 1500),
    ('ФИНТ', 'РУЛЕТКА', ('открывает разворот', 'под давлением'), 2500),
    ('ФИНТ', 'ЭЛАСТИКО', ('открывает приём', 'для игры один в один'), 4000),
    ('ПОСТОЯННЫЙ АТРИБУТ', 'ТОЧЕЧНЫЙ РОСТ', ('+1 к выбранной', 'характеристике'), 5000),
    ('ПОСТОЯННЫЙ АТРИБУТ', 'СЛАБАЯ НОГА', ('снижает штраф', 'нерабочей ноги'), 6000),
    ('ПОСТОЯННЫЙ АТРИБУТ', 'СКАНИРОВАНИЕ', ('+1 к видению', 'постоянно'), 4500),
    ('УСИЛЕНИЕ НА МАТЧ', 'ДОМАШНЕЕ ПОЛЕ', ('+1 ко всем характеристикам', 'на 1 домашний матч'), 3000),
    ('УСИЛЕНИЕ НА МАТЧ', 'ХОЛОДНАЯ ГОЛОВА', ('+3 к принятию решений', 'на 1 матч'), 1800),
    ('УСИЛЕНИЕ НА МАТЧ', 'ВТОРОЕ ДЫХАНИЕ', ('+3 к выносливости', 'после 75′ · на 1 матч'), 2200),
]
assert len(SHOP_ITEMS) >= 10
assert min(item[3] for item in SHOP_ITEMS) >= 1000
assert {item[0] for item in SHOP_ITEMS} == {'ФИНТ', 'ПОСТОЯННЫЙ АТРИБУТ', 'УСИЛЕНИЕ НА МАТЧ'}

_CMAP = set()
for family in ('Bold', 'Medium', 'Light'):
    for table in TTFont(f'fonts/Exo2-{family}.ttf')['cmap'].tables:
        _CMAP |= set(table.cmap.keys())


class SafeText:
    def __init__(self, panel, pad=(24, 58, 24, 18)):
        self.p = panel
        self.pad = pad
        self.items = []

    def text(self, xy, text, font, fill, anchor='la', glow=False):
        for ch in text:
            if ch not in ' \n' and ord(ch) not in _CMAP:
                raise ValueError(f'нет глифа {ch!r} в «{text}»')
        if glow:
            col = glow if isinstance(glow, tuple) else self.p.st['edge']
            bb = glow_text(self.p.lay, xy, text, font, fill, col, anchor=anchor,
                           radius=8, strength=0.68)
            self.p.d = ImageDraw.Draw(self.p.lay)
        else:
            bb = self.p.d.textbbox(xy, text, font=font, anchor=anchor)
            self.p.d.text(xy, text, font=font, fill=fill, anchor=anchor)
        self.items.append((text, bb))
        return bb

    def check(self, overlap=False):
        x0, y0, x1, y1 = self.p.box
        l, t, r, b = self.pad
        for text, bb in self.items:
            if bb[0] < x0 + l - 3 or bb[2] > x1 - r + 3 or bb[1] < y0 + t - 3 or bb[3] > y1 - b + 3:
                raise ValueError(f'«{text}» выходит за панель: {bb} / {self.p.box}')
        if overlap:
            for i, (ta, a) in enumerate(self.items):
                for tb, b2 in self.items[i + 1:]:
                    if a[0] < b2[2] - 2 and b2[0] < a[2] - 2 and a[1] < b2[3] - 2 and b2[1] < a[3] - 2:
                        raise ValueError(f'пересечение «{ta}» / «{tb}»')


def save(panel, safe, path):
    safe.check(overlap=False)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    OUT.append(panel.save(path))


def item_box(p, sc, y0, y1, kind, title, detail_lines, price):
    subbox(p, p.x0 + 30, y0, p.x1 - 30, y1, alpha=102)
    sc.text((p.g['lbl'], y0 + 24), kind, F('m', 15), p.st['dim'] + (230,))
    sc.text((p.g['lbl'], y0 + 52), title, F('b', 25), (248, 253, 255, 255), glow=True)
    yy = y0 + 92
    for line in detail_lines:
        sc.text((p.g['lbl'], yy), line, F('l', 16), p.st['ink'] + (225,))
        yy += 27
    sc.text((p.g['val'], y1 - 40), price, F('b', 24), YEL + (255,), anchor='ra', glow=YEL)


# 14 · первый квест — одно условие, награда +2 к принятию решений
box = (42, 76, 758, 844)
p = Panel(void_bg('n', box, h=920), box, 'n', frame_id=None)
sc = SafeText(p)
rank_crest(p, p.cx, 142, 244, w_half=82)
sc.text((p.cx, 192), 'F−', F('b', 58), (244, 252, 255, 255), anchor='mm', glow=True)
sc.text((p.cx, 264), sp('КВЕСТ', 2), F('b', 26), p.st['hot'] + (252,), anchor='ma', glow=True)
p.div(314)
subbox(p, box[0] + 38, 342, box[2] - 38, 500, alpha=108)
dx = p.g['lbl'] + 2
p.d.polygon([(dx, 409), (dx + 9, 394), (dx + 18, 409), (dx + 9, 424)],
            fill=p.st['hot'] + (245,), outline=p.st['edge'] + (255,))
sc.text((dx + 34, 374), '0 ПОТЕРЬ В СВОЕЙ ТРЕТИ', F('b', 26), INK + (255,), glow=True)
sc.text((dx + 34, 424), 'ДО ФИНАЛЬНОГО СВИСТКА', F('m', 24), INK + (245,))
p.div(530)
sc.text((p.cx, 556), sp('НАГРАДА', 2), F('m', 17), p.st['dim'] + (225,), anchor='ma')
sc.text((p.cx, 592), 'ПРИНЯТИЕ РЕШЕНИЙ', F('b', 27), p.st['ink'] + (255,), anchor='ma', glow=True)
bb = num_change(p, 650, DECISION, REWARD, size=46, color_r=(112, 224, 255), align='center')
sc.items.append(('26-28', bb))
sc.text((p.cx, 726), 'награда только при выполнении', F('l', 18), p.st['dim'] + (220,), anchor='ma')
save(p, sc, 'ch1/p07_quest.png')


# Служебная панель выхода (не входит в ленту, но остаётся согласованной)
box = (44, 72, 756, 496)
p = Panel(void_bg('g', box, h=568), box, 'g', frame_id=None)
sc = SafeText(p)
sc.text((p.cx, 150), sp('ВЫХОД НА ПОЛЕ', 2), F('b', 31), p.st['hot'] + (255,), anchor='ma', glow=True)
p.div(212)
sc.text((p.cx, 240), '72′ · ЗАМЕНА', F('b', 30), p.st['ink'] + (252,), anchor='ma', glow=True)
p.div(302)
sc.text((p.cx, 322), 'КВЕСТ АКТИВЕН', F('m', 24), p.st['ink'] + (240,), anchor='ma')
sc.text((p.cx, 366), '0 ПОТЕРЬ В СВОЕЙ ТРЕТИ', F('m', 19), p.st['ink'] + (235,), anchor='ma')
sc.text((p.cx, 404), 'ДО ФИНАЛЬНОГО СВИСТКА', F('l', 18), p.st['dim'] + (225,), anchor='ma')
save(p, sc, 'ch1/p18_enter.png')


# 19 · провал без штрафа: решение остаётся 26
box = (42, 76, 758, 624)
p = Panel(void_bg('f', box, h=700), box, 'f', frame_id=None)
sc = SafeText(p)
sc.text((p.cx, 150), sp('НЕ ВЫПОЛНЕНО', 2), F('b', 34), (255, 240, 238, 255), anchor='ma', glow=True)
p.div(214)
subbox(p, box[0] + 40, 238, box[2] - 40, 382, alpha=110)
sc.text((p.cx, 264), '0 ПОТЕРЬ В СВОЕЙ ТРЕТИ', F('m', 22), p.st['ink'] + (245,), anchor='ma')
sc.text((p.cx, 312), 'ПРИНЯТИЕ РЕШЕНИЙ 26', F('b', 28), (255, 245, 242, 255), anchor='ma', glow=True)
sc.text((p.cx, 354), 'БЕЗ ИЗМЕНЕНИЙ', F('m', 20), p.st['dim'] + (235,), anchor='ma')
p.div(412)
sc.text((p.cx, 444), 'НАГРАДА НЕ ПОЛУЧЕНА', F('m', 20), RED + (245,), anchor='ma')
sc.text((p.cx, 492), '88′ · ПОТЕРЯ ПОД ПРЕССИНГОМ', F('m', 22), p.st['ink'] + (242,), anchor='ma')
sc.text((p.cx, 540), 'штрафа за провал нет', F('l', 18), p.st['dim'] + (215,), anchor='ma')
save(p, sc, 'ch1/p23_fail.png')


# 24 · профиль после матча: все 12 характеристик + понятное ИВ
box = (42, 76, 758, 1424)
p = Panel(void_bg('n', box, h=1500), box, 'n', frame_id=None)
sc = SafeText(p, pad=(18, 58, 18, 18))
sc.text((p.cx, 142), sp('ПРОФИЛЬ ИГРОКА', 2), F('b', 32), (245, 252, 255, 255), anchor='ma', glow=True)
sc.text((p.cx, 188), 'ВЕТРОВ · ЦПЗ · 15 ЛЕТ', F('m', 18), p.st['dim'] + (235,), anchor='ma')
p.div(222)
sc.text((p.cx, 246), '12 ХАРАКТЕРИСТИК', F('m', 18), p.st['ink'] + (240,), anchor='ma')
subbox(p, 68, 282, 732, 790, alpha=100)
p.d.line([(400, 298), (400, 774)], fill=p.st['edge'] + (85,), width=1)
left = STATS[:6]
right = STATS[6:]
for col, rows in enumerate((left, right)):
    lx = 92 if col == 0 else 424
    vx = 366 if col == 0 else 708
    for i, (name, value) in enumerate(rows):
        y = 312 + i * 78
        size = 14 if len(name) > 17 else 17
        sc.text((lx, y), name, F('m', size), p.st['dim'] + (238,))
        sc.text((vx, y - 5), str(value), F('b', 25), p.st['hot'] + (255,), anchor='ra', glow=True)
        if i < 5:
            p.d.line([(lx, y + 38), (vx, y + 38)], fill=p.st['edge'] + (40,), width=1)
p.div(826)
sc.text((p.cx, 852), f'ОБЩ {OVERALL:.2f}', F('b', 27), p.st['ink'] + (250,), anchor='ma')
sc.text((p.cx, 892), 'квест не выполнен · характеристики не изменились', F('l', 16), p.st['dim'] + (215,), anchor='ma')
p.div(928)
sc.text((p.cx, 956), 'ИВ — ИНДЕКС ВЛИЯНИЯ', F('b', 26), p.st['hot'] + (255,), anchor='ma', glow=True)
sc.text((p.cx, 1000), f'ТЕКУЩИЙ БАЛАНС · {IV}', F('m', 22), YEL + (250,), anchor='ma')
subbox(p, 90, 1042, 710, 1252, alpha=105)
sc.text((p.cx, 1080), 'ОЧКИ ИВ НАЧИСЛЯЮТСЯ ЗА ДЕЙСТВИЯ,', F('m', 17), p.st['ink'] + (240,), anchor='ma')
sc.text((p.cx, 1114), 'КОТОРЫЕ МЕНЯЮТ ХОД МАТЧА', F('b', 20), p.st['hot'] + (250,), anchor='ma')
sc.text((p.cx, 1170), 'очки накапливаются', F('l', 18), p.st['dim'] + (225,), anchor='ma')
sc.text((p.cx, 1204), 'и расходуются в магазине влияния', F('l', 18), p.st['dim'] + (225,), anchor='ma')
p.div(1284)
subbox(p, 218, 1302, 582, 1386, alpha=105)
sc.text((p.cx, 1318), 'ВКЛАДКА «МАГАЗИН»', F('m', 19), p.st['ink'] + (245,), anchor='ma')
sc.text((p.cx, 1356), 'коснись, чтобы открыть', F('l', 16), p.st['dim'] + (220,), anchor='ma')
save(p, sc, 'ch1/p37_day.png')


# 27 · длинный магазин влияния: 10 товаров, все недоступны при балансе 68
SHOP_H = 2500
box = (42, 76, 758, SHOP_H - 76)
p = Panel(void_bg('n', box, h=SHOP_H), box, 'n', frame_id=None)
sc = SafeText(p, pad=(18, 58, 18, 18))
sc.text((p.cx, 142), sp('МАГАЗИН ВЛИЯНИЯ', 2), F('b', 31), (245, 252, 255, 255), anchor='ma', glow=True)
sc.text((p.cx, 190), f'БАЛАНС · {IV} ИВ', F('m', 21), YEL + (250,), anchor='ma')
sc.text((p.cx, 222), f'ТОВАРОВ · {len(SHOP_ITEMS)}', F('l', 16), p.st['dim'] + (220,), anchor='ma')
p.div(250)
for i, (kind, title, lines, price) in enumerate(SHOP_ITEMS):
    y0 = 278 + i * 200
    item_box(p, sc, y0, y0 + 180, kind, title, lines,
             f'{price:,}'.replace(',', ' ') + ' ИВ')
p.div(2298)
sc.text((p.cx, 2324), 'НЕДОСТАТОЧНО ИВ', F('b', 24), RED + (255,), anchor='ma', glow=RED)
sc.text((p.cx, 2366), 'минимальная цена · 1 000 ИВ', F('m', 18), p.st['dim'] + (230,), anchor='ma')
sc.text((p.cx, 2386), 'покупка недоступна', F('l', 17), p.st['dim'] + (205,), anchor='ma')
save(p, sc, 'ch1/p38_shop.png')

print(f'Глава 1: собрано панелей {len(OUT)}')
print(f'Характеристики: {TOTAL} / {OVERALL:.2f} · ИВ {IV}')
for path in OUT:
    print(' ', path)
