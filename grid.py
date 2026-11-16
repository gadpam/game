"""
Единая сетка панелей Системы («Пока повременим»).
Все панели собираются ТОЛЬКО через этот модуль — чтобы пропорции не плыли.

Экран 800x1600. Панель может занимать часть кадра, но внутренняя сетка
всегда одна: отступы, вертикали, шаг строк, размеры шрифтов.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 1600
FONT = {'b': 'fonts/Exo2-Bold.ttf', 'm': 'fonts/Exo2-Medium.ttf', 'l': 'fonts/Exo2-Light.ttf'}
_fcache = {}

# ─── палитра состояний ───────────────────────────────────────────
STATE = {
    'n': dict(edge=(120, 210, 255), inner=(196, 236, 255),
              glass=((12, 24, 38), (6, 14, 24)),
              ink=(238, 246, 255), dim=(150, 178, 202)),
    'g': dict(edge=(120, 235, 180), inner=(186, 246, 220),
              glass=((10, 30, 24), (4, 14, 11)),
              ink=(226, 250, 238), dim=(140, 196, 168)),
    'f': dict(edge=(255, 128, 108), inner=(255, 205, 196),
              glass=((34, 12, 14), (14, 6, 8)),
              ink=(255, 228, 220), dim=(216, 162, 154)),
}
YELLOW = (255, 222, 96)


def F(weight, size):
    key = (weight, size)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(FONT[weight], size)
    return _fcache[key]


def sp(text, n=2):
    """Разрядка в ширину — шапка панели и группы."""
    return (' ' * n).join(list(text))


def cover(im, w=W, h=H, focus=3):
    """Кроп с фокусом по вертикали: 0 — верх, 3 — центр, 10 — низ."""
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((int(iw * s + 1), int(ih * s + 1)), Image.LANCZOS)
    iw, ih = im.size
    left = (iw - w) // 2
    top = int((ih - h) * focus / 10)
    return im.crop((left, top, left + w, top + h))


# ─── геометрия ───────────────────────────────────────────────────
PAD_IN = 62          # отступ содержимого от рамки
ROW = 34             # шаг строки в списках
BARW = 216           # длина полосы
GAP_BAR_VAL = 88     # от конца полосы до правого края цифры


def arrow(d, x_head, y, length=18, color=(150, 178, 202), alpha=225, width=2):
    """Стрелка линиями. В Exo 2 символа U+2192 нет — текстом печатать нельзя."""
    x0 = x_head - length
    d.line([(x0, y), (x_head - 2, y)], fill=color + (alpha,), width=width)
    d.line([(x_head - 7, y - 4), (x_head - 1, y)], fill=color + (alpha,), width=width)
    d.line([(x_head - 7, y + 4), (x_head - 1, y)], fill=color + (alpha,), width=width)


def num_change(p, y, left, right, size=34, color_r=(255, 128, 108), left_w='b', right_w='b'):
    """«26 → 25» по правому краю: цифры + рисованная стрелка между ними."""
    fl, fr = F(left_w, size), F(right_w, size)
    wl, wr = p.d.textlength(str(left), font=fl), p.d.textlength(str(right), font=fr)
    gap = 30
    x_r = p.g['val'] - wr
    x_head = x_r - 6
    x_l = x_head - 18 - 8 - wl
    p.d.text((x_l, y), str(left), font=fl, fill=p.st['ink'] + (255,))
    arrow(p.d, x_head, y + size * 0.36, length=18, color=p.st['dim'], alpha=230, width=2)
    p.d.text((x_r, y), str(right), font=fr, fill=color_r + (255,))


def geometry(x0, x1):
    """Возвращает 4 вертикали, к которым привязано всё содержимое."""
    return dict(
        lbl=x0 + PAD_IN,        # подписи
        bar0=x1 - PAD_IN - GAP_BAR_VAL - BARW,   # начало полосы
        bar1=x1 - PAD_IN - GAP_BAR_VAL,          # конец полосы
        val=x1 - PAD_IN,        # цифры, по правому краю
    )


class Panel:
    """Панель Системы. Рисует рамку, стекло, шапку и разделители."""

    def __init__(self, base, box, kind='n', frame_id=None, glow=True):
        self.base = base.convert('RGBA')
        self.box = box
        self.x0, self.y0, self.x1, self.y1 = box
        self.kind = kind
        self.st = STATE[kind]
        self.cx = (self.x0 + self.x1) // 2
        self.g = geometry(self.x0, self.x1)
        self.lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        self._glow(glow)
        self._glass()
        self.d = ImageDraw.Draw(self.lay)
        self._corners()
        self._header(frame_id)

    def _glow(self, on):
        if not on:
            return
        x0, y0, x1, y1 = self.box
        e = self.st['edge']
        dd = ImageDraw.Draw(self.lay)
        for i in range(26, 0, -2):
            a = int(26 * (1 - i / 26) ** 1.5)
            dd.rounded_rectangle([x0 - i, y0 - i, x1 + i, y1 + i],
                                 radius=9, outline=e + (a,), width=3)

    def _glass(self):
        x0, y0, x1, y1 = self.box
        a, b = self.st['glass']
        grad = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dg = ImageDraw.Draw(grad)
        for y in range(y0, y1):
            t = (y - y0) / max(1, (y1 - y0))
            dg.line([(0, y), (W, y)],
                    fill=tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3)) + (198,))
        mask = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle([x0, y0, x1, y1], radius=9, fill=255)
        self.lay.paste(grad, (0, 0), mask)

    def _corners(self):
        x0, y0, x1, y1 = self.box
        e, i = self.st['edge'], self.st['inner']
        d = ImageDraw.Draw(self.lay)
        d.rounded_rectangle([x0, y0, x1, y1], radius=9, outline=e + (255,), width=3)
        d.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=6, outline=i + (65,), width=1)
        L = 30
        for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(cx, cy + dy * L), (cx, cy), (cx + dx * L, cy)], fill=e + (255,), width=4)
            d.polygon([(cx + dx * 7, cy + dy * 3), (cx + dx * 11, cy + dy * 7),
                       (cx + dx * 7, cy + dy * 11), (cx + dx * 3, cy + dy * 7)], fill=e + (255,))

    def _header(self, frame_id):
        x0, y0, x1 = self.x0, self.y0, self.x1
        e, ink, dim, d = self.st['edge'], self.st['ink'], self.st['dim'], self.d
        t = sp('СИСТЕМА', 2)
        f = F('m', 19)
        tw = d.textlength(t, font=f)
        d.text((self.cx, y0 + 28), t, font=f, fill=ink + (242,), anchor='ma')
        ly = y0 + 38
        d.line([(x0 + 82, ly), (self.cx - tw / 2 - 26, ly)], fill=dim + (130,), width=1)
        d.line([(self.cx + tw / 2 + 26, ly), (x1 - 82, ly)], fill=dim + (130,), width=1)
        for xx in (self.cx - tw / 2 - 15, self.cx + tw / 2 + 15):
            d.polygon([(xx, ly - 3), (xx + 3, ly), (xx, ly + 3), (xx - 3, ly)], fill=e + (205,))
        if frame_id:
            d.text((self.g['val'], y0 + 60), sp(str(frame_id), 1),
                   font=F('l', 11), fill=dim + (135,), anchor='ra')

    # ─── элементы ────────────────────────────────────────────────
    def div(self, y):
        x0, x1, cx, dim, e = self.x0, self.x1, self.cx, self.st['dim'], self.st['edge']
        self.d.line([(x0 + 52, y), (cx - 15, y)], fill=dim + (95,), width=1)
        self.d.line([(cx + 15, y), (x1 - 52, y)], fill=dim + (95,), width=1)
        self.d.polygon([(cx, y - 5), (cx + 5, y), (cx, y + 5), (cx - 5, y)], fill=e + (215,))

    def center(self, y, text, weight='l', size=13, color=None, spacing=None):
        s = sp(text, spacing) if spacing else text
        col = (color if color else self.st['dim']) + (205,)
        self.d.text((self.cx, y), s, font=F(weight, size), fill=col, anchor='ma')

    def left(self, y, text, weight='l', size=15, color=None, alpha=235):
        col = (color if color else self.st['ink'])
        self.d.text((self.g['lbl'], y), text, font=F(weight, size), fill=col + (alpha,))

    def value(self, y, text, weight='m', size=16, color=None):
        col = (color if color else self.st['ink'])
        self.d.text((self.g['val'], y), text, font=F(weight, size), fill=col + (245,), anchor='ra')

    def group(self, y, name):
        """Заголовок группы с линейкой до правого края. Возвращает y следующей строки."""
        gl = sp(name, 3)
        f = F('m', 11)
        self.d.text((self.g['lbl'], y), gl, font=f, fill=self.st['dim'] + (185,))
        gw = self.d.textlength(gl, font=f)
        self.d.line([(self.g['lbl'] + gw + 16, y + 6), (self.g['val'], y + 6)],
                    fill=self.st['dim'] + (50,), width=1)
        return y + 32

    def row(self, y, name, val, color=None, bar=True):
        """Строка списка: подпись · полоса · цифра. Шаг ровно ROW."""
        e = self.st['edge']
        col = (color if color else self.st['ink'])
        self.d.text((self.g['lbl'], y + 3), name, font=F('l', 15), fill=col + (235,))
        if bar:
            by = y + 11
            self.d.line([(self.g['bar0'], by), (self.g['bar1'], by)],
                        fill=(120, 160, 200, 45), width=3)
            self.d.line([(self.g['bar0'], by),
                         (self.g['bar0'] + max(3, int(BARW * val / 100)), by)],
                        fill=e + (200,), width=3)
        hot = val >= 85
        self.d.text((self.g['val'], y + 2), str(val),
                    font=F('b' if hot else 'm', 19 if hot else 16),
                    fill=col + (255,), anchor='ra')
        return y + ROW

    # ─── вывод ───────────────────────────────────────────────────
    def save(self, path):
        Image.alpha_composite(self.base, self.lay).convert('RGB').save(path)
        return path


# ─── вертикальный поток ──────────────────────────────────────────
def text_h(weight, size):
    """Реальная высота строки в пикселях."""
    f = F(weight, size)
    a, d = f.getmetrics()
    return a + d


class Flow:
    """Раскладывает блоки сверху вниз, распределяя свободное место в зазоры.

    Каждый блок — функция (panel, y) -> высота. Зазоры задаются весами:
    чем больше вес, тем больше воздуха до блока.
    """

    def __init__(self, panel, y_top, y_bottom):
        self.p = panel
        self.top = y_top
        self.bottom = y_bottom
        self.blocks = []      # (weight_before, fn, h)

    def add(self, fn, h, weight=1.0):
        self.blocks.append([weight, fn, h])
        return self

    def run(self):
        used = sum(b[2] for b in self.blocks)
        wsum = sum(b[0] for b in self.blocks)
        free = self.bottom - self.top - used
        if free < 0:
            raise ValueError(f'не влезает: нужно {used}, есть {self.bottom-self.top}')
        y = self.top
        for w, fn, h in self.blocks:
            y += free * (w / wsum)
            fn(self.p, int(round(y)))
            y += h
        return y

    def check(self):
        """Проверка: блоки не пересекаются и не выходят за границы."""
        used = sum(b[2] for b in self.blocks)
        free = self.bottom - self.top - used
        y = self.top
        spans = []
        for w, fn, h in self.blocks:
            y += free * (w / sum(b[0] for b in self.blocks))
            spans.append((int(y), int(y + h)))
            y += h
        for i in range(len(spans) - 1):
            if spans[i][1] > spans[i + 1][0]:
                raise ValueError(f'перекрытие блоков {i} и {i+1}: {spans[i]} / {spans[i+1]}')
        if spans and spans[-1][1] > self.bottom:
            raise ValueError('последний блок выходит за низ')
        return spans
